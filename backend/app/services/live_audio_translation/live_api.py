"""One request-local Gemini Live WebSocket for speech-to-speech translation."""

from __future__ import annotations

import asyncio
import base64
import binascii
import json
import logging
import os
import wave
from pathlib import Path
from typing import Callable
from urllib.parse import quote

from websockets.asyncio.client import connect as websocket_connect


WS_URL = ("wss://generativelanguage.googleapis.com/ws/"
          "google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent")
CHUNK_BYTES = 3200  # 100 ms, signed 16-bit mono 16 kHz
MAX_OUTPUT_BYTES = 32 * 1024 * 1024
WIRE_LOGGER = logging.getLogger(__name__ + ".wire")
WIRE_LOGGER.setLevel(logging.WARNING)  # WebSocket DEBUG frames include the key and audio.


class LiveTranslationError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _upstream_code(code: object) -> str:
    if code in (401, 403):
        return "invalid_api_key"
    if code == 404:
        return "model_unavailable"
    if code in (429, 8):
        return "quota_or_rate_limit"
    if code in (503, 504):
        return "connection_failure"
    return "live_api_error"


async def translate_pcm(source: Path, output: Path, *, key: str, model: str,
                        connect=websocket_connect, pace=asyncio.sleep,
                        on_connected: Callable[[], None] | None = None,
                        drain_seconds: float = 4.0, final_timeout: float = 30.0) -> None:
    """Stream real-time PCM, collect translated PCM, and atomically publish WAV."""
    if not key or not model or not model.replace("-", "").replace("_", "").replace(".", "").isalnum():
        raise LiveTranslationError("invalid_configuration")
    uri = f"{WS_URL}?key={quote(key, safe='')}"
    raw_output = output.with_suffix(".output.pcm")
    wav_output = output.with_suffix(".partial.wav")
    sender = None
    try:
        async with connect(uri, open_timeout=10, close_timeout=5,
                           max_size=1024 * 1024, logger=WIRE_LOGGER) as socket:
            await socket.send(json.dumps({"setup": {
                "model": f"models/{model}",
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "translationConfig": {"targetLanguageCode": "vi",
                                                           "echoTargetLanguage": True}},
            }}))
            first = await asyncio.wait_for(socket.recv(), timeout=15)
            try:
                setup = json.loads(first)
            except (TypeError, json.JSONDecodeError) as error:
                raise LiveTranslationError("malformed_response") from error
            if not isinstance(setup, dict):
                raise LiveTranslationError("malformed_response")
            if isinstance(setup.get("error"), dict):
                raise LiveTranslationError(_upstream_code(setup["error"].get("code")))
            if "setupComplete" not in setup:
                raise LiveTranslationError("malformed_response")
            if on_connected is not None:
                on_connected()

            sent_end = asyncio.Event()
            sent_end_at = None

            async def send_input():
                nonlocal sent_end_at
                with source.open("rb") as file:
                    while chunk := file.read(CHUNK_BYTES):
                        await socket.send(json.dumps({"realtimeInput": {"audio": {
                            "data": base64.b64encode(chunk).decode("ascii"),
                            "mimeType": "audio/pcm;rate=16000",
                        }}}))
                        await pace(len(chunk) / 32000)
                await socket.send(json.dumps({"realtimeInput": {"audioStreamEnd": True}}))
                sent_end_at = asyncio.get_running_loop().time()
                sent_end.set()

            sender = asyncio.create_task(send_input())
            size = 0
            complete = False
            last_audio_at = None
            loop = asyncio.get_running_loop()
            with raw_output.open("wb") as file:
                while not complete:
                    if sender.done():
                        sender.result()
                    if sent_end.is_set():
                        now = loop.time()
                        if now >= sent_end_at + final_timeout:
                            if size:
                                raise LiveTranslationError("timeout")
                            raise LiveTranslationError("no_translated_audio")
                        quiet_at = max(sent_end_at, last_audio_at or sent_end_at) + drain_seconds
                        if size and now >= quiet_at:
                            break
                        wait = min(sent_end_at + final_timeout - now,
                                   quiet_at - now if size else final_timeout)
                    else:
                        # Recheck the sender every second even if Gemini is quiet.
                        wait = 1.0
                    try:
                        frame = await asyncio.wait_for(socket.recv(), timeout=max(0.001, wait))
                    except TimeoutError:
                        continue
                    try:
                        data = json.loads(frame)
                    except (TypeError, json.JSONDecodeError) as error:
                        raise LiveTranslationError("malformed_response") from error
                    if not isinstance(data, dict):
                        raise LiveTranslationError("malformed_response")
                    if isinstance(data.get("error"), dict):
                        raise LiveTranslationError(_upstream_code(data["error"].get("code")))
                    content = data.get("serverContent")
                    if content is None:
                        continue
                    if not isinstance(content, dict):
                        raise LiveTranslationError("malformed_response")
                    turn = content.get("modelTurn")
                    parts = turn.get("parts", []) if isinstance(turn, dict) else []
                    if not isinstance(parts, list):
                        raise LiveTranslationError("malformed_response")
                    for part in parts:
                        inline = part.get("inlineData") if isinstance(part, dict) else None
                        if inline is None:
                            continue
                        if not isinstance(inline, dict) or inline.get("mimeType") != "audio/pcm;rate=24000":
                            raise LiveTranslationError("malformed_response")
                        try:
                            chunk = base64.b64decode(inline["data"], validate=True)
                        except (KeyError, TypeError, binascii.Error) as error:
                            raise LiveTranslationError("malformed_response") from error
                        if not chunk or len(chunk) % 2:
                            raise LiveTranslationError("malformed_response")
                        size += len(chunk)
                        if size > MAX_OUTPUT_BYTES:
                            raise LiveTranslationError("session_limit")
                        file.write(chunk)
                        last_audio_at = loop.time()
                    if content.get("turnComplete") and sent_end.is_set():
                        complete = True
            await sender
            if size == 0:
                raise LiveTranslationError("no_translated_audio")
            with wave.open(str(wav_output), "wb") as wav, raw_output.open("rb") as file:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(24000)
                while chunk := file.read(64 * 1024):
                    wav.writeframes(chunk)
            os.replace(wav_output, output)
    except LiveTranslationError:
        raise
    except TimeoutError as error:
        raise LiveTranslationError("timeout") from error
    except Exception as error:
        status = getattr(getattr(error, "response", None), "status_code", None)
        raise LiveTranslationError(_upstream_code(status) if status else "connection_failure") from None
    finally:
        if sender is not None and not sender.done():
            sender.cancel()
            await asyncio.gather(sender, return_exceptions=True)
        raw_output.unlink(missing_ok=True)
        wav_output.unlink(missing_ok=True)

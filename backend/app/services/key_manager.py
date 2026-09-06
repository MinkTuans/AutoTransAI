"""
KeyManager Service — Multi-API Key Management & Failover System.

Handles API key rotation, state tracking, cooldowns, local statistics,
and persistence to data/api_keys.json.
"""

from __future__ import annotations

import asyncio
from enum import Enum
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.config import get_settings
from app.core import get_logger

logger = get_logger(__name__)
settings = get_settings()

STORAGE_FILE = settings.DATA_DIR / "api_keys.json"


class KeyStatus(str, Enum):
    ACTIVE = "active"             # Currently active / selected
    READY = "ready"               # Ready in pool
    RATE_LIMITED = "rate_limited" # Rate limited (cooldown)
    EXHAUSTED = "exhausted"       # Out of credits / balance
    INVALID = "invalid"           # 401/403 invalid API key
    DISABLED = "disabled"         # Disabled by user


class KeyEntry:
    def __init__(
        self,
        key_id: str,
        provider_id: str,
        api_key: str,
        priority: int = 1,
        status: str = KeyStatus.READY.value,
        total_requests: int = 0,
        successful_requests: int = 0,
        failed_requests: int = 0,
        last_used_at: float | None = None,
        last_error: str | None = None,
        cooldown_until: float | None = None,
        quota_info: dict | None = None,
    ):
        self.key_id = key_id
        self.provider_id = provider_id
        self.api_key = api_key
        self.priority = priority
        self.status = status
        self.total_requests = total_requests
        self.successful_requests = successful_requests
        self.failed_requests = failed_requests
        self.last_used_at = last_used_at
        self.last_error = last_error
        self.cooldown_until = cooldown_until
        self.quota_info = quota_info or {"status": "Unknown / Not available"}

    @property
    def masked_key(self) -> str:
        k = self.api_key.strip()
        if len(k) <= 8:
            return "********"
        return f"{k[:4]}-***-{k[-4:]}"

    def to_dict(self, include_raw_key: bool = False) -> Dict[str, Any]:
        data = {
            "key_id": self.key_id,
            "provider_id": self.provider_id,
            "masked_key": self.masked_key,
            "priority": self.priority,
            "status": self.status,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "last_used_at": self.last_used_at,
            "last_error": self.last_error,
            "cooldown_until": self.cooldown_until,
            "quota_info": self.quota_info,
        }
        if include_raw_key:
            data["api_key"] = self.api_key
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KeyEntry:
        return cls(
            key_id=data["key_id"],
            provider_id=data["provider_id"],
            api_key=data["api_key"],
            priority=data.get("priority", 1),
            status=data.get("status", KeyStatus.READY.value),
            total_requests=data.get("total_requests", 0),
            successful_requests=data.get("successful_requests", 0),
            failed_requests=data.get("failed_requests", 0),
            last_used_at=data.get("last_used_at"),
            last_error=data.get("last_error"),
            cooldown_until=data.get("cooldown_until"),
            quota_info=data.get("quota_info"),
        )


class KeyManager:
    """Singleton Key Manager servicing all providers."""

    _instance: Optional[KeyManager] = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        self.keys: Dict[str, List[KeyEntry]] = {}  # provider_id -> list of KeyEntry
        self._load_keys()

    @classmethod
    def get_instance(cls) -> KeyManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_keys(self) -> None:
        """Load keys from data/api_keys.json or bootstrap from .env."""
        STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if STORAGE_FILE.exists():
            try:
                raw_data = json.loads(STORAGE_FILE.read_text(encoding="utf-8"))
                for p_id, key_list in raw_data.items():
                    self.keys[p_id] = [KeyEntry.from_dict(k) for k in key_list]
                logger.info("Loaded API keys from storage", file=str(STORAGE_FILE))
                return
            except Exception as e:
                logger.error("Failed to parse api_keys.json, bootstrapping from env", error=str(e))

        # Bootstrap from .env if storage file does not exist or is invalid
        self._bootstrap_from_env()
        self._save_keys()

    def _bootstrap_from_env(self) -> None:
        """Populate initial key pool from .env variables for all providers."""
        self.keys = {
            "gemini": [],
            "openai": [],
            "google_cloud_tts": [],
            "elevenlabs": [],
            "kling": [],
            "fal": [],
        }

        # Helper to populate pool from primary env var + indexed env vars
        provider_env_map = {
            "gemini": ("GEMINI_API_KEY", "GEMINI_API_KEY_"),
            "openai": ("OPENAI_API_KEY", "OPENAI_API_KEY_"),
            "google_cloud_tts": ("GOOGLE_CLOUD_TTS_API_KEY", "GOOGLE_CLOUD_TTS_API_KEY_"),
            "elevenlabs": ("ELEVENLABS_API_KEY", "ELEVENLABS_API_KEY_"),
            "kling": ("KLING_API_KEY", "KLING_API_KEY_"),
            "fal": ("FAL_API_KEY", "FAL_API_KEY_"),
        }

        for p_id, (main_env, prefix) in provider_env_map.items():
            keys_found = []
            val = getattr(settings, main_env, "") or os.getenv(main_env, "")
            if val and isinstance(val, str):
                for line in val.splitlines():
                    clean = line.strip()
                    if clean and clean not in keys_found:
                        keys_found.append(clean)

            for idx in range(1, 10):
                k = os.getenv(f"{prefix}{idx}")
                if k and k.strip() and k.strip() not in keys_found:
                    keys_found.append(k.strip())

            for idx, k in enumerate(keys_found, start=1):
                self.keys[p_id].append(
                    KeyEntry(
                        key_id=f"{p_id}_key_{idx}",
                        provider_id=p_id,
                        api_key=k,
                        priority=idx,
                        status=KeyStatus.READY.value,
                    )
                )


    def _save_keys(self) -> None:
        """Persist current key configuration to storage file and sync to .env."""
        try:
            data = {}
            for p_id, k_list in self.keys.items():
                data[p_id] = [k.to_dict(include_raw_key=True) for k in k_list]
            STORAGE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            self._sync_env_file()
        except Exception as e:
            logger.error("Failed to save api_keys.json / .env", error=str(e))

    def _sync_env_file(self) -> None:
        """Synchronize primary and multi-keys for all AI providers to .env file."""
        try:
            from app.config import ENV_FILE_PATH
            env_path = Path(ENV_FILE_PATH)
            if not env_path.exists():
                return

            lines = env_path.read_text(encoding="utf-8").splitlines()
            new_lines = []

            provider_env_map = {
                "gemini": "GEMINI_API_KEY",
                "openai": "OPENAI_API_KEY",
                "google_cloud_tts": "GOOGLE_CLOUD_TTS_API_KEY",
                "elevenlabs": "ELEVENLABS_API_KEY",
                "kling": "KLING_API_KEY",
                "fal": "FAL_API_KEY",
            }

            managed_prefixes = [f"{var}" for var in provider_env_map.values()]

            # Keep non-managed key lines
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("# --- Auto-Synchronized"):
                    continue
                skip = False
                for prefix in managed_prefixes:
                    if stripped.startswith(f"{prefix}=") or stripped.startswith(f"{prefix}_"):
                        skip = True
                        break
                if not skip:
                    new_lines.append(line)

            # Append auto-synchronized provider key section
            new_lines.append("# --- Auto-Synchronized AI Provider API Keys ---")
            for p_id, main_env in provider_env_map.items():
                p_keys = sorted(self.keys.get(p_id, []), key=lambda x: x.priority)
                for idx, k in enumerate(p_keys, start=1):
                    var_name = main_env if idx == 1 else f"{main_env}_{idx}"
                    new_lines.append(f"{var_name}={k.api_key}")
                    if idx == 1 and k.api_key:
                        os.environ[main_env] = k.api_key
                        setattr(settings, main_env, k.api_key)

            env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        except Exception as e:
            logger.error("Failed to sync .env file", error=str(e))

    async def get_active_key(self, provider_id: str) -> KeyEntry | None:
        """
        Get highest-priority usable key for a provider.
        Auto-resets rate-limited keys if cooldown expired.
        """
        async with self._lock:
            k_list = self.keys.get(provider_id, [])
            now = time.time()

            usable_keys: List[KeyEntry] = []
            for k in k_list:
                if k.status == KeyStatus.DISABLED or k.status == KeyStatus.INVALID or k.status == KeyStatus.EXHAUSTED:
                    continue

                if k.status == KeyStatus.RATE_LIMITED:
                    if k.cooldown_until and now >= k.cooldown_until:
                        logger.info("Key rate limit cooldown expired, resetting to READY", key_id=k.key_id)
                        k.status = KeyStatus.READY.value
                        k.cooldown_until = None
                        usable_keys.append(k)
                    else:
                        continue
                else:
                    usable_keys.append(k)

            if not usable_keys:
                logger.warning("No usable API key available for provider", provider_id=provider_id)
                return None

            # Sort by priority ascending, then by total_requests ascending
            usable_keys.sort(key=lambda x: (x.priority, x.total_requests))
            selected = usable_keys[0]
            selected.last_used_at = now
            self._save_keys()
            return selected

    async def report_result(
        self,
        provider_id: str,
        key_id: str,
        success: bool,
        status_code: int = 200,
        error_message: str = "",
        details: dict | None = None,
    ) -> str:
        """
        Report the result of an API call using key_id.
        Applies failover rules to update key status:
        - 401/403 -> INVALID (disable)
        - 429 / Rate Limit -> RATE_LIMITED (cooldown 60s)
        - Quota Exceeded / Balance Empty -> EXHAUSTED (disable)
        - 400 Invalid Param -> DO NOT change status (request error)
        - 5xx / Timeout -> Keep READY (allow retry)

        Returns action description string (e.g. "Key marked EXHAUSTED, switching key").
        """
        async with self._lock:
            k_list = self.keys.get(provider_id, [])
            target_key = next((k for k in k_list if k.key_id == key_id), None)
            if not target_key:
                return "Key not found"

            target_key.total_requests += 1

            if success:
                target_key.successful_requests += 1
                target_key.status = KeyStatus.ACTIVE.value
                target_key.last_error = None
                self._save_keys()
                return "Success"

            target_key.failed_requests += 1
            target_key.last_error = error_message
            err_lower = error_message.lower()

            action_summary = "Failed, key retained for retry"

            # Rule 1: 401 or Unauthorized / Invalid key
            if status_code in (401, 403) and ("unauthorized" in err_lower or "invalid key" in err_lower or "token invalid" in err_lower):
                target_key.status = KeyStatus.INVALID.value
                action_summary = f"Key {target_key.masked_key} disabled automatically due to Invalid API Key (HTTP {status_code}). Next key will be used."

            # Rule 2: Balance empty / Quota exceeded
            elif "balance" in err_lower or "quota" in err_lower or "insufficient" in err_lower or "exhausted" in err_lower or status_code in (402, 403) and ("locked" in err_lower or "balance" in err_lower):
                target_key.status = KeyStatus.EXHAUSTED.value
                action_summary = f"Key {target_key.masked_key} disabled automatically due to Exhausted Quota/Balance. Automatically switching to next key."

            # Rule 3: 429 Rate limit
            elif status_code == 429 or "rate limit" in err_lower or "too many requests" in err_lower:
                target_key.status = KeyStatus.RATE_LIMITED.value
                target_key.cooldown_until = time.time() + 60.0
                action_summary = f"Key {target_key.masked_key} hit Rate Limit (HTTP 429). Placed on 60s cooldown. Automatically switching to next key."

            # Rule 4: 400 Invalid request parameter -> DO NOT rotate key!
            elif status_code == 400 or "invalid parameter" in err_lower or "bad request" in err_lower:
                action_summary = f"Invalid request parameter error (HTTP 400). No API key rotation performed."

            # Rule 5: 5xx Server Error or Timeout -> keep ready for retry
            elif status_code >= 500 or "timeout" in err_lower:
                action_summary = f"Provider server error / timeout (HTTP {status_code}). No key status change, standard retry active."

            self._save_keys()
            logger.info("Reported key execution result", key_id=key_id, status=target_key.status, action=action_summary)
            return action_summary

    async def get_keys_for_provider(self, provider_id: str) -> List[Dict[str, Any]]:
        """Return all keys for provider formatted for UI display (masked)."""
        async with self._lock:
            now = time.time()
            res = []
            for k in self.keys.get(provider_id, []):
                d = k.to_dict(include_raw_key=False)
                if k.status == KeyStatus.RATE_LIMITED and k.cooldown_until:
                    rem = int(max(0, k.cooldown_until - now))
                    d["retry_after_seconds"] = rem
                res.append(d)
            return res

    async def add_key(self, provider_id: str, api_key: str, priority: int | None = None) -> KeyEntry:
        """Add a new API key for a provider."""
        async with self._lock:
            if provider_id not in self.keys:
                self.keys[provider_id] = []
            k_list = self.keys[provider_id]

            idx = len(k_list) + 1
            key_id = f"{provider_id}_key_{int(time.time())}_{idx}"
            prio = priority if priority is not None else idx

            entry = KeyEntry(
                key_id=key_id,
                provider_id=provider_id,
                api_key=api_key.strip(),
                priority=prio,
                status=KeyStatus.READY.value,
            )
            k_list.append(entry)

            # Synchronize to settings/os env if first key
            if len(k_list) == 1:
                env_var = f"{provider_id.upper()}_API_KEY"
                os.environ[env_var] = api_key.strip()
                setattr(settings, env_var, api_key.strip())

            self._save_keys()
            logger.info("Added new API key", key_id=key_id, provider_id=provider_id)
            return entry

    async def delete_key(self, provider_id: str, key_id: str) -> bool:
        """Delete an API key by key_id."""
        async with self._lock:
            k_list = self.keys.get(provider_id, [])
            self.keys[provider_id] = [k for k in k_list if k.key_id != key_id]
            self._save_keys()
            logger.info("Deleted API key", key_id=key_id, provider_id=provider_id)
            return True

    async def update_key(
        self,
        provider_id: str,
        key_id: str,
        priority: int | None = None,
        status: str | None = None,
    ) -> KeyEntry | None:
        """Update API key priority or status."""
        async with self._lock:
            k_list = self.keys.get(provider_id, [])
            target = next((k for k in k_list if k.key_id == key_id), None)
            if not target:
                return None

            if priority is not None:
                target.priority = priority
            if status is not None:
                target.status = status
                if status == KeyStatus.READY.value:
                    target.cooldown_until = None
                    target.last_error = None

            self._save_keys()
            logger.info("Updated API key", key_id=key_id, status=target.status, priority=target.priority)
            return target

    async def test_key(self, provider_id: str, key_id: str) -> Dict[str, Any]:
        """Test a specific key's validity against provider API."""
        async with self._lock:
            k_list = self.keys.get(provider_id, [])
            target = next((k for k in k_list if k.key_id == key_id), None)
            if not target:
                return {"valid": False, "message": "Key not found"}

            api_key = target.api_key

        # Test request outside lock
        if provider_id == "kling":
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            url = "https://api.klingai.com/v1/videos/text2video"
            payload = {"model_name": "kling-v1", "prompt": "test", "duration": "5", "aspect_ratio": "16:9"}
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.post(url, json=payload, headers=headers)
                    if res.status_code == 200:
                        return {"valid": True, "message": "Key is valid and active"}
                    err_txt = res.text
                    if "balance" in err_txt.lower() or res.status_code in (402, 403, 429):
                        return {"valid": False, "message": f"Account balance not enough / Rate limit (HTTP {res.status_code})"}
                    elif res.status_code in (401, 403):
                        return {"valid": False, "message": f"Invalid API Key (HTTP {res.status_code})"}
                    return {"valid": False, "message": f"HTTP {res.status_code}: {res.text[:100]}"}
            except Exception as e:
                return {"valid": False, "message": f"Connection error: {str(e)}"}

        elif provider_id == "fal":
            headers = {"Authorization": f"Key {api_key}"}
            url = "https://rest.alpha.fal.ai/tokens/"
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(url, headers=headers)
                    if res.status_code in (200, 400, 404):
                        return {"valid": True, "message": "Key authorized"}
                    return {"valid": False, "message": f"fal.ai HTTP {res.status_code}: {res.text[:100]}"}
            except Exception as e:
                return {"valid": False, "message": f"Connection error: {str(e)}"}

        return {"valid": True, "message": "Key validation not implemented for provider"}

    async def fetch_quota(self, provider_id: str, key_id: str) -> Dict[str, Any]:
        """Fetch official quota information from provider if available."""
        async with self._lock:
            k_list = self.keys.get(provider_id, [])
            target = next((k for k in k_list if k.key_id == key_id), None)
            if not target:
                return {"status": "Key not found"}
            api_key = target.api_key

        # fal.ai billing test
        if provider_id == "fal":
            try:
                headers = {"Authorization": f"Key {api_key}"}
                async with httpx.AsyncClient(timeout=8.0) as client:
                    res = await client.get("https://rest.alpha.fal.ai/user/info", headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        target.quota_info = data
                        self._save_keys()
                        return data
            except Exception:
                pass

        # If provider doesn't offer official quota API:
        info = {
            "status": "Unknown / Not available",
            "provider_api_quota": "Provider does not offer exact quota querying API",
            "local_stats": {
                "total_requests": target.total_requests,
                "successful_requests": target.successful_requests,
                "failed_requests": target.failed_requests,
            },
        }
        target.quota_info = info
        self._save_keys()
        return info


def get_key_manager() -> KeyManager:
    """Dependency injection helper."""
    return KeyManager.get_instance()

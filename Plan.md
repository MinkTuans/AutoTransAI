Tired:
[D:54d78f 1/9]
## 1. SYSTEM OVERVIEW

**Phạm vi audit:** repository `AutoTransAI`, nhánh `main`, commit `bb8cbab`. Đã đọc cả bốn ảnh. Các thay đổi Glossary chưa hoàn tất trong worktree riêng **không được coi là code đã tích hợp vào main**.

Trong lượt audit này không sửa/tạo/xóa file, không chạy migration, không chạy pipeline tạo media.

Quy ước:

- **FACT FROM CODE:** hành vi xác định từ code.
- **INFERENCE:** suy luận từ code và ảnh.
- **NEEDS VERIFICATION:** cần log, dữ liệu hoặc kiểm thử runtime để kết luận.
- **PROPOSED CHANGE:** thay đổi đề xuất cho phase implementation.

**FACT FROM CODE — có hai đường thực thi:**

```text
Studio Auto
Upload/URL → VideoAsset → VideoTranslationJob
→ Extract audio → STT → Glossary → Translation
→ Character mapping → Voice assignment
→ Review hoặc Auto-confirm
→ TTS → Scheduling → Audio sync → PCM assembly
→ FFmpeg mux → Watermark tùy chọn
→ Output validation → Persistent storage → Completed → Player

Unified Workflow
WorkflowEngine
→ INGEST → ANALYZE → TRANSLATE → DUB → PRODUCE → PUBLISH
```

Không thể sửa riêng Studio rồi mặc định Unified cũng được bảo vệ.

**Đối chiếu ảnh:**

| Ảnh | Quan sát |
|---|---|
| 1 | Player đen, có thời lượng `1:00`, vị trí `0:31`. Chưa đủ chứng minh output không tồn tại. |
| 2 | Segment tiếng Việt dùng `edge_tts/en-US-GuyNeural`; Character là UUID; Speaker unresolved; confidence 0%. |
| 3 | Đúng component “Video Editing & Branding Automation Studio”. |
| 4 | Upload filename Unicode; target Vietnamese; giọng đầu vào Hoài My; Auto-confirm Translation bật. |

Ảnh 2 và 4 cho thấy cấu hình giọng ở đầu workflow không kiểm soát được giọng cuối cùng của từng character.

## 2. CURRENT ARCHITECTURE

Các đường dẫn dưới đây tính từ repository `AutoTransAI`.

| Layer | File/function chính | Trách nhiệm |
|---|---|---|
| UI workflow | `frontend/src/pages/VideoTranslator.jsx` | Upload, tạo job, polling, editor, confirmation, player |
| API client | `frontend/src/api.js` | `importUpload`, `createJob`, `startJob`, provider voices, review/render |
| Upload | `backend/app/api/routes/video_translator.py::import_video_asset` | Nhận multipart, lưu tạm, tạo `VideoAsset` |
| Import service | `backend/app/services/video_source/service.py::import_uploaded_file` | Đổi tên file lưu, probe, giới hạn size/duration |
| Studio orchestration | `video_translator.py::start_translation_pipeline` | STT, translation, character/voice, review |
| Translation/STT | `backend/app/services/video_translator/translator_service.py` | Extract audio, STT, normalization timeline, translation, glossary, render wrapper |
| Character | `backend/app/services/video_translator/character_mapping_service.py` | `validate_character_mapping`, `map_and_persist` |
| Voice allocation | `backend/app/services/video_translator/voice_assignment_service.py` | `assign_voices`, `assign_project_voices` |
| Provider registry | `backend/app/providers/registry.py` | Adapter lookup bằng provider ID |
| Voice metadata | `backend/app/providers/base.py::VoiceInfo` | `id`, `name`, `language`, `gender` |
| Provider catalog API | `backend/app/api/routes/providers.py::list_voices` | Danh sách voice theo provider/language |
| TTS adapters | `backend/app/providers/audio/*_provider.py` | Edge, Google, ElevenLabs |
| TTS/render execution | `video_translator.py::execute_job_render_pipeline` | TTS từng segment, schedule, sync, render, lưu output |
| Scheduling | `backend/app/services/video_translator/timeline_scheduler.py` | Lịch audio sau TTS |
| Audio/render | `backend/app/services/video_translator/sync_service.py` | PCM assembly, `render_and_mux_video`, `validate_output` |
| FFmpeg execution | `backend/app/media/ffmpeg_process.py` | Subprocess, progress, exit code, stderr |
| Probe | `backend/app/media/ffprobe.py` | Metadata và duration |
|

Tired:
[D:54d78f 2/9]
Storage | `backend/app/services/storage_service.py` | Copy sang persistent storage, tạo URL |
| Serving | `backend/app/api/routes/storage.py`, `backend/app/main.py` | FileResponse và `/media` |
| Cleanup | `backend/app/services/cleanup_service.py` | Xóa intermediate files |
| Unified | `backend/app/workflow/workflow_engine.py`, `stages/*.py` | Workflow/stage/step execution |
| Branding UI | `frontend/src/components/VideoEditorStudio.jsx` | Aspect ratio, logo, subtitle, ducking |
| Editor backend | `backend/app/api/routes/video_editor.py`, `services/video_editor/*` | Config, watermark, subtitle, QC, publishing |
| DB | `backend/app/models/video_translator.py`, `workflow_engine.py`, `video_editor.py` | Assets, jobs, segments, profiles, voice pool, editor config |

## 3. PROBLEMS FOUND

| Mức độ | Vấn đề | Kết luận |
|---|---|---|
| P0 | Voice pool chứa giọng Anh và allocator không lọc target language | **FACT FROM CODE** |
| P0 | Unknown gender vẫn có thể nhận voice đầu tiên còn trống | **FACT FROM CODE** |
| P0 | Profile có voice được tái sử dụng mà không kiểm tra locale/gender/provider | **FACT FROM CODE** |
| P0 | Validation trước confirm không kiểm tra đầy đủ gender/provider/voice language | **FACT FROM CODE** |
| P0 | Segment provider không tồn tại có thể fallback sang job provider | **FACT FROM CODE** |
| P1 | Character UUID được render trực tiếp; name/gender không được đưa vào segment response tương ứng | **FACT FROM CODE** |
| P1 | UI review cho nhập tự do provider/voice | **FACT FROM CODE** |
| P1 | Translation confirmation và Character/Voice review dùng các gate khác nhau, thiếu mô hình confirmation thống nhất | **FACT FROM CODE** |
| P1 | Một số lỗi TTS bị chuyển thành silence; pipeline có thể tiếp tục với audio thiếu | **FACT FROM CODE** |
| P1 | TTS cache tái sử dụng theo file tồn tại, không gắn với text/voice/provider hiện tại | **FACT FROM CODE** |
| P1 | Render copy video codec, thiếu kiểm tra khả năng phát trên browser | **FACT FROM CODE**; liên hệ với ảnh đen là **INFERENCE** |
| P1 | Kết quả duration validation `passed=False` không được wrapper dùng để chặn | **FACT FROM CODE** |
| P1 | Unified DUB/PRODUCE tham chiếu class không tồn tại trong module được import | **FACT FROM CODE** |
| P2 | Lặp `voice_conflict` do nhiều overlap pairs và UI nối reason trực tiếp | **FACT FROM CODE** |
| P2 | Branding editor xuất hiện trong vùng kết quả dù không cần cho flow chính | **FACT FROM CODE** |
| P2 | Download link hard-code `127.0.0.1:8000` | **FACT FROM CODE** |
| Chưa kết luận | Filename Unicode làm thất bại video cụ thể | **NEEDS VERIFICATION** |

## 4. ROOT CAUSE ANALYSIS

### Voice US

**FACT FROM CODE**

[voice_assignment_service.py](/home/codexproxy/Codex-project-2/AutoTransAI/backend/app/services/video_translator/voice_assignment_service.py:20):

- `assign_project_voices()` seed cả hai voice Việt và hai voice Anh.
- Query lấy toàn bộ voice enabled.
- Không nhận `target_language`.
- `assign_voices()` ưu tiên voice theo gender, sau đó lấy `choices[0]`.
- Existing profile có voice được dùng ngay.
- Conflict exclusion so sánh `voice_id`, chưa dùng cặp `(provider, voice_id)`.

[video_translator.py](/home/codexproxy/Codex-project-2/AutoTransAI/backend/app/api/routes/video_translator.py:1836):

- TTS ưu tiên voice của segment hơn voice của job.
- Lookup segment provider thất bại thì dùng job provider.
- Không có gate locale/gender ngay trước `generate_audio()`.

**INFERENCE:** giọng Hoài My chọn ở đầu UI bị voice assignment cấp character thay thế. Khi allocator tránh voice đã dùng hoặc tái sử dụng profile cũ, `en-US-GuyNeural` có thể được chọn hợp lệ theo logic hiện tại.

**PROPOSED CHANGE:** lọc bắt buộc theo target/gender/provider trước allocation; kiểm tra lại ngay trước TTS; loại fallback khác ngôn ngữ.

Tired:
[D:54d78f 3/9]

### Character UUID

[character_mapping_service.py](/home/codexproxy/Codex-project-2/AutoTransAI/backend/app/services/video_translator/character_mapping_service.py:48):

- UUID5 được tạo từ project và identifier do LLM trả về.
- Fallback unresolved cũng được chuyển thành UUID.
- `CharacterVoiceProfile` đã có `name`, `gender`, confidence và confirmation.
- Validator kiểm tra confidence/mapping, chưa bắt buộc gender hợp lệ.

[VideoTranslator.jsx](/home/codexproxy/Codex-project-2/AutoTransAI/frontend/src/pages/VideoTranslator.jsx:1805):

- Character input lấy trực tiếp `seg.character_id`.
- Job segment serialization chưa trả character name/gender tương ứng.
- Frontend review fallback name về character ID, gender về `unknown`.

**PROPOSED CHANGE:** giữ ID nội bộ, join profile trong response; UI dùng name/gender và trạng thái unresolved. Không cần thêm một bảng Character song song.

### Provider/Voice input

**FACT FROM CODE:** form đầu workflow đã có voice catalog, nhưng editor từng segment dùng `<input>`. API review chấp nhận string và không kiểm tra membership đầy đủ.

Ngoài allocator:

- Google TTS có fallback catalog chứa cả Việt và Anh.
- ElevenLabs dùng `category` như language metadata ở một nhánh và có fallback voices tiếng Anh.
- Vì vậy không thể tin mọi danh sách từ adapter hiện tại đã lọc đúng locale.

**PROPOSED CHANGE:** tận dụng provider registry, `VoiceInfo`, `VoicePoolEntry`; chuẩn hóa và kiểm tra catalog trước khi UI lẫn backend sử dụng.

### Auto-confirm

[video_translator.py](/home/codexproxy/Codex-project-2/AutoTransAI/backend/app/api/routes/video_translator.py:1014):

- Character/Voice needs-review được ưu tiên trước `auto_confirm_translation`.
- Checkbox bật nhưng vẫn dừng Character/Voice là hành vi hiện tại, không phải chỉ lỗi checkbox.
- Chỉ có một cờ translation, chưa có cờ auto-confirm voice độc lập.
- Helper `auto_confirm_and_start_render_if_needed()` kiểm tra status/stage nhưng không chạy đầy đủ Character/Voice validator.
- Review confirm đánh dấu tất cả profile trong project confirmed, thay vì chỉ các profile liên quan job.
- Nhánh auto-confirm sau `flush()` duyệt `session.new`; các segment đã flush thường không còn nằm trong tập này.

**PROPOSED CHANGE:** một quyết định chuyển sang DUB dựa trên hai gate độc lập; mọi entry point dùng cùng quyết định và cùng validator.

### Video output upload

[sync_service.py](/home/codexproxy/Codex-project-2/AutoTransAI/backend/app/services/video_translator/sync_service.py), `render_and_mux_video()`:

- Cả mute/duck/keep dùng `-c:v copy`.
- Audio được encode AAC.
- Có map video/audio rõ ràng.
- Có kiểm tra file output tồn tại và khác rỗng.

[translator_service.py](/home/codexproxy/Codex-project-2/AutoTransAI/backend/app/services/video_translator/translator_service.py:1377):

- `validate_output()` trả `passed` theo duration.
- Wrapper vẫn log “Validation passed” và return mà không kiểm tra boolean đó.

**INFERENCE — ưu tiên xác minh:** nếu player thực sự đang phát output, codec/profile/pixel format không tương thích browser là ứng viên mạnh vì video stream được giữ nguyên. Duration hiển thị không chứng minh video frames giải mã được.

**NEEDS VERIFICATION:** codec nguồn/output, URL player thực tế, browser media error, FFmpeg stderr và job state. Chưa thể kết luận đây chính là nguyên nhân của video trên máy bạn.

### Unicode filename

[service.py](/home/codexproxy/Codex-project-2/AutoTransAI/backend/app/services/video_source/service.py:113):

```text
Tên upload Unicode
→ raw_input_<asset_id>.mp4
→ input_source<original_extension>
```

Tên gốc được giữ làm metadata/title; basename tiếng Hán không được dùng làm tên input xử lý cuối.

`ffmpeg_process.py` dùng `subprocess.Popen()` với danh sách arguments, không ghép shell command để thực thi.

**Kết luận:**

Tired:
[D:54d78f 4/9]
không có cơ sở đề xuất “đổi hết tên Unicode sang ASCII” như bản sửa nguyên nhân gốc. Vẫn phải kiểm thử Unicode trong đường dẫn cha, Windows, extension, filename dài và response headers.

## 5. PROPOSED ARCHITECTURE

Giữ route orchestration và workflow engine hiện có; bổ sung policy/validation dùng chung.

```text
Upload + Media validation
→ STT + Speaker preservation
→ Character Resolution
→ Gender Resolution
→ Translation + Glossary
→ Translation Validation
→ Translation confirmation gate
→ Character/Voice Resolution
→ Voice Validation
→ Character/Voice confirmation gate
→ TTS
→ Audio Validation + Scheduling
→ Video Rendering
→ Output Validation
→ Persistent storage
→ Final Video
```

Các quyết định cụ thể:

- Character resolution đọc source transcript/speaker evidence; translation có thể bổ sung tên hiển thị sau đó.
- Gender unresolved không nhất thiết chặn dịch, nhưng luôn chặn TTS.
- `CharacterVoiceProfile` là nguồn name/gender/assignment theo project.
- Segment giữ character reference và assignment snapshot phục vụ job/retry.
- Một validator dùng chung cho review, auto-confirm, manual render, resume/retry và Unified DUB.
- Glossary validation giữ riêng domain lỗi; không chuyển lỗi Glossary thành voice conflict.
- Các giá trị confidence là evidence, không tự động tương đương user confirmation.

Đường Unified cần sửa đúng lời gọi service đang thiếu; không tạo pipeline thứ ba hoặc class wrapper giả chỉ để hết ImportError.

## 6. DATABASE CHANGES

**FACT FROM CODE:** đã có đủ nền tảng:

- `CharacterVoiceProfile`: name, gender, provider, voice, confidence, confirmed.
- `SpeakerVoiceMapping`: speaker → character.
- `VoicePoolEntry`: provider, language, gender, display name, metadata.
- Job có settings snapshot và studio state.

**PROPOSED CHANGE — tối thiểu:**

1. Không migration cho việc hiển thị name/gender hoặc dropdown.
2. Thêm `auto_confirm_voice` vào project settings và job settings snapshot JSON.
3. Lưu hai confirmation states cùng revision trong JSON hiện có; không dùng progress/stage làm bằng chứng đã confirm.
4. Lưu evidence/status của character/gender nếu cần bền vững. Chỉ đề xuất migration additive sau khi chốt nơi lưu, không thêm bảng trùng chức năng.

**Dữ liệu cũ:**

- Giữ nguyên IDs, output paths, completed jobs.
- Không đoán gender từ voice đã gán.
- Job cũ chưa hoàn tất: thiếu evidence thì review trước lần TTS tiếp theo.
- Giọng nước ngoài giữ lại để hiển thị nguyên nhân invalid; không xóa catalog vì còn project target khác.
- Completed jobs vẫn xem/tải bình thường; rerender phải qua policy mới.
- Không tự merge character theo tên giống nhau.
- Missing `auto_confirm_voice` mặc định OFF; giữ nguyên giá trị `auto_confirm_translation`.

Nếu cần migration evidence fields: thêm nullable, backfill trạng thái legacy/unverified, tuyệt đối không đánh dấu legacy là confirmed hàng loạt.

## 7. BACKEND CHANGES

**PROPOSED CHANGE:**

1. **Character mapping**
- Validate gender enum và character membership theo project.
- Duy trì một gender authoritative cho cùng character.
- Không ghi đè profile đã confirmed bằng kết quả LLM thấp tin cậy.
- Tái sử dụng character qua episode bằng evidence; không tin identifier LLM ổn định.

2. **Voice allocation**
- Nhận target language và danh sách character thực sự thuộc job.
- Revalidate existing assignments.
- Lọc locale/gender trước ranking và conflict checks.
- Dùng identity `(provider_id, voice_id)`.
- Không chọn voice khác gender/language khi pool hết.

3. **Review validation**
- Kiểm tra character, gender, provider adapter/configuration, catalog membership, language, gender compatibility, conflict.
- Gom cùng conflict character-pair/voice thành một issue với danh sách affected segments.
- Không gom tất cả conflicts khác nhau thành một

Tired:
[D:54d78f 5/9]
lỗi vô nghĩa.

4. **Confirmation**
- Một hàm quyết định transition dùng chung.
- Transaction/conditional update để concurrent polling/confirm chỉ launch một job.
- Manual confirmation không bypass invalid.
- Chỉ confirm profiles thuộc job.

5. **TTS**
- Gate bắt buộc trước provider call.
- Bỏ silent provider fallback trong flow này.
- Cache key gồm text, provider, voice, model/settings cần thiết.
- Không tiếp tục thành công với failed speech segments bị thay bằng silence.

6. **Render/output**
- Kiểm tra stream/codec trước copy.
- Encode tương thích browser khi cần.
- Chặn khi output validation không pass.
- Chỉ completed sau kiểm tra persistent artifact.

7. **Unified**
- Nối DUB/PRODUCE vào các service có thật.
- Chạy cùng voice/confirmation/audio/output validators.

## 8. FRONTEND CHANGES

**PROPOSED CHANGE:**

- Character selector hiển thị `Tên — Nam/Nữ/Chưa xác định`.
- Không dùng UUID làm display fallback; dùng `Nhân vật chưa xác định`.
- Gender edit ở cấp character; cập nhật mọi segment cùng character.
- Provider dropdown chỉ có audio adapters khả dụng.
- Voice dropdown phụ thuộc provider, target, gender.
- Giữ selection hiện tại nếu còn hợp lệ; không luôn chọn `voices[0]`.
- Chống response catalog cũ ghi đè sau khi đổi provider nhanh.
- Legacy invalid selection hiển thị lỗi và yêu cầu chọn lại.
- Hai checkbox:
- `Tự xác nhận bản dịch hợp lệ`
- `Tự xác nhận nhân vật và giọng hợp lệ`
- UI trạng thái: Valid / Need confirmation / Invalid / Unresolved.
- Error card nhóm theo violation, có character/segments liên quan và hành động sửa.
- Giữ Final Video player/download.
- Bỏ `VideoEditorStudio` khỏi workflow chính.
- Player xử lý `onError`, hiển thị lỗi tải/giải mã; dùng URL backend nhất quán cho phát và download.

## 9. API CHANGES

Ưu tiên mở rộng endpoint hiện có.

| Endpoint | Đề xuất |
|---|---|
| `GET /api/providers` | Chỉ rõ adapter supported/configured/available |
| `GET /api/providers/{id}/voices` | Lọc language/gender đáng tin cậy; metadata chuẩn hóa |
| `GET /api/video-translator/voice-pool` | Chuẩn hóa `vi`/`vi-VN`; không chỉ equality gây mismatch |
| `GET /api/video-translator/jobs/{id}` | Bổ sung character object và confirmation states |
| `GET .../character-voice-review` | Character name/gender/evidence; structured issues |
| `PUT .../character-voice-review` | Validate input; reject cập nhật mâu thuẫn cùng character |
| `POST .../character-voice-review/validate` | Validator đầy đủ, dedup backend |
| `POST .../character-voice-review/confirm-resume` | Confirm đúng gate/revision; chỉ resume khi cả hai gate đạt |
| Job creation/settings | Nhận `auto_confirm_voice`, giữ field cũ |
| Render/resume/retry | Dùng chung transition guard |
| Storage/download | URL chuẩn; filename Unicode response header hợp lệ |

Issue response đề xuất giữ `reason`, bổ sung các field:

```json
{
"reason": "NON_VIETNAMESE_VOICE",
"character_id": "...",
"segment_ids": ["..."],
"provider": "edge_tts",
"voice_id": "en-US-GuyNeural",
"message": "Nhân vật đang dùng giọng tiếng Anh; cần chọn giọng tiếng Việt."
}
```

Backend không được dựa vào dropdown để coi input là hợp lệ.

## 10. VOICE RESOLUTION RULES

| Điều kiện | Kết quả bắt buộc |
|---|---|
| Target vi + male đã được resolve/chấp nhận | Voice Việt male |
| Target vi + female đã được resolve/chấp nhận | Voice Việt female |
| Gender unknown hoặc thiếu evidence cần thiết | `GENDER_UNRESOLVED`, block TTS |
| Character thiếu/unresolved | `CHARACTER_UNRESOLVED`, block TTS |
| Provider không có adapter | `INVALID_PROVIDER` |
| Provider thiếu cấu hình | `PROVIDER_UNAVAILABLE` |
| Voice không thuộc provider catalog | `INVALID_VOICE` |
| Target vi + English/Chinese/Japanese voice | `NON_VIETNAMESE_VOICE` |
| Voice gender không

Tired:
[D:54d78f 6/9]
phù hợp | `VOICE_GENDER_MISMATCH` |
| Không có voice Việt phù hợp | `NO_COMPATIBLE_VOICE` |
| Profile cũ đã confirmed | Vẫn phải pass policy hiện tại |
| Nhiều character, thiếu voice để giải quyết overlap | Review/block; không dùng voice nước ngoài |

Whitelist nên dựa trên **catalog metadata đã xác thực + policy target**, không chỉ prefix voice ID. Với provider opaque IDs, prefix không có ý nghĩa.

Với Edge, có thể dùng hai voice Việt đang được code hỗ trợ làm catalog offline có kiểm soát; không suy luận metadata cho provider khác.

## 11. CONFIRMATION STATE MACHINE

Hai gate độc lập:

| Gate | Validation | Auto flag | State |
|---|---|---|---|
| Translation | Pass | ON | Accepted automatically |
| Translation | Pass | OFF | Awaiting manual confirmation |
| Translation | Fail | Bất kỳ | Invalid; chưa accepted |
| Character/Voice | Pass | ON | Accepted automatically |
| Character/Voice | Pass | OFF | Awaiting manual confirmation |
| Character/Voice | Unresolved/Fail | Bất kỳ | Needs review/blocked |

```text
TRANSLATION_READY
→ validate translation
→ translation accepted hoặc translation review

CHARACTER_VOICE_READY
→ validate character/gender/provider/voice
→ voice accepted hoặc character/voice review

translation accepted AND voice accepted
→ atomic transition to TTS_READY
→ launch TTS once
```

Quy tắc invalidation:

- Sửa translated text: hủy translation acceptance và TTS cache liên quan.
- Sửa character/gender/provider/voice: hủy voice acceptance và audio liên quan.
- Sửa timing: đánh giá lại scheduling/conflicts.
- Accepted phải gắn revision; không dùng acceptance của dữ liệu cũ.
- GET polling không tự xác nhận dựa trên stage string; nếu giữ helper recovery thì helper cũng dùng đầy đủ transition guard.
- `AUDIO_SCHEDULE_REVIEW` là gate riêng, không được nút voice-confirm vượt qua.

## 12. VIDEO OUTPUT DEBUG PLAN

Thực hiện trong phase kiểm chứng runtime sau này, trên bản sao dữ liệu/test workspace.

| Bước | Kiểm tra và bằng chứng |
|---|---|
| 1. Browser | File name, size, MIME; request multipart có `file` và `source_type=upload` |
| 2. Upload endpoint | HTTP status, asset ID, lỗi upload cụ thể |
| 3. Temp file | Size/hash so với input; quyền ghi; đủ disk space |
| 4. Stored source | `input_source.ext` tồn tại, extension, FFprobe format/video/audio |
| 5. Path | Windows/Linux separators; Unicode/spaces trong thư mục cha; cwd |
| 6. Job creation | asset ID, target, settings snapshot, provider/voice |
| 7. STT/translation | Status/checkpoint và lỗi trước DUB; copyright/review holds |
| 8. Character/voice | Có thực sự đạt gate hay đang needs-review |
| 9. TTS | Mỗi speech segment có audio đọc được, duration > 0; không dùng cache sai |
| 10. Schedule/sync | scheduled timestamps; missing/failed audio; audio duration |
| 11. FFmpeg | Arguments thực tế, executable, exit code, stderr, progress, timeout |
| 12. Local output | File tồn tại/size; video+audio streams; duration; decode frames |
| 13. Codec | Codec/profile/pixel format có được browser/WebView hỗ trợ |
| 14. Persistent copy | Object key, destination tồn tại, size/hash khớp |
| 15. API result | `status`, `output_url`, `output_video_path` đúng artifact |
| 16. HTTP media | GET/Range trả bytes đúng; MIME, content length; không trả HTML |
| 17. Frontend | `<video currentSrc>`, media error code, dimensions, readyState |
| 18. Cleanup | Final và persistent copy còn sau cleanup/reload |

Các lệnh chẩn đoán đề xuất:

```text
ffprobe -v error -show_format -show_streams -of json "<input>"
ffprobe -v error -show_format -show_streams -of json "<output>"
ffmpeg -v error -i "<output>" -map 0:v:0 -frames:v 1 -f null -
```

**Phân nhánh kết luận:**

- Chưa qua review/TTS → lỗi workflow gate, chưa phải render.
- FFmpeg nonzero → dùng stderr xác định nguyên nhân.
- Output

Tired:
[D:54d78f 7/9]
local tốt nhưng URL 404 → storage/serving/path.
- URL trả file đúng, browser không decode nhưng FFmpeg decode được → compatibility.
- Cả FFmpeg decode lỗi → artifact hỏng.
- Decode được nhưng hình đen → đối chiếu frames nguồn, trim và watermark.

**Filename test bắt buộc:** `未日临先锋圣母_哔哩哔哩_bilibili.mp4`, giữ nguyên tên khi gửi multipart.

**NEEDS VERIFICATION cho video trong ảnh:** chưa có job ID, input/output media, log FFmpeg hoặc Network response của máy bạn. Không thể xác nhận root cause cuối cùng từ screenshot.

## 13. FILES TO MODIFY

Danh sách là kế hoạch, chưa có chỉnh sửa.

| File | Mục đích | Ảnh hưởng |
|---|---|---|
| `backend/app/services/video_translator/character_mapping_service.py` | Character identity, gender validation, evidence | Cao |
| `backend/app/services/video_translator/voice_assignment_service.py` | Language/gender filtering, reuse validation, stable conflict grouping | Cao |
| `backend/app/providers/base.py` | Chuẩn hóa voice metadata nếu cần | Trung bình |
| `backend/app/providers/audio/google_tts_provider.py` | Sửa fallback catalog/filter và metadata | Trung bình |
| `backend/app/providers/audio/elevenlabs_provider.py` | Không dùng category như locale; kiểm soát fallback | Trung bình |
| `backend/app/providers/audio/edge_tts_provider.py` | Xác minh catalog normalization; sửa nếu test chứng minh thiếu | Thấp |
| `backend/app/api/routes/providers.py` | Catalog filtering/availability contract | Trung bình |
| `backend/app/api/routes/video_translator.py` | Gate, serialization, confirmation, TTS validation/cache, output | Cao |
| `backend/app/workflow/stages/analyze_stage.py` | Nối Character/Gender resolution trước translation | Trung bình |
| `backend/app/workflow/stages/dub_stage.py` | Shared voice gate; thay lời gọi service không tồn tại | Cao |
| `backend/app/workflow/stages/produce_stage.py` | Render/output contract có thật | Cao |
| `backend/app/workflow/workflow_context.py` | Persist confirmation/settings context | Trung bình |
| `backend/app/services/video_translator/translator_service.py` | Chặn output QC fail; bảo toàn source/translation invariants | Cao |
| `backend/app/services/video_translator/sync_service.py` | Codec policy, audio/output validation | Cao |
| `backend/app/media/ffmpeg_process.py` | Timeout thực sự bao trùm process, diagnostic evidence | Trung bình |
| `backend/app/services/video_source/service.py` | Input format/stream validation theo kết quả debug | Trung bình |
| `backend/app/api/routes/storage.py` | Canonical path, Unicode download headers, serving validation | Trung bình |
| `frontend/src/pages/VideoTranslator.jsx` | Character UX, dropdown, two gates, player errors, bỏ Branding card | Cao |
| `frontend/src/api.js` | Response/confirmation/catalog extensions | Trung bình |
| `backend/app/models/*` | Chỉ khi cần evidence fields additive đã chốt | Có điều kiện |
| `PROJECT_KNOWLEDGE_BASE.md`, `CHANGELOG_AI.md` | Cập nhật sau implementation | Tài liệu |

Có thể thêm một module nhỏ dùng chung cho validation/transition nếu việc đặt trong service hiện hữu gây import vòng. Không tách hàng loạt route trong task này.

## 14. FILES TO DELETE/DEPRECATE

| Thành phần | Quyết định |
|---|---|
| Mount/import `VideoEditorStudio` trong `VideoTranslator.jsx` | **REMOVE FROM UI** |
| Branding configuration như điều kiện bắt buộc để dịch/render | **REMOVE FROM WORKFLOW**, chỉ nơi thực sự đang chặn |
| `frontend/src/components/VideoEditorStudio.jsx` | **SAFE TO DELETE CODE sau khi bỏ sole consumer và xác nhận lại references/build** |
| `videoEditorApi.saveConfig/uploadLogo` | Chỉ deprecate hoặc xóa method riêng khi không còn consumer |
| `backend/app/api/routes/video_editor.py` | **Giữ**: còn QC/publishing |
| `backend/app/models/video_editor.py` | **Giữ**: gồm dữ liệu editor và

Tired:
[D:54d78f 8/9]
publishing |
| `services/video_editor/watermark_service.py` | **Giữ**: Studio/Produce/preflight còn dùng |
| Subtitle/QC/YouTube/TikTok services | **Giữ** |
| Final Video player/download | **Giữ** |
| DB `VideoEditConfig` và assets cũ | **Giữ**, không drop theo việc ẩn UI |

**FACT FROM CODE:** card Branding này nằm trong vùng completed output. Vì vậy bản thân việc chưa bấm “Save video configuration” không phải điều kiện bắt buộc của render Studio đang trace.

## 15. IMPLEMENTATION PHASES

| Phase | Công việc | Điều kiện hoàn thành |
|---|---|---|
| 0 — Reproduction | Capture job/input/output/log; phân loại lỗi video | Xác định nhánh fail; chưa đổi policy dựa trên phỏng đoán |
| 1 — Character contract | Name/gender authoritative, unresolved/evidence, response hydration | Cùng character nhất quán; UUID không là label |
| 2 — Voice policy | Catalog normalization, language/gender rules, existing assignments | Voice nước ngoài không thể tới TTS target vi |
| 3 — Backend gates | Shared validator, stable issues, hard pre-TTS checks | Mọi render/resume path đều bị bảo vệ |
| 4 — Confirmation | Hai flags/states, revisions, atomic transitions | ON/OFF hoạt động độc lập; launch một lần |
| 5 — UI | Dropdown, name/gender, actionable errors, unique reason display | Không nhập arbitrary provider/voice |
| 6 — Audio/output | Cache validity, no silent failure, codec/QC/storage fixes theo evidence | Output phát hình/tiếng, seek/download được |
| 7 — Branding UI | Bỏ card đúng scope, giữ shared backend | Workflow không còn card; module khác không regression |
| 8 — Integration | Studio + Unified + Windows/Linux + legacy jobs | Test matrix đạt; docs/changelog cập nhật |

Mỗi phase implementation: test tái hiện lỗi → xác nhận fail → sửa tối thiểu → test regression → review diff.

## 16. TEST PLAN

| Test case | Kết quả yêu cầu |
|---|---|
| Male Vietnamese character | Chỉ voice Việt male |
| Female Vietnamese character | Chỉ voice Việt female |
| Unknown gender | Block TTS, `GENDER_UNRESOLVED` |
| Missing/unresolved character | Block TTS |
| Invalid provider | Không fallback ngầm |
| Provider chưa configured | Báo rõ unavailable |
| Invalid voice | Reject tại API và pre-TTS |
| English voice selected | Target vi bị block |
| Chinese voice selected | Target vi bị block |
| Vietnamese compatible voice | Pass |
| Voice Việt sai gender | Block |
| Existing confirmed foreign voice | Vẫn block |
| Auto translation ON/OFF | Tự accept hoặc chờ đúng gate |
| Auto voice ON/OFF | Tự accept chỉ khi valid hoặc chờ thủ công |
| Bốn tổ hợp hai flags | Không vượt gate còn thiếu |
| Manual confirm invalid | 409/issues, không gọi TTS |
| Voice conflict lặp | Một semantic issue, đủ affected segments |
| Distinct conflicts | Không mất thông tin vì dedup |
| Multiple characters | Assignment nhất quán |
| Duplicate characters/mappings | Không merge tùy tiện; phát hiện mâu thuẫn |
| Cùng voice ID khác provider | Identity không bị nhầm |
| Text/voice thay đổi sau confirm | Invalidate confirmation/cache |
| Concurrent polling/confirm | Một transition, một launch |
| Unicode filename | Upload → render → player thành công |
| Spaces/special characters | Không split arguments/injection |
| Long filename | Metadata giữ đúng hoặc lỗi giới hạn rõ ràng |
| Unicode parent path trên Windows | Probe/FFmpeg/storage hoạt động |
| Extension/MIME không khớp | Content validation rõ ràng |
| FFmpeg failure | Job failed, lưu stderr, không completed |
| Missing/empty output | Block completion |
| Audio-only output | Block completion |
| Unsupported browser codec | Encode compatible hoặc lỗi rõ ràng |
| Duration mismatch | Không log pass giả |
| Một TTS segment thất bại | Không âm thầm coi final là thành công |
| Storage URL 404/HTML | Player báo lỗi; không coi có playable

Tired:
[D:54d78f 9/9]
output |
| Successful output | Video+audio, duration, browser playback, seek, download |
| Cleanup | Không xóa final đang dùng |
| Legacy completed job | Vẫn xem/tải được |
| Unified DUB/PRODUCE | Không ImportError; dùng cùng policy Studio |

Ưu tiên mở rộng các test hiện hữu:

- `test_character_mapping_service.py`
- `test_voice_assignment_service.py`
- `test_auto_confirm_and_stage_sync.py`
- `test_timeline_scheduler.py`
- `test_workflow_engine.py`
- `test_unified_workflow_preflight.py`

Bổ sung integration upload/render/storage và UI tests ở phase implementation. Audit này chưa chạy các test tạo file hoặc ghi DB.

## 17. RISKS & EDGE CASES

- Hai voice Việt Edge không đủ cho mọi nhu cầu character đồng thời. Hết lựa chọn phải review, không chuyển sang tiếng Anh.
- Dialogue text thường không đủ xác định gender. Không suy luận chắc chắn từ tên hoặc cách xưng hô đơn lẻ.
- Speaker labels có thể tái dùng giữa video; mapping project-wide theo `SPEAKER_01` cần evidence trước khi tái sử dụng.
- Một character nhiều segment phải có một assignment; frontend hiện gửi theo segment có thể ghi đè lặp cùng speaker.
- Profile shared giữa jobs: sửa cho job mới không được âm thầm làm thay đổi lịch sử job đã hoàn tất.
- Catalog provider lỗi/mất mạng phải phân biệt với “không có voice tương thích”.
- Có nhiều conflict pairs thật; UI unique reason không thay thế backend grouping.
- FFmpeg timeout hiện đặt ở `process.wait()` sau vòng đọc stdout; process treo trước EOF có thể không chịu timeout như mong muốn.
- FileResponse/storage hiện có nhánh nhận absolute path và fallback cwd; cần giới hạn đường dẫn phục vụ khi sửa serving, nhưng phải bảo toàn legacy path hợp lệ.
- Download tự tạo `Content-Disposition` cần kiểm tra tên Unicode; đây là vấn đề khác với upload basename.
- Không mặc định hình đen là codec: input có thể đen, trim sai hoặc artifact khác đang được phát.
- Worktree Glossary còn dang dở phải được review riêng trước tích hợp; không dùng kết quả test cũ làm bằng chứng bản nâng cấp này đã pass.
- Registry/adapter/model routing có trách nhiệm khác nhau; không thay voice catalog bằng AI model resolver.
- Không có bằng chứng runtime trên Windows của người dùng trong audit này.

## 18. FINAL IMPLEMENTATION ORDER

1. Chốt input/job/output mẫu và xác minh nhánh lỗi video cụ thể.
2. Chuẩn hóa Character/name/gender và metadata voice bằng cấu trúc hiện có.
3. Viết test chặn foreign voice, unknown gender, invalid provider.
4. Hoàn thiện allocator và validator dùng chung.
5. Đặt gate trước mọi TTS entry point, gồm Studio và Unified.
6. Tách hai confirmation states, thêm revision và atomic transition.
7. Sửa API hydration/validation, rồi thay editor thành dropdown/name+gender.
8. Sửa TTS cache và audio failure handling.
9. Sửa render/output/serving theo bằng chứng; enforce toàn bộ output QC.
10. Gỡ Branding card khỏi UI, giữ shared services và dữ liệu.
11. Chạy matrix regression, media integration, browser/WebView và legacy tests.
12. Cập nhật knowledge base/changelog, cung cấp diff cùng bằng chứng kiểm thử để duyệt implementation.
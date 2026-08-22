# BÁO CÁO AUDIT & ĐÁNH GIÁ HỆ THỐNG GHÉP VIDEO VỚI AUDIO THOẠI DỊCH (VIDEO-AUDIO SYNC)
**Dự án:** WorkflowVdAi  
**Ngày kiểm tra:** 2026-08-22  
**Tác giả:** Antigravity AI  

---

## 1. Tổng quan Kiến trúc Pipeline Hiện tại

Hệ thống **WorkflowVdAi** xây dựng tính năng dịch & lồng tiếng video qua quy trình xử lý đa bước (2-phase workflow):

```text
[Phase 1: Phân tích & Dịch]
Upload / Link Video
    ↓
Trích xuất Audio (16kHz MONO WAV) ── (FFmpeg)
    ↓
Nhận diện Giọng nói & Timestamps (STT) ── (Gemini STT / Fallback Chunker)
    ↓
Dịch Lời thoại (LLM Translation) ── (Gemini LLM)
    ↓
Tạo Segments & Chờ xem lại (SEGMENT_EDITING) ── (Frontend UI)

[Phase 2: Tạo giọng & Ghép Timeline]
Người dùng xác nhận / sửa bản dịch
    ↓
Tạo Giọng đọc TTS từng đoạn (TTS Generation) ── (EdgeTTS / Google / ElevenLabs)
    ↓
Đồng bộ Thời lượng Audio (Audio Sync / Time-Stretch) ── (sync_and_stretch_audio)
    ↓
Tạo Timeline Audio & Mux Video (FFmpeg Render) ── (render_dubbed_video)
    ↓
Kiểm tra Đầu ra (FFprobe Validation) & Upload Cloud (R2 Storage)
    ↓
Final Video (.mp4)
```

---

## 2. Kết quả Kiểm tra Chi tiết (15 Câu hỏi Audit)

1. **Video gốc được lưu ở đâu?**
   - File video được lưu cục bộ tại `data/translator/assets/{asset_id}/{filename}` (đường dẫn lưu trong `VideoAsset.file_path`). Nếu bật R2, file được đồng bộ lên Cloudflare R2 (`VideoAsset.r2_key` / `VideoAsset.url`).

2. **Transcript gốc và timestamp được lưu ở đâu?**
   - Lưu trong bảng `video_translation_segments` (Model `VideoTranslationSegment`). Mỗi record gắn liền với `job_id` và chứa: `segment_number`, `start_time` (float giây), `end_time` (float giây), `original_text`, `translated_text`, `tts_audio_path`, `tts_audio_duration`, `synced_audio_path`, `status`.

3. **Timestamp của từng segment đang có định dạng gì?**
   - Số thực tính bằng giây (ví dụ: `start_time = 2.50`, `end_time = 5.80`).

4. **Translation được liên kết với segment gốc bằng ID/cấu trúc nào?**
   - `VideoTranslationSegment` lưu trực tiếp cả `original_text` và `translated_text` trên cùng 1 record theo `job_id` và `segment_number`.

5. **Audio TTS được tạo cho từng segment hay thành file duy nhất?**
   - Được tạo theo từng segment riêng biệt: `data/translator/jobs/{job_id}/tts/seg_{segment_number:03d}.wav`.

6. **Audio file có lưu duration thực tế không?**
   - Cột `VideoTranslationSegment.tts_audio_duration` lưu duration đo bằng FFprobe. Khi xử lý, `probe_duration_async` đo trực tiếp từ file WAV.

7. **Có các field thông tin cần thiết không?**
   - `VideoTranslationSegment`: `start_time`, `end_time`, `tts_audio_duration`, `tts_audio_path`, `synced_audio_path`.
   - `VideoTranslationJob`: `voice_id`, `audio_provider_id`, `original_audio_mode` (`mute`, `duck`, `keep`).

8. **Pipeline hiện tại ghép audio/video bằng cách nào?**
   - Trong `translator_service.py` (`render_dubbed_video`):
     Hệ thống dựng filter graph FFmpeg với `adelay=delays={start_time_ms}:all=1` và `amix=inputs=N:duration=longest`.
     Sau đó mux `combined_dubbed_audio.wav` vào video bằng stream copy (`-c:v copy -c:a aac`).

9. **Có FFmpeg chưa?**
   - Đã có tích hợp FFmpeg/FFprobe qua `app.media.ffmpeg`, `app.media.ffprobe`, `app.media.ffmpeg_process`.

10. **Có chỗ nào đang nối các audio thành một file liên tục (sai timeline) không?**
    - **CÓ! (Lỗi nghiêm trọng)**: Trong `render_dubbed_video` (dòng 414-431), nếu bộ lọc `amix` bị lỗi, hệ thống kích hoạt **Fallback Concat** (`audio_concat.txt` sử dụng `ffmpeg -f concat`). Chế độ này nối thẳng `audio_1 + audio_2 + audio_3...` từ 0 giây, làm mất toàn bộ mốc thời gian và khoảng im lặng!
    - Ngoài ra, bộ lọc `amix` mặc định của FFmpeg tự động giảm âm lượng từng input theo tỷ lệ $1/N$ ($N$ là số segment). Ví dụ với 10 segment, mỗi segment bị suy hao 20dB (giọng nói cực nhỏ/gần như mất tiếng).

11. **Có chỗ nào đang overwrite/mute audio gốc của video không?**
    - Tùy thuộc vào `original_audio_mode`: `mute` (tắt audio gốc), `duck` (giảm volume audio gốc xuống 15%), `keep` (giữ nguyên volume audio gốc).

12. **Output video cuối cùng được tạo ở đâu?**
    - `data/translator/jobs/{job_id}/final_dubbed_video.mp4` (và upload lên Cloudflare R2).

13. **Frontend đang chờ trạng thái processing như thế nào?**
    - Frontend (`VideoTranslator.jsx`) thực hiện polling định kỳ 1.5s tới `/api/video-translator/jobs/{job_id}` và cập nhật tiến độ real-time.

14. **Có progress/job status không?**
    - Có, `VideoTranslationJob` quản lý `status`, `stage`, `stage_progress_pct`, `overall_progress_pct`, `current_step`, `pid`, `ffmpeg_stats_json`.

15. **Có xử lý lỗi khi 1 segment TTS thất bại không?**
    - Hiện tại nếu 1 segment TTS thất bại, hệ thống ném `RuntimeError` khiến toàn bộ Job thất bại (FAIL).

---

## 3. Các Thành Phần Hiện Có (Có thể tái sử dụng)

- **Database & Schemas:** `VideoAsset`, `VideoTranslationJob`, `VideoTranslationSegment` đã đầy đủ các trường thông tin cần thiết.
- **FFmpeg Execution Engine:** `run_ffmpeg_with_progress_async` hỗ trợ parse progress, timeout, hủy process PID.
- **FFprobe Utilities:** `probe_duration_async`, `get_video_metadata_async`.
- **Storage Service:** Upload R2, quản lý đường dẫn file cục bộ.
- **State Machine & Logging:** `log_job_event`, `start_job_heartbeat`, `calculate_overall_progress`.
- **Frontend Management:** Polling, xem log, chỉnh sửa segment text, chọn giọng đọc, chọn mode audio.

---

## 4. Những Gì Còn Thiếu & Nhược Điểm Cần Khắc Phục

1. **Timeline-based Audio Construction Engine (Thiếu quan trọng nhất):**
   - Chưa có cơ chế lắp ghép Audio PCM chuẩn xác từng sample dựa trên timeline gốc (`segment.start_time`).
   - Phụ thuộc vào `amix` của FFmpeg dễ làm suy hao âm lượng ($1/N$) và bị lỗi khi số lượng segment lớn.
   - Cần một module xây dựng `combined_dubbed_audio.wav` dựa trên timeline chính xác tuyệt đối, tự động chèn silence ở các khoảng lặng và xử lý overlap.

2. **Chế độ Time-Stretching & Tempo Adjustment chưa hoàn thiện:**
   - Hàm `sync_and_stretch_audio` đang clamp tempo trong khoảng `[0.75, 1.5]`. Nếu TTS dài hơn khung thời gian 3 lần (ví dụ: TTS 6s, target 2s), tempo bị tràn ra 4s gây đè câu tiếp theo.
   - Chưa hỗ trợ chuỗi filter `atempo` của FFmpeg (khi ratio $< 0.5$ hoặc $> 2.0$, FFmpeg yêu cầu nối nhiều bộ lọc `atempo`).

3. **Chưa có xử lý Overlap Segments:**
   - Khi `Segment A` chưa kết thúc mà `Segment B` đã bắt đầu, hệ thống chưa phát hiện hoặc cảnh báo `OVERLAPPING_SEGMENTS`.

4. **Thiếu Silence Padding & Gap Preservation:**
   - Khoảng trống giữa các câu thoại (ví dụ: câu 1 kết thúc ở 5s, câu 2 bắt đầu ở 9s) phải được lấp đầy bằng silence PCM chính xác $4.0\text{s}$.

5. **Thiếu Báo Cáo Alignment & Output Duration Validation:**
   - Chưa kiểm tra khớp độ dài video đầu ra với video đầu vào (Master Timeline) sau khi render.

---

## 5. Phân Tích Các Trường Hợp Rủi Ro Kỹ Thuật

| Kịch bản Rủi ro | Tình trạng hiện tại | Giải pháp thiết kế mới |
| :--- | :--- | :--- |
| **1. Audio TTS dài hơn timestamp gốc** | Bị clamp 1.5x, audio tràn sang segment sau gây đè thoại | Áp dụng Multi-stage `atempo` (tăng tốc độ lên tới 2.0x). Nếu vượt ngưỡng an toàn, tự động trim và log cảnh báo |
| **2. Audio TTS ngắn hơn timestamp gốc** | Trả về file ngắn, có thể làm lệch vị trí nếu concat | Giữ nguyên tốc độ đọc tự nhiên + Chèn silence padding để đủ khung thời lượng |
| **3. Khoảng im lặng giữa 2 câu thoại** | Bị bỏ qua nếu dùng concat fallback | Chèn PCM Silence chính xác từ `end_time(i)` tới `start_time(i+1)` |
| **4. Segment bắt đầu từ 30s** | Nếu dùng concat, audio bị đẩy lên 0s | Timeline Builder đặt mốc sample tại `30.0s * sample_rate`, 30s đầu là silence |
| **5. Segments bị Overlap timestamp** | Gây chồng âm thanh hoặc lỗi filter FFmpeg | Log `OVERLAPPING_SEGMENTS`, áp dụng crossfade / ducking nhẹ hoặc điều chỉnh offset |
| **6. TTS thất bại ở 1 segment** | Làm sập toàn bộ Job render | Cho phép Fallback: giữ audio gốc tại segment lỗi hoặc dùng silence + ghi log chi tiết |
| **7. Video không có thoại / Nhiều khoảng lặng** | Dễ bị mất audio track ở video thành phẩm | Video gốc là **Master Timeline**, audio output được lấp đầy silence đúng bằng $T_{\text{video}}$ |
| **8. Video có Audio gốc / Không Audio gốc** | Xử lý chưa nhất quán | Kiểm tra `audio_available`. Nếu không có audio gốc, ép về mode `mute` |

---

## 6. Đề Xuất Giải Pháp Kiến Trúc Mới (`VideoAudioSyncService`)

Xây dựng module **`VideoAudioSyncService`** độc lập trong `backend/app/services/video_translator/sync_service.py`:

1. **Normalize Segment Audio:** Chuẩn hóa toàn bộ TTS audio thành PCM WAV (44.1kHz / 16-bit / Stereo).
2. **Tempo Adjustment Strategy:**
   - Tính tỷ lệ $R = \text{duration}_{\text{actual}} / \text{duration}_{\text{target}}$.
   - Nếu $R > 1.0$: Tăng tốc bằng `atempo` (ghép chuỗi nếu $R > 2.0$). Giới hạn max tempo $= 1.85$ để giữ chất giọng tự nhiên.
   - Nếu $R < 1.0$: Giữ nguyên tốc độ đọc (1.0x) và đệm silence.
3. **Timeline PCM Builder:**
   - Khởi tạo mảng PCM Silence với độ dài đúng bằng $\text{Duration}_{\text{video}} \times \text{SampleRate}$.
   - Ghi từng segment vào vị trí $\text{start\_time} \times \text{SampleRate}$.
   - Tránh hiện tượng suy hao volume $1/N$ của FFmpeg `amix`.
4. **Muxing & Audio Mixing:**
   - Kết hợp `combined_dubbed_audio.wav` với Video gốc dựa trên `original_audio_mode` (`mute`, `duck`, `keep`).
5. **Output Validation & Report:**
   - Dùng FFprobe kiểm tra độ dài video thành phẩm $T_{\text{out}} \approx T_{\text{source}}$.
   - Xuất bảng báo cáo Alignment từng segment (`Expected Start`, `Actual Start`, `Status`).

# BÁO CÁO ĐIỀU TRA LỖI: JOB FAILED KHI XỬ LÝ VIDEO DÀI (30 PHÚT)

**Ngày điều tra:** 2026-08-22  
**Hệ thống:** WorkflowVdAi (FastAPI Backend + React Frontend + FFmpeg + SQLite)  
**File báo cáo:** `docs/debug/job-failed-video-processing.md`  

---

## A. Root Cause (Nguyên nhân gốc rễ)

Qua việc trace toàn bộ luồng xử lý từ Frontend (React) tới Backend (FastAPI, FFmpeg, Asyncio Worker, Database, Storage), đã xác định được **5 nguyên nhân gốc rễ** gây ra lỗi `Job Failed (500)` và nút **"Xem Log Chi Tiết"** không hoạt động khi xử lý video dài (30 phút):

### 1. Nút "Xem Log Chi Tiết" bị vô hiệu hóa khi Job chưa kịp lưu state hoặc Import/Start thất bại
- **Hiện tượng:** Người dùng bấm "Xem Log Chi Tiết", không có phản ứng gì (nút bị trơ/chết).
- **Nguyên nhân:** Trong `VideoTranslator.jsx`, hàm `handleOpenLogs` kiểm tra `if (activeJobId)`. Khi luồng `handleStartImportAndTranslation` gặp lỗi (ví dụ: HTTP 500 ở API import/job start), `setJob(null)` đã được gọi ở đầu hàm. Do `job` bằng `null`, `activeJobId` bị `undefined`. Do đó điều kiện `if (activeJobId)` trả về `false` và `handleOpenLogs` bỏ qua toàn bộ sự kiện click, không mở Modal log và không thông báo cho người dùng.

### 2. FFmpeg Process Deadlock do Pipe Buffer bị đầy khi xử lý Video dài
- **Hiện tượng:** FFmpeg xử lý video ngắn 30s-2m thành công, nhưng với video 30 phút hệ thống bị treo hoặc throw `FFmpegExecutionError` / timeout.
- **Nguyên nhân:** Trong `backend/app/media/ffmpeg_process.py`, hàm `_read_process_worker` đọc luồng `stdout` tuần tự bằng vòng lặp `for line in process.stdout:`. Trong khi đó, luồng `stderr` chỉ được đọc **sau khi** `stdout` kết thúc. Với video 30 phút, FFmpeg ghi rất nhiều thông tin log/warning vào `stderr`. Khi `stderr` pipe buffer của Hệ điều hành (4KB-64KB) bị đầy, tiến trình FFmpeg bị block chờ Python đọc `stderr`. Ngược lại, Python đang block chờ FFmpeg ghi xong `stdout`. Dẫn tới **Deadlock hoàn toàn giữa Python và FFmpeg**.

### 3. Hardcoded Timeout 300 giây (5 phút) cho FFmpeg Extraction
- **Hiện tượng:** Xử lý video khoảng 30 phút tự động bị ngắt đứt sau đúng 5 phút.
- **Nguyên nhân:** Trong `backend/app/services/video_translator/translator_service.py` (dòng 111), bước `extract_audio_from_video` cài đặt `timeout=300.0` (5 phút). Đối với video 30 phút, việc trích xuất audio PCM WAV hoặc render/sync trên CPU bình thường có thể mất > 300 giây, dẫn tới FFmpeg bị `kill` cưỡng chế và Job bị đánh dấu `FAILED`.

### 4. Đọc toàn bộ File Video dung lượng lớn vào RAM (`file.read()`)
- **Hiện tượng:** Backend ném lỗi HTTP 500 / MemoryError khi upload video dài 30 phút (dung lượng 300MB - 1GB).
- **Nguyên nhân:** Tại endpoint `POST /api/video-translator/import` (`backend/app/api/routes/video_translator.py`), code thực hiện `content = await file.read()` nạp toàn bộ byte của file upload vào bộ nhớ RAM cùng một lúc thay vì ghi theo chunk (chunk streaming).

### 5. Frontend nuốt thông tin lỗi HTTP 500 & Backend thiếu Global Exception Handling chi tiết
- **Hiện tượng:** Màn hình chỉ hiển thị chuỗi vô nghĩa: `Request failed with status code 500`.
- **Nguyên nhân:** Khi API trả về 500 (chưa qua custom error wrapper), Axios ở frontend trả về error message mặc định `Request failed with status code 500`. Frontend không hiển thị HTTP Method, URL, Response payload, hay Job ID. Đồng thời Backend FastAPI chưa có Custom Global Exception Handler để capture chi tiết traceback và trả về JSON chuẩn cho client.

---

## B. Reproduction (Các bước tái hiện)

1. Mở trang **Video Translator** trên Web UI.
2. Tải lên một video dài khoảng 30 phút (dung lượng ~400MB - 800MB) hoặc dán URL video dài.
3. Nhấn **"🚀 Bắt đầu Nhập & Dịch Video"**.
4. **Kết quả:**
   - Hệ thống lập tức hoặc sau 5 phút báo:  
     `❌ Xử Lý Thất Bại (Job Failed)`  
     `Request failed with status code 500`
   - Người dùng nhấp vào nút **"📜 Xem Log Chi Tiết"** -> Không có bất kỳ phản ứng nào, Modal log không mở được.

---

## C. Failed Step (Bước thất bại)

- **Bước 0 (Import / Job Creation):** Thất bại do nạp toàn bộ file vào RAM hoặc ném uncaught exception trả HTTP 500 mà chưa lưu `Job ID` vào React State.
- **Bước 1 (Extract Audio):** Thất bại do Deadlock Pipe Buffer hoặc do vượt quá hardcoded timeout 300s.

---

## D. Backend Error (Lỗi phía Backend)

```text
FFmpegExecutionError: FFmpeg execution timed out or failed (exit code -1)
  or
MemoryError / Out of Memory during await file.read()
  or
HTTP 500 Internal Server Error (Uncaught exception in background task or endpoint route)
```

---

## E. Frontend Error (Lỗi phía Frontend)

- Axios Catch Block: `err.message` = `"Request failed with status code 500"`.
- `activeJobId` = `undefined` -> `handleOpenLogs` hủy thao tác mở Modal log.

---

## F. Log System (Vấn đề của hệ thống Log)

- Khi API `/import` hoặc `/jobs` fail ở tầng HTTP Request, file `job.log` chưa được khởi tạo.
- Nút "Xem Log Chi Tiết" không có cơ chế fallback để hiển thị log khởi tạo/lỗi request khi chưa có `activeJobId`.
- Log trong DB bị cắt ngắn ở 300 ký tự (`err_msg[:300]`), làm mất `stackTrace` và `stderr` thực tế của FFmpeg.

---

## G. Architecture Issue (Vấn đề Kiến trúc)

1. **FFmpeg Subprocess Execution:** Thiếu reader concurrent (đọc song song `stdout` và `stderr` bằng `asyncio` hoặc thread riêng) gây ra I/O Pipe Deadlock.
2. **Synchronous Upload Handling:** Đọc toàn bộ file video vào RAM thay vì dùng async chunked streaming.
3. **Timeout Strategy:** Cấu hình timeout cứng 300s không tỉ lệ với thời lượng video (`total_duration`).
4. **Error Handling & State Consistency:** Chưa lưu `job_id` lập tức vào state trước khi gọi API `start`, khiến Frontend mất dấu Job khi API `start` fail.

---

## H. Proposed Fix (Danh sách thay đổi đề xuất)

### 1. Fix Subprocess FFmpeg Deadlock & Dynamic Timeout
- Sửa `backend/app/media/ffmpeg_process.py`: Sử dụng 2 worker thread riêng biệt để đọc `stdout` và `stderr` đồng thời (concurrent reading), triệt tiêu hoàn toàn nguy cơ pipe buffer deadlock.
- Tự động tính toán timeout của FFmpeg dựa trên `total_duration` (ví dụ: `max(600.0, total_duration * 3.0)`), không dùng timeout cứng 300s.

### 2. Fix File Upload Chunk Streaming
- Sửa `backend/app/api/routes/video_translator.py` tại endpoint `/import`: Ghi file upload theo từng chunk (1MB/chunk) xuống đĩa thay vì `await file.read()`.

### 3. Fix Frontend "Xem Log Chi Tiết" & Job State & Error Display
- Sửa `VideoTranslator.jsx`:
  - Lưu `pendingJobId` ngay khi tạo job xong, đảm bảo `activeJobId` luôn có giá trị trước khi gọi `startJob`.
  - Sửa `handleOpenLogs`: Nếu chưa có `activeJobId`, hiển thị Modal chứa chi tiết lỗi Pipeline Error hiện tại thay vì bỏ qua click.
  - Cải tiến hiển thị lỗi: Hiện chi tiết `HTTP Status`, `Endpoint`, `Message` và `Traceback` nếu có.

### 4. Upgrade Backend Job Logger & Exception Handler
- Sửa `backend/app/core/job_logger.py` & `video_translator.py`: Lưu đầy đủ stack trace, FFmpeg stderr và step status vào log file và DB.
- Thêm Global Exception Handler trong FastAPI (`main.py`) để bắt mọi uncaught 500 error và format JSON trả về chi tiết cho client.

### 5. Smart Retry Enhancement
- Cho phép Smart Retry nhận biết Stage thất bại và khôi phục từ Stage đó thay vì chạy lại toàn bộ từ đầu nếu Phase 1 đã thành công.

---

## I. Risk (Đánh giá rủi ro)

- **Rủi ro thấp:** Thay đổi logic đọc pipe FFmpeg và chunk stream upload an toàn tuyệt đối, cải thiện hiệu năng và độ ổn định.
- **Tương thích:** Không làm thay đổi DB Schema hay đứt gãy API Contract hiện có.

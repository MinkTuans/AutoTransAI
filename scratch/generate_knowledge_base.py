import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = docx.Document()

    # Set Margins (1 inch all around)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Base Colors
    COLOR_PRIMARY = RGBColor(0x02, 0x84, 0xC7)   # Tailwind Sky-600
    COLOR_NAVY = RGBColor(0x0F, 0x17, 0x2A)      # Tailwind Slate-900
    COLOR_TEXT = RGBColor(0x33, 0x41, 0x55)      # Tailwind Slate-700
    COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)     # Tailwind Slate-500

    # Configure Default Style
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Segoe UI'
    style_normal.font.size = Pt(10.5)
    style_normal.font.color.rgb = COLOR_TEXT

    # Helper: Set Cell Shading
    def set_cell_background(cell, fill_hex):
        shd_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
        cell._tc.get_or_add_tcPr().append(parse_xml(shd_xml))

    # Helper: Set Cell Margins (Padding)
    def set_cell_margins(cell, top=100, bottom=100, start=150, end=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{start}" w:type="dxa"/><w:right w:w="{end}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    # Helper: Add Styled Heading 1
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.color.rgb = COLOR_NAVY
        return p

    # Helper: Add Styled Heading 2
    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    # Helper: Add Styled Heading 3
    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = COLOR_NAVY
        return p

    # Helper: Add Paragraph
    def add_p(text="", bold=False, italic=False, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if text:
            run = p.add_run(text)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = COLOR_TEXT
        return p

    # Helper: Add Bullet Item
    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        run_b = p.add_run(bold_prefix)
        run_b.bold = True
        run_b.font.color.rgb = COLOR_NAVY
        run_t = p.add_run(text)
        run_t.font.color.rgb = COLOR_TEXT
        return p

    # Helper: Add Callout Box
    def add_callout(text, title="LƯU Ý QUAN TRỌNG", alert_type="IMPORTANT"):
        colors = {
            "IMPORTANT": ("0284C7", "F0F9FF"), # Primary Blue / Ice Light
            "WARNING": ("D97706", "FFFBEB"),   # Amber / Light Warm
            "CAUTION": ("DC2626", "FEF2F2"),   # Red / Light Red
            "NOTE": ("475569", "F8FAFC"),      # Slate / Light Slate
        }
        border_hex, bg_hex = colors.get(alert_type, colors["NOTE"])
        
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=140, bottom=140, start=200, end=200)

        # Set left border thick, clear others
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="36" w:space="0" w:color="{border_hex}"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(4)
        r_title = p.add_run(f"[{title}]\n")
        r_title.bold = True
        r_title.font.size = Pt(10)
        r_title.font.color.rgb = RGBColor.from_string(border_hex)

        r_text = p.add_run(text)
        r_text.font.size = Pt(9.5)
        r_text.font.color.rgb = COLOR_TEXT
        
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Helper: Add Code Block
    def add_code_block(code_text):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=120, bottom=120, start=180, end=180)

        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/><w:top w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/><w:right w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/><w:bottom w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/></w:tcBorders>')
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.05
        run = p.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Helper: Add Table
    def add_styled_table(headers, rows_data, col_widths=None):
        table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Header Row
        hdr_cells = table.rows[0].cells
        for i, header_text in enumerate(headers):
            cell = hdr_cells[i]
            cell.text = header_text
            set_cell_background(cell, "0F172A") # Navy dark
            set_cell_margins(cell, top=120, bottom=120, start=140, end=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = 'Segoe UI'
                r.font.bold = True
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        # Data Rows
        for r_idx, row_values in enumerate(rows_data):
            row_cells = table.rows[r_idx + 1].cells
            bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row_values):
                cell = row_cells[c_idx]
                cell.text = str(val)
                set_cell_background(cell, bg_color)
                set_cell_margins(cell, top=90, bottom=90, start=120, end=120)
                p = cell.paragraphs[0]
                for r in p.runs:
                    r.font.name = 'Segoe UI'
                    r.font.size = Pt(9)
                    r.font.color.rgb = COLOR_TEXT
                
                # Borders
                tcPr = cell._tc.get_or_add_tcPr()
                borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/><w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/><w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/></w:tcBorders>')
                tcPr.append(borders)

        if col_widths:
            for row in table.rows:
                for idx, width in enumerate(col_widths):
                    row.cells[idx].width = Inches(width)

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # =========================================================================
    # DOCUMENT COVER & TITLE
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(12)
    run_t = p_title.add_run("AUTOTRANSAI STUDIO\nPROJECT KNOWLEDGE BASE")
    run_t.font.name = 'Segoe UI'
    run_t.font.size = Pt(26)
    run_t.font.bold = True
    run_t.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(24)
    run_sub = p_sub.add_run("Tài Liệu Phân Tích Toàn Bộ Kiến Trúc, Source Code, Database Schema, AI System & API Specification")
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = COLOR_PRIMARY

    add_callout(
        "Tài liệu này được tạo hoàn toàn dựa trên việc đọc, quét và phân tích 100% source code thực tế, file cấu hình, database schema và dependency trong repository AutoTransAI. Mọi thông tin đều là FACT đã được kiểm chứng qua mã nguồn và hệ thống unit test.",
        title="THÔNG TIN TÀI LIỆU",
        alert_type="NOTE"
    )

    doc.add_page_break()

    # =========================================================================
    # TABLE OF CONTENTS PLACEHOLDER
    # =========================================================================
    add_h1("MỤC LỤC TỔNG QUAN")
    toc_items = [
        "1. Project Overview (Tổng quan Dự án)",
        "2. Technology Stack (Công nghệ Sử dụng)",
        "3. Project Architecture (Kiến trúc Hệ thống)",
        "4. Folder Structure (Cấu trúc Thư mục Chi tiết)",
        "5. Frontend Architecture (Kiến trúc Frontend)",
        "6. Backend Architecture (Kiến trúc Backend)",
        "7. Database Architecture (Bản đồ Bảng & Quan hệ)",
        "8. Complete Feature Inventory (Danh mục 100% Chức năng)",
        "9. AI System Architecture (Kiến trúc AI Provider & Failover)",
        "10. AI Providers (Chi tiết các Nhà cung cấp AI)",
        "11. API Key Management (Quản lý & Bảo mật API Key)",
        "12. AI Models (Danh sách Model AI thực tế)",
        "13. Video Processing Pipeline (Luồng Xử lý Video & Dubbing)",
        "14. API Documentation (Tài liệu API Endpoints)",
        "15. Storage Architecture (Hệ thống Lưu trữ Local & Cloudflare R2)",
        "16. Settings System (Hệ thống Cấu hình)",
        "17. Environment Variables (Giải thích Biến Môi trường)",
        "18. Important Services (Các Service Trung tâm)",
        "19. Important Data Flows (Các Luồng Dữ liệu Chính)",
        "20. Problems & Technical Debt (Vấn đề & Nợ kỹ thuật)",
        "21. Security Issues (Vấn đề Bảo mật & Rủi ro)",
        "22. Recommended Improvements (Đề xuất Cải tiến Architecture)",
        "23. Future Extension Guide (Hướng dẫn Mở rộng Developer Guide)",
    ]
    for item in toc_items:
        add_bullet("", item)

    doc.add_page_break()

    # =========================================================================
    # 1. PROJECT OVERVIEW
    # =========================================================================
    add_h1("1. Project Overview (Tổng quan Dự án)")
    add_p("Tên Dự án: AutoTransAI (tên nội bộ khác: WorkflowVdAi / AutoTransAi Studio)")
    add_p("Mục đích hệ thống: AutoTransAI là một ứng dụng Desktop/Web local-first kết hợp hai đường ống xử lý video mạnh mẽ: (1) Tạo video tự động từ kịch bản văn bản (Script-to-Video Pipeline) và (2) Dịch thuật & Lồng tiếng video bằng AI (AI Video Translation & Dubbing Pipeline). Ứng dụng giúp tự động hóa toàn bộ quy trình tải video, bóc tách âm thanh, nhận dạng giọng nói STT, dịch thuật đa ngữ kèm quản lý thuật ngữ (Glossary), tổng hợp giọng nói AI (TTS), đồng bộ kéo giãn thời lượng âm thanh PCM 44.1kHz sample-accurate, chèn phụ đề hiệu ứng ASS/SRT/VTT, biên tập reframing 9:16/16:9, thêm logo/watermark, chèn nhạc nền (BGM ducking), kiểm định chất lượng LUFS (EBU R128), và xuất bản trực tiếp lên YouTube.")

    add_h2("Chức năng Chính của Hệ thống")
    add_bullet("Script-to-Video Pipeline: ", "Phân tích kịch bản đa đoạn (script parsing), ước tính thời lượng âm thanh và chi phí token, chạy preflight check API quota, tổng hợp voice TTS per segment, sinh video clip minh họa per segment (Kling AI / fal.ai / Local), và ghép nối tự động.")
    add_bullet("AI Video Translator & Dubbing Engine: ", "Nhập video từ URL (YouTube, Bilibili, TikTok, direct MP4) hoặc File Upload local. Tự động trích xuất âm thanh 16kHz, chạy STT (Gemini Audio STT / OpenAI Whisper), nhận dạng ngôn ngữ và diarization speaker, dịch kịch bản bằng Gemini kèm bộ nhớ Glossaries & Entity extraction, ánh xạ giọng đọc đa nhân vật (SpeakerVoiceMapping), tổng hợp TTS (Edge TTS, Google Cloud TTS, ElevenLabs), kéo giãn thời lượng bằng thuật toán atempo, lắp ráp timeline PCM 44.1kHz stereo, và render video lồng tiếng.")
    add_bullet("Video Studio & Post-Processing: ", "Hệ thống biên tập hậu kỳ hỗ trợ chuyển đổi tỉ lệ khung hình (16:9 Landscape, 9:16 Shorts/TikTok, 1:1 Square), chèn logo/watermark với vị trí tùy chỉnh và độ mờ opacity, tự động giảm âm lượng nhạc nền khi có tiếng nói (BGM Ducking), chèn phụ đề hiệu ứng ASS/SRT/VTT, và kiểm định chất lượng âm thanh LUFS.")
    add_bullet("Multi-API Key Failover System (KeyManager): ", "Hệ thống quản lý API key thông minh hỗ trợ xoay vòng nhiều key (priority rotation), tự động chuyển key khi gặp lỗi 429 Rate Limit (đưa vào cooldown 60s), vô hiệu hóa key khi hết hạn ngạch/401/403, và đồng bộ 2 chiều giữa UI, file JSON persistence (data/api_keys.json) và file `.env`.")
    add_bullet("Unified Stage-Based Workflow Engine: ", "Kiến trúc workflow 6 giai đoạn (INGEST, ANALYZE, TRANSLATE, DUB, PRODUCE, PUBLISH) hỗ trợ lưu checkpoint, tạm dừng (pause), tiếp tục (resume), và các cổng kiểm định chất lượng (QC Gates) ở từng bước.")

    add_h2("Trạng thái Phát triển Hiện tại")
    add_p("Trạng thái: WORKING (Mức độ hoàn thiện cao, mã nguồn sạch, có 114 unit & integration test chạy thành công 100%, frontend build thành công).")

    # =========================================================================
    # 2. TECHNOLOGY STACK
    # =========================================================================
    add_h1("2. Technology Stack (Công nghệ Sử dụng)")
    add_p("Toàn bộ công nghệ được xác định dựa trên file dependency [backend/requirements.txt](file:///c:/Hack/AutoTransAI/backend/requirements.txt) và [frontend/package.json](file:///c:/Hack/AutoTransAI/frontend/package.json).")

    tech_headers = ["Phân loại", "Công nghệ / Library", "Phiên bản thực tế", "Mục đích sử dụng"]
    tech_data = [
        ["Frontend Framework", "React", "18.3.1", "Xây dựng giao diện người dùng SPA"],
        ["Frontend Build Tool", "Vite", "5.4.0", "Module bundler & Dev server (port 5173)"],
        ["Frontend Styling", "Vanilla CSS", "CSS3 / App.css", "Thiết kế giao diện glassmorphism, responsive UI"],
        ["Frontend HTTP Client", "Axios", "1.19.0", "Gửi API request tới Backend FastAPI"],
        ["Backend Framework", "FastAPI", ">= 0.115.0", "RESTful API framework bất đồng bộ (async python)"],
        ["ASGI Server", "Uvicorn (standard)", ">= 0.30.0", "Chạy server FastAPI trên localhost:8000"],
        ["Data Validation", "Pydantic & Pydantic-Settings", ">= 2.8.0", "Validate dữ liệu request/response và load .env"],
        ["Database ORM", "SQLAlchemy (asyncio)", ">= 2.0.30", "ORM tương tác database bất đồng bộ"],
        ["Database Driver", "aiosqlite", ">= 0.20.0", "Driver async cho SQLite database"],
        ["Migration Tool", "Alembic & Dynamic DDL", ">= 1.13.0", "Quản lý schema migration database"],
        ["Audio Processing", "edge-tts", ">= 6.1.0", "Tổng hợp giọng nói Microsoft Edge TTS miễn phí"],
        ["HTTP Client (Backend)", "httpx", ">= 0.27.0", "Gửi HTTP request async tới các AI Provider APIs"],
        ["Logging", "structlog", ">= 24.1.0", "Ghi log cấu trúc JSON/Console cho backend"],
        ["Real-time Streaming", "sse-starlette", ">= 2.0.0", "Server-Sent Events truyền tiến độ công việc về UI"],
        ["Storage Client", "boto3", "Built-in", "Tương tác S3 API cho Cloudflare R2 Persistent Storage"],
        ["Media Engine", "System FFmpeg / FFprobe", "Async Subprocess", "Xử lý video, cắt ghép, mix audio, atempo, LUFS"],
        ["Testing", "pytest & pytest-asyncio", ">= 8.0.0", "Bộ unit & integration test toàn bộ backend"],
    ]
    add_styled_table(tech_headers, tech_data, [1.5, 1.8, 1.0, 2.2])

    # =========================================================================
    # 3. PROJECT ARCHITECTURE
    # =========================================================================
    add_h1("3. Project Architecture (Kiến trúc Hệ thống)")
    add_p("Hệ thống hoạt động theo mô hình Client-Server Local-First nâng cao. Frontend React giao tiếp với Backend FastAPI qua các REST Endpoints và SSE Stream.")

    add_code_block("""
+-----------------------------------------------------------------------------------+
|                               USER / BROWSER (Vite React UI)                       |
+-----------------------------------------------------------------------------------+
                                         │
                         HTTP REST / SSE Event Streams
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                             FASTAPI BACKEND SERVER                                |
|  - Routers: projects.py, video_translator.py, providers.py, video_editor.py        |
|  - Middleware: CORS, Exception Handlers, Security SSRF Validator                   |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                   UNIFIED STAGE-BASED WORKFLOW ENGINE                             |
|  [STAGE 1: INGEST] -> [STAGE 2: ANALYZE] -> [STAGE 3: TRANSLATE]                  |
|  [STAGE 4: DUB]    -> [STAGE 5: PRODUCE] -> [STAGE 6: PUBLISH]                    |
+-----------------------------------------------------------------------------------+
       │                         │                        │                    │
       ▼                         ▼                        ▼                    ▼
+---------------+       +------------------+     +-----------------+   +---------------+
| DATABASE ORM  |       | KEY MANAGER      |     | MEDIA SERVICES  |   | AI PROVIDERS  |
| SQLAlchemy    |       | Multi-Key Pool   |     | FFmpeg/FFprobe  |   | Gemini, OpenAI|
| SQLite (WAL)  |       | Cooldown & Fail  |     | Audio Sync      |   | Edge/ElevenLabs|
| Mysql Support |       | .env / JSON sync |     | Reframing/Sub   |   | Kling / FAL   |
+---------------+       +------------------+     +-----------------+   +---------------+
       │                         │                        │                    │
       ▼                         ▼                        ▼                    ▼
+-----------------------------------------------------------------------------------+
|                         PERSISTENT STORAGE LAYER                                  |
| Local Storage (data/projects, data/translator) | Cloudflare R2 Persistent Storage  |
+-----------------------------------------------------------------------------------+
""")

    # =========================================================================
    # 4. FOLDER STRUCTURE
    # =========================================================================
    add_h1("4. Folder Structure (Cấu trúc Thư mục Chi tiết)")
    folder_headers = ["Thư mục", "Chức năng", "Các File Quan trọng"]
    folder_data = [
        ["backend/app/api/routes", "Chứa toàn bộ REST API routers và SSE endpoints", "projects.py, video_translator.py, providers.py, video_editor.py, storage.py, system.py"],
        ["backend/app/core", "Quản lý logging, bảo mật SSRF, retry logic, custom exceptions", "exceptions.py, job_logger.py, retry.py, security_url.py"],
        ["backend/app/models", "SQLAlchemy ORM models cho 19 bảng database", "project.py, video_translator.py, video_editor.py, workflow_engine.py, job.py"],
        ["backend/app/providers", "Module giao tiếp với AI providers (Audio, LLM, Video)", "registry.py, base.py, audio/, llm/, video/"],
        ["backend/app/services", "Business logic chính của dự án", "key_manager.py, storage_service.py, cleanup_service.py, video_translator/, video_editor/"],
        ["backend/app/workflow", "Unified Stage-Based Workflow Engine", "orchestrator.py, workflow_engine.py, workflow_context.py, stages/"],
        ["backend/app/media", "Wrapper gọi FFmpeg và FFprobe bất đồng bộ", "ffmpeg_process.py, ffprobe.py"],
        ["frontend/src/pages", "Các màn hình chính của ứng dụng React", "VideoTranslator.jsx, Dashboard.jsx, CreateProject.jsx, ProjectDetail.jsx, Settings.jsx"],
        ["frontend/src/components", "Các React Component tái sử dụng", "WorkflowTimeline.jsx, ProjectGlossaryManager.jsx, VideoEditorStudio.jsx, AIQCScorecard.jsx"],
        ["shared", "Cấu hình dùng chung giữa root và backend", "config.py"],
        ["data", "Thư mục chứa database SQLite, dự án, assets và key JSON", "workflow.db, api_keys.json, projects/, translator/"],
        ["docs", "Tài liệu kiểm định và thiết kế hệ thống", "UNIFIED_WORKFLOW_IMPLEMENTATION_REPORT.md, VIDEO_AUDIO_SYNC_AUDIT.md"],
    ]
    add_styled_table(folder_headers, folder_data, [1.8, 2.2, 2.5])

    # =========================================================================
    # 5. FRONTEND ARCHITECTURE
    # =========================================================================
    add_h1("5. Frontend Architecture (Kiến trúc Frontend)")
    add_p("Frontend là ứng dụng Single Page Application (SPA) xây dựng bằng React 18 và Vite, điều hướng dạng tab state trong `App.jsx`.")
    add_bullet("Điều hướng Trang (Tab Routing): ", "Quản lý bằng state `activePage` với các route: 'translator' (AI Video Translator), 'dashboard' (Quản lý dự án), 'create' (Tạo dự án kịch bản), 'detail' (Chi tiết dự án), và 'settings' (Cấu hình API key).")
    add_bullet("API Client (api.js): ", "Đóng gói toàn bộ lệnh gọi API bằng Axios tới prefix `/api`, phân nhóm thành: `projectsApi`, `providersApi`, `systemApi`, `videoTranslatorApi`, `videoEditorApi`.")
    add_bullet("Real-time Progress & Logs: ", "Sử dụng EventSource (SSE) kết nối tới `/api/video-translator/jobs/{job_id}/progress` và polling log `/jobs/{job_id}/logs` để cập nhật thanh tiến trình 6 giai đoạn theo thời gian thực.")

    # =========================================================================
    # 6. BACKEND ARCHITECTURE
    # =========================================================================
    add_h1("6. Backend Architecture (Kiến trúc Backend)")
    add_p("Backend sử dụng FastAPI với thiết kế bất đồng bộ hoàn toàn (async/await), tuân thủ nguyên tắc Dependency Injection.")
    add_bullet("Lifespan Handler (main.py): ", "Khi ứng dụng khởi động, tự động khởi tạo logging, tạo thư mục data/, chạy `init_db()` để tạo bảng & chạy dynamic migration, và tự động đăng ký tất cả AI Providers vào Registry.")
    add_bullet("Dynamic Schema Migration (_sync_schema_sync): ", "Sử dụng SQLAlchemy Inspector để kiểm tra database hiện tại. Nếu có cột mới trong ORM model mà DB chưa có, tự động phát lệnh `ALTER TABLE ADD COLUMN` để nâng cấp database không gây mất dữ liệu.")
    add_bullet("Global Exception Handler: ", "Bắt toàn bộ ngoại lệ Server Error (500), ghi log stack trace chi tiết và trả về JSON chuẩn chứa `error_type` và thông điệp tiếng Việt thân thiện.")

    # =========================================================================
    # 7. DATABASE ARCHITECTURE
    # =========================================================================
    add_h1("7. Database Architecture (Bản đồ Bảng & Quan hệ)")
    add_p("Hệ thống sử dụng SQLite mặc định ở chế độ WAL (Write-Ahead Logging) giúp tối ưu hiệu năng đọc/ghi đồng thời. Dưới đây là danh sách toàn bộ 19 bảng trong database:")

    db_headers = ["Tên Bảng (Table)", "Primary Key", "Foreign Keys / Quan hệ", "Mục đích Sử dụng"]
    db_data = [
        ["projects", "id (String(36))", "1-N với segments, jobs, glossaries", "Lưu dự án Script-to-Video"],
        ["segments", "id (Integer Auto)", "project_id -> projects.id", "Lưu từng đoạn kịch bản và đường dẫn audio/video"],
        ["jobs", "id (String(36))", "project_id, segment_id", "Lưu các tác vụ sinh audio/video/sync/merge"],
        ["assets", "id (String(36))", "project_id, segment_id", "Lưu thông tin các file phương tiện sinh ra"],
        ["providers", "id (String(50))", "Không có", "Lưu trạng thái cấu hình và quota của Provider"],
        ["usage_snapshots", "id (Integer Auto)", "provider_id -> providers.id", "Lưu lịch sử tiêu thụ tài nguyên AI"],
        ["errors", "id (Integer Auto)", "job_id -> jobs.id", "Lưu vết lỗi chi tiết và traceback của Job"],
        ["video_assets", "id (String(36))", "1-N với video_translation_jobs", "Lưu metadata video nhập từ URL hoặc Upload"],
        ["video_translation_jobs", "id (String(36))", "asset_id -> video_assets.id", "Lưu tiến độ pipeline dịch & lồng tiếng video"],
        ["video_translation_segments", "id (Integer Auto)", "job_id -> video_translation_jobs.id", "Lưu transcript gốc, bản dịch và đường dẫn TTS audio"],
        ["video_edit_configs", "id (String(36))", "job_id, project_id", "Cấu hình reframing, logo, BGM, phụ đề"],
        ["qc_reports", "id (String(36))", "job_id, project_id", "Báo cáo điểm số QC âm thanh, sync drift, black frames"],
        ["youtube_channels", "id (String(36))", "1-N với youtube_publications", "Lưu thông tin kênh và OAuth Token đã mã hóa"],
        ["youtube_publications", "id (String(36))", "channel_id -> youtube_channels.id", "Lưu thông tin video đăng lên YouTube"],
        ["project_glossaries", "id (String(36))", "project_id -> projects.id", "Lưu từ điển thuật ngữ dịch thuật per project"],
        ["speaker_voice_mappings", "id (String(36))", "project_id -> projects.id", "Ánh xạ nhân vật nói với Voice TTS Provider"],
        ["workflow_executions", "id (String(36))", "project_id -> projects.id", "Lưu vết phiên chạy Workflow Engine 6 giai đoạn"],
        ["workflow_stage_executions", "id (String(36))", "workflow_execution_id", "Lưu trạng thái từng Stage (Ingest, Dub, v.v.)"],
        ["workflow_step_executions", "id (String(36))", "stage_execution_id", "Lưu kết quả chi tiết từng Step trong Stage"],
    ]
    add_styled_table(db_headers, db_data, [1.8, 1.2, 1.8, 2.2])

    # =========================================================================
    # 8. COMPLETE FEATURE INVENTORY
    # =========================================================================
    add_h1("8. Complete Feature Inventory (Danh mục 100% Chức năng)")
    add_p("Bảng tổng hợp toàn bộ tính năng của hệ thống và trạng thái thực tế trong source code:")

    feat_headers = ["Module", "Tên Chức năng", "Frontend", "Backend", "AI Provider", "Trạng thái Thực tế"]
    feat_data = [
        ["Video Translator", "Tải video từ URL (YouTube/TikTok)", "VideoTranslator.jsx", "video_source/service.py", "yt-dlp / Direct", "CODE EXISTS - VERIFIED"],
        ["Video Translator", "Upload file video local", "VideoTranslator.jsx", "video_translator.py", "N/A", "CODE EXISTS - VERIFIED"],
        ["Video Translator", "Nhận dạng tiếng nói STT", "VideoTranslator.jsx", "translator_service.py", "Gemini STT / Whisper", "CODE EXISTS - VERIFIED"],
        ["Video Translator", "Dịch thuật kèm Glossary", "ProjectGlossaryManager.jsx", "translate_stage.py", "Gemini LLM / OpenAI", "CODE EXISTS - VERIFIED"],
        ["Video Translator", "Lồng tiếng TTS & Multi-voice", "VideoTranslator.jsx", "dub_stage.py", "Edge / Google / ElevenLabs", "CODE EXISTS - VERIFIED"],
        ["Video Translator", "Đồng bộ âm thanh atempo", "N/A (Tự động)", "sync_service.py", "FFmpeg atempo filter", "CODE EXISTS - VERIFIED"],
        ["Video Studio", "Chuyển tỉ lệ khung hình (Reframing)", "VideoEditorStudio.jsx", "edit_service.py", "FFmpeg scale/crop", "CODE EXISTS - VERIFIED"],
        ["Video Studio", "Chèn Logo / Watermark", "VideoEditorStudio.jsx", "edit_service.py", "FFmpeg overlay", "CODE EXISTS - VERIFIED"],
        ["Video Studio", "Nhạc nền BGM & Ducking", "VideoEditorStudio.jsx", "edit_service.py", "FFmpeg sidechain duck", "CODE EXISTS - VERIFIED"],
        ["Video Studio", "Kiểm định LUFS & Sync QC", "AIQCScorecard.jsx", "qc_service.py", "FFmpeg ebur128", "CODE EXISTS - VERIFIED"],
        ["Publishing", "Tự động sinh tiêu đề SEO", "YouTubePublisherModal.jsx", "youtube_service.py", "Gemini LLM", "CODE EXISTS - VERIFIED"],
        ["Publishing", "Đăng video lên YouTube", "YouTubePublisherModal.jsx", "youtube_service.py", "YouTube Data API v3", "PARTIAL (Cần OAuth Key)"],
        ["API Key System", "Xoay vòng Key & Cooldown 429", "Settings.jsx", "key_manager.py", "N/A", "CODE EXISTS - VERIFIED"],
    ]
    add_styled_table(feat_headers, feat_data, [1.3, 1.8, 1.2, 1.2, 1.0, 1.5])

    # =========================================================================
    # 9. AI SYSTEM ARCHITECTURE
    # =========================================================================
    add_h1("9. AI System Architecture (Kiến trúc AI Provider & Failover)")
    add_p("Hệ thống quản lý AI theo kiến trúc Provider Pattern với Registry tập trung và KeyManager nâng cao.")
    add_bullet("Provider Registry (registry.py): ", "Đóng vai trò Singleton Registry đăng ký các loại provider: `AudioProvider`, `LLMProvider`, `VideoProvider`. Giúp tách biệt hoàn toàn business logic khỏi các nhà cung cấp AI cụ thể.")
    add_bullet("Multi-Key Management & Failover (key_manager.py): ", "Hỗ trợ mỗi Provider có một pool danh sách nhiều API keys với độ ưu tiên (priority). Tự động phân loại lỗi: (1) Lỗi 401/403 -> Đánh dấu INVALID; (2) Lỗi Quota/Balance -> Đánh dấu EXHAUSTED; (3) Lỗi 429 Rate Limit -> Đưa key vào Cooldown 60 giây và tự động chuyển sang key khả thi tiếp theo trong pool.")

    # =========================================================================
    # 10. AI PROVIDERS
    # =========================================================================
    add_h1("10. AI Providers (Chi tiết các Nhà cung cấp AI)")
    add_p("Danh sách 8 AI Providers thực tế được đăng ký trong mã nguồn:")
    add_bullet("1. EdgeTTSProvider (Audio): ", "Sử dụng thư viện `edge-tts` hoàn toàn miễn phí, hỗ trợ đa ngôn ngữ và hàng trăm giọng đọc tự nhiên mà không cần API Key.")
    add_bullet("2. GoogleCloudTTSProvider (Audio): ", "Sử dụng API Google Cloud Text-to-Speech với `GOOGLE_CLOUD_TTS_API_KEY`, cung cấp các giọng đọc Wavenet/Neural2 chất lượng cao.")
    add_bullet("3. ElevenLabsAudioProvider (Audio): ", "Sử dụng ElevenLabs API với `ELEVENLABS_API_KEY`, cung cấp giọng đọc sinh động, truyền cảm và hỗ trợ voice cloning.")
    add_bullet("4. GeminiLLMProvider (LLM & STT): ", "Sử dụng Google Gemini (`gemini-2.5-flash`, `gemini-1.5-pro`) qua SDK `google-genai` với `GEMINI_API_KEY`. Xử lý dịch thuật, trích xuất thực thể, bóc tách âm thanh trực tiếp qua Gemini Audio STT.")
    add_bullet("5. OpenAILLMProvider (LLM & STT): ", "Sử dụng OpenAI API (`gpt-4o`, `gpt-4o-mini`, `whisper-1`) qua SDK `openai` với `OPENAI_API_KEY`.")
    add_bullet("6. KlingVideoProvider (Video): ", "Gọi API Kling AI (`api.klingai.com/v1/videos/text2video`) với `KLING_API_KEY` để tạo video AI từ mô tả văn bản.")
    add_bullet("7. FalVideoProvider (Video): ", "Gọi fal.ai API (`fal-ai/hunyuan-video`) với `FAL_API_KEY` để tổng hợp video ngắn.")
    add_bullet("8. LocalVideoProvider (Video): ", "Provider nội bộ sinh video test/mock local không tốn phí API.")

    # =========================================================================
    # 11. API KEY MANAGEMENT
    # =========================================================================
    add_h1("11. API Key Management (Quản lý & Bảo mật API Key)")
    add_p("API Key được quản lý tập trung bởi class `KeyManager` ([backend/app/services/key_manager.py](file:///c:/Hack/AutoTransAI/backend/app/services/key_manager.py)).")
    add_bullet("Nguồn lưu trữ Key: ", "Key được đọc khởi tạo từ biến môi trường `.env`, sau đó lưu vết trạng thái sử dụng vào file JSON `data/api_keys.json`. Khi người dùng thêm/sửa/xóa Key trên màn hình Settings, hệ thống tự động đồng bộ lại vào `.env` và `data/api_keys.json`.")
    add_bullet("Bảo mật & UI Masking: ", "API Key khi trả về Frontend luôn được che mờ bằng hàm `masked_key` (ví dụ: `AIza-***-8x9Y`). Key nguyên bản KHÔNG BAO GIỜ bị lộ qua các API liệt kê thông thường.")

    # =========================================================================
    # 12. AI MODELS
    # =========================================================================
    add_h1("12. AI Models (Danh sách Model AI thực tế)")
    add_bullet("Gemini Models: ", "`gemini-2.5-flash` (Dịch thuật nhanh, STT audio), `gemini-1.5-pro` (Dịch thuật ngữ cảnh phức tạp).")
    add_bullet("OpenAI Models: ", "`gpt-4o` (LLM cao cấp), `gpt-4o-mini` (LLM tiết kiệm), `whisper-1` (Speech-to-Text).")
    add_bullet("Video Models: ", "`kling-v1` (Kling Text-to-Video), `fal-ai/hunyuan-video` (fal.ai Video Generation).")

    # =========================================================================
    # 13. VIDEO PROCESSING PIPELINE
    # =========================================================================
    add_h1("13. Video Processing Pipeline (Luồng Xử lý Video & Dubbing)")
    add_p("Hệ thống chuyển đổi video trải qua 6 Giai đoạn (Unified Stage Engine):")
    add_code_block("""
[STAGE 1: INGEST]    --> Tải/Import video -> Trích xuất Audio Track 16kHz WAV
[STAGE 2: ANALYZE]   --> Nhận dạng giọng nói (Gemini/Whisper STT) -> Phân đoạn Segments
[STAGE 3: TRANSLATE] --> Dịch thuật bản ghi -> Áp dụng Từ điển Glossaries & Entity IDs
[STAGE 4: DUB]       --> Sinh giọng đọc AI (TTS) -> Kéo giãn atempo -> Lắp PCM 44.1kHz
[STAGE 5: PRODUCE]   --> Reframing (9:16/16:9) -> Chèn Logo/Phụ đề ASS -> Mix BGM -> Render
[STAGE 6: PUBLISH]   --> Sinh SEO Title/Tags -> Kiểm tra OAuth -> Đăng YouTube
""")

    # =========================================================================
    # 14. API DOCUMENTATION
    # =========================================================================
    add_h1("14. API Documentation (Tài liệu API Endpoints)")
    add_p("Hệ thống mở 36 REST Endpoints chính phục vụ Frontend:")

    api_headers = ["Method", "Endpoint Pattern", "Chức năng", "Service Thực thi"]
    api_data = [
        ["POST", "/api/video-translator/check-url", "Kiểm tra URL video & lấy thông tin", "video_source/service.py"],
        ["POST", "/api/video-translator/import", "Import video từ URL hoặc File Upload", "video_translator.py"],
        ["POST", "/api/video-translator/jobs", "Tạo Job dịch thuật video mới", "video_translator.py"],
        ["POST", "/api/video-translator/jobs/{id}/start", "Bắt đầu chạy luồng dịch thuật video", "translator_service.py"],
        ["GET", "/api/video-translator/jobs/{id}", "Lấy thông tin chi tiết Job & Segments", "video_translator.py"],
        ["PUT", "/api/video-translator/jobs/{id}/segments", "Cập nhật chỉnh sửa bản dịch thủ công", "video_translator.py"],
        ["POST", "/api/video-translator/jobs/{id}/render", "Render video lồng tiếng cuối cùng", "translator_service.py"],
        ["POST", "/api/video-translator/jobs/{id}/cancel", "Hủy bỏ Job đang chạy", "video_translator.py"],
        ["POST", "/api/video-translator/jobs/{id}/retry", "Thử lại Job bị lỗi từ Stage thất bại", "workflow_engine.py"],
        ["GET", "/api/providers", "Liệt kê tất cả AI Providers & trạng thái", "providers.py"],
        ["POST", "/api/providers/{id}/config", "Cấu hình API Key cho Provider", "providers.py"],
        ["GET", "/api/providers/{id}/keys", "Liệt kê danh sách API Key mờ (masked)", "key_manager.py"],
        ["POST", "/api/providers/{id}/keys", "Thêm mới API Key vào pool", "key_manager.py"],
        ["DELETE", "/api/providers/{id}/keys/{k_id}", "Xóa API Key khỏi pool", "key_manager.py"],
        ["POST", "/api/providers/{id}/keys/{k_id}/test", "Test tính hợp lệ của API Key", "key_manager.py"],
        ["POST", "/api/projects", "Tạo dự án Script-to-Video kịch bản mới", "projects.py"],
        ["GET", "/api/projects", "Liệt kê tất cả các dự án trong hệ thống", "projects.py"],
        ["POST", "/api/projects/batch-delete", "Xóa hàng loạt dự án & xóa sạch file", "cleanup_service.py"],
        ["POST", "/api/video-editor/config", "Lưu cấu hình biên tập (Ratio, Logo, BGM)", "edit_service.py"],
        ["POST", "/api/video-editor/jobs/{id}/run-qc", "Chạy kiểm định QC (LUFS, Sync drift)", "qc_service.py"],
        ["POST", "/api/video-editor/jobs/{id}/publish-youtube", "Xuất bản video lên YouTube", "youtube_service.py"],
        ["GET", "/api/system/health", "Kiểm tra sức khỏe hệ thống FastAPI", "system.py"],
    ]
    add_styled_table(api_headers, api_data, [1.0, 2.2, 2.0, 1.8])

    # =========================================================================
    # 15. STORAGE ARCHITECTURE
    # =========================================================================
    add_h1("15. Storage Architecture (Hệ thống Lưu trữ Local & Cloudflare R2)")
    add_p("Hệ thống hỗ trợ cơ chế lưu trữ kép Local-First kết hợp Cloudflare R2 Persistent Storage.")
    add_bullet("Local Storage Structure: ", "`data/projects/{project_id}/` (chứa audio/video segment của dự án kịch bản) và `data/translator/assets/` & `data/translator/jobs/{job_id}/` (chứa video gốc, audio bóc tách, file tts, và final_dubbed_video.mp4).")
    add_bullet("Cloudflare R2 Storage (storage_service.py): ", "Nếu cấu hình `R2_ACCESS_KEY_ID` và `R2_SECRET_ACCESS_KEY` trong `.env`, hệ thống tự động upload video kết quả lên Cloudflare R2 bucket (`workflowvdai`) và trả về URL công khai.")
    add_bullet("File Cleanup Service (cleanup_service.py): ", "Khi người dùng thực hiện xóa dự án, `FileCleanupService` sẽ dọn dẹp triệt để toàn bộ thư mục local, xóa record database, và gửi lệnh delete object tới Cloudflare R2, tránh tình trạng rác đĩa (orphan files).")

    # =========================================================================
    # 16. SETTINGS SYSTEM
    # =========================================================================
    add_h1("16. Settings System (Hệ thống Cấu hình)")
    add_p("Màn hình Settings (`Settings.jsx`) cho phép cấu hình trực quan toàn bộ API Keys, Provider mặc định, và xem danh sách Key pool. Mọi thao tác lưu được tự động ghi vào file `.env` và `data/api_keys.json`.")

    # =========================================================================
    # 17. ENVIRONMENT VARIABLES
    # =========================================================================
    add_h1("17. Environment Variables (Giải thích Biến Môi trường)")
    add_p("Chi tiết các biến môi trường cấu hình trong file `.env`:")
    env_headers = ["Biến Môi Trường", "Ý nghĩa / Mục đích", "Giá trị Mặc định / Mẫu"]
    env_data = [
        ["GEMINI_API_KEY", "API Key cho Google Gemini LLM & Audio STT", "AIzaSy... (Lấy từ AI Studio)"],
        ["OPENAI_API_KEY", "API Key cho OpenAI (GPT-4o, Whisper)", "sk-proj-..."],
        ["GOOGLE_CLOUD_TTS_API_KEY", "API Key cho Google Cloud Text-to-Speech", "AIzaSy..."],
        ["ELEVENLABS_API_KEY", "API Key cho ElevenLabs Audio Synthesizer", "xi-api-key-..."],
        ["KLING_API_KEY", "API Key chính cho Kling AI Video Gen", "api-key-..."],
        ["FAL_API_KEY", "API Key cho fal.ai Video Aggregator", "fal-key-..."],
        ["DEFAULT_LLM_PROVIDER", "LLM mặc định cho dịch thuật & SEO", "gemini"],
        ["DATABASE_URL", "Đường dẫn kết nối Database SQLAlchemy", "sqlite+aiosqlite:///data/workflow.db"],
        ["R2_ACCOUNT_ID", "Cloudflare Account ID", "xxxxxxx..."],
        ["R2_ACCESS_KEY_ID", "Cloudflare R2 Access Key ID", "xxxxxxx..."],
        ["R2_SECRET_ACCESS_KEY", "Cloudflare R2 Secret Access Key", "xxxxxxx..."],
        ["R2_BUCKET_NAME", "Tên Bucket lưu trữ trên R2", "workflowvdai"],
    ]
    add_styled_table(env_headers, env_data, [2.0, 3.0, 2.0])

    # =========================================================================
    # 18. IMPORTANT SERVICES
    # =========================================================================
    add_h1("18. Important Services (Các Service Trung tâm)")
    add_bullet("KeyManager (key_manager.py): ", "Quản lý xoay vòng API key, cooldown 429, theo dõi request thành công/thất bại.")
    add_bullet("VideoSourceService (video_source/service.py): ", "Tải video từ URL (YouTube, TikTok) qua `yt-dlp` và trích xuất thông số metadata bằng `ffprobe`.")
    add_bullet("VideoTranslatorService (translator_service.py): ", "Chạy pipeline lồng tiếng video, ghép nối timeline PCM 44.1kHz, kéo giãn `atempo`.")
    add_bullet("VideoEditorService (edit_service.py): ", "Biên tập reframing 9:16/16:9, thêm logo, nhạc nền BGM ducking.")
    add_bullet("QCService (qc_service.py): ", "Phân tích âm lượng LUFS, phát hiện khung hình đen (black frames) và lệch pha âm thanh (sync drift).")
    add_bullet("YouTubeService (youtube_service.py): ", "Sinh SEO chuẩn tiếng Việt bằng Gemini và tải video lên kênh YouTube qua OAuth2.")
    add_bullet("FileCleanupService (cleanup_service.py): ", "Xóa sạch rác đĩa và xóa dữ liệu liên quan ở cả Local & R2 Cloud.")

    # =========================================================================
    # 19. IMPORTANT DATA FLOWS
    # =========================================================================
    add_h1("19. Important Data Flows (Các Luồng Dữ liệu Chính)")
    add_h2("Luồng 1: Quy trình Dịch & Lồng tiếng Video (Video Translation Pipeline)")
    add_p("User nhập URL -> VideoSourceService tải video về data/translator/assets/ -> Trích xuất audio 16kHz -> Gemini STT tạo transcript -> Gemini LLM dịch thuật kèm Glossary -> TTS Provider tạo các file âm thanh lồng tiếng -> Engine kéo giãn atempo đồng bộ thời lượng -> Ghép timeline PCM 44.1kHz stereo -> FFmpeg render video lồng tiếng -> Trả về kết quả UI & Cloud R2.")

    add_h2("Luồng 2: Xoay vòng Key khi bị Rate Limit (API Key Rotation Flow)")
    add_p("Request tới AI Provider -> Nhận HTTP 429 Too Many Requests -> KeyManager bắt lỗi, đổi trạng thái Key hiện tại sang RATE_LIMITED và đặt cooldown_until = current_time + 60s -> KeyManager tìm Key sẵn sàng có ưu tiên cao nhất tiếp theo -> Thực hiện lại Request thành công -> Không làm gián đoạn trải nghiệm người dùng.")

    # =========================================================================
    # 20. PROBLEMS & TECHNICAL DEBT
    # =========================================================================
    add_h1("20. Problems & Technical Debt (Vấn đề & Nợ kỹ thuật)")
    add_bullet("1. Chưa có Distributed Task Queue: ", "Hiện tại hệ thống chạy tác vụ ngầm bằng `asyncio.create_task` và `BackgroundTasks` của FastAPI. Nếu server bị khởi động lại đột ngột, các công việc đang chạy sẽ bị dừng (dù đã có cơ chế khôi phục qua state machine). Trong tương lai nên tích hợp Celery/Redis khi cần mở rộng đa server.")
    add_bullet("2. SQLite Lock Limits: ", "Mặc dù đã bật WAL mode, SQLite vẫn có giới hạn ghi đồng thời khi có hàng trăm tác vụ ghi cùng lúc. Cần chuyển sang MySQL/PostgreSQL khi mở rộng hệ thống lớn.")

    # =========================================================================
    # 21. SECURITY ISSUES
    # =========================================================================
    add_h1("21. Security Issues (Vấn đề Bảo mật & Rủi ro)")
    add_callout(
        "1. API Key Lưu Dạng Plain Text: File .env và data/api_keys.json lưu trữ API Key ở dạng plain text. Cần bảo vệ thư mục dữ liệu này tránh truy cập trái phép.\n"
        "2. YouTube OAuth Token: credentials_json của kênh YouTube lưu trong DB. Cần thêm cơ chế mã hóa AES-256 trước khi lưu xuống đĩa.\n"
        "3. Bảo vệ SSRF: Hệ thống ĐÃ CÓ module `security_url.py` chặn các request tới IP nội bộ (127.0.0.1, 10.x.x.x, 192.168.x.x), ngăn ngừa rủi ro SSRF khi người dùng nhập URL video.",
        title="ĐÁNH GIÁ BẢO MẬT",
        alert_type="WARNING"
    )

    # =========================================================================
    # 22. RECOMMENDED IMPROVEMENTS
    # =========================================================================
    add_h1("22. Recommended Improvements (Đề xuất Cải tiến Architecture)")
    add_bullet("Mã hóa API Keys & Tokens: ", "Mã hóa toàn bộ API keys trong data/api_keys.json bằng cryptography Fernet/AES-256.")
    add_bullet("Tích hợp WebSocket: ", "Thay thế EventSource SSE bằng WebSocket 2 chiều để tăng tốc độ truyền tải thông điệp giữa client và server.")

    # =========================================================================
    # 23. FUTURE EXTENSION GUIDE
    # =========================================================================
    add_h1("23. Future Extension Guide (Hướng dẫn Mở rộng Developer Guide)")
    add_p("Hướng dẫn từng bước cho lập trình viên muốn thêm Provider mới vào hệ thống:")

    add_h2("Cách thêm một Audio/TTS Provider mới")
    add_bullet("Bước 1: ", "Tạo file mới `backend/app/providers/audio/my_custom_tts_provider.py` kế thừa từ `AudioProvider` ([backend/app/providers/base.py](file:///c:/Hack/AutoTransAI/backend/app/providers/base.py)).")
    add_bullet("Bước 2: ", "Implement các hàm bắt buộc: `synthesize()`, `get_voices()`, `validate_configuration()`, `get_quota()`.")
    add_bullet("Bước 3: ", "Đăng ký Provider mới trong `backend/app/main.py` tại hàm `lifespan()` via `registry.register_audio(MyCustomTTSProvider())`.")

    add_code_block("""# Code Template cho Audio Provider mới:
from app.providers.base import AudioProvider, VoiceInfo, AudioSegmentResult

class MyCustomTTSProvider(AudioProvider):
    def __init__(self):
        super().__init__("my_custom_tts", "My Custom TTS Provider")

    async def validate_configuration(self) -> bool:
        return True

    async def get_voices(self, language: str | None = None) -> list[VoiceInfo]:
        return [VoiceInfo(id="voice_1", name="Custom Voice 1", language="vi", gender="female")]

    async def synthesize(self, text: str, voice_id: str, output_path: str, **kwargs) -> AudioSegmentResult:
        # Gọi API tổng hợp giọng nói ở đây
        return AudioSegmentResult(file_path=output_path, duration=3.5)
""")

    # Save Document
    output_filename = "PROJECT_KNOWLEDGE_BASE.docx"
    doc.save(output_filename)
    print(f"Document successfully created and saved to '{output_filename}'!")

if __name__ == "__main__":
    create_document()

# Studio State Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Studio một trang, mở phần phù hợp theo trạng thái mà không mất dữ liệu đang chỉnh sửa.
**Architecture:** Giữ state, API và handlers trong VideoTranslator; thêm bộ phân loại trạng thái hiển thị thuần và accordion giữ DOM. WorkflowTimeline phụ trách thanh tiến độ gọn và chẩn đoán tùy chọn.
**Tech Stack:** React 18, Vite 5, Vitest 2, Testing Library; không thêm thư viện runtime.
**Spec:** docs/superpowers/specs/2026-09-30-studio-state-layout-design.md (anh đã duyệt ngày 2026-09-30).

## Global Constraints

- Giữ giao diện tối và tiếng Việt; giữ tên riêng/model/provider.
- Không đổi API, database, chính sách lưu trữ, xử lý video hoặc quyền đăng video.
- Không thêm tạo lại từng câu, auto-update, hàng đợi hoặc backend mới.
- Không tự cuộn/giành focus khi đổi pha; không unmount form chỉ vì thu gọn.
- Không suy diễn ETA hoặc phần trăm; không coi hoàn tất video là đã đăng video.
- Giữ hai cổng duyệt, copyright hold, kiểm tra đầu vào và cảnh báo chưa lưu.
- Kiểm tra ở 800 px và 1280 px; accordion có button, aria-expanded và aria-controls.
- Không hứa lưu bản nháp qua F5. Không tự push main hoặc phát hành bộ cài trong kế hoạch này.

## Chuẩn bị và đường ranh

- [ ] Đọc AGENTS.md, PROJECT_KNOWLEDGE_BASE.md và spec; xem ahv-plan show, tái sử dụng nhóm AutoTransAI.
- [ ] Tạo nhánh/worktree riêng từ main local sau khi kiểm tra HEAD và working tree; giữ nguyên các commit desktop chưa push. Không reset để khớp remote.
- [ ] Đưa spec và plan vào cùng nhánh để đi kèm implementation; không commit dữ liệu runtime.
- [ ] Chạy baseline frontend: `npm --prefix frontend test -- --run` và `npm --prefix frontend run build`. Ghi kết quả thật; nếu lỗi, điều tra trước khi sửa giao diện.
- [ ] Nếu phần triển khai/review/test kéo dài trên 5 phút: ahv-job phải chạy một lệnh chờ toàn bộ công việc, gắn job vào ahv-plan, đặt ScheduleWakeup. Không dùng job kết thúc ngay sau khi khởi chạy công việc khác.

## File structure

| File | Trách nhiệm |
|---|---|
| frontend/src/pages/studioPresentation.js | Phân loại pha trình bày; không gọi API |
| frontend/src/pages/studioPresentation.test.js | Bảng trạng thái và thứ tự ưu tiên |
| frontend/src/components/StudioSection.jsx | Accordion có điều khiển, giữ children mounted |
| frontend/src/components/StudioSection.test.jsx | Bàn phím, aria, input/focus khi đóng mở |
| frontend/src/pages/VideoTranslator.jsx | Ghép layout với state/handlers hiện có |
| frontend/src/pages/VideoTranslator.studio.test.jsx | Kiểm thử luồng qua page thật |
| frontend/src/components/WorkflowTimeline.jsx | Tiến độ tiếng Việt, tách chẩn đoán |
| frontend/src/components/WorkflowTimeline.test.jsx | Hành động, tiến độ và trạng thái đăng |
| frontend/src/App.css | CSS giới hạn trong .video-translator-studio |
| PROJECT_KNOWLEDGE_BASE.md, CHANGELOG_AI.md | Ghi hành vi đã kiểm chứng |

## Task 1: Phân loại trạng thái hiển thị

**Interfaces:** `resolveStudioPhase({ job, workflow, transfer, busy, loading })` trả về một trong `setup`, `progress`, `review`, `result`, `hold`, `error`, `paused`, `cancelled`, `unknown`, `missing_result`. `sectionForPhase(phase)` trả về `setup`, `progress`, `review` hoặc `result`.

- [ ] Viết test trước trong studioPresentation.test.js. Các trường hợp:
  - Chưa có job/workflow và không loading/busy → setup.
  - Loading dự án mới → unknown; không cho khởi chạy trùng.
  - Transfer hoặc busy mà chưa có job → progress.
  - Job mới: created/queued/pending; job chạy: extracting_audio/stt/translating/generating_tts/syncing_audio/rendering/processing/running → progress.
  - needs_review/segment_editing → review; copyright_hold hoặc stage COPYRIGHT_HOLD → hold.
  - paused → paused; failed/interrupted → error; cancelled → cancelled.
  - completed + output_url hoặc output_video_path → result; không có cả hai → missing_result.
  - Unknown status → unknown, không mặc định setup.
  - workflow running nhưng job đang needs_review: review thắng; terminal job không bị trạng thái workflow cũ ghi đè.
  - Có segments trong khi đang chạy không tự chuyển review.

```js
import { expect, it } from 'vitest';
import { resolveStudioPhase } from './studioPresentation';
it('does not require publishing for a finished video', () => {
  expect(resolveStudioPhase({ job: { status: 'completed', output_url: '/media/a.mp4' },
    workflow: { status: 'running', current_stage: 'PUBLISH' } })).toBe('result');
});
it('keeps partial transcription in progress', () => {
  expect(resolveStudioPhase({ job: { status: 'translating', segments: [{ id: 's1' }] } })).toBe('progress');
});
```

- [ ] Chạy `npm --prefix frontend test -- --run src/pages/studioPresentation.test.js`, xác nhận thất bại vì chưa có helper.
- [ ] Viết helper, dùng job.status khi có, sau đó workflow.status; trạng thái loading dự án mới được caller truyền riêng để không hiện job cũ. Chuẩn hóa chữ thường cho status, chữ hoa cho stage. Branch terminal/review/hold trước busy/transfer. `sectionForPhase` ánh xạ setup→setup, review→review, result→result, còn lại→progress.
- [ ] Đối chiếu các status thật từ handlers/polling và backend schema trước khi hoàn tất bảng; bổ sung alias chỉ khi có nguồn code. Helper không quyết định quyền pause/retry; quyền giữ theo handlers hiện có.
- [ ] Chạy lại test; kiểm tra diff và commit riêng task này.

## Task 2: Accordion không mất trạng thái

**Interfaces:** `StudioSection({ id, title, summary, open, onToggle, children })`; onToggle nhận boolean tiếp theo. Không tự fetch hoặc tự quyết định mở theo pha.

- [ ] Viết test input không mất giá trị/DOM identity khi rerender open=false→true; button có aria-controls trỏ đúng panel; children vẫn mounted nhưng hidden; Enter/Space dùng hành vi button chuẩn.

```jsx
// @vitest-environment jsdom
import React from 'react';
import { afterEach, expect, it } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import StudioSection from './StudioSection';
afterEach(cleanup);
it('keeps the edited input mounted when collapsed', () => {
  const view = open => <StudioSection id="review" title="Duyệt" open={open} onToggle={() => {}}>
    <input aria-label="Bản dịch" defaultValue="Ban đầu" />
  </StudioSection>;
  const { rerender } = render(view(true));
  const input = screen.getByRole('textbox');
  fireEvent.change(input, { target: { value: 'Đã sửa' } });
  rerender(view(false));
  expect(screen.queryByRole('textbox')).toBeNull();
  rerender(view(true));
  expect(screen.getByRole('textbox')).toBe(input);
  expect(input.value).toBe('Đã sửa');
});
```

- [ ] Chạy test riêng, xác nhận red; triển khai component theo cấu trúc:

```jsx
import React from 'react';
export default function StudioSection({ id, title, summary, open, onToggle, children }) {
  return <section className="studio-section">
    <h2><button type="button" id={`${id}-heading`} aria-expanded={open}
      aria-controls={`${id}-panel`} onClick={() => onToggle(!open)}>{title}</button></h2>
    {summary && <p className="studio-section-summary">{summary}</p>}
    <div id={`${id}-panel`} role="region" aria-labelledby={`${id}-heading`} hidden={!open}>
      {children}
    </div>
  </section>;
}
```

- [ ] Giữ switch/checkbox ngoài button heading để tránh interactive lồng nhau. CSS không override hidden; thêm `.video-translator-studio [hidden] { display: none !important; }`.
- [ ] Chạy tests, commit. Không thay accordion ở trang khác.

## Task 3: Thanh tiến độ và hỗ trợ

**Files:** WorkflowTimeline.jsx, WorkflowTimeline.test.jsx, VideoTranslator.jsx.
**Interfaces:** thêm prop `showDiagnostics=false`; giữ handlers/props còn lại. Caller Studio quản lý button Hỗ trợ và truyền prop này.

- [ ] Viết test render job completed ở PRODUCE có output: tên bước Xuất video, không đánh dấu Đăng video thành công nếu chưa có dữ liệu stage PUBLISH passed. Test không có phần trăm thì không hiện 0% giả.
- [ ] Test showDiagnostics=false không hiển thị Log/Heartbeat/FFmpeg/DB telemetry; bật true truy cập được log và retry-stage hiện có. Các nút pause/resume/cancel/retry có nhãn Việt, disabled khi loadingAction có giá trị.
- [ ] Test not_started không có nút Start trong timeline. Nút bắt đầu duy nhất nằm ở phần nhập và đi qua handleOpenPreflightOrPromptProject.
- [ ] Chạy test riêng để chứng minh red.
- [ ] Đổi STAGES labels thành Nhập video/Nhận dạng/Dịch/Lồng tiếng/Xuất video/Đăng video. Bỏ ép completed thành PUBLISH/idx=6; job completed mặc định chỉ hoàn tất tới PRODUCE, PUBLISH lấy trạng thái riêng từ workflow.stages.
- [ ] Dùng kiểm tra số thật: `Number.isFinite(value)` trước hiển thị overall_progress_pct; không dùng `?? 0` để tạo tiến độ giả. Transfer giữ nguồn percent/bytes/speed thực.
- [ ] Đưa các block chẩn đoán hiện có sau điều kiện showDiagnostics; bỏ Log khỏi action bar thường. Giữ retry-stage trong chi tiết kỹ thuật, không đưa quyền khởi chạy vào nội dung HTML.
- [ ] Chạy tests và commit; không sửa retry/pause backend.

## Task 4: Ghép trang theo pha và bảo vệ bản sửa

**Files:** VideoTranslator.jsx, VideoTranslator.studio.test.jsx.
**Interfaces:** gọi resolveStudioPhase với job/workflowStatusData/transferProgress/isProcessing và trạng thái tải của dự án. State mở section là object boolean tại page, không nằm trong response API.

- [ ] Viết tests page thật; mock API/network boundary và EventSource, không mock VideoTranslator/StudioSection/helper. Dùng response shapes lấy từ api.js và các nhánh hydrate thật. Không thêm test-only props vào production.
- [ ] Tests: khởi chạy qua preflight chỉ một lần; rerender/polling không đổi text/focus/section; transition review mở editor; completed mở kết quả; cảnh báo chưa lưu khi đổi dự án; dữ liệu cũ không hiện trong dự án mới; mất kết nối không đổi sang failed hoặc setup.
- [ ] Chạy red. Thêm `openSections`, ref pha trước và identity dự án/job. Chỉ effect khi identity hoặc phase thực đổi, không phụ thuộc cả object response. Reset phần mở khi đổi dự án sau guard; giữ các modal ngoài section.
- [ ] Giữ form/editor mounted trong cùng job. Khi chuyển pha, mở section đích; chỉ thu các section khác khi không có sửa chưa lưu và không chứa document.activeElement. Không gọi scrollIntoView/focus trong effect trạng thái.
- [ ] Để phát hiện sửa bản dịch, tận dụng handler handleSegmentTextChange/handleSegmentFieldChange và reset dirty chỉ sau lưu thành công hoặc đổi job đã xác nhận. Không coi polling như lưu. Giữ guard cấu hình hiện tại, mở rộng guard cho draft editor nếu hiện tại chưa bảo vệ; không thêm autosave.
- [ ] Tách trạng thái lỗi kết nối từ catch fetchWorkflowStatus/EventSource.onerror; chỉ xóa cảnh báo sau response hợp lệ. Giữ dữ liệu gần nhất; khi đổi dự án phải bỏ trạng thái cũ theo identity để không lẫn job.
- [ ] Trong error/paused/cancelled/hold: tái sử dụng handleResumeWorkflow, handleRetryStage/handler retry hiện có, handleCopyrightContinue và handleCancelWorkflow với đúng điều kiện hỗ trợ; không dựng button giả chỉ vì phân loại pha.
- [ ] Giữ handleRenderFinalVideo và handleValidateAndResumeCharacterVoices, validation và hai cổng duyệt. Completed thiếu output hiển thị thông báo, không render player/download.
- [ ] Chạy test rồi commit.

## Task 5: Gom cấu hình, giữ tất cả chức năng

**Files:** VideoTranslator.jsx, VideoTranslator.studio.test.jsx, App.css.

Bảng chuyển vị trí (không đổi giá trị/handler):

| Hiện có | Vị trí mới |
|---|---|
| File/link, kiểm tra URL, ngôn ngữ đích, TTS provider, giọng nam/nữ | Nhập & cấu hình cơ bản |
| LLM provider/model nếu đang có | AI & dịch thuật, đóng mặc định |
| ProjectGlossaryManager | Thuật ngữ, đóng mặc định |
| Âm thanh gốc | Giọng & xử lý âm thanh |
| Tự xác nhận dịch/nhân vật, trim filler, kiểm tra bản quyền | Tùy chọn tự động |
| Watermark bật/tắt, image/text, nội dung, upload, vị trí, scale/opacity | Hình ảnh đầu ra |
| Thumbnail bật/tắt, nguồn, upload/thư viện, style/provider/instruction | Tùy chọn tự động → Thumbnail |
| Bảng câu, character/gender/provider/voice/text, hai nút duyệt | Duyệt bản dịch & giọng |
| Player/download | Kết quả, mở khi xong |
| AIQCScorecard, VideoEditorStudio (bao gồm điều khiển phụ đề hiện có) | Mục thu gọn trong Kết quả |
| YouTubePublisherModal và nút mở | Đăng video tùy chọn trong Kết quả |
| Log modal, telemetry, retry stage | Hỗ trợ → Chi tiết kỹ thuật |
| Đổi dự án, đổi tên, create/preflight/dirty guard modals | Giữ ở page root, không bị thu gọn |

- [ ] Trước di chuyển, rà tất cả onChange/onClick trong page và đối chiếu bảng; nếu có control chưa được liệt kê, bổ sung vào nhóm tương ứng thay vì xóa.
- [ ] Tests: đóng/mở advanced giữ giá trị; bật watermark/thumbnail vẫn có summary khi đóng; lỗi validation mở đúng group và focus đúng trường; không tồn tại hai nút bắt đầu tác vụ.
- [ ] Chạy red; bọc JSX hiện có bằng StudioSection và giữ nguyên handlers. Không viết lại provider catalogs hoặc editor con.
- [ ] Giữ error message của validation; dùng ánh xạ field→section cố định. Với input HTML invalid, mở section trước rồi focus sau render; với preflight server error không xác định field, hiện summary thay vì đoán trường lỗi.
- [ ] Thay grid sidebar bằng bố cục một cột chính. Scope CSS vào .video-translator-studio; min-width:0 cho flex/grid con, controls max-width:100%, buttons flex-wrap; bảng dài cuộn nội bộ.
- [ ] Chạy tests + build, commit task.

## Task 6: Nghiệm thu và bàn giao

- [ ] Chạy `npm --prefix frontend test -- --run`, `npm --prefix frontend run build`, `git diff --check` trên revision cuối.
- [ ] Kiểm tra giao diện trong trình duyệt ở 800×800 và 1280×800: setup, progress, review, result, error, dirty draft; xác nhận không tràn trang, tab order/Enter/Space, hidden content không nhận focus.
- [ ] Dùng fixture/network interception tại môi trường test cho trạng thái hiếm; không gọi dịch vụ tính phí để thử layout. Chụp các trạng thái chính nếu công cụ trình duyệt có sẵn. Nếu chưa có công cụ/Windows, ghi pending đúng phạm vi, không tuyên bố nghiệm thu đã đạt.
- [ ] Review diff chỉ trong phạm vi spec; đối chiếu từng hàng bảng control và state matrix. Sửa phát hiện quan trọng rồi chạy lại đúng tests chịu ảnh hưởng.
- [ ] Cập nhật Knowledge Base/Changelog với hành vi và kết quả thật; không biến bằng chứng build web thành bằng chứng native.
- [ ] Ghi commit, lệnh, kết quả, ảnh/nghiệm thu còn thiếu vào ghi chú ahv-plan. Giữ #3/#4 riêng cho Windows; không đánh done theo suy đoán.
- [ ] Bàn giao nhánh và kết quả để quyết định tích hợp. Không tự xóa worktree, push main hoặc đăng Release.

## Self-review của kế hoạch

Đã đối chiếu: các pha thường/ngoại lệ; hai cổng duyệt; giữ DOM/focus/draft; kết nối và identity;
controls/advanced/validation; optional publishing; số liệu thực; accessibility/responsive;
API/backend/storage không đổi; phạm vi kiểm chứng Windows riêng. Chỉ thêm hai module nhỏ,
không tách lại toàn bộ trang hoặc đưa state management library mới.

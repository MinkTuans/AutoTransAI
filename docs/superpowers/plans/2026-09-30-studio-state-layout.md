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

- [x] Đọc AGENTS.md, PROJECT_KNOWLEDGE_BASE.md, spec, plan và Superpowers guidance. Plan #8/nhóm AutoTransAI do parent quản lý; không tạo task mới.
- [x] Xác nhận worktree được parent cung cấp tại `.worktrees/studio-state-layout`, nhánh `feat/studio-state-layout`, base `4f3689e`. Chỉ hai tài liệu spec/plan untracked lúc bắt đầu; không reset hoặc sửa worktree khác.
- [x] Đưa spec và plan vào cùng nhánh để đi kèm implementation; không commit dữ liệu runtime.
- [x] Chạy baseline frontend: `npm --prefix frontend test -- --run` và `npm --prefix frontend run build`. Ghi kết quả thật; nếu lỗi, điều tra trước khi sửa giao diện.
- [x] Tái sử dụng ahv-job `835ef46a` do parent cung cấp, cập nhật tiến độ tiếng Việt. Parent sở hữu scheduling/ScheduleWakeup, gắn plan và completion #8; worker không tạo thêm job/task hoặc đánh dấu #8 done.

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

- [x] Viết test trước trong studioPresentation.test.js. Các trường hợp:
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

- [x] Chạy `npm --prefix frontend test -- --run src/pages/studioPresentation.test.js`, xác nhận thất bại vì chưa có helper.
- [x] Viết helper, dùng job.status khi có, sau đó workflow.status; trạng thái loading dự án mới được caller truyền riêng để không hiện job cũ. Chuẩn hóa chữ thường cho status, chữ hoa cho stage. Branch terminal/review/hold trước busy/transfer. `sectionForPhase` ánh xạ setup→setup, review→review, result→result, còn lại→progress.
- [x] Đối chiếu các status thật từ handlers/polling và backend schema trước khi hoàn tất bảng; bổ sung alias chỉ khi có nguồn code. Helper không quyết định quyền pause/retry; quyền giữ theo handlers hiện có.
- [x] Chạy lại test; kiểm tra diff và commit riêng task này.

## Task 2: Accordion không mất trạng thái

**Interfaces:** `StudioSection({ id, title, summary, open, onToggle, children })`; onToggle nhận boolean tiếp theo. Không tự fetch hoặc tự quyết định mở theo pha.

- [x] Viết test input không mất giá trị/DOM identity khi rerender open=false→true; button có aria-controls trỏ đúng panel; children vẫn mounted nhưng hidden; Enter/Space dùng hành vi button chuẩn.

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

- [x] Chạy test riêng, xác nhận red; triển khai component theo cấu trúc:

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

- [x] Giữ switch/checkbox ngoài button heading để tránh interactive lồng nhau. CSS không override hidden; thêm `.video-translator-studio [hidden] { display: none !important; }`.
- [x] Chạy tests, commit. Không thay accordion ở trang khác.

## Task 3: Thanh tiến độ và hỗ trợ

**Files:** WorkflowTimeline.jsx, WorkflowTimeline.test.jsx, VideoTranslator.jsx.
**Interfaces:** thêm prop `showDiagnostics=false`; giữ handlers/props còn lại. Caller Studio quản lý button Hỗ trợ và truyền prop này.

- [x] Viết test render job completed ở PRODUCE có output: tên bước Xuất video, không đánh dấu Đăng video thành công nếu chưa có dữ liệu stage PUBLISH passed. Test không có phần trăm thì không hiện 0% giả.
- [x] Test showDiagnostics=false không hiển thị Log/Heartbeat/FFmpeg/DB telemetry; bật true truy cập được log và retry-stage hiện có. Các nút pause/resume/cancel/retry có nhãn Việt, disabled khi loadingAction có giá trị.
- [x] Test not_started không có nút Start trong timeline. Nút bắt đầu duy nhất nằm ở phần nhập và đi qua handleOpenPreflightOrPromptProject.
- [x] Chạy test riêng để chứng minh red.
- [x] Đổi STAGES labels thành Nhập video/Nhận dạng/Dịch/Lồng tiếng/Xuất video/Đăng video. Bỏ ép completed thành PUBLISH/idx=6; job completed mặc định chỉ hoàn tất tới PRODUCE, PUBLISH lấy trạng thái riêng từ workflow.stages.
- [x] Dùng kiểm tra số thật: `Number.isFinite(value)` trước hiển thị overall_progress_pct; không dùng `?? 0` để tạo tiến độ giả. Transfer giữ nguồn percent/bytes/speed thực.
- [x] Đưa các block chẩn đoán hiện có sau điều kiện showDiagnostics; bỏ Log khỏi action bar thường. Giữ retry-stage trong chi tiết kỹ thuật, không đưa quyền khởi chạy vào nội dung HTML.
- [x] Chạy tests và commit; không sửa retry/pause backend.

## Task 4: Ghép trang theo pha và bảo vệ bản sửa

**Files:** VideoTranslator.jsx, VideoTranslator.studio.test.jsx.
**Interfaces:** gọi resolveStudioPhase với job/workflowStatusData/transferProgress/isProcessing và trạng thái tải của dự án. State mở section là object boolean tại page, không nằm trong response API.

- [x] Viết tests page thật; mock API/network boundary và EventSource, không mock VideoTranslator/StudioSection/helper. Dùng response shapes lấy từ api.js và các nhánh hydrate thật. Không thêm test-only props vào production.
- [x] Tests: khởi chạy qua preflight chỉ một lần; rerender/polling không đổi text/focus/section; transition review mở editor; completed mở kết quả; cảnh báo chưa lưu khi đổi dự án; dữ liệu cũ không hiện trong dự án mới; mất kết nối không đổi sang failed hoặc setup.
- [x] Chạy red. Thêm `openSections`, ref pha trước và identity dự án/job. Chỉ effect khi identity hoặc phase thực đổi, không phụ thuộc cả object response. Reset phần mở khi đổi dự án sau guard; giữ các modal ngoài section.
- [x] Giữ form/editor mounted trong cùng job. Khi chuyển pha, mở section đích; chỉ thu các section khác khi không có sửa chưa lưu và không chứa document.activeElement. Không gọi scrollIntoView/focus trong effect trạng thái.
- [x] Để phát hiện sửa bản dịch, tận dụng handler handleSegmentTextChange/handleSegmentFieldChange và reset dirty chỉ sau lưu thành công hoặc đổi job đã xác nhận. Không coi polling như lưu. Giữ guard cấu hình hiện tại, mở rộng guard cho draft editor nếu hiện tại chưa bảo vệ; không thêm autosave.
- [x] Tách trạng thái lỗi kết nối từ catch fetchWorkflowStatus/EventSource.onerror; chỉ xóa cảnh báo sau response hợp lệ. Giữ dữ liệu gần nhất; khi đổi dự án phải bỏ trạng thái cũ theo identity để không lẫn job.
- [x] Trong error/paused/cancelled/hold: tái sử dụng handleResumeWorkflow, handleRetryStage/handler retry hiện có, handleCopyrightContinue và handleCancelWorkflow với đúng điều kiện hỗ trợ; không dựng button giả chỉ vì phân loại pha.
- [x] Giữ handleRenderFinalVideo và handleValidateAndResumeCharacterVoices, validation và hai cổng duyệt. Completed thiếu output hiển thị thông báo, không render player/download.
- [x] Chạy test rồi commit.

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

- [x] Trước di chuyển, rà tất cả onChange/onClick trong page và đối chiếu bảng; nếu có control chưa được liệt kê, bổ sung vào nhóm tương ứng thay vì xóa.
- [x] Tests: đóng/mở advanced giữ giá trị; bật watermark/thumbnail vẫn có summary khi đóng; lỗi validation mở đúng group và focus đúng trường; không tồn tại hai nút bắt đầu tác vụ.
- [x] Chạy red; bọc JSX hiện có bằng StudioSection và giữ nguyên handlers. Không viết lại provider catalogs hoặc editor con.
- [x] Giữ error message của validation; dùng ánh xạ field→section cố định. Với input HTML invalid, mở section trước rồi focus sau render; với preflight server error không xác định field, hiện summary thay vì đoán trường lỗi.
- [x] Thay grid sidebar bằng bố cục một cột chính. Scope CSS vào .video-translator-studio; min-width:0 cho flex/grid con, controls max-width:100%, buttons flex-wrap; bảng dài cuộn nội bộ.
- [x] Chạy tests + build, commit task.

## Task 6: Nghiệm thu và bàn giao

- [x] Chạy `npm --prefix frontend test -- --run`, `npm --prefix frontend run build`, `git diff --check` trên revision cuối.
- [x] Kiểm tra giao diện trong trình duyệt ở 800×800 và 1280×800: setup, progress, review, result, error, dirty draft; xác nhận không tràn trang, tab order/Enter/Space, hidden content không nhận focus.
- [x] Dùng fixture/network interception tại môi trường test cho trạng thái hiếm; không gọi dịch vụ tính phí để thử layout. Chụp các trạng thái chính nếu công cụ trình duyệt có sẵn. Nếu chưa có công cụ/Windows, ghi pending đúng phạm vi, không tuyên bố nghiệm thu đã đạt.
- [x] Review diff chỉ trong phạm vi spec; đối chiếu từng hàng bảng control và state matrix. Sửa phát hiện quan trọng rồi chạy lại đúng tests chịu ảnh hưởng.
- [x] Cập nhật Knowledge Base/Changelog với hành vi và kết quả thật; không biến bằng chứng build web thành bằng chứng native.
- [ ] Parent ghi báo cáo worker vào ahv-plan #8 và quản lý #3/#4 Windows. Worker cung cấp `/tmp/autotransai-studio-result.md`; không tự ghi plan completion hoặc tạo task mới.
- [x] Bàn giao nhánh và kết quả để quyết định tích hợp. Không tự xóa worktree, push main hoặc đăng Release.

## Self-review của kế hoạch

Đã đối chiếu: các pha thường/ngoại lệ; hai cổng duyệt; giữ DOM/focus/draft; kết nối và identity;
controls/advanced/validation; optional publishing; số liệu thực; accessibility/responsive;
API/backend/storage không đổi; phạm vi kiểm chứng Windows riêng. Chỉ thêm hai module nhỏ,
không tách lại toàn bộ trang hoặc đưa state management library mới.


## Evidence / impact review (worker, 2026-09-30)

- Base `4f3689e`; implementation commits task 1-5: `4b264e8`, `5fe6a5d`, `77cc3bd`, `dd68511`, `86c0b3b`. Final self-review/documentation commit recorded in worker result report.
- Baseline needed `npm --prefix frontend ci` because this isolated worktree had no node_modules; after install: 6 files / 36 tests passed and production build passed. No package or lockfile change.
- Actual backend statuses inspected in `backend/app/models/video_translator.py` and `workflow_engine.py`. Actual preflight, workflow-status, studio-state, job, segment and voice-mapping response/payload shapes inspected before frontend edits. Imports/usages show only Studio consumes WorkflowTimeline.
- Existing onChange handlers were all retained. Old collapse toggle/header propagation and save-and-switch callback were replaced; no control removed. Source language/model state without a rendered control was retained without adding new controls. Subtitle controls remain in VideoEditorStudio.
- API/schema/database/storage/provider contracts and desktop/F5 code unchanged. Workflow-status synthesizes every stage as passed for completed jobs; job-derived PUBLISH status is ignored, independent stage evidence remains usable. Publishing is still optional and requires the existing explicit YouTube action.
- Red/green logs in `/tmp/studio-task*-*.log` and `/tmp/studio-*-red.log`: classifier/aliases, mounted section, timeline, page layout, advanced validation/result groups and self-review regressions. Existing segment text autosave remains; draft flags only clear after successful saves, voice edits require the existing voice-mapping save. Save-and-switch failure keeps the current project. A newly selected local file is guarded and can be explicitly discarded, without a new backend persistence feature.
- Self-review fixed hydration briefly enabling Start, stale original job identity on returning to a project, incoming job/project resets, gender/focused edits overwritten by polls, glossary draft carryover, incomplete setting/input dirty tracking, request actions left locked after import, synthesized local overall transfer percentages and diagnostics disclosure placement.
- Browser: Linux Chrome via Playwright installed only under `/tmp/autotransai-studio-browser`; mocked API/SSE and a locally generated silent 1-second MP4, no provider calls. Setup/progress/review/result/error/dirty at 800×800 and 1280×800; page scrollWidth equals viewport width. Native Enter/Space, hidden-panel tab exclusion, draft preservation and paused result video verified. Main/panel/result-tool screenshots and `evidence.json` retained in that directory.
- Native Windows packaging, installed GUI, WebView2 shortcut/F5, installer/Job Object/lifecycle, real provider STT/TTS/render/edit/QC and OAuth publishing remain unverified here. Parent owns native acceptance and integration. Linux emoji glyphs may show missing-glyph boxes; text labels remain accessible, Windows fonts require native verification.

- Operational source check: workflow Pause/Cancel control WorkflowExecution tasks, not direct imported jobs. Direct jobs therefore use existing cancelJob/resumeJobFromCheckpoint methods; Pause is shown only for an independent workflow execution. The cancel endpoint returns failed/CANCELLED, normalized to cancellation in presentation. No new backend feature or endpoint.

### Final worker verification

- `npm --prefix frontend test -- --run`: exit 0, 10 files / 113 tests passed (36 baseline + 77 new). Log: `/tmp/studio-final-tests.log`.
- `npm --prefix frontend run build`: exit 0, Vite production build, 106 modules. Log: `/tmp/studio-final-build.log`.
- `git diff --check`: exit 0.
- `node /tmp/autotransai-studio-browser/validate.cjs`: exit 0; 12 state/viewport combinations, no JS errors or page overflow, 26 screenshots. Browser log: `/tmp/studio-browser-final.log`; fixtures/script/sample/evidence/screenshots: `/tmp/autotransai-studio-browser/`.
- Worker tasks 1-6 complete; handoff report `/tmp/autotransai-studio-result.md` records final branch HEAD/files/commands/scopes. Only unchecked item is parent-owned incorporation into AHV plan/native acceptance; worker does not mark #8 done. No merge/push/release or extra agent delegation.

# Studio một trang theo trạng thái

Ngày: 2026-09-30. Trạng thái: anh đã duyệt (#6), ngày 2026-09-30.
Quyết định đã chốt (#5): giữ một trang, tự mở phần cần dùng theo trạng thái.

## Mục tiêu và phạm vi

Giảm thông tin kỹ thuật và thao tác trùng trên Studio, giữ các chức năng hiện có.
Giữ giao diện tối và ngôn ngữ tiếng Việt. Chỉ thay cách trình bày frontend;
không đổi API, database, cơ chế xử lý, quyền đăng video hoặc chính sách lưu trữ.
Không thêm tạo lại từng câu, auto-update, hàng đợi hoặc chức năng backend mới.

## Bố cục

1. Thanh đầu: tên Studio, chọn/tạo/đổi tên dự án, mục Hỗ trợ.
2. Cảnh báo cấu hình chưa lưu: giữ Lưu và Hủy thay đổi, không bị thu gọn.
3. Thanh trạng thái gọn: Nhập video → Nhận dạng → Dịch → Lồng tiếng → Xuất video → Đăng video.
4. Các phần trên cùng trang: Nhập & cấu hình; Tiến độ; Duyệt bản dịch & giọng; Kết quả.
5. Chi tiết kỹ thuật nằm trong Hỗ trợ, đóng mặc định.

Đăng video là tùy chọn; tạo xong video vẫn được coi là hoàn tất mà không cần đăng.
Khi chưa có tác vụ, thanh trạng thái chỉ thể hiện hướng dẫn, không có phần trăm giả.
Không tự dịch tên riêng, tên model hoặc tên nhà cung cấp.

## Trạng thái và hành động

| Trạng thái | Phần mở chính | Hành động |
|---|---|---|
| Chưa chạy | Nhập & cấu hình | Một nút Bắt đầu dịch qua kiểm tra đầu vào hiện có |
| Đang tải lên/tải xuống | Tiến độ | Hiện tiến độ truyền thực tế; không cho bấm bắt đầu lần nữa |
| Nhận dạng/dịch/tạo giọng/render | Tiến độ | Tạm dừng/Hủy chỉ khi luồng hiện có hỗ trợ; giữ trạng thái đang yêu cầu |
| Tạm dừng | Tiến độ | Tiếp tục và Hủy theo khả năng hiện có |
| segment_editing/needs_review | Duyệt bản dịch & giọng | Giữ kiểm tra giọng, chỉnh câu và các bước xác nhận hiện có |
| copyright_hold | Thông báo cần xử lý | Giữ nguyên luồng quyết định hiện có; không tự bỏ qua |
| failed/interrupted | Thông báo lỗi trong Tiến độ | Thử lại/Tiếp tục chỉ nếu có hành động hợp lệ; không khởi chạy mới ngầm |
| cancelled | Tiến độ với trạng thái Đã hủy | Không tự chạy lại; dùng hành động hợp lệ hiện có |
| completed và có kết quả | Kết quả | Xem và tải video; Đăng YouTube ở mục tùy chọn |
| completed nhưng thiếu kết quả | Thông báo chưa có file kết quả | Không hiện player/link tải hỏng hoặc tự gọi render |
| Đang lấy trạng thái/không nhận diện được | Thông báo đang xác định trạng thái | Không suy đoán hoàn tất hoặc cho khởi chạy trùng |

Bản triển khai phải đối chiếu cả trạng thái workflow và job với các điều kiện hiện có.
Không quyết định trạng thái chỉ dựa trên việc đã có vài segment. Lỗi lấy trạng thái
không đồng nghĩa tác vụ thất bại; giữ thông tin gần nhất và báo mất kết nối riêng.
Không hiển thị hai nút Start/Bắt đầu dịch cho cùng tác vụ.

## Quy tắc tự mở và giữ dữ liệu

- Khi đổi dự án/tác vụ: mở phần phù hợp với trạng thái đã tải về, giữ cảnh báo rời form chưa lưu.
- Khi chuyển sang một pha mới: mở phần liên quan; không mở lại mỗi lần polling/SSE cập nhật.
- Người dùng có thể chủ động mở phần khác để xem. Lựa chọn đóng/mở được giữ trong cùng pha.
- Không tự cuộn trang hoặc giành focus khi người dùng đang gõ. Báo Cần duyệt/Kết quả đã sẵn sàng tại thanh trạng thái.
- Thu gọn bằng cơ chế giữ component/form và giá trị đang nhập; không unmount làm mất bản sửa hoặc khởi tạo lại tác vụ.
- Khi chuyển pha, không ép đóng phần có sửa chưa lưu. Mọi hạn chế sửa trong lúc chạy giữ nguyên.
- Chuyển dự án không đem dữ liệu chưa lưu của dự án cũ sang dự án mới.
- Không hứa giữ bản nháp chưa lưu qua F5 trong phạm vi này; giữ cảnh báo rời/refresh hiện có.

## Nhập và cấu hình

Hiện ngay chọn file/dán link, ngôn ngữ đích và cấu hình giọng cơ bản hiện có.
Gom cấu hình còn lại vào mục thu gọn: AI & dịch thuật; Thuật ngữ; Giọng & xử lý âm thanh;
Hình ảnh đầu ra (phụ đề, watermark); Tùy chọn tự động (thumbnail, xác nhận tự động, kiểm tra/cắt nội dung).
Trước triển khai phải lập bảng ánh xạ toàn bộ control hiện có để không làm mất chức năng.
Giữ giá trị mặc định, validation và dữ liệu lưu của từng control. Mục đóng có tóm tắt
các tùy chọn đang bật. Nếu validation lỗi trong mục đóng, mở đúng mục và dẫn focus đến trường lỗi.

## Duyệt và kết quả

Giữ editor câu thoại/nhân vật/giọng và điều kiện xác nhận hiện có. Không gộp mất hai
cổng duyệt bản dịch và giọng; nhãn nút phản ánh thao tác thực tế còn phải làm.
Khi hoàn tất, ưu tiên player và tải video, thu gọn bảng câu thoại. Giữ AIQCScorecard,
VideoEditorStudio và đăng YouTube trong các mục có nhãn rõ, có thể mở lại.
Không tự bật âm thanh/phát video hoặc tự mở hộp thoại đăng video.

## Tiến độ và hỗ trợ

Hiện tên bước bằng tiếng Việt, số liệu thực có sẵn. Không suy diễn ETA hoặc làm mượt
phần trăm thành số giả. Nếu không có phần trăm đáng tin, chỉ hiển thị đang xử lý.
Heartbeat, FFmpeg Process, stage/job ID, DB telemetry và Log chuyển vào Hỗ trợ → Chi tiết kỹ thuật.
Không thêm thu thập/chia sẻ log. Thông báo lỗi chính dễ hiểu; thông tin chẩn đoán vẫn truy cập được.
Các nút đang gửi yêu cầu bị khóa để tránh gửi lặp; hành động Hủy tác vụ khác Hủy thay đổi form.

## Khả năng sử dụng

Ở chiều rộng 800 px và 1280 px: không tràn ngang toàn trang, nút chính dễ tìm;
bảng câu thoại được phép cuộn trong vùng riêng. Accordion dùng button, aria-expanded,
liên kết panel và bàn phím; trạng thái không chỉ phân biệt bằng màu.

## Phạm vi mã và kiểm chứng

Nguồn chính: frontend/src/pages/VideoTranslator.jsx, frontend/src/components/WorkflowTimeline.jsx,
CSS liên quan được xác định khi lập kế hoạch. Chỉ tách component/helper khi cần cho thay đổi này.
Giữ API/event handlers hiện có; kiểm tra các nơi dùng WorkflowTimeline trước khi đổi props.

Tiêu chí nghiệm thu:
- Chưa chạy chỉ có một hành động bắt đầu; cấu hình nâng cao và chẩn đoán đóng mặc định.
- Mỗi trạng thái trong bảng có nội dung/hành động phù hợp; completed không phụ thuộc đăng video.
- Polling không giật focus, không xóa bản sửa câu hoặc lựa chọn đóng/mở; đổi dự án không lẫn dữ liệu.
- Các cổng duyệt, cảnh báo chưa lưu, copyright hold, mất kết nối, lỗi và hủy vẫn hoạt động.
- Tất cả control cũ được ánh xạ; lỗi validation không bị che trong mục đóng.
- Test tương tác React cho luồng nhập → xử lý → duyệt → kết quả và các trạng thái ngoại lệ;
  chạy suite frontend hiện có và production build, xem giao diện ở hai kích thước đã nêu.
- Việc nghiệm thu bản Windows đóng gói tiếp tục theo #3/#4; build web không chứng minh nghiệm thu native.

## Sau duyệt

Viết kế hoạch triển khai #7 theo spec này, rồi mới sửa mã. Bản spec không tự cấp phép
push main, phát hành Release hoặc thay đổi các chức năng ngoài phạm vi thiết kế Studio.

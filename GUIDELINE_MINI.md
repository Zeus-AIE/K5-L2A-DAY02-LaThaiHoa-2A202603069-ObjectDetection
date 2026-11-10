# Bản quy tắc gán nhãn cá nhân (Mini guideline)

## Định nghĩa các lớp xe

| Lớp xe | Định nghĩa | Dấu hiệu nhận biết và phân biệt |
| --- | --- | --- |
| `car` | Các loại xe ô tô con thông thường dùng cho cá nhân hoặc gia đình, bao gồm xe sedan 4 chỗ, xe đuôi cụt (hatchback), xe gầm cao 5–7 chỗ (SUV, CUV), xe taxi và xe bán tải gia đình. | Thân xe liền khối, chiều cao vừa phải. Xe bán tải cabin kép có thùng nhỏ phía sau vẫn tính là xe con vì mục đích sử dụng gia đình. |
| `truck` | Các loại xe tải chuyên dụng dùng để chở hàng hóa nặng, xe ben, xe bồn chở chất lỏng, xe đầu kéo kéo theo rơ-moóc hoặc container. | Có phần thùng chở hàng hoặc sàn cơ giới gắn tách rời rõ ràng với cabin lái; kích thước xe to và gầm cao hơn xe con. |
| `bus` | Xe buýt phục vụ giao thông công cộng trong thành phố, xe khách liên tỉnh đường dài, xe buýt nhỏ đưa đón theo tuyến. | Thân xe dài, có nhiều hàng ghế chở đông người và dãy cửa sổ kính chạy dài liên tục dọc hai bên sườn xe. |
| `van` | Xe tải nhỏ chở hàng thân kín, xe minivan, xe chở khách loại nhỏ (từ 7 đến 16 chỗ ngồi). | Thân xe dạng khối hộp kín liền mạch từ đầu đến đuôi; không có thùng hàng rời như xe tải và không quá dài nhiều ô cửa sổ như xe buýt. |

## Quy tắc vẽ khung bao chung

- Khung bao ôm sát vật thể: Khung hình chữ nhật phải vẽ ôm khít toàn bộ phần vỏ ngoài nhìn thấy được của xe (tính cả bánh xe chạm mặt đường và gương chiếu hậu nếu thấy rõ). Tuyệt đối không lấy lấn sang mặt đường, khoảng trống trên trời hay phần thân của xe đi bên cạnh.
- Xe bị che khuất một phần: Chỉ vẽ khung bao quanh đúng phần thân xe thực tế nhìn thấy bằng mắt. Không tự ý suy đoán hoặc vẽ bao trùm qua những chỗ bị xe khác, cột đèn hay dải phân cách che khuất.
- Xe bị cắt bởi mép khung hình: Vẽ khung ôm sát phần thân xe nằm trong ảnh và kéo mép khung chạm đúng mép biên của bức ảnh (chạm tọa độ 0 hoặc 1). Không ước lượng hay vẽ phần xe bị tràn ra ngoài khung ảnh.
- Xe ở quá xa hoặc quá mờ: Nếu xe chỉ còn là một chấm nhỏ hoặc một góc rất mờ không thể nhận diện chắc chắn loại xe thì không tự đoán để gán nhãn, tránh gây nhiễu cho mô hình.

## Quyết định cho ba trường hợp khó quan sát trong tập ảnh

| Ảnh | Tình huống thực tế | Quyết định xử lý | Lý do căn cứ theo hướng dẫn |
| --- | --- | --- | --- |
| `drive_008.jpg` | Ở sát mép bên trái ảnh có một chiếc xe to màu vàng bị cắt ngang thân bởi rìa ảnh và bị xe khác che một phần. | Gán nhãn `bus` (lớp 2) | Nhận diện rõ dãy cửa sổ kính dài đặc trưng của phương tiện chở khách công cộng; khung bao được kéo chạm mép trái ảnh theo đúng quy tắc vật thể bị cắt biên. |
| `drive_021.jpg` | Một chiếc xe bán tải màu bạc đang chạy ở làn giữa, phía sau có thùng chở đồ nhưng kích cỡ tương đương xe con. | Gán nhãn `car` (lớp 0) | Theo bảng phân loại của bài học, xe bán tải đi lại cá nhân được xếp vào nhóm xe con, chỉ những xe tải chở hàng có cabin tách rời với thùng lớn mới tính là xe tải. |
| `drive_038.jpg` | Ở ngã tư phía xa có một chiếc xe bị xe đi trước che khuất hơn 70%, chỉ nhìn thấy lấp ló một góc nhỏ của nóc xe. | Không gán nhãn | Diện tích nhìn thấy còn lại quá ít, không đủ đặc trưng rõ ràng để khẳng định chắc chắn là xe con, xe van hay xe tải, nếu cố đoán sẽ dễ gây sai lệch nhãn. |

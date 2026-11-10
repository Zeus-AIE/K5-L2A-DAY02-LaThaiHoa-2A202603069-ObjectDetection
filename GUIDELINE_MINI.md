# Mini guideline — bài làm cá nhân

## Định nghĩa lớp

| Lớp | Định nghĩa của bạn | Ví dụ/điểm phân biệt |
| --- | --- | --- |
| `car` | Xe con thông thường từ 4 đến 7 chỗ phục vụ đi lại cá nhân gồm sedan, hatchback, SUV, crossover, xe taxi và xe bán tải gia đình. | Thân xe liền khối, gầm thấp hoặc bán tải cabin đôi không có thùng chở hàng tải trọng lớn tách rời. |
| `truck` | Xe tải chở hàng hóa, xe ben, xe bồn, xe đầu kéo kéo rơ-moóc hoặc chở container. | Có thùng chở hàng, ben hoặc sàn cơ giới gắn tách rời rõ rệt với cabin lái. |
| `bus` | Xe buýt công cộng, xe khách liên tỉnh cỡ lớn, xe khách du lịch. | Thân xe dài, chở nhiều người, có các ô cửa sổ kính lớn liên tiếp chạy dọc hai bên thân xe. |
| `van` | Xe van, minivan dạng khối hộp cỡ trung dùng chở người hoặc chở hàng hóa (như Ford Transit, Hyundai Solati, minivan gia đình). | Thân xe dạng khối hộp kín liền mạch một khoang giữa cabin và khoang sau; không dài nhiều cửa sổ như xe buýt và không tách thùng rời như xe tải. |

## Quy tắc chung

- Box bám sát vật thể nghĩa là: Khung bao phải vẽ ôm sát toàn bộ phần vỏ xe nhìn thấy được (tính cả bánh xe tiếp đất và gương chiếu hậu nếu thấy rõ). Không lấy thêm khoảng trống mặt đường, trời, bóng đổ dưới gầm hoặc lấn sang xe bên cạnh.
- Vật thể bị che khuất: Chỉ vẽ khung bao quanh phần thực tế nhìn thấy được của xe. Tuyệt đối không suy đoán phần bị che khuất bởi xe khác, cột đèn hay dải phân cách.
- Vật thể bị cắt bởi rìa ảnh: Khung bao ôm sát phần nhìn thấy và kéo mép khung chạm đúng rìa viền ảnh. Không ước lượng phần xe nằm bên ngoài khung hình.
- Vật thể rất nhỏ/mơ hồ: Xe ở quá xa, hình ảnh mờ hoặc chỉ thấy một góc nhỏ không đủ dấu hiệu tin cậy để xác định chính xác thuộc lớp nào thì không tự đoán và không gán nhãn, tránh gây nhiễu cho dữ liệu.

## Ghi lại quyết định cho ít nhất ba ca mơ hồ

| Ảnh | Tình huống | Quyết định cuối | Lý do theo schema |
| --- | --- | --- | --- |
| `drive_008.jpg` | Ở rìa trái ảnh có một xe lớn màu vàng bị cắt ngang thân bởi mép ảnh và bị xe khác che một phần. | Gán nhãn `bus` (Lớp 2) | Quan sát thấy các ô cửa sổ kính lớn đặc trưng của xe khách chở người; khung bao kéo chạm sát mép trái ảnh theo đúng quy tắc vật thể bị cắt rìa. |
| `drive_021.jpg` | Xe bán tải đang chạy ở làn giữa, phía sau có thùng hàng nhưng kích thước tương đương xe con. | Gán nhãn `car` (Lớp 0) | Theo quy định schema của bài lab, xe bán tải cabin nhỏ phục vụ cá nhân thuộc lớp `car`, không tính là `truck`. |
| `drive_038.jpg` | Xe ở vị trí ngã tư phía xa bị che khuất phần lớn thân bởi các xe chạy phía trước, chỉ nhô ra một góc nhỏ ở nóc xe. | Không gán nhãn | Phần nhìn thấy còn lại quá bé, không đủ đặc trưng tin cậy để phân biệt chắc chắn giữa `car`, `van` hay `truck`. |

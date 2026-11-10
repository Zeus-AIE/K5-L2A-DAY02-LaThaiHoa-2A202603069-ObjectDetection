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
| `drive_002.jpg` | Ở sát mép phải ảnh có một xe minivan màu bạc đang chạy ở làn ngoài cùng, bị mép phải ảnh cắt dọc khoảng 30% thân xe bên phải (tọa độ khung 574, 310 đến 639, 433). Dáng xe dạng khối hộp cao một khoang, đuôi dốc đứng, dễ phân vân giữa xe 7 chỗ và xe van. | Gán nhãn `van` (Lớp 3) | Tôi nhận diện được kiểu dáng một khoang liền khối không có cốp sau tách rời và trần xe cao đặc trưng của dòng minivan. Khung bao vẽ ôm sát phần thân nhìn thấy và kéo mép phải chạm đúng viền ảnh x = 639 theo quy tắc vật thể bị cắt rìa. |
| `drive_049.jpg` | Ở mép trên cùng của ảnh có một xe dài đang di chuyển ở làn xa phía trên, bị mép trên ảnh cắt ngang một phần nóc xe (tọa độ khung 330, 0 đến 355, 49). Nhìn từ góc camera trên cao xuống ngã tư, xe dễ bị lẫn giữa xe tải thùng phẳng và xe khách. | Gán nhãn `bus` (Lớp 2) | Tôi quan sát thấy trên nóc xe có chi tiết dàn điều hòa và hình khối thuôn dài phẳng liên tục, không có khoảng cách chia đôi giữa cabin và thùng hàng như xe tải. Tôi đã chỉnh sửa nhãn này từ xe tải sang xe buýt ở lần cập nhật dữ liệu mới nhất. Khung bao kéo sát mép trên y = 0 theo đúng quy tắc vật thể bị cắt rìa. |
| `drive_038.jpg` | Ở rìa mép trái ảnh có một xe chở khách cỡ lớn đang qua ngã tư, bị viền ảnh cắt dọc thân xe chỉ còn thấy khoảng 1/3 bề ngang thân bên phải (tọa độ khung 0, 95 đến 44, 190), đầu và đuôi xe bị khuất góc. | Gán nhãn `bus` (Lớp 2) | Dù bị mép ảnh che mất hơn nửa thân xe, phần còn lại vẫn lộ rất rõ các ô cửa sổ kính lớn liên tiếp chạy dọc hông xe khách và chiều dài trục bánh xe vượt trội so với xe con hay xe van. Tôi kéo mép khung ép sát viền trái x = 0 theo đúng quy tắc xử lý vật thể bị cắt mép. |

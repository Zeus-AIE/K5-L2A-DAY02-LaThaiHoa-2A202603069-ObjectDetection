# Mini guideline — bài làm cá nhân

> Điền nội dung này trước khi bắt đầu gán nhãn. Giữ lại các quyết định sau khi self-QC.

## Định nghĩa lớp

| Lớp | Định nghĩa của bạn | Ví dụ/điểm phân biệt |
| --- | --- | --- |
| `car` | Xe con cá nhân thông thường gồm sedan, hatchback, SUV, crossover, xe taxi, và xe bán tải (pickup) phục vụ gia đình/cá nhân. | Thân xe liền khối, gầm thấp hoặc bán tải cabin đôi không có thùng hàng trọng tải lớn chuyên dụng tách rời. |
| `truck` | Xe tải chở hàng, xe ben, xe bồn, xe đầu kéo kéo rơ-moóc hoặc chở container. | Có thùng/ben chở hàng hoặc sàn cơ giới gắn tách rời rõ rệt với cabin điều khiển của lái xe. |
| `bus` | Xe buýt công cộng, xe khách liên tỉnh, minibus chở khách theo tuyến. | Xe thân dài, có nhiều hàng ghế và nhiều ô cửa sổ kính liên tiếp chạy dọc hai bên thân xe. |
| `van` | Xe van, minivan thân hộp kín một khối (monovolume) dùng chở người hoặc hàng hóa nhẹ. | Thân xe dạng khối hộp kín liền mạch giữa cabin và khoang sau; không dài nhiều cửa sổ như bus và không tách thùng rời như truck. |

## Quy tắc chung

- Box bám sát vật thể nghĩa là: Bounding box phải ôm khít các mép ngoài cùng của phần thân xe nhìn thấy được (kể cả bánh xe tiếp đất và gương chiếu hậu nếu thấy rõ). Không bao gồm khoảng trống, bóng xe dưới lòng đường hay phần đường xung quanh.
- Vật thể bị che khuất: Chỉ vẽ box bao quanh **phần thực tế nhìn thấy được** của xe. Tuyệt đối không suy đoán hoặc vẽ bao luôn cả phần bị che khuất bởi xe khác, cột đèn, dải phân cách.
- Vật thể bị cắt bởi rìa ảnh: Vẽ box ôm sát phần nhìn thấy và kéo mép box chạm sát biên ảnh (tọa độ chạm 0 hoặc 1). Không ước lượng phần xe bị tràn ra ngoài khung ảnh.
- Vật thể rất nhỏ/mơ hồ: Xe ở quá xa, bị mờ hoặc chỉ nhìn thấy một góc rất nhỏ không đủ bằng chứng tin cậy để xác định chính xác thuộc lớp nào thì **không gán** để tránh sinh ra false positive cho mô hình.

## Ghi lại quyết định cho ít nhất ba ca mơ hồ

| Ảnh | Tình huống | Quyết định cuối | Lý do theo schema |
| --- | --- | --- | --- |
| `drive_008.jpg` | Ở rìa trái ảnh có một xe lớn màu vàng bị cắt mép ảnh và bị che một phần thân. | Gán nhãn `bus` (Class 2) | Quan sát thấy các ô kính đặc trưng của phương tiện vận tải hành khách công cộng; box kéo sát mép trái của ảnh đúng theo quy tắc cắt biên (truncated). |
| `drive_021.jpg` | Xe bán tải (pickup) đang lưu thông ở làn giữa, có thùng hàng phía sau nhưng kích thước xe con. | Gán nhãn `car` (Class 0) | Theo quy ước schema, xe bán tải phục vụ đi lại cá nhân thuộc nhóm `car`, chỉ xe tải chở hàng có thùng/ben tách rời chuyên dụng mới gán `truck`. |
| `drive_038.jpg` | Có xe ở vị trí ngã tư phía xa bị che khuất hơn 70% bởi xe phía trước. | Không gán nhãn | Phần nhìn thấy còn lại quá nhỏ (chỉ thấy một góc nóc xe), không đủ đặc trưng tin cậy để phân biệt rõ giữa `car`, `van` hay `truck`. |

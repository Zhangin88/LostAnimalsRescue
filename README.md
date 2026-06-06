# Lost Animals Rescue

Lost Animals Rescue là trò chơi mê cung giải cứu động vật, sử dụng các thuật toán AI gồm **BFS, DFS, A\*** và **Minimax**.

## 1. Giới thiệu

Dự án mô phỏng trực quan các thuật toán tìm kiếm đường đi trong trí tuệ nhân tạo thông qua trò chơi mê cung. Người chơi chọn thuật toán, quan sát quá trình duyệt ô, đường đi cuối cùng và hành vi truy đuổi của kẻ địch.

## 2. Chức năng chính

- Đăng ký / đăng nhập tài khoản.
- Lưu tài khoản và tiến trình người chơi bằng database.
- Chọn màn chơi theo tiến trình mở khóa.
- 5 màn chơi với độ khó tăng dần:
  - Level 1: Nông trại - 10x10
  - Level 2: Khu rừng - 15x15
  - Level 3: Đầm lầy - 15x15
  - Level 4: Đại dương - 20x20
  - Level 5: Bầu trời - 20x20
- Chọn thuật toán rồi bấm **Bắt đầu giải cứu** để chạy.
- Hiển thị quá trình duyệt ô và đường đi cuối cùng.
- Kẻ địch sử dụng Minimax để truy đuổi.
- Có đồ họa, hiệu ứng, âm thanh và nhạc nền.

## 3. Thuật toán sử dụng

### BFS

BFS duyệt theo chiều rộng, phù hợp để tìm đường đi ngắn nhất trong mê cung khi các bước đi có cùng chi phí.

### DFS

DFS duyệt theo chiều sâu, có thể tìm được đường đi nhưng không đảm bảo đường đi ngắn nhất.

### A\*

A\* sử dụng hàm đánh giá kết hợp giữa chi phí đã đi và khoảng cách ước lượng đến đích, giúp tìm đường hiệu quả hơn trong nhiều trường hợp.

### Minimax

Minimax được sử dụng cho kẻ địch để mô phỏng hành vi truy đuổi nhân vật trong mê cung.

## 4. Cấu trúc thư mục

```text
LostAnimalsRescue/
│
├── main.py
├── settings.py
├── database.py
├── maps.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── algorithms/
│   ├── bfs.py
│   ├── dfs.py
│   ├── astar.py
│   └── minimax.py
│
├── screens/
│   ├── game_screen.py
│   ├── main_menu.py
│   ├── login_screen.py
│   ├── register_screen.py
│   └── level_select_screen.py
│
├── assets/
│   └── sounds/
│       └── background.mp3
│
└── database/
    └── game.db
```

Lưu ý: tên file trong project có thể khác một chút tùy cách tổ chức. Chỉ cần các đường dẫn trong code được khai báo đúng.

## 5. Cài đặt

Khuyến nghị sử dụng Python 3.12.

Kiểm tra phiên bản Python:

```bash
python --version
```

Hoặc trên Windows:

```bash
py --version
```

Cài đặt thư viện cần thiết:

```bash
pip install -r requirements.txt
```

Nếu lệnh trên không chạy, sử dụng:

```bash
py -m pip install -r requirements.txt
```

## 6. Chạy chương trình

Mở terminal tại thư mục project:

```bash
cd LostAnimalsRescue
```

Chạy game:

```bash
python main.py
```

Hoặc trên Windows:

```bash
py main.py
```

Nếu sử dụng Python 3.12:

```bash
py -3.12 main.py
```

## 7. Âm thanh và nhạc nền

File nhạc nền được đặt trong thư mục:

```text
assets/sounds/
```

Ví dụ:

```text
assets/sounds/background.mp3
```

Trong code nên sử dụng đường dẫn tương đối:

```python
path = "assets/sounds/background.mp3"
```

Không nên sử dụng đường dẫn tuyệt đối như:

```python
path = "D:/AI/DOAN/LostAnimalsRescue/assets/sounds/background.mp3"
```

Điều này giúp chương trình có thể chạy trên nhiều máy khác nhau mà không bị lỗi đường dẫn.

## 8. Database

Dự án sử dụng database để lưu tài khoản và tiến trình người chơi.

Ví dụ database có thể nằm tại:

```text
database/game.db
```

Hoặc nằm trực tiếp trong thư mục gốc:

```text
game.db
```

Trong `database.py`, nên sử dụng đường dẫn tương đối, ví dụ:

```python
DB_PATH = "database/game.db"
```

hoặc:

```python
DB_PATH = "game.db"
```

Không nên sử dụng đường dẫn tuyệt đối như:

```python
DB_PATH = "D:/AI/DOAN/LostAnimalsRescue/database/game.db"
```

## 9. Tải dự án từ GitHub

Có thể tải dự án bằng Git:

```bash
git clone https://github.com/Zhangin88/LostAnimalsRescue.git
cd LostAnimalsRescue
pip install -r requirements.txt
python main.py
```

Trên Windows có thể sử dụng:

```bash
git clone https://github.com/Zhangin88/LostAnimalsRescue.git
cd LostAnimalsRescue
py -m pip install -r requirements.txt
py main.py
```

Hoặc tải file ZIP trực tiếp trên GitHub:

```text
Code → Download ZIP
```

Sau khi giải nén, mở terminal trong thư mục project và chạy:

```bash
pip install -r requirements.txt
python main.py
```

## 10. Cập nhật project lên GitHub

Sau khi chỉnh sửa code, sử dụng các lệnh sau để cập nhật lên GitHub:

```bash
git add .
git commit -m "Update project"
git push
```

Kiểm tra trạng thái project:

```bash
git status
```

Nếu hiển thị:

```text
nothing to commit, working tree clean
```

nghĩa là project hiện tại đã được lưu trong Git.

## 11. Lưu ý khi public repository

- Có thể upload file nhạc MP3 nếu file không vi phạm bản quyền.
- Có thể upload database mẫu nếu cần chạy chương trình ngay sau khi tải.
- Không nên upload tài khoản hoặc mật khẩu thật quan trọng.
- Không nên upload file video gốc `.mp4` vì thường có dung lượng lớn.
- Không upload thư mục `venv`, `.venv`, `__pycache__`.

## 12. Lỗi thường gặp

### Lỗi thiếu pygame

```text
ModuleNotFoundError: No module named 'pygame'
```

Cách sửa:

```bash
pip install pygame
```

Hoặc:

```bash
py -m pip install pygame
```

### Lỗi không phát nhạc

Kiểm tra file nhạc có tồn tại không:

```text
assets/sounds/background.mp3
```

Kiểm tra đường dẫn trong code:

```python
path = "assets/sounds/background.mp3"
```

### Lỗi không tìm thấy database

Kiểm tra file database có tồn tại không:

```bash
dir
dir database
```

Nếu chương trình báo lỗi không tìm thấy database, kiểm tra lại đường dẫn trong `database.py`.

### Lỗi chạy sai thư mục

Cần chạy chương trình từ thư mục gốc của project:

```bash
cd LostAnimalsRescue
python main.py
```

Không nên chạy trực tiếp từ thư mục `screens`.

## 13. Thành viên thực hiện

- Châu Hữu Nghị - 24110036
- Trần Hữu Lộc - 24110275
- Trịnh Văn Phú Hào - 24110013

## 14. Mục tiêu đồ án

Mục tiêu của đồ án là xây dựng trò chơi mê cung có áp dụng các thuật toán trí tuệ nhân tạo, giúp trực quan hóa quá trình tìm kiếm đường đi và so sánh hoạt động của BFS, DFS, A\* và Minimax trong môi trường trò chơi.

# Lost Animals Rescue

Lost Animals Rescue là trò chơi mê cung giải cứu động vật, sử dụng các thuật toán AI gồm **BFS, DFS, A\*** và **Minimax**.

## 1. Chức năng chính

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
- Kẻ địch dùng Minimax để truy đuổi.
- Có đồ họa, hiệu ứng, âm thanh và nhạc nền.

## 2. Cấu trúc thư mục

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

Lưu ý: tên file database của bạn có thể là `game.db`, `users.db`, `database.db` hoặc tên khác. Chỉ cần code trong `database.py` đang trỏ đúng đến file đó.

## 3. Cài đặt

Yêu cầu Python 3.10 trở lên. Khuyến nghị Python 3.12.

Kiểm tra Python:

```bash
python --version
```

Hoặc trên Windows:

```bash
py --version
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

Nếu lỗi, dùng:

```bash
py -m pip install -r requirements.txt
```

## 4. Chạy game

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

Nếu dùng Python 3.12:

```bash
py -3.12 main.py
```

## 5. Âm thanh / nhạc nền

File nhạc nền nằm trong:

```text
assets/sounds/background.mp3
```

Trong code nên dùng đường dẫn tương đối:

```python
path = "assets/sounds/background.mp3"
```

Không dùng đường dẫn tuyệt đối như:

```python
path = "D:/AI/DOAN/LostAnimalsRescue/assets/sounds/background.mp3"
```

vì bạn bè tải project về máy khác sẽ bị lỗi.

## 6. Database

Project có thể upload database mẫu để bạn bè tải về chạy được ngay.

Ví dụ database nằm ở:

```text
database/game.db
```

Hoặc nằm trực tiếp ở thư mục gốc:

```text
game.db
```

Nếu upload database, cần kiểm tra:

- Database không chứa mật khẩu thật quan trọng.
- Nếu có tài khoản demo, nên dùng tài khoản đơn giản như:
  - username: `demo`
  - password: `123`
- Code trong `database.py` phải dùng đường dẫn tương đối.

Ví dụ đường dẫn nên dùng:

```python
DB_PATH = "database/game.db"
```

hoặc:

```python
DB_PATH = "game.db"
```

Không nên dùng:

```python
DB_PATH = "D:/AI/DOAN/LostAnimalsRescue/database/game.db"
```


## 7. Bạn trong nhóm tải về

### Cách 1: Clone bằng Git

```bash
git clone https://github.com/TEN_GITHUB_CUA_BAN/LostAnimalsRescue.git
cd LostAnimalsRescue
pip install -r requirements.txt
python main.py
```

Trên Windows có thể dùng:

```bash
git clone https://github.com/TEN_GITHUB_CUA_BAN/LostAnimalsRescue.git
cd LostAnimalsRescue
py -m pip install -r requirements.txt
py main.py
```

### Cách 2: Download ZIP

Trên GitHub:

```text
Code → Download ZIP
```

Sau đó giải nén, mở terminal trong thư mục project và chạy:

```bash
pip install -r requirements.txt
python main.py
```

## 8. Cập nhật code sau khi sửa

Mỗi lần sửa xong:

```bash
git add .
git commit -m "Update game"
git push
```

Bạn trong nhóm cập nhật code mới bằng:

```bash
git pull
```

## 10. Lưu ý khi public repository

- MP3 không bản quyền thì có thể upload.
- Có thể upload database mẫu nếu muốn bạn bè tải về chạy ngay.
- Không nên upload tài khoản/mật khẩu thật quan trọng.
- Không upload file video gốc `.mp4` vì thường nặng.
- Không upload thư mục `venv`, `__pycache__`.

## 10. Lỗi thường gặp

### Lỗi thiếu pygame

```text
ModuleNotFoundError: No module named 'pygame'
```

Sửa bằng:

```bash
pip install pygame
```

### Lỗi không phát nhạc

Kiểm tra file có tồn tại không:

```text
assets/sounds/background.mp3
```

Kiểm tra đường dẫn trong code:

```python
path = "assets/sounds/background.mp3"
```

### Lỗi không thấy database sau khi tải về

Kiểm tra database có được upload chưa:

```bash
dir
dir database
```

Nếu code báo không tìm thấy database, kiểm tra đường dẫn trong `database.py`.

### Lỗi chạy sai thư mục

Cần chạy từ thư mục gốc:

```bash
cd LostAnimalsRescue
python main.py
```

Không chạy trực tiếp từ thư mục `screens`.

## 11. Thành viên

- Châu Hữu Nghị - 24110036
- Trần Hữu Lộc -  24110275
- Trịnh Văn Phú Hào - 24110013
## 12. Mục tiêu đồ án

Mục tiêu của đồ án là mô phỏng trực quan các thuật toán tìm kiếm đường đi trong trí tuệ nhân tạo thông qua trò chơi mê cung. Người chơi có thể so sánh BFS, DFS, A* và quan sát Minimax trong hành vi truy đuổi của kẻ địch.

# WalletBot - Hướng dẫn cài đặt và chạy dự án

## Giới thiệu

WalletBot là hệ thống chatbot AI kết hợp với backend để hỗ trợ giao dịch ví điện tử. Dự án bao gồm ba phần:

- **BE-WalletBot**: Backend xử lý xác thực và giao dịch.
- **AI-WalletBot**: Mô hình AI hỗ trợ người dùng tương tác thông qua chatbot.
- **AIChatBot\_Frontend**: Giao diện web để người dùng tương tác với chatbot.

## 1. Chuẩn bị môi trường

### 1.1. Clone dự án

```sh
# Clone backend
git clone https://github.com/dung1311/BE-WalletBot.git

# Clone AI chatbot
git clone https://github.com/dung1311/AI-WalletBot.git

# Clone frontend
git clone https://github.com/HoangAnhEm/AIChatBot_Frontend.git
```

### 1.2. Cài đặt các công cụ cần thiết

#### Cài đặt Ollama

Tải và cài đặt Ollama: [Tải tại đây](https://ollama.com/)

Sau khi cài đặt, tải một mô hình AI có hỗ trợ Function Calling. Dự án này sử dụng `qwen2.5:7b`:

```sh
ollama pull qwen2.5:7b
```

#### Cài đặt Miniconda và Python 3.12

Tải Miniconda và cài đặt môi trường Python 3.12: [Hướng dẫn cài đặt](https://www.anaconda.com/docs/getting-started/anaconda/install)

```sh
conda create -n walletbot python=3.12 -y
conda activate walletbot
```

#### Cài đặt thư viện cần thiết

Di chuyển vào thư mục dự án và cài đặt các thư viện từ `requirements.txt`:

```sh
pip install -r requirements.txt
```

## 2. Cấu hình môi trường

Tạo file `.env` trong thư mục dự án với nội dung sau:

```env
PORT=8080
HOST=0.0.0.0
JWT_SECRET_ACCESS=conboanco  # Cần trùng với backend

OLLAMA_HOST=http://localhost:11434
NODE_URL=http://localhost:3000
```

## 3. Chạy dự án

Khởi chạy server bằng lệnh:

```sh
python server.py
```

## 4. Chạy giao diện web

Nếu muốn sử dụng giao diện web để tương tác với chatbot, hãy clone và chạy frontend:

```sh
git clone https://github.com/HoangAnhEm/AIChatBot_Frontend.git
```

## 5. Liên hệ & Đóng góp

Nếu bạn gặp bất kỳ vấn đề nào hoặc muốn đóng góp cho dự án, hãy mở issue trên GitHub hoặc liên hệ trực tiếp với chúng tôi!

Email: tiendung13112004\@gmail.com


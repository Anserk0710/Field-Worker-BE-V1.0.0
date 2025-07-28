# 🤖 Trading Bot - MetaTrader 5 & Telegram

Bot trading otomatis yang terintegrasi dengan MetaTrader 5 dan Telegram untuk analisis teknikal real-time dan monitoring trading.

## ✨ Fitur Utama

- 🔌 **Koneksi MT5**: Integrasi langsung dengan MetaTrader 5
- 📱 **Bot Telegram**: Interface user-friendly melalui Telegram
- 📊 **Analisis Real-time**: Analisis teknikal otomatis
- 💰 **Monitoring Akun**: Informasi balance dan equity real-time
- 🔍 **Status Monitoring**: Health check sistem otomatis
- 📝 **Logging**: Sistem logging lengkap dengan rotasi file

## 🚀 Quick Start

### 1. Persiapan Environment

```bash
# Clone atau download project
git clone <repository-url>
cd trading-bot

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi MetaTrader 5

1. **Install MetaTrader 5**
   - Download dari [MetaQuotes](https://www.metatrader5.com/)
   - Install dan login ke akun trading Anda

2. **Enable Algorithmic Trading**
   - Buka MT5 → Tools → Options → Expert Advisors
   - Centang "Allow algorithmic trading"
   - Centang "Allow DLL imports"

### 3. Setup Bot Telegram

1. **Buat Bot Telegram**
   ```
   1. Chat dengan @BotFather di Telegram
   2. Ketik /newbot
   3. Ikuti instruksi untuk membuat bot
   4. Simpan TOKEN yang diberikan
   ```

2. **Dapatkan Chat ID**
   ```
   1. Chat dengan bot Anda
   2. Kirim pesan apa saja
   3. Buka: https://api.telegram.org/bot<TOKEN>/getUpdates
   4. Cari "chat":{"id": XXXXXX}
   5. Simpan Chat ID tersebut
   ```

### 4. Konfigurasi Environment

1. **Copy file konfigurasi**
   ```bash
   cp .env.example .env
   ```

2. **Edit file .env**
   ```env
   # MetaTrader 5 Configuration
   MT5_LOGIN=12345678
   MT5_PASSWORD=your_password
   MT5_SERVER=YourBroker-Demo
   MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
   
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=987654321
   
   # Trading Configuration
   RISK_PERCENTAGE=2.0
   MAX_OPEN_POSITIONS=5
   SYMBOL_LIST=EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD
   ```

### 5. Test Koneksi

```bash
# Test koneksi MT5
python test_mt5_connection.py

# Jika berhasil, jalankan bot
python run_bot.py
```

## 📋 Struktur Proyek

```
trading_bot/
├── config/
│   ├── __init__.py
│   └── settings.py          # Konfigurasi aplikasi
├── mt5/
│   ├── __init__.py
│   └── connection.py        # Koneksi MetaTrader 5
├── telegram/
│   ├── __init__.py
│   └── bot.py              # Bot Telegram
├── strategies/
│   └── __init__.py         # Strategi trading (future)
├── utils/
│   ├── __init__.py
│   └── logger.py           # Sistem logging
├── logs/                   # File log
├── data/                   # Data trading
└── main.py                 # Aplikasi utama
```

## 🎮 Perintah Bot Telegram

| Perintah | Deskripsi |
|----------|-----------|
| `/start` | Memulai bot dan menampilkan menu utama |
| `/analisa` | Melakukan analisis teknikal real-time |
| `/status` | Mengecek status koneksi MT5 dan sistem |
| `/account` | Menampilkan informasi akun trading |
| `/help` | Menampilkan bantuan penggunaan |

## ⚙️ Konfigurasi Lanjutan

### Environment Variables

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `MT5_LOGIN` | Login akun MT5 | Required |
| `MT5_PASSWORD` | Password akun MT5 | Required |
| `MT5_SERVER` | Server broker | Required |
| `MT5_PATH` | Path instalasi MT5 | Windows default |
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram | Required |
| `TELEGRAM_CHAT_ID` | Chat ID Telegram | Required |
| `RISK_PERCENTAGE` | Persentase risiko per trade | 2.0 |
| `MAX_OPEN_POSITIONS` | Maksimal posisi terbuka | 5 |
| `SYMBOL_LIST` | Daftar symbol trading | EURUSD,GBPUSD,... |
| `LOG_LEVEL` | Level logging | INFO |

### Logging Configuration

Bot menggunakan sistem logging berlapis:
- **Console**: Output real-time dengan warna
- **File**: Log lengkap dengan rotasi otomatis
- **Error**: File khusus untuk error

File log disimpan di direktori `logs/`:
- `trading_bot.log`: Log utama
- `trading_bot_error.log`: Log error

## 🔧 Troubleshooting

### Masalah Umum

1. **MT5 Connection Failed**
   ```
   Solusi:
   - Pastikan MT5 sudah berjalan dan login
   - Periksa kredensial di .env
   - Aktifkan "Allow algorithmic trading"
   - Periksa koneksi internet
   ```

2. **Telegram Bot Not Responding**
   ```
   Solusi:
   - Periksa TELEGRAM_BOT_TOKEN
   - Pastikan bot sudah distart dengan /start
   - Periksa TELEGRAM_CHAT_ID
   - Cek koneksi internet
   ```

3. **Symbol Not Found**
   ```
   Solusi:
   - Periksa nama symbol di MT5
   - Pastikan symbol aktif di Market Watch
   - Sesuaikan SYMBOL_LIST di .env
   ```

### Debug Mode

Untuk debugging, ubah log level:
```env
LOG_LEVEL=DEBUG
```

### Test Commands

```bash
# Test koneksi MT5
python test_mt5_connection.py

# Test dengan verbose logging
LOG_LEVEL=DEBUG python run_bot.py

# Check logs
tail -f logs/trading_bot.log
```

## 📊 Monitoring & Maintenance

### Health Checks

Bot melakukan health check otomatis setiap 30 detik:
- Koneksi MT5
- Status Telegram bot
- Sistem resources

### Log Rotation

- File log dirotasi otomatis saat mencapai 10MB
- Error log dirotasi saat mencapai 5MB
- Retensi 30 hari dengan kompresi zip

### Backup Recommendations

Backup file penting:
- `.env` (konfigurasi)
- `logs/` (riwayat aktivitas)
- `data/` (data trading)

## 🚨 Keamanan

⚠️ **PENTING**: 
- Jangan commit file `.env` ke repository
- Gunakan akun demo untuk testing
- Batasi akses ke server/VPS
- Monitor aktivitas bot secara berkala

## 📈 Roadmap

- ✅ **Fase 1**: Setup dasar & koneksi MT5/Telegram
- 🔄 **Fase 2**: Strategi trading otomatis
- 📋 **Fase 3**: Risk management
- 📊 **Fase 4**: Dashboard web
- 🤖 **Fase 5**: Machine learning integration

## 🤝 Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Buat Pull Request

## 📄 License

Project ini menggunakan MIT License. Lihat file `LICENSE` untuk detail.

## ⚠️ Disclaimer

Bot ini dibuat untuk tujuan edukasi dan riset. Trading forex mengandung risiko tinggi. Selalu gunakan akun demo untuk testing dan pahami risiko sebelum trading dengan uang sungguhan.

---

**Happy Trading! 🚀**
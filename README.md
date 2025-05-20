# Field Worker Backend API

## Deskripsi
Program ini adalah backend API yang dibangun menggunakan FastAPI untuk mengelola absensi pekerja lapangan (field worker). Fitur utama meliputi pendaftaran dan autentikasi pengguna, pencatatan absensi dengan bukti foto dan lokasi, serta pengelolaan data proyek dan divisi. API ini mendukung otorisasi berbasis peran dan memastikan keamanan melalui JWT.

## Teknologi yang Digunakan
- Python 3.x
- FastAPI
- SQLAlchemy (ORM)
- Databases (async database connection)
- JWT (JSON Web Token) untuk autentikasi
- CORS Middleware
- MySql (tergantung konfigurasi database)
- Pydantic untuk validasi data

## Alur Kerja
1. Pengguna mendaftar sebagai pekerja lapangan dengan mengisi data yang diperlukan.
2. Pengguna melakukan login untuk mendapatkan token JWT yang digunakan untuk otorisasi.
3. Pengguna dapat melakukan absensi dengan mengirimkan data lokasi, foto dalam format base64, dan informasi proyek serta divisi.
4. Data absensi disimpan dengan timestamp yang disesuaikan dengan zona waktu pengguna.
5. Admin atau pengguna dapat mengambil data absensi berdasarkan user, tanggal mulai, dan tanggal akhir.
6. Sistem mengelola data pengguna, proyek, divisi, dan absensi secara terintegrasi.

## Cara Pengetesan
1. Pastikan environment Python sudah terpasang dan dependencies sudah diinstall, misalnya dengan:
   ```
   pip install -r requirements.txt
   ```
2. Jalankan server FastAPI dengan perintah:
   ```
   uvicorn app.main:app --reload
   ```
3. Gunakan tools seperti Postman atau curl untuk mengakses endpoint API berikut:
   - **Autentikasi:**
     - POST `/register-worker` : Mendaftar pengguna baru dengan data username, password, role, nama lengkap, dan division_id.
     - POST `/login` : Login untuk mendapatkan token JWT.
   - **User Management:**
     - GET `/users` : Mendapatkan daftar pengguna (hanya untuk admin dan staff).
     - GET `/me` : Mendapatkan data pengguna saat ini (menggunakan token).
     - PUT `/users/{user_id}` : Mengubah data pengguna (admin dan staff).
     - DELETE `/users/{user_id}` : Menghapus (menonaktifkan) pengguna (admin dan staff).
     - GET `/divisions` : Mendapatkan daftar divisi.
   - **Absensi:**
     - POST `/absensi` : Melakukan absensi dengan data lokasi, foto base64, project_id, division_id, dan tipe absensi (gunakan token JWT).
     - GET `/absensi` : Mengambil data absensi berdasarkan filter user_id dan rentang tanggal.
   - **Proyek:**
     - POST `/project` : Membuat proyek baru dengan nama proyek, deskripsi, dan lokasi. QR code akan dihasilkan otomatis.
4. Pastikan mengirim data sesuai schema yang ditentukan, termasuk foto dalam base64 untuk absensi.
5. Gunakan header `Authorization: Bearer <token>` untuk endpoint yang memerlukan autentikasi.

## Struktur Folder
- `app/main.py` : Entry point aplikasi FastAPI.
- `app/routes/` : Berisi definisi endpoint API.
- `app/db/` : Model dan konfigurasi database.
- `app/utils/` : Utilitas pendukung seperti JWT handler, penyimpanan foto, dan QR code.
- `app/schemas.py` : Definisi schema data menggunakan Pydantic.

---

README ini memberikan gambaran lengkap tentang program backend Field Worker dan cara menggunakannya untuk pengembangan dan pengujian lebih lanjut.

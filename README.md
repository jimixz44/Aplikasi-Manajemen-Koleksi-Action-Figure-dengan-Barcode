# Aplikasi-Manajemen-Koleksi-Action-Figure-dengan-Barcode

Tugas Kelompok 4

Aplikasi manajemen koleksi action figure dengan fitur:
- CRUD (Create, Read, Update, Delete) koleksi
- Generate barcode untuk setiap figure
- Scan barcode via kamera atau upload gambar
- Data tersimpan di Excel

## Cara Menjalankan

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi

```bash
streamlit run main.py
```

> ✅ **Tidak perlu install Visual C++ atau software tambahan lainnya!**

## Troubleshooting

### Error: "Cannot add data" / Gagal simpan
- Tutup file `data.xlsx` jika sedang dibuka di Excel
- Pastikan folder memiliki izin write

### Barcode tidak terdeteksi
- Pastikan gambar barcode jelas dan tidak blur
- Pastikan pencahayaan cukup
- Coba dengan barcode yang lebih besar di layar

### Error: OpenCV versi lama
```bash
pip install --upgrade opencv-python-headless
```

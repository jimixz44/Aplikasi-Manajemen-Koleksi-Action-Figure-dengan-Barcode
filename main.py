import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image
import os

st.set_page_config(page_title="Koleksi Action Figure", layout="wide", initial_sidebar_state="expanded")

NAMA_FILE_DATA = 'data.xlsx'
KOLOM_DATA = ['ID', 'Nama Figure', 'Seri', 'Kondisi', 'Harga Beli', 'Harga Pasar']
DAFTAR_KONDISI = ["Baru (Segel)", "Baru (Tanpa Segel)", "Bekas - Seperti Baru", "Bekas - Baik", "Bekas - Cukup", "Rusak Ringan", "Rusak Berat"]

def muat_data():
    if os.path.exists(NAMA_FILE_DATA):
        try:
            df = pd.read_excel(NAMA_FILE_DATA)
            for kolom in KOLOM_DATA:
                if kolom not in df.columns:
                    df[kolom] = ""
            return df
        except:
            return pd.DataFrame(columns=KOLOM_DATA)
    return pd.DataFrame(columns=KOLOM_DATA)

def simpan_data(df):
    try:
        df.to_excel(NAMA_FILE_DATA, index=False)
        return True
    except:
        return False

def buat_id_baru(df):
    if df.empty:
        return "AF001"
    nomor = max([int(x[2:]) for x in df['ID'] if isinstance(x, str) and x.startswith('AF')] or [0])
    return f"AF{str(nomor + 1).zfill(3)}"

def buat_barcode(id_figure):
    try:
        writer = ImageWriter()
        writer.set_options({'module_width': 0.4, 'module_height': 8.0, 'quiet_zone': 2.0, 'font_size': 10, 'text_distance': 3.0})
        bc = barcode.get_barcode_class('code128')(str(id_figure), writer=writer)
        buffer = BytesIO()
        bc.write(buffer)
        buffer.seek(0)
        return Image.open(buffer)
    except:
        return None

def format_rupiah(angka):
    try:
        return f"Rp {int(angka):,}".replace(",", ".")
    except:
        return f"Rp {angka}"

def decode_barcode(gambar_bytes):
    try:
        from pyzbar.pyzbar import decode
        import cv2
        import numpy as np
        
        # Konversi bytes ke gambar
        arr = np.frombuffer(gambar_bytes, np.uint8)
        gambar = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        
        if gambar is None:
            return None, None
        
        # Konversi ke abu-abu (grayscale)
        abu = cv2.cvtColor(gambar, cv2.COLOR_BGR2GRAY)
        
        # Daftar metode preprocessing yang akan dicoba
        daftar_gambar = []
        
        # 1. Gambar asli berwarna
        daftar_gambar.append(gambar)
        
        # 2. Abu-abu (grayscale)
        daftar_gambar.append(abu)
        
        # 3. Bilateral filter (pengurangan noise sambil mempertahankan tepi)
        bilateral = cv2.bilateralFilter(abu, 9, 75, 75)
        daftar_gambar.append(bilateral)
        
        # 4. Binary threshold sederhana
        _, biner = cv2.threshold(abu, 127, 255, cv2.THRESH_BINARY)
        daftar_gambar.append(biner)
        
        # 5. Inverted binary threshold (untuk background gelap)
        _, biner_inv = cv2.threshold(abu, 127, 255, cv2.THRESH_BINARY_INV)
        daftar_gambar.append(biner_inv)
        
        # 6. Adaptive threshold Gaussian
        adaptive_gauss = cv2.adaptiveThreshold(abu, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        daftar_gambar.append(adaptive_gauss)
        
        # 7. Adaptive threshold Mean
        adaptive_mean = cv2.adaptiveThreshold(abu, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        daftar_gambar.append(adaptive_mean)
        
        # 8. CLAHE (peningkatan kontras)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        clahe_img = clahe.apply(abu)
        daftar_gambar.append(clahe_img)
        
        # 9. Otsu's thresholding (threshold otomatis)
        _, otsu = cv2.threshold(abu, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        daftar_gambar.append(otsu)
        
        # 10. Operasi morfologi closing (menutup celah)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(biner, cv2.MORPH_CLOSE, kernel)
        daftar_gambar.append(morph)
        
        # 11. Sharpening (penajaman tepi)
        kernel_sharp = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(abu, -1, kernel_sharp)
        daftar_gambar.append(sharpened)
        
        # Coba decode setiap gambar yang sudah diproses
        for gambar_proses in daftar_gambar:
            hasil = decode(gambar_proses)
            if hasil:
                # Barcode ditemukan, kembalikan hasilnya
                return hasil[0].data.decode('utf-8'), hasil[0].type
        
        # Jika tidak ditemukan, kembalikan None
        return None, None
        
    except Exception as e:
        # Gagal silent, bisa log error untuk debugging
        return None, None

def tampilkan_barcode(id_figure, key_suffix=""):
    bc = buat_barcode(id_figure)
    if bc:
        st.image(bc, width=200)
        buffer = BytesIO()
        bc.save(buffer, format='PNG')
        buffer.seek(0)
        st.download_button("Download Barcode", buffer, f"barcode_{id_figure}.png", "image/png", key=f"dl_{id_figure}_{key_suffix}")

# Sidebar
with st.sidebar:
    st.title("Action Figure Manager")
    menu = option_menu(None, ["Koleksi", "Tambah", "Scan", "Kelola"], 
                       icons=["collection", "plus-circle", "upc-scan", "pencil-square"], default_index=0)
    st.divider()
    df = muat_data()
    st.write(f"**Total:** {len(df)}")
    if not df.empty:
        st.write(f"**Nilai:** {format_rupiah(df['Harga Pasar'].sum())}")

# Halaman Koleksi
if menu == "Koleksi":
    st.title("Daftar Koleksi Action Figure")
    df = muat_data()
    if df.empty:
        st.info("Belum ada koleksi.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", len(df))
        c2.metric("Harga Beli", format_rupiah(df['Harga Beli'].sum()))
        c3.metric("Harga Pasar", format_rupiah(df['Harga Pasar'].sum()))
        c4.metric("Keuntungan", format_rupiah(df['Harga Pasar'].sum() - df['Harga Beli'].sum()))
        st.divider()
        
        col1, col2 = st.columns(2)
        cari = col1.text_input("Cari", placeholder="Nama atau seri...")
        seri = col2.selectbox("Seri", ["Semua"] + list(df['Seri'].unique()))
        
        data = df.copy()
        if cari:
            data = data[data['Nama Figure'].str.contains(cari, case=False, na=False) | data['Seri'].str.contains(cari, case=False, na=False)]
        if seri != "Semua":
            data = data[data['Seri'] == seri]
        
        st.write(f"**{len(data)}/{len(df)} koleksi**")
        for _, baris in data.iterrows():
            with st.expander(f"**{baris['ID']}** - {baris['Nama Figure']} | {baris['Kondisi']} | {format_rupiah(baris['Harga Pasar'])}"):
                c1, c2 = st.columns([3, 2])
                c1.write(f"**ID:** {baris['ID']}\n\n**Nama:** {baris['Nama Figure']}\n\n**Seri:** {baris['Seri']}\n\n**Kondisi:** {baris['Kondisi']}\n\n**Beli:** {format_rupiah(baris['Harga Beli'])}\n\n**Pasar:** {format_rupiah(baris['Harga Pasar'])}")
                with c2:
                    tampilkan_barcode(baris['ID'], f"col_{baris['ID']}")

# Halaman Tambah
elif menu == "Tambah":
    st.title("Tambah Koleksi Baru")
    df = muat_data()
    id_baru = buat_id_baru(df)
    st.info(f"ID: **{id_baru}**")
    
    if 'tersimpan' not in st.session_state:
        st.session_state.tersimpan = None
    
    with st.form("tambah", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Figure *")
        seri = c1.text_input("Seri *")
        kondisi = c1.selectbox("Kondisi", DAFTAR_KONDISI)
        beli = c2.number_input("Harga Beli (Rp)", min_value=0, step=10000)
        pasar = c2.number_input("Harga Pasar (Rp)", min_value=0, step=10000)
        
        if st.form_submit_button("Simpan", use_container_width=True):
            if nama and seri:
                baru = pd.DataFrame([{'ID': id_baru, 'Nama Figure': nama, 'Seri': seri, 'Kondisi': kondisi, 
                                     'Harga Beli': beli, 'Harga Pasar': pasar if pasar > 0 else beli}])
                if simpan_data(pd.concat([df, baru], ignore_index=True)):
                    st.session_state.tersimpan = {'id': id_baru, 'nama': nama}
            else:
                st.error("Nama dan Seri wajib diisi!")
    
    if st.session_state.tersimpan:
        st.success(f"**{st.session_state.tersimpan['nama']}** tersimpan dengan ID: **{st.session_state.tersimpan['id']}**")
        tampilkan_barcode(st.session_state.tersimpan['id'], "tambah")
        if st.button("Tambah Lagi"):
            st.session_state.tersimpan = None
            st.rerun()

# Halaman Scan
elif menu == "Scan":
    st.title("Scan / Cari Koleksi")
    df = muat_data()
    if 'scan_id' not in st.session_state:
        st.session_state.scan_id = ""
    
    tab1, tab2, tab3 = st.tabs(["Manual", "Kamera", "Upload"])
    
    with tab1:
        c1, c2 = st.columns([3, 1])
        id_input = c1.text_input("ID Figure", placeholder="AF001", label_visibility="collapsed")
        if c2.button("Cari", use_container_width=True) and id_input:
            st.session_state.scan_id = id_input
    
    with tab2:
        foto = st.camera_input("Ambil foto barcode")
        if foto:
            st.image(foto, width=300)
            data_hasil, tipe = decode_barcode(foto.getvalue())
            if data_hasil:
                st.success(f"Terdeteksi: **{data_hasil}** ({tipe})")
                st.session_state.scan_id = data_hasil
            else:
                st.error("Barcode tidak terdeteksi")
    
    with tab3:
        berkas = st.file_uploader("Upload gambar", type=['png', 'jpg', 'jpeg'])
        if berkas:
            st.image(berkas, width=300)
            data_hasil, tipe = decode_barcode(berkas.getvalue())
            if data_hasil:
                st.success(f"Terdeteksi: **{data_hasil}** ({tipe})")
                st.session_state.scan_id = data_hasil
            else:
                st.error("Barcode tidak terdeteksi")
    
    if st.session_state.scan_id:
        hasil = df[df['ID'].str.upper() == st.session_state.scan_id.upper()]
        st.divider()
        if hasil.empty:
            st.warning(f"ID **{st.session_state.scan_id}** tidak ditemukan")
        else:
            baris = hasil.iloc[0]
            st.subheader(baris['Nama Figure'])
            c1, c2 = st.columns([3, 2])
            c1.write(f"**ID:** {baris['ID']}\n\n**Seri:** {baris['Seri']}\n\n**Kondisi:** {baris['Kondisi']}\n\n**Beli:** {format_rupiah(baris['Harga Beli'])}\n\n**Pasar:** {format_rupiah(baris['Harga Pasar'])}")
            with c2:
                tampilkan_barcode(baris['ID'], "scan")
        
        if st.button("Reset", key="reset_scan"):
            st.session_state.scan_id = ""
            st.rerun()


# Halaman Kelola
elif menu == "Kelola":
    st.title("Kelola Koleksi")
    df = muat_data()
    if df.empty:
        st.info("Belum ada koleksi")
    else:
        if 'edit' not in st.session_state:
            st.session_state.edit = None
        if 'hapus' not in st.session_state:
            st.session_state.hapus = None
        
        st.write(f"**Total: {len(df)}**")
        for indeks, baris in df.iterrows():
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{baris['ID']}** - {baris['Nama Figure']} | {baris['Kondisi']} | {format_rupiah(baris['Harga Pasar'])}")
            b1, b2 = c2.columns(2)
            if b1.button("Edit", key=f"e_{baris['ID']}"):
                st.session_state.edit = baris['ID']
                st.session_state.hapus = None
            if b2.button("Hapus", key=f"h_{baris['ID']}"):
                st.session_state.hapus = baris['ID']
                st.session_state.edit = None
            
            if st.session_state.edit == baris['ID']:
                with st.form(f"edit_{baris['ID']}"):
                    c1, c2 = st.columns(2)
                    nama = c1.text_input("Nama", value=baris['Nama Figure'])
                    seri = c1.text_input("Seri", value=baris['Seri'])
                    kondisi = c1.selectbox("Kondisi", DAFTAR_KONDISI, index=DAFTAR_KONDISI.index(baris['Kondisi']) if baris['Kondisi'] in DAFTAR_KONDISI else 0)
                    beli = c2.number_input("Harga Beli", value=int(baris['Harga Beli']), min_value=0, step=10000)
                    pasar = c2.number_input("Harga Pasar", value=int(baris['Harga Pasar']), min_value=0, step=10000)
                    s1, s2 = st.columns(2)
                    if s1.form_submit_button("Simpan", use_container_width=True):
                        df.at[indeks, 'Nama Figure'] = nama
                        df.at[indeks, 'Seri'] = seri
                        df.at[indeks, 'Kondisi'] = kondisi
                        df.at[indeks, 'Harga Beli'] = beli
                        df.at[indeks, 'Harga Pasar'] = pasar
                        simpan_data(df)
                        st.session_state.edit = None
                        st.rerun()
                    if s2.form_submit_button("Batal", use_container_width=True):
                        st.session_state.edit = None
                        st.rerun()
            
            if st.session_state.hapus == baris['ID']:
                st.warning(f"Hapus **{baris['Nama Figure']}**?")
                h1, h2 = st.columns(2)
                if h1.button("Ya", key=f"y_{baris['ID']}", type="primary"):
                    simpan_data(df[df['ID'] != baris['ID']])
                    st.session_state.hapus = None
                    st.rerun()
                if h2.button("Batal", key=f"n_{baris['ID']}"):
                    st.session_state.hapus = None
                    st.rerun()
            st.divider()

st.divider()
st.caption("Manajemen Action Figure | Kelompok 4")
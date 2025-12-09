import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image
import os

# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="Koleksi Action Figure",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SVG ICONS ====================
ICONS = {
    "collection": '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>''',
    "plus": '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg>''',
    "search": '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>''',
    "edit": '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>''',
    "box": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>''',
    "tag": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>''',
    "barcode": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5v14"></path><path d="M8 5v14"></path><path d="M12 5v14"></path><path d="M17 5v14"></path><path d="M21 5v14"></path></svg>''',
    "money": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>''',
    "trending_up": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>''',
    "trending_down": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>''',
    "download": '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>''',
    "trash": '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>''',
    "save": '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>''',
    "figure": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line><line x1="12" y1="16" x2="8" y2="22"></line><line x1="12" y1="16" x2="16" y2="22"></line></svg>''',
    "folder": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>''',
    "star": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>''',
    "id": '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"></rect><line x1="7" y1="8" x2="7" y2="8"></line><line x1="7" y1="12" x2="7" y2="12"></line><line x1="7" y1="16" x2="7" y2="16"></line><line x1="11" y1="8" x2="17" y2="8"></line><line x1="11" y1="12" x2="17" y2="12"></line><line x1="11" y1="16" x2="17" y2="16"></line></svg>''',
}

# ==================== CUSTOM CSS STYLING ====================
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Card styling */
    .kartu-figure {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border: 1px solid #3a5a7c;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .kartu-figure h3 {
        color: #00d4ff;
        margin-bottom: 15px;
        font-size: 1.4rem;
    }
    
    .kartu-figure p {
        color: #e0e0e0;
        margin: 8px 0;
        font-size: 1rem;
    }
    
    .label-info {
        color: #7fb3d5;
        font-weight: 600;
    }
    
    .nilai-info {
        color: #ffffff;
    }
    
    /* Header styling */
    .judul-utama {
        text-align: center;
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 30px;
    }
    
    /* SVG icon inline */
    .icon-inline {
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    .icon-inline svg {
        vertical-align: middle;
    }
    
    /* Stats cards */
    .kartu-statistik {
        background: linear-gradient(135deg, #2d3e50 0%, #1a252f 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #4a6fa5;
    }
    
    /* Barcode container */
    .wadah-barcode {
        background: white;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 10px 0;
    }
    
    /* Sidebar title */
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #00d4ff;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== NAMA FILE DATA ====================
NAMA_FILE_DATA = 'data.xlsx'

# ==================== DAFTAR KONDISI (Bahasa Indonesia) ====================
DAFTAR_KONDISI = [
    "Baru (Segel)",
    "Baru (Tanpa Segel)",
    "Bekas - Seperti Baru",
    "Bekas - Baik",
    "Bekas - Cukup",
    "Rusak Ringan",
    "Rusak Berat"
]

# ==================== FUNGSI DATA ====================

def muat_data():
    """Memuat data koleksi dari file Excel"""
    if os.path.exists(NAMA_FILE_DATA):
        try:
            data_koleksi = pd.read_excel(NAMA_FILE_DATA)
            kolom_wajib = ['ID', 'Nama Figure', 'Seri', 'Kondisi', 'Harga Beli', 'Harga Pasar']
            for kolom in kolom_wajib:
                if kolom not in data_koleksi.columns:
                    data_koleksi[kolom] = ""
            return data_koleksi
        except Exception as e:
            st.error(f"Error membaca file: {e}")
            return pd.DataFrame(columns=['ID', 'Nama Figure', 'Seri', 'Kondisi', 'Harga Beli', 'Harga Pasar'])
    else:
        return pd.DataFrame(columns=['ID', 'Nama Figure', 'Seri', 'Kondisi', 'Harga Beli', 'Harga Pasar'])

def simpan_data(data_koleksi):
    """Menyimpan data koleksi ke file Excel"""
    try:
        data_koleksi.to_excel(NAMA_FILE_DATA, index=False)
        return True
    except Exception as e:
        st.error(f"Error menyimpan file: {e}")
        return False

def buat_id_baru(data_koleksi):
    """Membuat ID baru secara otomatis (AF001, AF002, dst.)"""
    if data_koleksi.empty:
        return "AF001"
    
    nomor_terbesar = 0
    for id_figure in data_koleksi['ID']:
        if isinstance(id_figure, str) and id_figure.startswith('AF'):
            try:
                nomor = int(id_figure[2:])
                if nomor > nomor_terbesar:
                    nomor_terbesar = nomor
            except ValueError:
                continue
    
    id_baru = f"AF{str(nomor_terbesar + 1).zfill(3)}"
    return id_baru

def buat_barcode(id_figure):
    """Membuat gambar barcode Code128 dari ID figure"""
    try:
        kelas_code128 = barcode.get_barcode_class('code128')
        
        # Konfigurasi writer untuk barcode lebih panjang/horizontal
        writer = ImageWriter()
        writer.set_options({
            'module_width': 0.4,      # Lebar garis barcode
            'module_height': 8.0,     # Tinggi barcode (lebih pendek)
            'quiet_zone': 2.0,        # Zona kosong di sekitar
            'font_size': 10,          # Ukuran font teks
            'text_distance': 3.0,     # Jarak teks dari barcode
        })
        
        objek_barcode = kelas_code128(str(id_figure), writer=writer)
        
        buffer = BytesIO()
        objek_barcode.write(buffer)
        buffer.seek(0)
        
        gambar_barcode = Image.open(buffer)
        return gambar_barcode
    except Exception as e:
        st.error(f"Error membuat barcode: {e}")
        return None

def format_rupiah(angka):
    """Format angka ke format Rupiah"""
    try:
        return f"Rp {int(angka):,}".replace(",", ".")
    except:
        return f"Rp {angka}"

def dapatkan_warna_kondisi(kondisi):
    """Mendapatkan warna badge berdasarkan kondisi"""
    kondisi_lower = kondisi.lower() if isinstance(kondisi, str) else ""
    if "baru" in kondisi_lower and "segel" in kondisi_lower:
        return "#28a745"  # Hijau
    elif "baru" in kondisi_lower:
        return "#20c997"  # Teal
    elif "seperti baru" in kondisi_lower:
        return "#17a2b8"  # Cyan
    elif "baik" in kondisi_lower:
        return "#007bff"  # Biru
    elif "cukup" in kondisi_lower:
        return "#ffc107"  # Kuning
    elif "rusak ringan" in kondisi_lower:
        return "#fd7e14"  # Orange
    elif "rusak" in kondisi_lower:
        return "#dc3545"  # Merah
    else:
        return "#6c757d"  # Abu-abu

# ==================== SIDEBAR NAVIGATION ====================

with st.sidebar:
    st.markdown('<p class="sidebar-title">Action Figure Manager</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    menu_terpilih = option_menu(
        menu_title=None,
        options=["Koleksi", "Tambah", "Scan", "Kelola"],
        icons=["collection", "plus-circle", "upc-scan", "pencil-square"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#0e1117"},
            "icon": {"color": "#00d4ff", "font-size": "18px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "5px",
                "padding": "10px 15px",
                "border-radius": "10px",
                "--hover-color": "#1e3a5f",
                "white-space": "nowrap"
            },
            "nav-link-selected": {
                "background-color": "#1e3a5f",
                "color": "#00d4ff",
                "font-weight": "600"
            },
        }
    )
    
    st.markdown("---")
    
    # Statistik singkat di sidebar
    data_koleksi = muat_data()
    total_koleksi = len(data_koleksi)
    
    st.markdown(f"**Total Koleksi:** {total_koleksi}")
    
    if not data_koleksi.empty:
        try:
            total_nilai = data_koleksi['Harga Pasar'].sum()
            st.markdown(f"**Total Nilai:** {format_rupiah(total_nilai)}")
        except:
            pass

# ==================== HALAMAN: LIHAT KOLEKSI ====================

if menu_terpilih == "Koleksi":
    st.markdown('<h1 class="judul-utama">Daftar Koleksi Action Figure</h1>', unsafe_allow_html=True)
    
    data_koleksi = muat_data()
    
    if data_koleksi.empty:
        st.info("Belum ada koleksi. Silakan tambahkan koleksi baru!")
    else:
        # Statistik Cards
        kol1, kol2, kol3, kol4 = st.columns(4)
        
        with kol1:
            st.metric(label="Total Koleksi", value=len(data_koleksi))
        
        with kol2:
            try:
                total_beli = data_koleksi['Harga Beli'].sum()
                st.metric(label="Total Harga Beli", value=format_rupiah(total_beli))
            except:
                st.metric(label="Total Harga Beli", value="N/A")
        
        with kol3:
            try:
                total_pasar = data_koleksi['Harga Pasar'].sum()
                st.metric(label="Total Harga Pasar", value=format_rupiah(total_pasar))
            except:
                st.metric(label="Total Harga Pasar", value="N/A")
        
        with kol4:
            try:
                keuntungan = data_koleksi['Harga Pasar'].sum() - data_koleksi['Harga Beli'].sum()
                st.metric(label="Keuntungan", value=format_rupiah(keuntungan), delta=f"{keuntungan:+,}".replace(",", "."))
            except:
                st.metric(label="Keuntungan", value="N/A")
        
        st.markdown("---")
        
        # Filter dan Search
        kol_filter1, kol_filter2 = st.columns(2)
        
        with kol_filter1:
            kata_pencarian = st.text_input("Cari Figure", placeholder="Ketik nama atau seri...")
        
        with kol_filter2:
            daftar_seri = ["Semua"] + list(data_koleksi['Seri'].unique())
            filter_seri = st.selectbox("Filter Seri", daftar_seri)
        
        # Apply filters
        data_tampil = data_koleksi.copy()
        
        if kata_pencarian:
            data_tampil = data_tampil[
                data_tampil['Nama Figure'].str.contains(kata_pencarian, case=False, na=False) |
                data_tampil['Seri'].str.contains(kata_pencarian, case=False, na=False)
            ]
        
        if filter_seri != "Semua":
            data_tampil = data_tampil[data_tampil['Seri'] == filter_seri]
        
        st.markdown(f"**Menampilkan {len(data_tampil)} dari {len(data_koleksi)} koleksi**")
        
        # Tampilkan setiap figure sebagai card dengan expander untuk barcode
        for idx, row in data_tampil.iterrows():
            warna_kondisi = dapatkan_warna_kondisi(row['Kondisi'])
            
            with st.expander(f"**{row['ID']}** - {row['Nama Figure']} ({row['Seri']}) | {row['Kondisi']} | {format_rupiah(row['Harga Pasar'])}"):
                kol_info, kol_barcode = st.columns([3, 2])
                
                with kol_info:
                    st.markdown(f"**ID:** {row['ID']}")
                    st.markdown(f"**Nama:** {row['Nama Figure']}")
                    st.markdown(f"**Seri:** {row['Seri']}")
                    st.markdown(f"**Kondisi:** {row['Kondisi']}")
                    st.markdown(f"**Harga Beli:** {format_rupiah(row['Harga Beli'])}")
                    st.markdown(f"**Harga Pasar:** {format_rupiah(row['Harga Pasar'])}")
                
                with kol_barcode:
                    gambar_barcode = buat_barcode(row['ID'])
                    if gambar_barcode:
                        st.image(gambar_barcode, width=200)
                        
                        buffer = BytesIO()
                        gambar_barcode.save(buffer, format='PNG')
                        buffer.seek(0)
                        
                        st.download_button(
                            label="Download Barcode",
                            data=buffer,
                            file_name=f"barcode_{row['ID']}.png",
                            mime="image/png",
                            key=f"download_{row['ID']}"
                        )

# ==================== HALAMAN: TAMBAH KOLEKSI ====================

elif menu_terpilih == "Tambah":
    st.markdown('<h1 class="judul-utama">Tambah Koleksi Baru</h1>', unsafe_allow_html=True)
    
    data_koleksi = muat_data()
    id_baru = buat_id_baru(data_koleksi)
    
    st.info(f"ID Otomatis: **{id_baru}**")
    
    # Inisialisasi session state untuk tracking hasil simpan
    if 'koleksi_tersimpan' not in st.session_state:
        st.session_state.koleksi_tersimpan = None
    
    with st.form("form_tambah_koleksi", clear_on_submit=True):
        kol_form1, kol_form2 = st.columns(2)
        
        with kol_form1:
            nama_figure = st.text_input("Nama Figure *", placeholder="Contoh: Goku Ultra Instinct")
            seri_figure = st.text_input("Seri/Franchise *", placeholder="Contoh: Dragon Ball Super")
            kondisi_figure = st.selectbox("Kondisi *", DAFTAR_KONDISI)
        
        with kol_form2:
            harga_beli = st.number_input("Harga Beli (Rp) *", min_value=0, step=10000, value=0)
            harga_pasar = st.number_input("Harga Pasar (Rp)", min_value=0, step=10000, value=0)
            catatan = st.text_area("Catatan (opsional)", placeholder="Catatan tambahan...")
        
        tombol_simpan = st.form_submit_button("Simpan Koleksi", use_container_width=True)
        
        if tombol_simpan:
            # Validasi
            if not nama_figure or not seri_figure:
                st.error("Nama Figure dan Seri harus diisi!")
                st.session_state.koleksi_tersimpan = None
            else:
                # Buat data baru
                data_baru = {
                    'ID': id_baru,
                    'Nama Figure': nama_figure,
                    'Seri': seri_figure,
                    'Kondisi': kondisi_figure,
                    'Harga Beli': harga_beli,
                    'Harga Pasar': harga_pasar if harga_pasar > 0 else harga_beli
                }
                
                # Tambahkan ke dataframe
                data_koleksi = pd.concat([data_koleksi, pd.DataFrame([data_baru])], ignore_index=True)
                
                # Simpan
                if simpan_data(data_koleksi):
                    st.session_state.koleksi_tersimpan = {
                        'id': id_baru,
                        'nama': nama_figure
                    }
                else:
                    st.session_state.koleksi_tersimpan = None
    
    # Tampilkan barcode di luar form jika berhasil disimpan
    if st.session_state.koleksi_tersimpan:
        id_tersimpan = st.session_state.koleksi_tersimpan['id']
        nama_tersimpan = st.session_state.koleksi_tersimpan['nama']
        
        st.success(f"Koleksi **{nama_tersimpan}** berhasil ditambahkan dengan ID: **{id_tersimpan}**")
        
        st.markdown("---")
        st.subheader("Barcode Anda")
        
        gambar_barcode = buat_barcode(id_tersimpan)
        if gambar_barcode:
            kol_bc1, kol_bc2, kol_bc3 = st.columns([1, 2, 1])
            with kol_bc2:
                st.image(gambar_barcode, caption=f"Barcode: {id_tersimpan}", use_container_width=True)
                
                buffer = BytesIO()
                gambar_barcode.save(buffer, format='PNG')
                buffer.seek(0)
                
                st.download_button(
                    label="Download Barcode",
                    data=buffer,
                    file_name=f"barcode_{id_tersimpan}.png",
                    mime="image/png",
                    key="download_barcode_tambah"
                )
        
        # Tombol untuk reset dan tambah baru
        if st.button("Tambah Koleksi Baru"):
            st.session_state.koleksi_tersimpan = None
            st.rerun()


# ==================== HALAMAN: SCAN BARCODE ====================

elif menu_terpilih == "Scan":
    st.markdown('<h1 class="judul-utama">Scan / Cari Koleksi</h1>', unsafe_allow_html=True)
    
    data_koleksi = muat_data()
    
    # Inisialisasi session state untuk hasil scan
    if 'id_hasil_scan' not in st.session_state:
        st.session_state.id_hasil_scan = ""
    
    # Tab untuk berbagai metode input
    tab_manual, tab_kamera, tab_upload = st.tabs(["Input Manual", "Scan Kamera", "Upload Gambar"])
    
    with tab_manual:
        st.markdown("### Masukkan ID Figure")
        st.markdown("*Ketik ID manual untuk melihat detail figure*")
        
        kol_input1, kol_input2 = st.columns([3, 1])
        
        with kol_input1:
            id_dicari_manual = st.text_input("ID Figure", placeholder="Contoh: AF001", label_visibility="collapsed", key="manual_input")
        
        with kol_input2:
            tombol_cari = st.button("Cari", use_container_width=True, key="btn_cari_manual")
        
        if tombol_cari and id_dicari_manual:
            st.session_state.id_hasil_scan = id_dicari_manual
    
    with tab_kamera:
        st.markdown("### Scan Barcode dengan Kamera")
        st.markdown("*Ambil foto barcode menggunakan kamera*")
        
        # Gunakan camera_input untuk mengambil foto
        foto_kamera = st.camera_input("Arahkan kamera ke barcode", key="camera_scan")
        
        if foto_kamera:
            try:
                # Import pyzbar untuk decode barcode
                from pyzbar.pyzbar import decode
                import cv2
                import numpy as np
                
                # Konversi foto ke format yang bisa dibaca
                gambar_bytes = foto_kamera.getvalue()
                gambar_array = np.frombuffer(gambar_bytes, np.uint8)
                gambar_cv = cv2.imdecode(gambar_array, cv2.IMREAD_COLOR)
                
                # Decode barcode
                hasil_decode = decode(gambar_cv)
                
                if hasil_decode:
                    for barcode_obj in hasil_decode:
                        data_barcode = barcode_obj.data.decode('utf-8')
                        tipe_barcode = barcode_obj.type
                        st.success(f"Barcode terdeteksi: **{data_barcode}** (Tipe: {tipe_barcode})")
                        st.session_state.id_hasil_scan = data_barcode
                        break
                else:
                    st.warning("Tidak ada barcode yang terdeteksi. Pastikan barcode terlihat jelas dan coba lagi.")
            except ImportError:
                st.error("Library pyzbar belum terinstall. Jalankan: `pip install pyzbar`")
            except Exception as e:
                st.error(f"Error saat scan: {e}")
    
    with tab_upload:
        st.markdown("### Upload Gambar Barcode")
        st.markdown("*Upload file gambar yang berisi barcode*")
        
        file_upload = st.file_uploader("Pilih file gambar", type=['png', 'jpg', 'jpeg', 'gif', 'bmp'], key="upload_barcode")
        
        if file_upload:
            try:
                # Import pyzbar untuk decode barcode
                from pyzbar.pyzbar import decode
                import cv2
                import numpy as np
                
                # Tampilkan preview gambar
                st.image(file_upload, caption="Preview gambar", width=300)
                
                # Konversi ke format yang bisa dibaca
                gambar_bytes = file_upload.getvalue()
                gambar_array = np.frombuffer(gambar_bytes, np.uint8)
                gambar_cv = cv2.imdecode(gambar_array, cv2.IMREAD_COLOR)
                
                # Decode barcode
                hasil_decode = decode(gambar_cv)
                
                if hasil_decode:
                    for barcode_obj in hasil_decode:
                        data_barcode = barcode_obj.data.decode('utf-8')
                        tipe_barcode = barcode_obj.type
                        st.success(f"Barcode terdeteksi: **{data_barcode}** (Tipe: {tipe_barcode})")
                        st.session_state.id_hasil_scan = data_barcode
                        break
                else:
                    st.warning("Tidak ada barcode yang terdeteksi dalam gambar.")
            except ImportError:
                st.error("Library pyzbar belum terinstall. Jalankan: `pip install pyzbar`")
            except Exception as e:
                st.error(f"Error saat membaca gambar: {e}")
    
    # Tampilkan hasil pencarian jika ada ID
    id_dicari = st.session_state.id_hasil_scan or id_dicari_manual if 'id_dicari_manual' in dir() else st.session_state.id_hasil_scan
    
    if id_dicari:
        # Cari di database
        hasil_pencarian = data_koleksi[data_koleksi['ID'].str.upper() == id_dicari.upper()]
        
        if hasil_pencarian.empty:
            st.markdown("---")
            st.warning(f"Figure dengan ID **{id_dicari}** tidak ditemukan!")
        else:
            figure = hasil_pencarian.iloc[0]
            warna_kondisi = dapatkan_warna_kondisi(figure['Kondisi'])
            
            st.markdown("---")
            st.markdown(f"### {figure['Nama Figure']}")
            
            kol_info, kol_barcode = st.columns([3, 2])
            
            with kol_info:
                st.markdown(f"**ID:** {figure['ID']}")
                st.markdown(f"**Seri:** {figure['Seri']}")
                st.markdown(f"**Kondisi:** {figure['Kondisi']}")
                st.markdown(f"**Harga Beli:** {format_rupiah(figure['Harga Beli'])}")
                st.markdown(f"**Harga Pasar:** {format_rupiah(figure['Harga Pasar'])}")
            
            with kol_barcode:
                gambar_barcode = buat_barcode(figure['ID'])
                if gambar_barcode:
                    st.image(gambar_barcode, width=200)
                    
                    buffer = BytesIO()
                    gambar_barcode.save(buffer, format='PNG')
                    buffer.seek(0)
                    
                    st.download_button(
                        label="Download Barcode",
                        data=buffer,
                        file_name=f"barcode_{figure['ID']}.png",
                        mime="image/png"
                    )
        
        # Tombol reset
        if st.button("Scan Baru"):
            st.session_state.id_hasil_scan = ""
            st.rerun()


# ==================== HALAMAN: UPDATE KOLEKSI ====================

elif menu_terpilih == "Kelola":
    st.markdown('<h1 class="judul-utama">Kelola Koleksi</h1>', unsafe_allow_html=True)
    
    data_koleksi = muat_data()
    
    if data_koleksi.empty:
        st.info("Belum ada koleksi untuk dikelola.")
    else:
        # Inisialisasi session state untuk mode edit
        if 'mode_edit' not in st.session_state:
            st.session_state.mode_edit = None
        if 'konfirmasi_hapus' not in st.session_state:
            st.session_state.konfirmasi_hapus = None
        
        st.markdown(f"**Total {len(data_koleksi)} koleksi**")
        
        # Tampilkan setiap item dengan action buttons
        for idx, row in data_koleksi.iterrows():
            with st.container():
                kol_info, kol_aksi = st.columns([4, 1])
                
                with kol_info:
                    st.markdown(f"**{row['ID']}** - {row['Nama Figure']} | {row['Seri']} | {row['Kondisi']} | {format_rupiah(row['Harga Pasar'])}")
                
                with kol_aksi:
                    kol_btn1, kol_btn2 = st.columns(2)
                    with kol_btn1:
                        if st.button("Edit", key=f"edit_{row['ID']}", use_container_width=True):
                            st.session_state.mode_edit = row['ID']
                            st.session_state.konfirmasi_hapus = None
                    with kol_btn2:
                        if st.button("Hapus", key=f"hapus_{row['ID']}", use_container_width=True):
                            st.session_state.konfirmasi_hapus = row['ID']
                            st.session_state.mode_edit = None
                
                # Form Edit inline
                if st.session_state.mode_edit == row['ID']:
                    st.markdown("---")
                    with st.form(f"form_edit_{row['ID']}"):
                        st.markdown(f"### Edit: {row['Nama Figure']}")
                        kol_e1, kol_e2 = st.columns(2)
                        
                        with kol_e1:
                            nama_baru = st.text_input("Nama Figure", value=row['Nama Figure'], key=f"nama_{row['ID']}")
                            seri_baru = st.text_input("Seri", value=row['Seri'], key=f"seri_{row['ID']}")
                            kondisi_idx = DAFTAR_KONDISI.index(row['Kondisi']) if row['Kondisi'] in DAFTAR_KONDISI else 0
                            kondisi_baru = st.selectbox("Kondisi", DAFTAR_KONDISI, index=kondisi_idx, key=f"kondisi_{row['ID']}")
                        
                        with kol_e2:
                            harga_beli_baru = st.number_input("Harga Beli (Rp)", value=int(row['Harga Beli']), min_value=0, step=10000, key=f"beli_{row['ID']}")
                            harga_pasar_baru = st.number_input("Harga Pasar (Rp)", value=int(row['Harga Pasar']), min_value=0, step=10000, key=f"pasar_{row['ID']}")
                        
                        kol_s1, kol_s2 = st.columns(2)
                        with kol_s1:
                            if st.form_submit_button("Simpan", use_container_width=True):
                                data_koleksi.at[idx, 'Nama Figure'] = nama_baru
                                data_koleksi.at[idx, 'Seri'] = seri_baru
                                data_koleksi.at[idx, 'Kondisi'] = kondisi_baru
                                data_koleksi.at[idx, 'Harga Beli'] = harga_beli_baru
                                data_koleksi.at[idx, 'Harga Pasar'] = harga_pasar_baru
                                if simpan_data(data_koleksi):
                                    st.success(f"{nama_baru} berhasil diupdate!")
                                    st.session_state.mode_edit = None
                                    st.rerun()
                        with kol_s2:
                            if st.form_submit_button("Batal", use_container_width=True):
                                st.session_state.mode_edit = None
                                st.rerun()
                    st.markdown("---")
                
                # Konfirmasi Hapus inline
                if st.session_state.konfirmasi_hapus == row['ID']:
                    st.warning(f"Yakin hapus **{row['Nama Figure']}**?")
                    kol_h1, kol_h2 = st.columns(2)
                    with kol_h1:
                        if st.button("Ya, Hapus", key=f"konfirm_hapus_{row['ID']}", type="primary", use_container_width=True):
                            data_koleksi = data_koleksi[data_koleksi['ID'] != row['ID']]
                            if simpan_data(data_koleksi):
                                st.success(f"{row['Nama Figure']} berhasil dihapus!")
                                st.session_state.konfirmasi_hapus = None
                                st.rerun()
                    with kol_h2:
                        if st.button("Batal", key=f"batal_hapus_{row['ID']}", use_container_width=True):
                            st.session_state.konfirmasi_hapus = None
                            st.rerun()
                
                st.markdown("---")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'> Manajemen Action Figure  | tugas Kelompok 4</div>",
    unsafe_allow_html=True
)
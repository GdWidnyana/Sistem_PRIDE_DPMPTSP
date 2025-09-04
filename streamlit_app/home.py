import streamlit as st

def home():
    # Menampilkan judul halaman
    st.markdown("<h1 style='text-align: center;'>Sistem PRIDE (Prediksi dan Analisa Data Investasi)</h1>", unsafe_allow_html=True)
    
    st.write("----------------------------------------------------------------")
    # Deskripsi singkat
    st.header("Deskripsi Sistem💻")
    st.write("""
        Sistem ini dirancang untuk membantu Dinas Penanaman Modal dalam menganalisis dan memprediksi data investasi. Dengan menggunakan sistem ini, Anda dapat:
        
        - **Menganalisis Data:** Memvisualisasikan data proyek yang terdaftar di OSS (Online Single Submission)
          untuk mendapatkan wawasan lebih dalam mengenai tren, distribusi, dan aspek penting lainnya.
        
        - **Memprediksi Data:** Menggunakan teknik prediksi untuk meramalkan tren investasi di masa depan dan membuat keputusan
          strategis yang lebih baik berdasarkan data historis.
          
        Sistem ini menyediakan beberapa fitur utama antara lain:

        1. **Menu Home:** Menampilkan deskripsi sistem dan cara penggunaannya.
           
        2. **Analisa Data:** Mengolah dan memvisualisasikan data proyek untuk mendapatkan gambaran yang jelas tentang
           distribusi dan tren data investasi.
        
        3. **Prediksi Data:** Menerapkan model prediktif untuk meramalkan tren jumlah investasi di masa depan.
        
        4. **Profil:** Melihat informasi profil pengembang sistem dan hak cipta produk.
        
        **❗Catatan Penting**: Pastikan Anda sudah melakukan login untuk mengakses fitur-fitur di atas.
    """)
    
    st.write("----------------------------------------------------------------")
    # Penjelasan tambahan jika diperlukan
    st.subheader("Cara Menggunakan Sistem🧑‍💻")
    st.write("""
        1. **Login:** Pertama, lakukan login dengan kredensial yang valid.
        2. **Pilih Halaman:** Setelah login, pilih halaman yang ingin Anda akses melalui menu sidebar.
        3. **Analisa dan Prediksi:** Gunakan fitur yang tersedia untuk menganalisis data dan membuat prediksi. Ikuti perintah yang diminta sistem untuk menggunakan fitur analisa data dan prediksi data. **Ketelitian dan Kecermatan** sangat dibutuhkan untuk menggunakan fitur tersebut secara maksimal.
        4. **Logout:** Setelah selesai menggunakan semua fitur, pastikan untuk logout dari sistem untuk menjaga keamanan akun Anda.
        5. **Panduan penggunaaan sistem** secara lengkap disajikan dalam guide book di link : https://bit.ly/GuideBook-Sistem-PRIDE
    """)
    
    # st.write("----------------------------------------------------------------")
    # Informasi kontak atau bantuan
    # st.subheader("Kontak dan Bantuan⚠️")
    # st.write("""
    #     Jika Anda memerlukan bantuan atau memiliki pertanyaan lebih lanjut, silakan hubungi **Pengembang Sistem** melalui 
    #    **[email 📩 : gedewidnyana430@gmail.com](mailto:@gedewidnyana430@gmail.com)**
    # """)

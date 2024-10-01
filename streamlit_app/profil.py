# profil.py
import streamlit as st

def profil():
    # Membuat judul dengan class CSS yang diatur
    st.markdown("<h1 style='text-align: center;'>Profil Pengembang Sistem PRIDE</h1>", unsafe_allow_html=True)
    # Menggunakan CSS untuk meratakan gambar di tengah
    st.markdown(
        """
        <style>
        .center {
            display: flex;
            justify-content: center;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    st.markdown('<div class="center">', unsafe_allow_html=True)
    st.image("resources/profil1.png", caption= "I Gede Widnyana")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown("""
    ### Detail Pengembang Sistem🧑‍💻
    Halo! Saya adalah pengembang **Sistem PRIDE**. Berikut adalah detail informasi tentang saya.

    - **Nama**: I Gede Widnyana
    - **Instansi** : Universitas Udayana
    - **Email**: gedewidnyana430@gmail.com
    - **LinkedIn**: https://www.linkedin.com/in/i-gede-widnyana
    - **GitHub**: https://github.com/GdWidnyana
    - **Keahlian**: Python, Machine Learning, Deep Learning, Data Visualization, dan Businnes Inteligence.
    - **Dokumen Hak Cipta (HKI) Sistem PRIDE** : https://bit.ly/HKI_IGedeWidnyana 

    Jika Anda memiliki pertanyaan atau ingin berdiskusi, jangan ragu untuk menghubungi saya melalui platform di atas.
    """)

    st.markdown("---")
    st.markdown("Terima kasih telah menggunakan sistem ini! 😊")

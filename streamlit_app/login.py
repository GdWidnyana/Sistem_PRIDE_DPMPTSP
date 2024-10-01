import streamlit as st
from utils import login_user

def login():
    st.markdown("<h1 style='text-align: center;'>Sistem PRIDE (Prediksi dan Analisa Data Investasi)</h1>", unsafe_allow_html=True)

    # Cek jika pengguna sudah login
    if 'loggedIn' in st.session_state and st.session_state['loggedIn']:
        st.success(f"Anda sudah login sebagai {st.session_state['username']}.")
        return  # Jika sudah login, keluar dari fungsi ini

    # Form login
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        # Memeriksa kredensial
        if login_user(username, password):
            st.session_state['loggedIn'] = True
            st.session_state['username'] = username
            
            # Gunakan try-except untuk menangani AttributeError
            try:
                st.experimental_rerun()  # Refresh the page setelah login
            except AttributeError:
                pass  # Abaikan kesalahan dan teruskan

        else:
            st.error("Username atau Password salah")

    # Center align the login button and increase size
    st.markdown("""
        <style>
            div.stButton > button:first-child {
                display: block;
                margin: 0 auto;
                padding: 10px 20px;  /* Increase padding for larger button */
                font-size: 18px;      /* Increase font size */
                border-radius: 10px;  /* Optional: rounded corners */
            }
        </style>""", unsafe_allow_html=True)

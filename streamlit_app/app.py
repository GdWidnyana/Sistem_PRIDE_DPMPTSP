import streamlit as st
from login import login
from home import home
from profil import profil
from analisa_data import analisa_data
from prediksi import prediksi

# Set page config di sini
st.set_page_config(page_title="Sistem Analisa dan Prediksi")

# Menampilkan logo di sidebar
st.sidebar.image("streamlit_app/resources/Logo_Badung.png", use_column_width=True)

# Menampilkan heading di sidebar dengan rata tengah dan tautan ke LinkedIn
# st.sidebar.markdown(
#     """
#     <div style="text-align: center;">
#         <h1>Sistem PRIDE</h1>
#         <h2><a href="https://www.linkedin.com/in/i-gede-widnyana/" target="_blank" style="text-decoration: none; color: inherit;">oleh I Gede Widnyana</a></h2>
#     </div>
#     """, 
#     unsafe_allow_html=True
# )

# Inisialisasi state sesi
if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False

if not st.session_state['loggedIn']:
    login()
else:
    st.sidebar.title("Menu")
    
    # Menampilkan sidebar hanya jika pengguna sudah login
    page = st.sidebar.selectbox("Select a page:", ["Home", "Analisa", "Prediksi", "Profil"])

    if page == "Home":
        home()
    elif page == "Analisa":
        analisa_data()
    elif page == "Prediksi":
        prediksi()
    # elif page == "Profil":
    #     profil()

    # Button untuk logout
    if st.sidebar.button("Logout"):
        st.session_state['loggedIn'] = False
        st.experimental_rerun()

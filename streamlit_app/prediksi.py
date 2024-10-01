import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from sklearn.preprocessing import StandardScaler
from io import BytesIO  # Untuk menyimpan file secara sementara

# Fungsi untuk memuat model dan scaler dari file pickle
def load_model_and_scaler(model_filename, scaler_filename):
    with open(model_filename, 'rb') as model_file:
        loaded_model = pickle.load(model_file)
    with open(scaler_filename, 'rb') as scaler_file:
        loaded_scaler = pickle.load(scaler_file)
    return loaded_model, loaded_scaler

# Fungsi untuk melakukan prediksi berdasarkan input pengguna
def predict_user_input(user_input, model_filename, scaler_filename):
    model, scaler = load_model_and_scaler(model_filename, scaler_filename)
    user_input_scaled = scaler.transform([user_input])
    prediction = model.predict(user_input_scaled)
    return prediction[0]

# Fungsi untuk mapping kategori prediksi investasi
def map_kategori_investasi(predictionRF):
    if predictionRF == 1:
        return "Tinggi"
    else:
        return "Rendah"

# Fungsi untuk mengubah dataframe menjadi file Excel yang bisa diunduh
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# Fungsi untuk menghasilkan deskripsi otomatis dari diagram pie
def generate_pie_description(category_counts):
    total = category_counts.sum()
    deskripsi = "Berdasarkan visualisasi hasil prediksi jumlah investasi dari **diagram pie** di atas:\n"
    
    for category, count in category_counts.items():
        persentase = (count / total) * 100
        deskripsi += f"- Jumlah Investasi dengan kategori **{category}** adalah **{count}** dengan persentase **({persentase:.2f}%)**\n"
    
    return deskripsi

def prediksi():
    # Memuat model yang sudah disimpan
    with open('streamlit_app/linear_regression_model.pkl', 'rb') as file:
        loaded_model = pickle.load(file)
        
    st.markdown("<h1 style='text-align: center;'>Menu Prediksi Investasi</h1>", unsafe_allow_html=True)
    
    # Menu dropdown untuk memilih jenis prediksi
    option = st.selectbox(
        'Pilih Jenis Prediksi:',
        ['Prediksi Jumlah Investasi Berdasarkan Tahun',
         'Prediksi Jumlah Investasi Berdasarkan Komponen']
    )

    if option == 'Prediksi Jumlah Investasi Berdasarkan Tahun':
        # Memuat model regresi linear
        model_filename = 'streamlit_app/linear_regression_model.pkl'

        data = pd.DataFrame({
            'Year': [2018, 2019, 2020, 2021, 2022, 2023],
            'Jumlah Investasi': [8233274390221, 20717720510244, 15666957301328, 16720571318394, 7947606550602, 120869283284370]
        })

        # Input dari pengguna untuk tahun prediksi
        year_input = st.number_input('Masukkan Tahun:', min_value=2024, max_value=2100, step=1)

        if st.button('Prediksi'):
            # Melakukan prediksi menggunakan model
            input_data = pd.DataFrame({'Year': [year_input]})
            prediction = loaded_model.predict(input_data)

            # Menambahkan hasil prediksi ke data historis
            data = data.append({'Year': year_input, 'Jumlah Investasi': prediction[0]}, ignore_index=True)

            st.write(f'Prediksi Jumlah Investasi **Tahun {year_input}** adalah **Rp {prediction[0]:,.2f}**')

            # Visualisasi tren jumlah investasi per tahun (termasuk prediksi)
            fig = px.line(data, x='Year', y='Jumlah Investasi', 
                          title='Tren Jumlah Investasi per Tahun',
                          markers=True, text='Jumlah Investasi')

            # Menampilkan angka di atas titik
            fig.update_traces(textposition='top center')

            # Format dan label sumbu
            fig.update_layout(
                xaxis_title='Tahun',
                yaxis_title='Jumlah Investasi',
                yaxis_tickformat=',',  # Format angka dengan koma
            )

            # Menampilkan grafik di Streamlit
            st.plotly_chart(fig)

    elif option == 'Prediksi Jumlah Investasi Berdasarkan Komponen':
        # Memuat model regresi linear dan scaler
        model_filename = 'streamlit_app/resources/linear_model.pkl'
        scaler_filename = 'streamlit_app/resources/scaler.pkl'
        modelRF_filename = 'streamlit_app/resources/random_forest_model.pkl'

        # Opsi untuk memilih input manual atau unggah file
        input_option = st.radio("Pilih Metode Input:", ('Input Manual', 'Unggah File Excel'))

        if input_option == 'Input Manual':
            # Input manual dari pengguna untuk fitur komponen
            st.write('Masukkan nilai untuk setiap komponen:')
            feature_columns = ['Mesin Peralatan', 'Mesin Peralatan Impor', 'Pembelian Pematangan Tanah', 'Bangunan Gedung', 'Modal Kerja',  'Lain Lain', 'TKI']
            user_input = []

            for feature in feature_columns:
                value = st.number_input(f'Masukkan nilai untuk {feature}:', min_value=0.0)
                user_input.append(value)

            if st.button('Prediksi'):
                # Prediksi jumlah investasi berdasarkan komponen
                prediction = predict_user_input(user_input, model_filename, scaler_filename)
                st.write(f'Prediksi Jumlah Investasi Berdasarkan Komponen: **Rp {prediction:,.2f}**')

                # Prediksi kategori jumlah investasi berdasarkan komponen
                predictionRF = predict_user_input(user_input, modelRF_filename, scaler_filename)
                kategori_investasi = map_kategori_investasi(predictionRF)
                st.write(f'Prediksi Kategori Jumlah Investasi Berdasarkan Komponen: **{kategori_investasi}**')
        
        elif input_option == 'Unggah File Excel':
            # Unggah file Excel
            uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx", "xls"])
            
            if uploaded_file is not None:
                # Membaca file Excel
                df = pd.read_excel(uploaded_file)
                st.write("Data yang diunggah:")
                st.write(df)

                # Pastikan kolom yang dibutuhkan ada
                required_columns = ['Mesin Peralatan', 'Mesin Peralatan Impor', 'Pembelian Pematangan Tanah', 'Bangunan Gedung', 'Modal Kerja', 'Lain Lain', 'TKI']
                if all(col in df.columns for col in required_columns):
                    # Mengambil hanya kolom yang diperlukan
                    feature_data = df[required_columns]

                    if st.button('Prediksi'):
                        # Melakukan prediksi untuk setiap baris data
                        predictions = []
                        categories = []
                        for i, row in feature_data.iterrows():
                            user_input = row.values.tolist()
                            pred = predict_user_input(user_input, model_filename, scaler_filename)
                            predRF = predict_user_input(user_input, modelRF_filename, scaler_filename)
                            predictions.append(pred)
                            categories.append(map_kategori_investasi(predRF))

                        # Menambahkan hasil prediksi ke dataframe
                        df['Prediksi Investasi'] = predictions
                        df['Kategori Investasi'] = categories

                        st.write("Hasil Prediksi:")
                        st.write(df)

                        # Menampilkan visualisasi pie chart
                        st.write("Visualisasi Rasio Investasi Kategori Tinggi dan Rendah:")
                        category_counts = df['Kategori Investasi'].value_counts()
                        fig_pie = px.pie(values=category_counts.values, names=category_counts.index,
                                         title='Rasio Investasi Kategori Tinggi dan Rendah',
                                         labels={'index': 'Kategori', 'values': 'Jumlah'})
                        st.plotly_chart(fig_pie)

                        # Deskripsi otomatis berdasarkan diagram pie
                        pie_description = generate_pie_description(category_counts)
                        st.write("**Analisis deskriptif hasil prediksi :**")
                        st.write(pie_description)

                        # Menyediakan opsi untuk mengunduh hasil prediksi
                        result_xlsx = to_excel(df)
                        st.download_button(label="Unduh Hasil Prediksi", data=result_xlsx, file_name="hasil_prediksi.xlsx", mime="application/vnd.ms-excel")
                else:
                    st.error(f"File harus mengandung kolom berikut: {', '.join(required_columns)}")

if __name__ == "__main__":
    prediksi()

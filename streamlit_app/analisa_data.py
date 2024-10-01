import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import io
import difflib

def load_data(uploaded_file):
    # Pastikan file yang diunggah adalah file Excel
    if not uploaded_file.name.endswith('.xlsx'):
        st.error("Format file tidak sesuai. Silakan unggah file Excel (.xlsx).")
        return None
    
    try:
        # Load data dari file Excel
        data = pd.read_excel(uploaded_file)
        
        # Konversi 'Tanggal Terbit Oss' menjadi datetime
        if 'Tanggal Terbit Oss' in data.columns:
            data['Tanggal Terbit Oss'] = pd.to_datetime(data['Tanggal Terbit Oss'], errors='coerce')
        else:
            st.error("Kolom 'Tanggal Terbit Oss' tidak ditemukan dalam file.")
            return None
        
        return data
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data: {e}")
        return None

def correct_column_names(df, correct_columns):
    """
    Mengganti nama kolom DataFrame dengan nama kolom yang benar dari daftar yang disediakan.
    """
    # Membuat mapping nama kolom yang benar
    column_mapping = {old: new for old, new in zip(df.columns, correct_columns)}

    # Mengganti nama kolom di DataFrame
    df.rename(columns=column_mapping, inplace=True)
    return df


def generate_insight(insight_type, **kwargs):
    if insight_type == "risk_distribution":
        return (f"Diagram Distribusi Resiko Proyek berdasarkan Jenis Proyek {kwargs['jenis_proyek']} "
                f"menunjukkan bahwa Resiko Proyek {kwargs['highest_risk']} merupakan jumlah resiko proyek tertinggi "
                f"dengan nilai {kwargs['highest_count']}. Jumlah yang terendah adalah risiko proyek dengan status "
                f"{kwargs['lowest_risk']} dengan jumlah {kwargs['lowest_count']}.")

    elif insight_type == "company_distribution":
        return (f"Persebaran perusahaan {kwargs['jenis_perusahaan']} menunjukkan "
                f"jumlah perusahaan tertinggi ada di Kecamatan {kwargs['highest_kecamatan']} dengan total {kwargs['highest_count']}. "
                f"Sedangkan kecamatan dengan jumlah perusahaan terendah adalah {kwargs['lowest_kecamatan']} "
                f"dengan jumlah {kwargs['lowest_count']}.")
    
    # Insight untuk Persebaran Jenis Perusahaan berdasarkan Kelurahan
    elif insight_type == "kelurahan_distribution":
        return (f"Persebaran perusahaan {kwargs['jenis_perusahaan']} di tahun {kwargs['tahun_kelurahan']} menunjukkan bahwa "
                f"Kelurahan {kwargs['highest_kelurahan']} memiliki jumlah perusahaan tertinggi dengan total {kwargs['highest_count']}. "
                f"Sedangkan kelurahan dengan jumlah perusahaan terendah adalah {kwargs['lowest_kelurahan']} "
                f"dengan jumlah {kwargs['lowest_count']}.")

    # Insight untuk Pergerakan Jumlah Investasi
    elif insight_type == "investment_movement":
        return (f"Pada tahun {kwargs['tahun_investasi']}, Kecamatan {kwargs['kecamatan']} mengalami pergerakan investasi "
                f"dengan jumlah investasi tertinggi pada bulan {kwargs['highest_month']} sebesar {kwargs['highest_investment']:,}. "
                f"Jumlah investasi terendah terjadi pada bulan {kwargs['lowest_month']} dengan total {kwargs['lowest_investment']:,}. "
                f"Kenaikan terbesar terjadi pada bulan {kwargs['largest_increase_month']} dengan peningkatan sebesar "
                f"{kwargs['largest_increase_value']:,}, sedangkan penurunan terbesar terjadi pada bulan "
                f"{kwargs['largest_decrease_month']} dengan penurunan sebesar {kwargs['largest_decrease_value']:,}.")

    # Insight untuk Uraian Skala Usaha dan Jumlah Investasi
    elif insight_type == "skala_usaha_investment":
        return (f"Jumlah investasi terbesar diperoleh pada skala usaha '{kwargs['highest_skala_usaha']}' "
                f"dengan total investasi sebesar {kwargs['highest_investment']:,}. "
                f"Sedangkan jumlah investasi terendah terjadi pada skala usaha '{kwargs['lowest_skala_usaha']}' "
                f"dengan total investasi sebesar {kwargs['lowest_investment']:,}.")

    # Insight untuk Persebaran KLBI berdasarkan Sektor Pembina
    elif insight_type == "klbi_distribution":
        return (f"Persebaran KLBI dalam sektor '{kwargs['sektor_pembina']}' menunjukkan bahwa KLBI '{kwargs['highest_klbi']}' "
                f"memiliki jumlah terbanyak dengan total {kwargs['highest_count']}. "
                f"Sebaliknya, KLBI dengan jumlah paling sedikit adalah '{kwargs['lowest_klbi']}' "
                f"dengan jumlah {kwargs['lowest_count']}.")

    #Insight untuk 10 KLBI Teratas
    elif insight_type == "top_10_klbi":
        top_klbi_insights = "\n".join([f"{i+1}. {row['Judul Kbli']} = {row['Count']}" for i, row in kwargs['top_10'].iterrows()])
        return (f"10 KLBI teratas berdasarkan sektor pembina '{kwargs['sektor_pembina']}' adalah:\n{top_klbi_insights}")

    # Insight untuk 10 KLBI Terbawah dengan format daftar bernomor
    elif insight_type == "bottom_10_klbi":
        j=0
        bottom_klbi_insights = "\n".join([f"{j+1}. {row['Judul Kbli']} = {row['Count']}" for i, row in kwargs['bottom_10'].iterrows()])
        return (f"10 KLBI terbawah berdasarkan sektor pembina '{kwargs['sektor_pembina']}' adalah:\n{bottom_klbi_insights}")

    elif insight_type == "investment_distribution":
        return (f"Distribusi {kwargs['jenis_perusahaan']} berdasarkan kecamatan menunjukkan bahwa kecamatan dengan {kwargs['metric_type']} "
                f"tertinggi adalah {kwargs['highest_kecamatan']} dengan nilai {kwargs['highest_value']:,}. "
                f"Sebaliknya, kecamatan dengan {kwargs['metric_type']} terendah adalah {kwargs['lowest_kecamatan']} "
                f"dengan nilai {kwargs['lowest_value']:,}.")
    
    elif insight_type == "investment_summary":
        return (f"Pada analisis Perusahaan {kwargs['jenis_perusahaan']}, distribusi {kwargs['metric_type']} menunjukkan bahwa:\n"
                f"- Kecamatan dengan {kwargs['metric_type']} tertinggi adalah {kwargs['highest_kecamatan']} dengan nilai {kwargs['highest_value']:,}.\n"
                f"- Kecamatan dengan {kwargs['metric_type']} terendah adalah {kwargs['lowest_kecamatan']} dengan nilai {kwargs['lowest_value']:,}.\n"
                f"- Rentang nilai {kwargs['metric_type']} adalah dari {kwargs['range_min']:,} hingga {kwargs['range_max']:,}.")

def analisa_data():
    st.markdown("<h1 style='text-align: center;'>Analisa Data Investasi</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
    **Petunjuk:** Silahkan unggah file Excel (.xlsx) yang sesuai dengan ketentuan sistem di sini. 
    Format file yang diterima adalah Excel (.xlsx). Pastikan kolom pada file Anda sesuai dengan yang diminta oleh sistem, 
    yaitu sebagai berikut:
    """)
    
    correct_columns = [
        "No.", "Id Proyek", "Uraian_Jenis_Proyek", "Nib", "Nama Perusahaan", 
        "Tanggal Terbit Oss", "Uraian Status Penanaman Modal", "Uraian Jenis Perusahaan", 
        "Uraian Risiko Proyek", "nama_proyek", "Uraian Skala Usaha", "Alamat Usaha", 
        "Kab Kota Usaha", "kecamatan_usaha", "kelurahan_usaha", "longitude", 
        "latitude", "Kbli", "Judul Kbli", "KL/Sektor Pembina", "Nama User", 
        "Nomor Identitas User", "Email", "Nomor Telp", "luas_tanah", 
        "satuan_tanah", "Mesin Peralatan", "Mesin Peralatan Impor", 
        "Pembelian Pematangan Tanah", "Bangunan Gedung", "Modal Kerja", 
        "Lain Lain", "Jumlah Investasi", "TKI"
    ]

    formatted_columns = "\n".join([f"- **{col}**" for col in correct_columns])
    st.markdown(formatted_columns)
    
    uploaded_file = st.file_uploader("Upload file Excel (.xlsx)", type=["xlsx"])

    if uploaded_file:
        try:
            # Membaca file yang diupload
            data = pd.read_excel(uploaded_file)
            
            # Menyesuaikan nama kolom
            adjusted_data = correct_column_names(data, correct_columns)
            
            # Cek dan konversi kolom 'Tanggal Terbit Oss' ke tipe datetime
            if 'Tanggal Terbit Oss' in adjusted_data.columns:
                adjusted_data['Tanggal Terbit Oss'] = pd.to_datetime(adjusted_data['Tanggal Terbit Oss'], errors='coerce')
                
                # Tambahkan kolom 'Bulan Terbit' jika kolom 'Tanggal Terbit Oss' valid
                if pd.api.types.is_datetime64_any_dtype(adjusted_data['Tanggal Terbit Oss']):
                    adjusted_data['Bulan Terbit'] = adjusted_data['Tanggal Terbit Oss'].dt.to_period('M')
                else:
                    st.warning("Kolom 'Tanggal Terbit Oss' tidak berisi data datetime yang valid.")
            else:
                st.warning("Kolom 'Tanggal Terbit Oss' tidak ditemukan dalam data.")
            
            # Menampilkan preview data yang sudah disesuaikan
            st.write("Berikut adalah preview data yang sudah disesuaikan:")
            st.dataframe(adjusted_data.head())
            
            # Menyimpan DataFrame yang sudah diperbaiki ke file Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                adjusted_data.to_excel(writer, index=False, sheet_name='Data Disesuaikan')
                writer.save()
            
            output.seek(0)
            
            st.markdown("### Unduh file yang sudah disesuaikan dalam format Excel:")
            st.download_button(
                label="Download Excel",
                data=output,
                file_name='adjusted_file.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            st.success("File Anda sudah disesuaikan dengan format yang diminta.")
            # Proses selanjutnya jika file sesuai (misalnya analisis data)
            # ...

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {e}")


        # Pembatas garis
        st.markdown("---")
        # Judul halaman
        st.markdown("## Analisis Sektor Terbanyak di Setiap Kecamatan")

        # Filter berdasarkan tahun dan kecamatan
        st.markdown("### Filter Data")

        selected_kecamatan = st.selectbox("Pilih Kecamatan", data['kecamatan_usaha'].unique())

        # Menambahkan opsi "Keseluruhan Tahun" di selectbox
        years = sorted(data['Tanggal Terbit Oss'].dt.year.unique())  # Mengambil daftar tahun yang unik
        years.insert(0, "Keseluruhan Tahun")  # Menambahkan opsi "Keseluruhan Tahun" sebagai pilihan pertama

        selected_year = st.selectbox("Pilih Tahun", years)

        # Filter data berdasarkan input user
        if selected_year == "Keseluruhan Tahun":
            filtered_data = data[data['kecamatan_usaha'] == selected_kecamatan]
        else:
            filtered_data = data[(data['kecamatan_usaha'] == selected_kecamatan) & 
                                (data['Tanggal Terbit Oss'].dt.year == selected_year)]      
        # selected_kecamatan = st.selectbox("Pilih Kecamatan", data['kecamatan_usaha'].unique())
        # selected_year = st.selectbox(
        #     "Pilih Tahun", 
        #     sorted(data['Tanggal Terbit Oss'].dt.year.unique()),  # Mengambil tahun unik dari data dan mengurutkannya
        # )

        # # Filter data berdasarkan input user
        # filtered_data = data[(data['kecamatan_usaha'] == selected_kecamatan) & 
        #                     (data['Tanggal Terbit Oss'].dt.year == selected_year)]

        # ----------------------- Diagram Batang Judul Kbli -----------------------
        st.markdown("### Diagram Batang Berdasarkan Judul Kbli")

        # Hitung jumlah proyek berdasarkan Judul Kbli di kecamatan terpilih pada tahun terpilih
        klbi_count = filtered_data.groupby('Judul Kbli').size().reset_index(name='Jumlah')

        # Sort data dari yang terbesar ke terkecil
        klbi_count = klbi_count.sort_values(by='Jumlah', ascending=False)

        # Jika data kosong, berikan pesan
        if klbi_count.empty:
            st.write("Tidak ada data untuk kecamatan dan tahun yang dipilih.")
        else:
            # Membuat diagram batang untuk Judul Kbli
            fig_klbi = px.bar(klbi_count, x='Judul Kbli', y='Jumlah', 
                            title=f"Judul Kbli Terbanyak di Kecamatan {selected_kecamatan} pada Tahun {selected_year if selected_year != 'Keseluruhan Tahun' else 'Keseluruhan Tahun'}",
                            labels={'Judul Kbli': 'Judul Kbli', 'Jumlah': 'Jumlah Proyek'},
                            text='Jumlah')

            # Update layout diagram batang
            fig_klbi.update_layout(xaxis_title='Judul Kbli', yaxis_title='Jumlah Proyek', 
                                xaxis_tickangle=-45)  # Rotasi label x-axis untuk lebih mudah dibaca
                      
            # Tampilkan diagram batang Judul Kbli
            st.plotly_chart(fig_klbi)

#        ----------------------- Diagram Batang Sektor Pembina -----------------------
        st.markdown("### Diagram Batang Berdasarkan Sektor Pembina")

        # Hitung jumlah proyek berdasarkan Sektor Pembina di kecamatan terpilih pada tahun terpilih
        sektor_count = filtered_data.groupby('KL/Sektor Pembina').size().reset_index(name='Jumlah')

        # Sort data dari yang terbesar ke terkecil
        sektor_count = sektor_count.sort_values(by='Jumlah', ascending=False)

        # Jika data kosong, berikan pesan
        if sektor_count.empty:
            st.write("Tidak ada data untuk kecamatan dan tahun yang dipilih.")
        else:
            # Membuat diagram batang untuk Sektor Pembina
            fig_sektor = px.bar(sektor_count, x='KL/Sektor Pembina', y='Jumlah', 
                                title=f"Sektor Pembina Terbanyak di Kecamatan {selected_kecamatan} pada Tahun {selected_year if selected_year != 'Keseluruhan Tahun' else 'Keseluruhan Tahun'}",
                                labels={'KL/Sektor Pembina': 'Sektor Pembina', 'Jumlah': 'Jumlah Proyek'},
                                text='Jumlah')

            # Update layout diagram batang
            fig_sektor.update_layout(xaxis_title='Sektor Pembina', yaxis_title='Jumlah Proyek', 
                                    xaxis_tickangle=-45)  # Rotasi label x-axis untuk lebih mudah dibaca
                      
            # Tampilkan diagram batang Sektor Pembina
            st.plotly_chart(fig_sektor)

        # ----------------------- Generate Insights -----------------------
        if not klbi_count.empty and not sektor_count.empty:
            # Generate insights: Finding the sector with highest and lowest project counts (Judul Kbli)
            highest_klbi = klbi_count.loc[klbi_count['Jumlah'].idxmax()]
            lowest_klbi = klbi_count.loc[klbi_count['Jumlah'].idxmin()]

            # Generate insights: Finding the sector with highest and lowest project counts (Sektor Pembina)
            highest_sektor = sektor_count.loc[sektor_count['Jumlah'].idxmax()]
            lowest_sektor = sektor_count.loc[sektor_count['Jumlah'].idxmin()]

            # Total projects in the selected kecamatan and year
            total_projects_klbi = klbi_count['Jumlah'].sum()
            total_projects_sektor = sektor_count['Jumlah'].sum()

            # Generate insights
            insight_sector = (
                f"Pada tahun **{selected_year if selected_year != 'Keseluruhan Tahun' else 'Keseluruhan Tahun'}**, di Kecamatan **{selected_kecamatan}**:\n"
                f"- **Judul Kbli dengan jumlah proyek terbanyak** adalah {highest_klbi['Judul Kbli']} "
                f"dengan total proyek sebanyak {highest_klbi['Jumlah']}.\n"
                f"- **Judul Kbli dengan jumlah proyek paling sedikit** adalah {lowest_klbi['Judul Kbli']} "
                f"dengan total proyek sebanyak {lowest_klbi['Jumlah']}.\n"
                f"- **Sektor Pembina dengan jumlah proyek terbanyak** adalah {highest_sektor['KL/Sektor Pembina']} "
                f"dengan total proyek sebanyak {highest_sektor['Jumlah']}.\n"
                f"- **Sektor Pembina dengan jumlah proyek paling sedikit** adalah {lowest_sektor['KL/Sektor Pembina']} "
                f"dengan total proyek sebanyak {lowest_sektor['Jumlah']}.\n"
                f"- Total jumlah proyek di kecamatan **{selected_kecamatan}** untuk Judul Kbli adalah **{total_projects_klbi}** proyek, "
                f"dan untuk Sektor Pembina adalah **{total_projects_sektor}** proyek."
            )

            # Tampilkan deskripsi
            st.write(insight_sector)
            
            
        # Judul halaman
        st.markdown("## Analisis Jumlah Investasi di Setiap Kecamatan")

        # Filter berdasarkan tahun dan kecamatan
        st.markdown("### Filter Data")
        selected_kecamatan = st.selectbox("Pilih Kecamatan", data['kecamatan_usaha'].unique(), key='selectbox_kecamatan')

        # Menambahkan opsi "Keseluruhan Tahun" di selectbox
        years = sorted(data['Tanggal Terbit Oss'].dt.year.unique())  # Mengambil daftar tahun yang unik
        years.insert(0, "Keseluruhan Tahun")  # Menambahkan opsi "Keseluruhan Tahun" sebagai pilihan pertama

        selected_year = st.selectbox("Pilih Tahun", years, key='selectbox_tahun')  # Selectbox untuk memilih tahun atau keseluruhan tahun

        # Filter data berdasarkan input user
        if selected_year == "Keseluruhan Tahun":
            filtered_data = data[data['kecamatan_usaha'] == selected_kecamatan]
        else:
            filtered_data = data[(data['kecamatan_usaha'] == selected_kecamatan) & 
                                (data['Tanggal Terbit Oss'].dt.year == selected_year)]

# ----------------------- Diagram Batang Jumlah Investasi Berdasarkan Judul Kbli -----------------------
        st.markdown("### Diagram Jumlah Investasi Berdasarkan Judul Kbli")

# Hitung total investasi berdasarkan Judul Kbli di kecamatan terpilih pada tahun terpilih
        klbi_investment = filtered_data.groupby('Judul Kbli')['Jumlah Investasi'].sum().reset_index()

# Sort data dari yang terbesar ke terkecil
        klbi_investment = klbi_investment.sort_values(by='Jumlah Investasi', ascending=False)

# Jika data kosong, berikan pesan
        if klbi_investment.empty:
            st.write("Tidak ada data investasi untuk kecamatan dan tahun yang dipilih.")
        else:
    # Membuat diagram batang untuk Judul Kbli
            fig_klbi_investment = px.bar(klbi_investment, x='Judul Kbli', y='Jumlah Investasi', 
                                        title=f"Jumlah Investasi Berdasarkan Judul Kbli di Kecamatan {selected_kecamatan} pada Tahun {selected_year if selected_year != 'Keseluruhan Tahun' else 'Keseluruhan Tahun'}",
                                        labels={'Judul Kbli': 'Judul Kbli', 'Jumlah Investasi': 'Jumlah Investasi (Rp)'},
                                        text='Jumlah Investasi')

    # Update layout diagram batang
            fig_klbi_investment.update_layout(xaxis_title='Judul Kbli', yaxis_title='Jumlah Investasi (Rp)', 
                                            xaxis_tickangle=-45)  # Rotasi label x-axis untuk lebih mudah dibaca
                      
    # Tampilkan diagram batang Judul Kbli
            st.plotly_chart(fig_klbi_investment)

# ----------------------- Diagram Batang Jumlah Investasi Berdasarkan Sektor Pembina -----------------------
        st.markdown("### Diagram Jumlah Investasi Berdasarkan Sektor Pembina")

# Hitung total investasi berdasarkan Sektor Pembina di kecamatan terpilih pada tahun terpilih
        sektor_investment = filtered_data.groupby('KL/Sektor Pembina')['Jumlah Investasi'].sum().reset_index()

# Sort data dari yang terbesar ke terkecil
        sektor_investment = sektor_investment.sort_values(by='Jumlah Investasi', ascending=False)

# Jika data kosong, berikan pesan
        if sektor_investment.empty:
            st.write("Tidak ada data investasi untuk kecamatan dan tahun yang dipilih.")
        else:
    # Membuat diagram batang untuk Sektor Pembina
            fig_sektor_investment = px.bar(sektor_investment, x='KL/Sektor Pembina', y='Jumlah Investasi', 
                                        title=f"Jumlah Investasi Berdasarkan Sektor Pembina di Kecamatan {selected_kecamatan} pada Tahun {selected_year if selected_year != 'Keseluruhan Tahun' else 'Keseluruhan Tahun'}",
                                        labels={'KL/Sektor Pembina': 'Sektor Pembina', 'Jumlah Investasi': 'Jumlah Investasi (Rp)'},
                                        text='Jumlah Investasi')

    # Update layout diagram batang
            fig_sektor_investment.update_layout(xaxis_title='Sektor Pembina', yaxis_title='Jumlah Investasi (Rp)', 
                                                xaxis_tickangle=-45)  # Rotasi label x-axis untuk lebih mudah dibaca
                      
    # Tampilkan diagram batang Sektor Pembina
            st.plotly_chart(fig_sektor_investment)

# ----------------------- Generate Insights -----------------------
        if not klbi_investment.empty and not sektor_investment.empty:
            # Generate insights: Finding the sector with highest and lowest investments (Judul Kbli)
            highest_klbi_investment = klbi_investment.loc[klbi_investment['Jumlah Investasi'].idxmax()]
            lowest_klbi_investment = klbi_investment.loc[klbi_investment['Jumlah Investasi'].idxmin()]

            # Generate insights: Finding the sector with highest and lowest investments (Sektor Pembina)
            highest_sektor_investment = sektor_investment.loc[sektor_investment['Jumlah Investasi'].idxmax()]
            lowest_sektor_investment = sektor_investment.loc[sektor_investment['Jumlah Investasi'].idxmin()]

    # Total investments in the selected kecamatan and year
            total_investment_klbi = klbi_investment['Jumlah Investasi'].sum()
            total_investment_sektor = sektor_investment['Jumlah Investasi'].sum()

    # Generate insights
            insight_investment = (
                f"Pada tahun **{selected_year if selected_year != 'Keseluruhan Tahun' else 'Keseluruhan Tahun'}**, di Kecamatan **{selected_kecamatan}**:\n"
                f"- **Judul Kbli dengan total investasi terbesar** adalah {highest_klbi_investment['Judul Kbli']} "
                f"dengan total investasi sebesar Rp {highest_klbi_investment['Jumlah Investasi']:,}.\n"
                f"- **Judul Kbli dengan total investasi terkecil** adalah {lowest_klbi_investment['Judul Kbli']} "
                f"dengan total investasi sebesar Rp {lowest_klbi_investment['Jumlah Investasi']:,}.\n"
                f"- **Sektor Pembina dengan total investasi terbesar** adalah {highest_sektor_investment['KL/Sektor Pembina']} "
                f"dengan total investasi sebesar Rp {highest_sektor_investment['Jumlah Investasi']:,}.\n"
                f"- **Sektor Pembina dengan total investasi terkecil** adalah {lowest_sektor_investment['KL/Sektor Pembina']} "
                f"dengan total investasi sebesar Rp {lowest_sektor_investment['Jumlah Investasi']:,}.\n"
                f"- Total investasi di kecamatan **{selected_kecamatan}** untuk Judul Kbli adalah Rp **{total_investment_klbi:,}**, "
                f"dan untuk Sektor Pembina adalah Rp **{total_investment_sektor:,}**."
            )

            # Tampilkan deskripsi
            st.write(insight_investment)
            
        # Judul halaman
        st.markdown("## Analisis Investasi dan Sektor Terbanyak Berdasarkan Tahun")  
        
        # Ambil data tahun unik dan tambahkan opsi "Keseluruhan Tahun"
        years = sorted(data['Tanggal Terbit Oss'].dt.year.unique())

        # Membuat selectbox untuk memilih tahun
        selected_year = st.selectbox("Pilih Tahun", years)

        # Filter data berdasarkan tahun yang dipilih
        filtered_data = data[data['Tanggal Terbit Oss'].dt.year == selected_year]
        
        # Jika tidak ada data untuk tahun yang dipilih
        if filtered_data.empty:
            st.write(f"Tidak ada data untuk tahun {selected_year}.")
        else:
            # ------------------ Analisis 1: Kecamatan dengan Investasi Terbesar -------------------
            # Hitung total investasi berdasarkan kecamatan
            kecamatan_investment = filtered_data.groupby('kecamatan_usaha')['Jumlah Investasi'].sum().reset_index()

            # Temukan kecamatan dengan jumlah investasi tertinggi
            top_kecamatan = kecamatan_investment.loc[kecamatan_investment['Jumlah Investasi'].idxmax()]

            # ------------------ Filter Data Berdasarkan top_kecamatan -------------------
            #        Filter data untuk kecamatan dengan investasi terbesar
            filtered_top_kecamatan = filtered_data[filtered_data['kecamatan_usaha'] == top_kecamatan['kecamatan_usaha']]

            # ------------------ Analisis 2: Sektor dengan Proyek Terbanyak di top_kecamatan -------------------
            # Hitung jumlah proyek berdasarkan sektor (KL/Sektor Pembina) untuk kecamatan dengan investasi terbesar
            sektor_proyek_count = filtered_top_kecamatan.groupby('KL/Sektor Pembina').size().reset_index(name='Jumlah Proyek')

            # ------------------ Analisis 3: Sektor dengan Investasi Terbesar di top_kecamatan -------------------
            # Hitung total investasi berdasarkan sektor (KL/Sektor Pembina) untuk kecamatan dengan investasi terbesar
            sektor_investment = filtered_top_kecamatan.groupby('KL/Sektor Pembina')['Jumlah Investasi'].sum().reset_index()

            # ------------------ Visualisasi -------------------
            # Diagram batang kecamatan dengan jumlah investasi terbesar
            kecamatan_investment_sorted = kecamatan_investment.sort_values(by='Jumlah Investasi', ascending=False)
            sektor_proyek_count_sorted = sektor_proyek_count.sort_values(by='Jumlah Proyek', ascending=False)
            sektor_investment_sorted = sektor_investment.sort_values(by='Jumlah Investasi', ascending=False)
            
            fig_kecamatan = px.bar(kecamatan_investment_sorted, x='kecamatan_usaha', y='Jumlah Investasi', 
                                title=f"Jumlah Investasi di Setiap Kecamatan pada Tahun {selected_year}",
                                labels={'kecamatan_usaha': 'Kecamatan', 'Jumlah Investasi': 'Jumlah Investasi (Rp)'}, 
                                text='Jumlah Investasi')
            st.plotly_chart(fig_kecamatan)
            
            # Diagram batang sektor dengan proyek terbanyak berdasarkan top_kecamatan
            fig_sektor_proyek = px.bar(sektor_proyek_count_sorted, x='KL/Sektor Pembina', y='Jumlah Proyek', 
                                    title=f"Sektor dengan Proyek Terbanyak di Kecamatan Tertinggi yakni Kecamatan {top_kecamatan['kecamatan_usaha']} pada Tahun {selected_year}",
                                    labels={'KL/Sektor Pembina': 'Sektor Pembina', 'Jumlah Proyek': 'Jumlah Proyek'}, 
                                    text='Jumlah Proyek')

            # Tampilkan visualisasi proyek terbanyak
            st.plotly_chart(fig_sektor_proyek)

            # ------------------ Visualisasi: Sektor dengan Investasi Terbesar di top_kecamatan -------------------
            # Diagram batang sektor dengan investasi terbesar berdasarkan top_kecamatan
            fig_sektor_investment = px.bar(sektor_investment_sorted, x='KL/Sektor Pembina', y='Jumlah Investasi', 
                                        title=f"Sektor dengan Investasi Terbesar di Kecamatan Tertinggi yakni Kecamatan {top_kecamatan['kecamatan_usaha']} pada Tahun {selected_year}",
                                        labels={'KL/Sektor Pembina': 'Sektor Pembina', 'Jumlah Investasi': 'Jumlah Investasi (Rp)'}, 
                                        text='Jumlah Investasi')

            # Tampilkan visualisasi investasi terbesar
            st.plotly_chart(fig_sektor_investment)

            # ------------------ Generate Insights -------------------
            top_sektor_proyek = sektor_proyek_count.loc[sektor_proyek_count['Jumlah Proyek'].idxmax()]  # Sektor dengan proyek terbanyak
            top_sektor_investment = sektor_investment.loc[sektor_investment['Jumlah Investasi'].idxmax()]  # Sektor dengan investasi terbesar

            insight_high = (
                f"- Pada tahun {selected_year}, kecamatan dengan investasi tertinggi adalah **{top_kecamatan['kecamatan_usaha']}** "
                f"dengan total investasi sebesar Rp {top_kecamatan['Jumlah Investasi']:,}.\n"
                f"- Sektor dengan proyek terbanyak di kecamatan ini adalah **{top_sektor_proyek['KL/Sektor Pembina']}** "
                f"dengan **{top_sektor_proyek['Jumlah Proyek']}** proyek.\n"
                f"- Sektor dengan total investasi terbesar adalah **{top_sektor_investment['KL/Sektor Pembina']}** "
                f"dengan total investasi sebesar Rp {top_sektor_investment['Jumlah Investasi']:,}."
            )
            # Tampilkan insight
            st.write(insight_high)
            
            # ------------------ Analisis 1: Kecamatan dengan Investasi Terendah -------------------
            # Hitung total investasi berdasarkan kecamatan
            kecamatan_investment = filtered_data.groupby('kecamatan_usaha')['Jumlah Investasi'].sum().reset_index()

            # Temukan kecamatan dengan jumlah investasi terendah
            lowest_kecamatan = kecamatan_investment.loc[kecamatan_investment['Jumlah Investasi'].idxmin()]

            # ------------------ Filter Data Berdasarkan lowest_kecamatan -------------------
            # Filter data untuk kecamatan dengan investasi terendah
            filtered_lowest_kecamatan = filtered_data[filtered_data['kecamatan_usaha'] == lowest_kecamatan['kecamatan_usaha']]

            # ------------------ Analisis 2: Sektor dengan Proyek Terbanyak di lowest_kecamatan -------------------
            # Hitung jumlah proyek berdasarkan sektor (KL/Sektor Pembina) untuk kecamatan dengan investasi terendah
            sektor_proyek_count_lowest = filtered_lowest_kecamatan.groupby('KL/Sektor Pembina').size().reset_index(name='Jumlah Proyek')

            # ------------------ Analisis 3: Sektor dengan Investasi Terendah di lowest_kecamatan -------------------
            # Hitung total investasi berdasarkan sektor (KL/Sektor Pembina) untuk kecamatan dengan investasi terendah
            sektor_investment_lowest = filtered_lowest_kecamatan.groupby('KL/Sektor Pembina')['Jumlah Investasi'].sum().reset_index()

            # ------------------ Visualisasi -------------------
            # Diagram batang kecamatan dengan jumlah investasi terendah
            kecamatan_investment_sorted_lowest = kecamatan_investment.sort_values(by='Jumlah Investasi', ascending=True)
            sektor_proyek_count_sorted_lowest = sektor_proyek_count_lowest.sort_values(by='Jumlah Proyek', ascending=False)
            sektor_investment_sorted_lowest = sektor_investment_lowest.sort_values(by='Jumlah Investasi', ascending=False)

            fig_lowest_kecamatan = px.bar(kecamatan_investment_sorted_lowest, x='kecamatan_usaha', y='Jumlah Investasi', 
                                        title=f"Jumlah Investasi di Setiap Kecamatan pada Tahun {selected_year}",
                                        labels={'kecamatan_usaha': 'Kecamatan', 'Jumlah Investasi': 'Jumlah Investasi (Rp)'}, 
                                        text='Jumlah Investasi')
            st.plotly_chart(fig_lowest_kecamatan)

            # Diagram batang sektor dengan proyek terbanyak berdasarkan lowest_kecamatan
            fig_sektor_proyek_lowest = px.bar(sektor_proyek_count_sorted_lowest, x='KL/Sektor Pembina', y='Jumlah Proyek', 
                                            title=f"Jumlah Proyek di Kecamatan Terendah yakni Kecamatan {lowest_kecamatan['kecamatan_usaha']} pada Tahun {selected_year}",
                                            labels={'KL/Sektor Pembina': 'Sektor Pembina', 'Jumlah Proyek': 'Jumlah Proyek'}, 
                                            text='Jumlah Proyek')
            st.plotly_chart(fig_sektor_proyek_lowest)

            # ------------------ Visualisasi: Sektor dengan Investasi Terendah di lowest_kecamatan -------------------
            # Diagram batang sektor dengan investasi terendah berdasarkan lowest_kecamatan
            fig_sektor_investment_lowest = px.bar(sektor_investment_sorted_lowest, x='KL/Sektor Pembina', y='Jumlah Investasi', 
                                                title=f"Sektor dengan Investasi Terendah di Kecamatan Terendah yakni Kecamatan {lowest_kecamatan['kecamatan_usaha']} pada Tahun {selected_year}",
                                                labels={'KL/Sektor Pembina': 'Sektor Pembina', 'Jumlah Investasi': 'Jumlah Investasi (Rp)'}, 
                                                text='Jumlah Investasi')
            st.plotly_chart(fig_sektor_investment_lowest)

            # ------------------ Generate Insights -------------------
            top_sektor_proyek_lowest = sektor_proyek_count_lowest.loc[sektor_proyek_count_lowest['Jumlah Proyek'].idxmax()]  # Sektor dengan proyek terbanyak
            top_sektor_investment_lowest = sektor_investment_lowest.loc[sektor_investment_lowest['Jumlah Investasi'].idxmax()]  # Sektor dengan investasi terendah

            insight_lowest = (
                f"- Pada tahun {selected_year}, kecamatan dengan investasi terendah adalah **{lowest_kecamatan['kecamatan_usaha']}** "
                f"dengan total investasi sebesar Rp {lowest_kecamatan['Jumlah Investasi']:,}.\n"
                f"- Sektor dengan proyek terbanyak di kecamatan ini adalah **{top_sektor_proyek_lowest['KL/Sektor Pembina']}** "
                f"dengan **{top_sektor_proyek_lowest['Jumlah Proyek']}** proyek.\n"
                f"- Sektor dengan total investasi terendah adalah **{top_sektor_investment_lowest['KL/Sektor Pembina']}** "
                f"dengan total investasi sebesar Rp {top_sektor_investment_lowest['Jumlah Investasi']:,}."
            )

            # Tampilkan insight
            st.write(insight_lowest)
        
        # Korelasi dan Insight 1: Uraian_Jenis_Proyek dan Uraian Risiko Proyek
        st.markdown("## Distribusi Resiko Proyek berdasarkan Jenis Proyek")
        jenis_proyek = st.selectbox("Pilih Jenis Proyek:", data['Uraian_Jenis_Proyek'].unique())
        filtered_data = data[data['Uraian_Jenis_Proyek'] == jenis_proyek]

        # Hitung frekuensi setiap 'Uraian Risiko Proyek'
        risk_counts = filtered_data['Uraian Risiko Proyek'].value_counts().reset_index()
        risk_counts.columns = ['Uraian Risiko Proyek', 'Count']
        risk_counts = risk_counts.sort_values(by='Count', ascending=False)

        # Buat histogram
        fig1 = px.bar(risk_counts, x='Uraian Risiko Proyek', y='Count', color='Uraian Risiko Proyek', 
                     title=f"Distribusi Resiko Proyek berdasarkan {jenis_proyek}",
                     text_auto=True)  # Menampilkan angka di atas batang
        fig1.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig1)
        
        # Generate dynamic insight
        highest_risk = risk_counts.iloc[0]['Uraian Risiko Proyek']
        highest_count = risk_counts.iloc[0]['Count']
        lowest_risk = risk_counts.iloc[-1]['Uraian Risiko Proyek']
        lowest_count = risk_counts.iloc[-1]['Count']

        insight_1 = generate_insight("risk_distribution", jenis_proyek=jenis_proyek, highest_risk=highest_risk, 
                                     highest_count=highest_count, lowest_risk=lowest_risk, lowest_count=lowest_count)
        st.write(insight_1)
        
        # Pembatas garis
        st.markdown("---")
        
        # Korelasi dan Insight 12: Distribusi Risiko Proyek berdasarkan Skala Usaha
        st.markdown("## Distribusi Risiko Proyek berdasarkan Skala Usaha")
        
        # Filter Uraian Skala Usaha
        skala_usaha = st.selectbox("Pilih Uraian Skala Usaha:", data['Uraian Skala Usaha'].unique(), key='skala_usaha_filter')

        # Filter data berdasarkan skala usaha yang dipilih
        filtered_data_skala = data[data['Uraian Skala Usaha'] == skala_usaha]

        # Hitung frekuensi setiap 'Uraian Risiko Proyek'
        risiko_proyek_counts = filtered_data_skala['Uraian Risiko Proyek'].value_counts().reset_index()
        risiko_proyek_counts.columns = ['Uraian Risiko Proyek', 'Count']
        risiko_proyek_counts = risiko_proyek_counts.sort_values(by='Count', ascending=False)

        # Buat histogram
        fig12 = px.bar(risiko_proyek_counts, x='Uraian Risiko Proyek', y='Count', color='Uraian Risiko Proyek', 
                    title=f"Distribusi Risiko Proyek berdasarkan Skala Usaha: {skala_usaha}",
                    text_auto=True)  # Menampilkan angka di atas batang
        fig12.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig12) 

        # Calculate peaks and troughs
        highest_risk = risiko_proyek_counts.iloc[0]
        lowest_risk = risiko_proyek_counts.iloc[-1]

        # Generate dynamic insight
        insight_12 = (
            f"Distribusi risiko proyek untuk skala usaha '{skala_usaha}' menunjukkan bahwa:\n"
            f"- **Risiko Proyek dengan frekuensi tertinggi** adalah '{highest_risk['Uraian Risiko Proyek']}' "
            f"yang muncul sebanyak {highest_risk['Count']:,} kali.\n"
            f"- **Risiko Proyek dengan frekuensi terendah** adalah '{lowest_risk['Uraian Risiko Proyek']}' "
            f"yang muncul sebanyak {lowest_risk['Count']:,} kali."
        )
        st.write(insight_12)                     
          
        # Pembatas garis
        st.markdown("---")
                                      
        # Korelasi dan Insight 2: Tanggal Terbit Oss dan Jumlah Investasi
        st.markdown("## Tren Investasi dari Waktu ke Waktu")

        # Grouping data by month and year
        data['Bulan Terbit'] = data['Tanggal Terbit Oss'].dt.to_period('M')
        data_grouped_by_month = data.groupby('Bulan Terbit')['Jumlah Investasi'].sum().reset_index()
        data_grouped_by_month['Bulan Terbit'] = data_grouped_by_month['Bulan Terbit'].dt.to_timestamp()

        # Select year
        selected_year = st.selectbox("Pilih Tahun:", data_grouped_by_month['Bulan Terbit'].dt.year.unique())
        filtered_by_year = data_grouped_by_month[data_grouped_by_month['Bulan Terbit'].dt.year == selected_year]

        # Create time series plot
        fig2 = px.line(filtered_by_year, x='Bulan Terbit', y='Jumlah Investasi', 
                    title="Tren Jumlah Investasi per Bulan",
                    text='Jumlah Investasi')  # Menampilkan angka di atas titik
        fig2.update_layout(
            yaxis_tickformat=',',  # Format angka dengan koma
            xaxis_title='Bulan Terbit',
            yaxis_title='Jumlah Investasi'
        )
        st.plotly_chart(fig2)

        # Calculate peaks and troughs for investment data
        filtered_by_year['Previous_Investment'] = filtered_by_year['Jumlah Investasi'].shift(1)
        filtered_by_year['Change'] = filtered_by_year['Jumlah Investasi'] - filtered_by_year['Previous_Investment']
    
        # Identifying highest and lowest investments
        highest_investment = filtered_by_year.loc[filtered_by_year['Jumlah Investasi'].idxmax()]
        lowest_investment = filtered_by_year.loc[filtered_by_year['Jumlah Investasi'].idxmin()]
    
        # Identifying largest increase and decrease in investment
        largest_increase_investment = filtered_by_year.loc[filtered_by_year['Change'].idxmax()]
        largest_decrease_investment = filtered_by_year.loc[filtered_by_year['Change'].idxmin()]

        # Generate insights
        insight_2 = (
            f"Pada tahun {selected_year}:\n"
            f"- **Bulan dengan jumlah investasi tertinggi** adalah {highest_investment['Bulan Terbit'].strftime('%Y-%m')} "
            f"dengan total investasi sebesar {highest_investment['Jumlah Investasi']:,}.\n"
            f"- **Bulan dengan jumlah investasi terendah** adalah {lowest_investment['Bulan Terbit'].strftime('%Y-%m')} "
            f"dengan total investasi sebesar {lowest_investment['Jumlah Investasi']:,}.\n"
            f"- **Peningkatan terbesar** dalam investasi terjadi dari bulan {largest_increase_investment['Bulan Terbit'] - pd.DateOffset(months=1):%Y-%m} "
            f"ke bulan {largest_increase_investment['Bulan Terbit'].strftime('%Y-%m')} dengan peningkatan sebesar {largest_increase_investment['Change']:,}.\n"
            f"- **Penurunan terbesar** dalam investasi terjadi dari bulan {largest_decrease_investment['Bulan Terbit'] - pd.DateOffset(months=1):%Y-%m} "
            f"ke bulan {largest_decrease_investment['Bulan Terbit'].strftime('%Y-%m')} dengan penurunan sebesar {largest_decrease_investment['Change']:,}."
        )
        st.write(insight_2)
        
        # Pembatas garis
        st.markdown("---")

        # Korelasi dan Insight 3: Uraian Status Penanaman Modal dan Modal Kerja
        st.markdown("## Komparasi antara Status Penanaman Modal dan Modal Kerja")
    
        # Grouping data by 'Uraian Status Penanaman Modal'
        grouped_modal = data.groupby('Uraian Status Penanaman Modal')['Modal Kerja'].sum().reset_index()
        grouped_modal = grouped_modal.sort_values(by='Modal Kerja', ascending=False)
    
        # Create donut chart
        fig3 = px.pie(grouped_modal, names='Uraian Status Penanaman Modal', values='Modal Kerja',
                    title="Total Modal Kerja berdasarkan Status Penanaman Modal",
                    labels={'Modal Kerja': 'Jumlah Modal Kerja'},
                    hole=0.3)  # Using hole to make a donut chart
        fig3.update_traces(textinfo='label+percent+value', 
                        textposition='outside',
                        pull=[0.1] * len(grouped_modal))  # Adding distance for each slice
        st.plotly_chart(fig3)

        # Generate dynamic insights
        highest_modal_status = grouped_modal.iloc[0]['Uraian Status Penanaman Modal']
        highest_modal = grouped_modal.iloc[0]['Modal Kerja']
        lowest_modal_status = grouped_modal.iloc[-1]['Uraian Status Penanaman Modal']
        lowest_modal = grouped_modal.iloc[-1]['Modal Kerja']
    
        # Calculate percentages
        total_modal = grouped_modal['Modal Kerja'].sum()
        grouped_modal['Percentage'] = (grouped_modal['Modal Kerja'] / total_modal) * 100
    
        # Generate insights
        insight_text = (
            f"**Insight Komparasi Status Penanaman Modal dan Modal Kerja:**\n\n"
            f"1. **Status Penanaman Modal dengan Modal Kerja Tertinggi:**\n"
            f"   - **{highest_modal_status}** dengan total modal kerja sebesar {highest_modal:,.0f} IDR, "
            f"yang berkontribusi {grouped_modal[grouped_modal['Uraian Status Penanaman Modal'] == highest_modal_status]['Percentage'].values[0]:.2f}% dari total modal kerja.\n\n"
            f"2. **Status Penanaman Modal dengan Modal Kerja Terendah:**\n"
            f"   - **{lowest_modal_status}** dengan total modal kerja sebesar {lowest_modal:,.0f} IDR, "
            f"yang berkontribusi {grouped_modal[grouped_modal['Uraian Status Penanaman Modal'] == lowest_modal_status]['Percentage'].values[0]:.2f}% dari total modal kerja.\n\n"
            f"3. **Distribusi Modal Kerja:**\n"
            f"   - Diagram Pie di atas menunjukkan bagaimana modal kerja didistribusikan di antara berbagai status penanaman modal. "
            f"Anda dapat melihat proporsi kontribusi masing-masing status penanaman modal terhadap total modal kerja secara visual."
        )
    
        st.markdown(insight_text)
        
        # # Insight dinamis
        # highest_modal_status = grouped_modal.iloc[0]['Uraian Status Penanaman Modal']
        # highest_modal = grouped_modal.iloc[0]['Modal Kerja']
        # lowest_modal_status = grouped_modal.iloc[-1]['Uraian Status Penanaman Modal']
        # lowest_modal = grouped_modal.iloc[-1]['Modal Kerja']

        # insight_3 = generate_insight("modal_pie", highest_modal_status=highest_modal_status, highest_modal=highest_modal,
        #                              lowest_modal_status=lowest_modal_status, lowest_modal=lowest_modal)
        # st.write(insight_3)

        # Pembatas garis
        st.markdown("---")
        
        # Korelasi dan Insight 4: Uraian Jenis Perusahaan dan Kecamatan Usaha
        st.markdown("## Persebaran Jenis Perusahaan berdasarkan Kecamatan")
        jenis_perusahaan = st.selectbox("Pilih Jenis Perusahaan:", data['Uraian Jenis Perusahaan'].unique())
        filtered_company = data[data['Uraian Jenis Perusahaan'] == jenis_perusahaan]

        # Hitung frekuensi perusahaan di setiap kecamatan
        kecamatan_counts = filtered_company['kecamatan_usaha'].value_counts().reset_index()
        kecamatan_counts.columns = ['Kecamatan Usaha', 'Count']
        kecamatan_counts = kecamatan_counts.sort_values(by='Count', ascending=False)

        # Buat histogram
        fig4 = px.bar(kecamatan_counts, x='Kecamatan Usaha', y='Count', color='Kecamatan Usaha', 
                     title=f"Persebaran {jenis_perusahaan} berdasarkan Kecamatan",
                     text_auto=True)  # Menampilkan angka di atas batang
        fig4.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig4)
        
        # Insight dinamis
        highest_kecamatan = kecamatan_counts.iloc[0]['Kecamatan Usaha']
        highest_count = kecamatan_counts.iloc[0]['Count']
        lowest_kecamatan = kecamatan_counts.iloc[-1]['Kecamatan Usaha']
        lowest_count = kecamatan_counts.iloc[-1]['Count']

        insight_4 = generate_insight("company_distribution", jenis_perusahaan=jenis_perusahaan, highest_kecamatan=highest_kecamatan, 
                                     highest_count=highest_count, lowest_kecamatan=lowest_kecamatan, 
                                     lowest_count=lowest_count)
        st.write(insight_4)

        # Pembatas garis
        st.markdown("---")
        
        # Korelasi dan Insight 5: Persebaran Jenis Perusahaan berdasarkan Kelurahan
        st.markdown("## Persebaran Jenis Perusahaan berdasarkan Kelurahan")
        jenis_perusahaan = st.selectbox("Pilih Jenis Perusahaan:", data['Uraian Jenis Perusahaan'].unique(), key='jenis_perusahaan_kelurahan')
        tahun_kelurahan = st.selectbox("Pilih Tahun:", data['Tanggal Terbit Oss'].dt.year.unique(), key='tahun_kelurahan')
        
        filtered_kelurahan = data[(data['Uraian Jenis Perusahaan'] == jenis_perusahaan) & (data['Tanggal Terbit Oss'].dt.year == tahun_kelurahan)]
        grouped_kelurahan = filtered_kelurahan.groupby('kelurahan_usaha').size().reset_index(name='Total')
        grouped_kelurahan = grouped_kelurahan.sort_values(by='Total', ascending=False)
        
        fig5 = px.bar(grouped_kelurahan, x='kelurahan_usaha', y='Total', color='kelurahan_usaha', 
                      title=f"Persebaran Jenis Perusahaan {jenis_perusahaan} berdasarkan Kelurahan pada tahun {tahun_kelurahan}",
                      labels={'Total': 'Total', 'kelurahan_usaha': 'Kelurahan'},
                      text_auto=True)  # Menampilkan angka di atas batang
        fig5.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig5)
        
        # Menghitung kelurahan dengan jumlah tertinggi dan terendah
        highest_kelurahan = grouped_kelurahan.iloc[0]['kelurahan_usaha']
        highest_count = grouped_kelurahan.iloc[0]['Total']
        lowest_kelurahan = grouped_kelurahan.iloc[-1]['kelurahan_usaha']
        lowest_count = grouped_kelurahan.iloc[-1]['Total']
        # Menghasilkan insight 5 menggunakan fungsi di atas
        insight_5 = generate_insight("kelurahan_distribution", jenis_perusahaan=jenis_perusahaan, highest_kelurahan=highest_kelurahan, 
                                    highest_count=highest_count, lowest_kelurahan=lowest_kelurahan, 
                                    lowest_count=lowest_count, tahun_kelurahan=tahun_kelurahan)
        st.write(insight_5)

        # Pembatas garis
        st.markdown("---")
        
                
        # Korelasi dan Insight 6: Pergerakan Jumlah Investasi pada Setiap Kecamatan
        st.markdown("## Pergerakan Jumlah Investasi pada Setiap Kecamatan")
        kecamatan = st.selectbox("Pilih Kecamatan:", data['kecamatan_usaha'].unique(), key='kecamatan_investasi')
        tahun_investasi = st.selectbox("Pilih Tahun:", data['Tanggal Terbit Oss'].dt.year.unique(), key='tahun_investasi')

        filtered_kecamatan = data[(data['kecamatan_usaha'] == kecamatan) & (data['Tanggal Terbit Oss'].dt.year == tahun_investasi)]
        filtered_kecamatan['Bulan Terbit'] = pd.to_datetime(filtered_kecamatan['Tanggal Terbit Oss']).dt.to_period('M')
        grouped_kecamatan = filtered_kecamatan.groupby('Bulan Terbit')['Jumlah Investasi'].sum().reset_index()
        grouped_kecamatan['Bulan Terbit'] = grouped_kecamatan['Bulan Terbit'].dt.to_timestamp()

        fig6 = px.line(grouped_kecamatan, x='Bulan Terbit', y='Jumlah Investasi', 
                       title=f"Pergerakan Jumlah Investasi pada Kecamatan {kecamatan} ({tahun_investasi})",
                       labels={'Bulan Terbit': 'Bulan', 'Jumlah Investasi': 'Total Investasi'},
                       text='Jumlah Investasi')  # Menampilkan angka di atas titik
        fig6.update_layout(
            yaxis_tickformat=',',  # Format angka dengan koma
            xaxis_title='Bulan Terbit',
            yaxis_title='Jumlah Investasi'
        )
        st.plotly_chart(fig6)
        
        # Menentukan bulan dengan investasi tertinggi dan terendah
        highest_month = grouped_kecamatan.loc[grouped_kecamatan['Jumlah Investasi'].idxmax()]['Bulan Terbit'].strftime('%B %Y')
        highest_investment = grouped_kecamatan['Jumlah Investasi'].max()
        lowest_month = grouped_kecamatan.loc[grouped_kecamatan['Jumlah Investasi'].idxmin()]['Bulan Terbit'].strftime('%B %Y')
        lowest_investment = grouped_kecamatan['Jumlah Investasi'].min()
        
        # Mengidentifikasi bulan dengan kenaikan dan penurunan terbesar
        grouped_kecamatan['Change'] = grouped_kecamatan['Jumlah Investasi'].diff()
        largest_increase_month = grouped_kecamatan.loc[grouped_kecamatan['Change'].idxmax()]['Bulan Terbit'].strftime('%B %Y')
        largest_increase_value = grouped_kecamatan['Change'].max()
        largest_decrease_month = grouped_kecamatan.loc[grouped_kecamatan['Change'].idxmin()]['Bulan Terbit'].strftime('%B %Y')
        largest_decrease_value = grouped_kecamatan['Change'].min()

        # Menghasilkan insight 6 menggunakan fungsi di atas
        insight_6 = generate_insight("investment_movement", kecamatan=kecamatan, tahun_investasi=tahun_investasi,
                                    highest_month=highest_month, highest_investment=highest_investment,
                                    lowest_month=lowest_month, lowest_investment=lowest_investment,
                                    largest_increase_month=largest_increase_month, largest_increase_value=largest_increase_value,
                                    largest_decrease_month=largest_decrease_month, largest_decrease_value=largest_decrease_value)
        st.write(insight_6)

        # Pembatas garis
        st.markdown("---")
        
        # Korelasi dan Insight 7: Uraian Skala Usaha dan Jumlah Investasi
        st.markdown("## Skala Usaha dan Jumlah Investasi")
        grouped_skala_usaha = data.groupby('Uraian Skala Usaha')['Jumlah Investasi'].sum().reset_index()
        grouped_skala_usaha = grouped_skala_usaha.sort_values(by='Jumlah Investasi', ascending=False)
        
        fig7 = px.bar(grouped_skala_usaha, x='Uraian Skala Usaha', y='Jumlah Investasi', color='Uraian Skala Usaha', 
                      title="Jumlah Investasi berdasarkan Skala Usaha",
                      labels={'Jumlah Investasi': 'Jumlah Investasi', 'Uraian Skala Usaha': 'Skala Usaha'},
                      text_auto=True)  # Menampilkan angka di atas batang
        fig7.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig7)
        
        # Menentukan skala usaha dengan investasi tertinggi dan terendah
        highest_skala_usaha = grouped_skala_usaha.iloc[0]['Uraian Skala Usaha']
        highest_investment = grouped_skala_usaha.iloc[0]['Jumlah Investasi']
        lowest_skala_usaha = grouped_skala_usaha.iloc[-1]['Uraian Skala Usaha']
        lowest_investment = grouped_skala_usaha.iloc[-1]['Jumlah Investasi']
        
        # Menghasilkan insight 7 menggunakan fungsi di atas
        insight_7 = generate_insight("skala_usaha_investment", highest_skala_usaha=highest_skala_usaha, highest_investment=highest_investment,
                                    lowest_skala_usaha=lowest_skala_usaha, lowest_investment=lowest_investment)
        st.write(insight_7)
        
        # Pembatas garis
        st.markdown("---")
              
        # Korelasi dan Insight 8: KLBI dan KL/Sektor Pembina
        st.markdown("## Persebaran KLBI berdasarkan Sektor Pembina")
        sektor_pembina = st.selectbox("Pilih Sektor Pembina:", data['KL/Sektor Pembina'].unique())
        filtered_klbi = data[data['KL/Sektor Pembina'] == sektor_pembina]

        # Hitung frekuensi KLBI
        klbi_counts = filtered_klbi['Judul Kbli'].value_counts().reset_index()
        klbi_counts.columns = ['Judul Kbli', 'Count']

        # Diagram Batang untuk Persebaran KLBI
        fig8 = px.bar(klbi_counts, x='Judul Kbli', y='Count', 
                    title=f"Persebaran KLBI berdasarkan {sektor_pembina}",
                    labels={'Count': 'Jumlah'},
                    text_auto=True)  # Menampilkan angka di atas batang
        st.plotly_chart(fig8)
        
        # Menentukan KLBI dengan jumlah tertinggi dan terendah
        highest_klbi = klbi_counts.iloc[0]['Judul Kbli']
        highest_count = klbi_counts.iloc[0]['Count']
        lowest_klbi = klbi_counts.iloc[-1]['Judul Kbli']
        lowest_count = klbi_counts.iloc[-1]['Count']
        insight_8 = generate_insight("klbi_distribution", sektor_pembina=sektor_pembina, highest_klbi=highest_klbi, highest_count=highest_count,
                                    lowest_klbi=lowest_klbi, lowest_count=lowest_count)
        st.write(insight_8)

        # Pembatas garis
        st.markdown("---")
        
        # Diagram Batang 10 Teratas
        st.markdown("## 10 KLBI Teratas berdasarkan Sektor Pembina")
        klbi_top_10 = klbi_counts.nlargest(10, 'Count')  # Mengambil 10 teratas
        fig9 = px.bar(klbi_top_10, x='Judul Kbli', y='Count', 
                      title=f"10 KLBI Teratas berdasarkan {sektor_pembina}",
                      labels={'Count': 'Jumlah'},
                      text_auto=True)  # Menampilkan angka di atas batang
        st.plotly_chart(fig9)
        
        # Menghasilkan insight 10 menggunakan fungsi di atas
        insight_10 = generate_insight("top_10_klbi", sektor_pembina=sektor_pembina, top_10=klbi_top_10)
        st.write(insight_10)

        # Pembatas garis
        st.markdown("---")
        
        
        # Diagram Batang 10 Terbawah
        st.markdown("## 10 KLBI Terbawah berdasarkan Sektor Pembina")
        klbi_bottom_10 = klbi_counts.nsmallest(10, 'Count')  # Mengambil 10 terbawah
        fig10 = px.bar(klbi_bottom_10, x='Judul Kbli', y='Count', 
                       title=f"10 KLBI Terbawah berdasarkan {sektor_pembina}",
                       labels={'Count': 'Jumlah'},
                       text_auto=True)  # Menampilkan angka di atas batang
        st.plotly_chart(fig10)
        
        # Menghasilkan insight untuk 10 KLBI terbawah
        insight_bottom_10 = generate_insight("bottom_10_klbi", sektor_pembina=sektor_pembina, bottom_10=klbi_bottom_10)
        st.write(insight_bottom_10)
        # Pembatas garis
        st.markdown("---")
        
        # Create a simple interactive map
        st.markdown("## Peta Interaktif Berdasarkan Kecamatan")
        
        # Assume you have columns 'latitude' and 'longitude' for the mapping
        if 'latitude' in data.columns and 'longitude' in data.columns:
            st.write("Klik pada titik peta untuk melihat detail.")
            
            # Adjust size scale for better visualization
            max_investment = data['Jumlah Investasi'].max()
            size_scale = 40  # Adjust this factor based on your needs
            
            fig_map = px.scatter_mapbox(
                data,
                lat='latitude',
                lon='longitude',
                color='Jumlah Investasi',
                size='Jumlah Investasi',
                size_max=size_scale,  # Maximum size of the marker
                hover_name='kecamatan_usaha',
                hover_data={'latitude': False, 'longitude': False},
                color_continuous_scale="Viridis",
                mapbox_style="carto-positron",
                zoom=9,
                center={"lat": -8.670458, "lon": 115.212629},  # Center on Badung, Bali
                opacity=0.6
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map)
        else:
            st.error("Data harus memiliki kolom 'latitude' dan 'longitude' untuk peta.")

        # Show details when a region is clicked
        st.markdown("## Detail Kecamatan")
        kecamatan_selected = st.selectbox("Pilih Kecamatan:", data['kecamatan_usaha'].unique())

        if kecamatan_selected:
            selected_data = data[data['kecamatan_usaha'] == kecamatan_selected]
            jumlah_perusahaan = selected_data['Uraian Jenis Perusahaan'].count()
            total_investasi = selected_data['Jumlah Investasi'].sum()

            # Display details
            st.markdown(f"**Jumlah Perusahaan:** {jumlah_perusahaan}")
            st.markdown(f"**Total Investasi:** {total_investasi:,}")
     

        # Pembatas garis
        st.markdown("---")
           
        # Korelasi dan Insight: Rata-rata, Median, dan Modus Jumlah Investasi berdasarkan Kecamatan

        st.markdown("## Analisis Jumlah Investasi berdasarkan Kecamatan")

        # Filter jenis perusahaan
        jenis_perusahaan = st.selectbox("Pilih Jenis Perusahaan:", data['Uraian Jenis Perusahaan'].unique(), key='jenis_perusahaan_investasi')

        # Filter data berdasarkan jenis perusahaan yang dipilih
        filtered_data = data[data['Uraian Jenis Perusahaan'] == jenis_perusahaan]

        # Grouping data by kecamatan
        grouped_kecamatan = filtered_data.groupby('kecamatan_usaha')['Jumlah Investasi'].agg(['mean', 'median', lambda x: stats.mode(x)[0][0]]).reset_index()
        grouped_kecamatan.columns = ['Kecamatan Usaha', 'Rata-rata', 'Median', 'Modus']

        # Pilihan ukuran pemusatan data
        pilihan_pemusatan = st.radio("Pilih jenis ukuran pemusatan data:", ['Rata-rata', 'Median', 'Modus'])

        # Pilih data yang sesuai dengan ukuran pemusatan yang dipilih
        if pilihan_pemusatan == 'Rata-rata':
            y_data = grouped_kecamatan['Rata-rata']
            metric_type = 'Rata-rata'
        elif pilihan_pemusatan == 'Median':
            y_data = grouped_kecamatan['Median']
            metric_type = 'Median'
        else:
            y_data = grouped_kecamatan['Modus']
            metric_type = 'Modus'

        # Sort data dari terbesar ke terkecil
        sorted_grouped_kecamatan = grouped_kecamatan.sort_values(by=pilihan_pemusatan, ascending=False)

        # Buat histogram sesuai dengan pilihan pemusatan
        fig11 = go.Figure()
        fig11.add_trace(go.Bar(x=sorted_grouped_kecamatan['Kecamatan Usaha'], y=sorted_grouped_kecamatan[pilihan_pemusatan], 
                            text=sorted_grouped_kecamatan[pilihan_pemusatan], textposition='auto',
                            name=f'Jumlah Investasi ({metric_type})'))

        fig11.update_layout(title=f"Distribusi Jumlah Investasi berdasarkan Kecamatan ({metric_type})",
                            xaxis_title='Kecamatan Usaha',
                            yaxis_title=f'Jumlah Investasi ({metric_type})')
        fig11.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig11)

        # Generate dynamic insight
        highest_kecamatan = sorted_grouped_kecamatan.iloc[0]['Kecamatan Usaha']
        highest_value = sorted_grouped_kecamatan.iloc[0][pilihan_pemusatan]
        lowest_kecamatan = sorted_grouped_kecamatan.iloc[-1]['Kecamatan Usaha']
        lowest_value = sorted_grouped_kecamatan.iloc[-1][pilihan_pemusatan]
        range_min = sorted_grouped_kecamatan[pilihan_pemusatan].min()
        range_max = sorted_grouped_kecamatan[pilihan_pemusatan].max()

        insight_11 = generate_insight("investment_summary", jenis_perusahaan=jenis_perusahaan, metric_type=metric_type,
                                   highest_kecamatan=highest_kecamatan, highest_value=highest_value,
                                   lowest_kecamatan=lowest_kecamatan, lowest_value=lowest_value,
                                   range_min=range_min, range_max=range_max)
        st.write(insight_11)
        
        # Pembatas garis
        st.markdown("---")
        
        # Korelasi dan Insight: Tren Pertumbuhan Proyek dari Waktu ke Waktu
        st.markdown("## Tren Proyek dari Waktu ke Waktu")

        # Drop rows where 'Tanggal Terbit Oss' is NaT (Not a Time)
        data = data.dropna(subset=['Tanggal Terbit Oss'])

        # Grouping data by month and year
        data['YearMonth'] = data['Tanggal Terbit Oss'].dt.to_period('M')  # Extract year-month for monthly aggregation
        time_series_data = data['YearMonth'].value_counts().sort_index().reset_index()
        time_series_data.columns = ['YearMonth', 'Count']

        # Convert 'YearMonth' back to datetime for plotting
        time_series_data['YearMonth'] = time_series_data['YearMonth'].dt.to_timestamp()

        # Create time series plot
        fig_ts = px.line(time_series_data, x='YearMonth', y='Count', title='Tren Waktu Terbit OSS',
                        labels={'YearMonth': 'Tanggal', 'Count': 'Jumlah Proyek'},
                        markers=True)
    
        fig_ts.update_layout(xaxis_title='Tanggal Terbit Oss', yaxis_title='Jumlah Proyek',
                            xaxis=dict(tickformat='%Y-%m'))
        st.plotly_chart(fig_ts)

        # Calculate changes between periods
        time_series_data['Previous Count'] = time_series_data['Count'].shift(1)
        time_series_data['Change'] = time_series_data['Count'] - time_series_data['Previous Count']

        # Find largest increase and decrease
        largest_increase = time_series_data.loc[time_series_data['Change'].idxmax()]
        largest_decrease = time_series_data.loc[time_series_data['Change'].idxmin()]

        # Find periods with highest and lowest project counts
        highest = time_series_data.loc[time_series_data['Count'].idxmax()]
        lowest = time_series_data.loc[time_series_data['Count'].idxmin()]

        # Generate insights
        insight_12 = (
            f"Pada periode tren waktu terbit OSS:\n"
            f"- **Periode dengan jumlah proyek tertinggi** adalah {highest['YearMonth'].strftime('%Y-%m')} "
            f"dengan total proyek sebanyak {highest['Count']:,}.\n"
            f"- **Periode dengan jumlah proyek terendah** adalah {lowest['YearMonth'].strftime('%Y-%m')} "
            f"dengan total proyek sebanyak {lowest['Count']:,}.\n"
            f"- **Peningkatan terbesar** terjadi dari periode {largest_increase['YearMonth'] - pd.DateOffset(months=1):%Y-%m} "
            f"ke periode {largest_increase['YearMonth'].strftime('%Y-%m')} dengan peningkatan sebesar {largest_increase['Change']:,} proyek.\n"
            f"- **Penurunan terbesar** terjadi dari periode {largest_decrease['YearMonth'] - pd.DateOffset(months=1):%Y-%m} "
            f"ke periode {largest_decrease['YearMonth'].strftime('%Y-%m')} dengan penurunan sebesar {largest_decrease['Change']:,} proyek."
        )
        st.write(insight_12)

if __name__ == "__main__":
    analisa_data()

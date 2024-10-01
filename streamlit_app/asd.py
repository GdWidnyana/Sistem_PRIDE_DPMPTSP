import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

def load_data(uploaded_file):
    # Load data from the uploaded file
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
    
    # Convert 'Tanggal Terbit Oss' to datetime
    data['Tanggal Terbit Oss'] = pd.to_datetime(data['Tanggal Terbit Oss'], errors='coerce')
    
    return data

def analisa_data():
    st.title('Analisa Data')

    # Upload file
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file:
        # Load data from the uploaded file
        data = load_data(uploaded_file)

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
        
        # Korelasi dan Insight 12: Uraian_Jenis_Proyek dan Uraian Skala Usaha
        st.markdown("## Distribusi Resiko Proyek berdasarkan Skala Usaha")
        
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
                                        
        # Korelasi dan Insight 2: Tanggal Terbit Oss dan Jumlah Investasi
        st.markdown("## Tren Investasi dari Waktu ke Waktu")
        data['Bulan Terbit'] = data['Tanggal Terbit Oss'].dt.to_period('M')
        data_grouped_by_month = data.groupby('Bulan Terbit')['Jumlah Investasi'].sum().reset_index()
        data_grouped_by_month['Bulan Terbit'] = data_grouped_by_month['Bulan Terbit'].dt.to_timestamp()

        selected_year = st.selectbox("Pilih Tahun:", data_grouped_by_month['Bulan Terbit'].dt.year.unique())
        filtered_by_year = data_grouped_by_month[data_grouped_by_month['Bulan Terbit'].dt.year == selected_year]

        fig2 = px.line(filtered_by_year, x='Bulan Terbit', y='Jumlah Investasi', 
                       title="Tren Jumlah Investasi per Bulan",
                       text='Jumlah Investasi')  # Menampilkan angka di atas titik
        fig2.update_layout(
            yaxis_tickformat=',',  # Format angka dengan koma
            xaxis_title='Bulan Terbit',
            yaxis_title='Jumlah Investasi'
        )
        st.plotly_chart(fig2)

        # Korelasi dan Insight 3: Uraian Status Penanaman Modal dan Modal Kerja
        st.markdown("## Korelasi antara Status Penanaman Modal dan Modal Kerja")
        grouped_modal = data.groupby('Uraian Status Penanaman Modal')['Modal Kerja'].sum().reset_index()
        grouped_modal = grouped_modal.sort_values(by='Modal Kerja', ascending=False)

        fig3 = px.pie(grouped_modal, names='Uraian Status Penanaman Modal', values='Modal Kerja',
                      title="Total Modal Kerja berdasarkan Status Penanaman Modal",
                      labels={'Modal Kerja': 'Jumlah Modal Kerja'},
                      hole=0.3)  # Menggunakan hole untuk membuat donut chart
        fig3.update_traces(textinfo='label+percent+value', 
                           textposition='outside',
                           pull=[0.1] * len(grouped_modal))  # Menambahkan jarak untuk setiap slice
        st.plotly_chart(fig3)

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

        # Korelasi dan Insight 5: Persebaran Jenis Perusahaan berdasarkan Kelurahan
        st.markdown("## Persebaran Jenis Perusahaan berdasarkan Kelurahan")
        jenis_perusahaan = st.selectbox("Pilih Jenis Perusahaan:", data['Uraian Jenis Perusahaan'].unique(), key='jenis_perusahaan_kelurahan')
        tahun_kelurahan = st.selectbox("Pilih Tahun:", data['Tanggal Terbit Oss'].dt.year.unique(), key='tahun_kelurahan')
        
        filtered_kelurahan = data[(data['Uraian Jenis Perusahaan'] == jenis_perusahaan) & (data['Tanggal Terbit Oss'].dt.year == tahun_kelurahan)]
        grouped_kelurahan = filtered_kelurahan.groupby('kelurahan_usaha').size().reset_index(name='Total')
        grouped_kelurahan = grouped_kelurahan.sort_values(by='Total', ascending=False)
        
        fig5 = px.bar(grouped_kelurahan, x='kelurahan_usaha', y='Total', color='kelurahan_usaha', 
                      title=f"Persebaran Jenis Perusahaan berdasarkan Kelurahan {jenis_perusahaan} ({tahun_kelurahan})",
                      labels={'Total': 'Total', 'kelurahan_usaha': 'Kelurahan'},
                      text_auto=True)  # Menampilkan angka di atas batang
        fig5.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig5)

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

        # Diagram Batang 10 Teratas
        st.markdown("## 10 KLBI Teratas berdasarkan Sektor Pembina")
        klbi_top_10 = klbi_counts.nlargest(10, 'Count')  # Mengambil 10 teratas
        fig9 = px.bar(klbi_top_10, x='Judul Kbli', y='Count', 
                      title=f"10 KLBI Teratas berdasarkan {sektor_pembina}",
                      labels={'Count': 'Jumlah'},
                      text_auto=True)  # Menampilkan angka di atas batang
        st.plotly_chart(fig9)

        # Diagram Batang 10 Terbawah
        st.markdown("## 10 KLBI Terbawah berdasarkan Sektor Pembina")
        klbi_bottom_10 = klbi_counts.nsmallest(10, 'Count')  # Mengambil 10 terbawah
        fig10 = px.bar(klbi_bottom_10, x='Judul Kbli', y='Count', 
                       title=f"10 KLBI Terbawah berdasarkan {sektor_pembina}",
                       labels={'Count': 'Jumlah'},
                       text_auto=True)  # Menampilkan angka di atas batang
        st.plotly_chart(fig10)

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
        elif pilihan_pemusatan == 'Median':
            y_data = grouped_kecamatan['Median']
        else:
            y_data = grouped_kecamatan['Modus']

        # Sort data dari terbesar ke terkecil
        sorted_grouped_kecamatan = grouped_kecamatan.sort_values(by=pilihan_pemusatan, ascending=False)

        # Buat histogram sesuai dengan pilihan pemusatan
        fig11 = go.Figure()
        fig11.add_trace(go.Bar(x=sorted_grouped_kecamatan['Kecamatan Usaha'], y=sorted_grouped_kecamatan[pilihan_pemusatan], 
                            text=sorted_grouped_kecamatan[pilihan_pemusatan], textposition='auto',
                            name=f'Jumlah Investasi ({pilihan_pemusatan})'))

        fig11.update_layout(title=f"Distribusi Jumlah Investasi berdasarkan Kecamatan ({pilihan_pemusatan})",
                            xaxis_title='Kecamatan Usaha',
                            yaxis_title=f'Jumlah Investasi ({pilihan_pemusatan})')
        fig11.update_layout(yaxis_tickformat=',')
        st.plotly_chart(fig11)

        st.markdown("## Tren Pertumbuhan Proyek dari waktu ke waktu")
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
        
if __name__ == "__main__":
    analisa_data()

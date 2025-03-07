import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Judul
st.title("DASHBOARD PEMINJAMAN SEPEDA")

# Membaca dataset 
try:
    data_df = pd.read_csv('all_data.csv')

    # Menampilkan data
    st.subheader("Data Peminjaman Sepeda")
    st.write(data_df.head())
    
    # Menampilkan informasi tentang dataset dalam bentuk tabel
    info_df = pd.DataFrame({
        "Column": data_df.columns,
        "Non-Null Count": [data_df[col].notnull().sum() for col in data_df.columns],
        "Dtype": [data_df[col].dtype for col in data_df.columns]
    })
    
    st.subheader("Informasi Data")
    st.dataframe(info_df)  # Menampilkan informasi kolom dalam bentuk tabel

    # Mengecek apakah ada nilai yang hilang
    st.subheader("Nilai yang Hilang")
    st.write(data_df.isnull().sum())

    # Memeriksa duplikasi data
    st.write("Jumlah duplikasi: ", data_df.duplicated().sum())

    # Menghapus semua baris yang memiliki nilai hilang
    data_df.dropna(inplace=True)

    # Memilih kolom numerik dan visualisasi matriks korelasi
    numeric_data = data_df.select_dtypes(include='number')
    correlation = numeric_data.corr()
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation, annot=True, fmt=".2f", cmap='coolwarm', square=True)
    plt.title('Matriks Korelasi')
    st.pyplot(plt)
    plt.clf()

    # Mengonversi kolom tanggal menjadi tipe datetime jika ada
    if 'dteday' in data_df.columns:
        data_df['dteday'] = pd.to_datetime(data_df['dteday'])

        # Menambahkan kolom hari dalam seminggu
        data_df['Day_Of_Week'] = data_df['dteday'].dt .day_name()

        # Menghitung jumlah peminjam sepeda berdasarkan hari dalam seminggu
        day_counts = data_df.groupby('Day_Of_Week')['cnt'].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

        # Visualisasi
        plt.figure(figsize=(8, 5))
        day_counts.plot(kind='bar', color='skyblue')
        plt.title('Jumlah Peminjam Sepeda per Hari dalam Seminggu')
        plt.xlabel('Hari')
        plt.ylabel('Jumlah Peminjam')
        plt.xticks(rotation=40)
        st.pyplot(plt)
        plt.clf()

        # Menambahkan kolom bulan
        data_df['Month'] = data_df['dteday'].dt.month_name()

        # Menghitung jumlah peminjam sepeda berdasarkan bulan
        month_counts = data_df.groupby('Month')['cnt'].sum().reindex(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])

        # Visualisasi
        plt.figure(figsize=(8, 5))
        month_counts.plot(kind='bar', color='lightgreen')
        plt.title('Jumlah Peminjam Sepeda per Bulan')
        plt.xlabel('Bulan')
        plt.ylabel('Jumlah Peminjam')
        plt.xticks(rotation=40)
        st.pyplot(plt)
        plt.clf()

        # Menambahkan kolom musim
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'

        data_df['Season'] = data_df['dteday'].dt.month.apply(get_season)

        # Menghitung jumlah peminjam sepeda berdasarkan musim
        season_counts = data_df.groupby('Season')['cnt'].sum()

        # Visualisasi
        plt.figure(figsize=(8, 5))
        season_counts.plot(kind='bar', color='salmon')
        plt.title('Jumlah Peminjam Sepeda per Musim')
        plt.xlabel('Musim')
        plt.ylabel('Jumlah Peminjam')
        plt.xticks(rotation=0)
        st.pyplot(plt)
        plt.clf()

        # Menghitung RFM
        rfm_df = data_df.groupby(by="instant", as_index=False).agg({
            "dteday": "max",  # Mengambil tanggal peminjaman terakhir
            "cnt": "count"    # Menghitung jumlah peminjaman
        })

        rfm_df.columns = ["instant", "max_borrow_date", "frequency"]

        # Menghitung Recency
        recent_date = data_df['dteday'].max()
        rfm_df["recency"] = rfm_df["max_borrow_date"].apply(lambda x: (recent_date - x).days)

        # Menghapus kolom max_borrow_date
        rfm_df.drop("max_borrow_date", axis=1, inplace=True)

        # Menampilkan DataFrame RFM
        st.subheader("Data RFM")
        st.write(rfm_df.head())

        # Visualisasi pelanggan terbaik berdasarkan RFM
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

        colors = ["#72BCD4"] * 5  # Warna untuk visualisasi

        # Visualisasi berdasarkan Recency
        sns.barplot(y="recency", x="instant", data=rfm_df.sort_values(by="recency", ascending=True).head(5), hue="instant", palette=colors, dodge=False, ax=ax[0], legend=False)
        ax[0].set_ylabel(None)
        ax[0].set_xlabel(None)
        ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
        ax[0].tick_params(axis='x', labelsize=15)

        # Visualisasi berdasarkan Frequency
        sns.barplot(y="frequency", x="instant", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), hue="instant", palette=colors, dodge=False, ax=ax[1], legend=False)
        ax[1].set_ylabel(None)
        ax[1].set_xlabel(None)
        ax[1].set_title("By Frequency", loc="center", fontsize=18)
        ax[1].tick_params(axis='x', labelsize=15)

        # Menghitung nilai 'monetary' (misalnya, total cnt untuk setiap instant)
        rfm_df['monetary'] = data_df.groupby('instant')['cnt'].sum().values

        # Visualisasi berdasarkan Monetary
        sns.barplot(y="monetary", x="instant", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), hue="instant", palette=colors, dodge=False, ax=ax[2], legend=False)
        ax[2].set_ylabel(None)
        ax[2].set_xlabel(None)
        ax[2].set_title("By Monetary", loc="center", fontsize=18)
        ax[2].tick_params(axis='x', labelsize=15)

        plt.suptitle("Best Customers Based on RFM Parameters (instant)", fontsize=20)
        st.pyplot(fig)
        plt.clf()

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat data: {e}")
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load Data & helper Functions
@st.cache_data  
def load_data():
    df = pd.read_csv("all_data.csv", parse_dates=["dteday"]) 
    return df

df = load_data()

# --- Fungsi untuk Analisis RFM ---
def rfm_analysis(df_filtered):
    # Pastikan kolom 'dteday' bertipe datetime
    df_filtered['dteday'] = pd.to_datetime(df_filtered['dteday'])

    # --- Recency ---
    df_filtered["recency"] = (df_filtered["dteday"].max() - df_filtered["dteday"]).dt.days

    # --- Frequency ---
    freq_per_month = df_filtered.groupby("mnth_daily")["cnt_daily"].count().reset_index()
    freq_per_month.columns = ["mnth_daily", "frequency"]

    # --- Monetary ---
    monetary_per_month = df_filtered.groupby("mnth_daily")["cnt_daily"].sum().reset_index()
    monetary_per_month.columns = ["mnth_daily", "monetary"]

    # Gabungkan RFM
    rfm_df = pd.merge(df_filtered, freq_per_month, on="mnth_daily", how="left")
    rfm_df = pd.merge(rfm_df, monetary_per_month, on="mnth_daily", how="left")

    # --- Tentukan Skor RFM ---
    quantiles = rfm_df[['recency', 'frequency', 'monetary']].quantile([0.25, 0.5, 0.75])

    def rfm_score(x, q, variable):
        if x <= q[variable][0.25]:
            return 4
        elif x <= q[variable][0.50]:
            return 3
        elif x <= q[variable][0.75]:
            return 2
        else:
            return 1

    rfm_df['R_Score'] = rfm_df['recency'].apply(rfm_score, args=(quantiles, 'recency'))
    rfm_df['F_Score'] = rfm_df['frequency'].apply(rfm_score, args=(quantiles, 'frequency'))
    rfm_df['M_Score'] = rfm_df['monetary'].apply(rfm_score, args=(quantiles, 'monetary'))

    rfm_df['RFM_Score'] = rfm_df['R_Score'].astype(str) + rfm_df['F_Score'].astype(str) + rfm_df['M_Score'].astype(str)

    return rfm_df

# --- Sidebar ---
st.sidebar.image("d:\logo_bike.png", width=200) 
st.sidebar.title("Dashboard Peminjaman Sepeda 🚲")

# Sidebar Filters
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal", [df["dteday"].min(), df["dteday"].max()]
)

filtered_df = df[
    (df["dteday"] >= pd.to_datetime(date_range[0])) &
    (df["dteday"] <= pd.to_datetime(date_range[1]))
]

option = st.sidebar.selectbox(
    "Pilih Analisis",
    [
        "Pola Tren Peminjaman Berdasarkan Musim",
        "Faktor yang Mempengaruhi Jumlah Peminjaman",
        "Analisis RFM",
    ]
)

# --- Dashboard Sections ---
if option == "Pola Tren Peminjaman Berdasarkan Musim":
    st.title("Pola Tren Peminjaman Sepeda Berdasarkan Musim 🌸🚲")
    
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(x="season_daily", y="cnt_daily", data=filtered_df, ax=ax) 
    ax.set_title("Pola Tren Peminjaman Sepeda Berdasarkan Musim")
    ax.set_xlabel("Musim")
    ax.set_ylabel("Jumlah Peminjaman")
    plt.xticks(ticks=[0, 1, 2, 3], labels=['Winter', 'Spring', 'Summer', 'Fall'])
    st.pyplot(fig)


elif option == "Faktor yang Mempengaruhi Jumlah Peminjaman":
    st.title("Faktor yang Mempengaruhi Jumlah Peminjaman Sepeda 📉🚲")
    
    # Korelasi dengan 'cnt' untuk melihat faktor yang paling berpengaruh
    correlation = filtered_df[['temp_daily', 'atemp_daily', 'hum_daily', 'windspeed_daily', 'cnt_daily']].corr()

    # Mengambil nilai absolut korelasi dengan 'cnt'
    correlation_cnt = correlation['cnt_daily'].abs().sort_values(ascending=False)

    # Faktor yang paling berpengaruh (selain 'cnt' itu sendiri)
    most_influential_factor = correlation_cnt.index[1]

    # Visualisasi hubungan antara suhu dan jumlah peminjaman
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='temp_daily', y='cnt_daily', data=filtered_df)
    plt.title('Hubungan antara Suhu dan Jumlah Peminjaman Sepeda')
    plt.xlabel('Suhu (°C)')
    plt.ylabel('Jumlah Peminjaman')
    st.pyplot(plt)

elif option == "Analisis RFM":
    st.title("Analisis RFM Peminjaman Sepeda 📌🚲")
    
    # Panggil fungsi analisis RFM
    rfm_df = rfm_analysis(filtered_df)  
    
    # Menghitung jumlah pengguna di setiap segmen RFM
    segment_counts = rfm_df['RFM_Score'].value_counts().sort_index()

    # Membuat diagram batang
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(x=segment_counts.index, y=segment_counts.values, ax=ax)
    ax.set_title('Jumlah Pengguna di Setiap Segmen RFM')
    ax.set_xlabel('Segmen RFM')
    ax.set_ylabel('Jumlah Pengguna')
    plt.xticks(rotation=45, ha='right')  # Rotasi label sumbu x agar mudah dibaca
    plt.tight_layout()
    st.pyplot(fig)

    # Membuat diagram pie
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%', startangle=90)
    ax.set_title('Proporsi Pengguna di Setiap Segmen RFM')
    st.pyplot(fig)

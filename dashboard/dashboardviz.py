import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
sns.set(style='dark')

# import subprocess
# import sys
# subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "seaborn"])
def byworkday(df):
    byworkday_df = df.groupby(by="workingday_perjam").instant_perjam.nunique().reset_index()
    byworkday_df['workingday_perjam'] = byworkday_df['workingday_perjam'].replace({1: 'Working Day', 0: 'Non-Working Day'})
    return byworkday_df

def byweather(df):
    byweather_df = df.groupby(by=["weathersit_perjam"]).agg({
        "cnt_perjam": "sum",
        "temp_perjam": ["mean"],
        "hum_perjam": ["mean"],
        "windspeed_perjam": ["mean"]
    }).reset_index()
    byweather_df.columns = ['weathersit_perjam', 'Total Peminjaman', 'Rerata Suhu', 'Rerata Kelembapan', 'Rerata Kecepatan Angin']
    byweather_df['weathersit_perjam'] = byweather_df['weathersit_perjam'].replace({1: 'Cerah Sedikit Berawan', 2: 'Mendung Berawan', 3: 'Salju atau Hujan Ringan Berawan Gelap', 4: 'Hujan atau Salju Lebat disertai Petir'})
    return byweather_df

def byhour(df):
    freq_hour_df = df.groupby(by=["hr"]).agg({
        "cnt_perjam": "sum"
    }).reset_index()
    return freq_hour_df

def byworkingday(df):
    freq_hour_workingday_df = df.groupby(by=["hr", "workingday_perjam"]).agg({
        "cnt_perjam": "sum"
    }).reset_index()
    work_day = freq_hour_workingday_df[freq_hour_workingday_df["workingday_perjam"] == 1]
    nonwork_day = freq_hour_workingday_df[freq_hour_workingday_df["workingday_perjam"] == 0]
    return work_day, nonwork_day

script_dir = os.path.dirname(os.path.realpath(__file__))
all_df= pd.read_csv(f"{script_dir}/main_data.csv")

datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()
 
with st.sidebar:
    st.image("https://i.pinimg.com/736x/4c/cf/6e/4ccf6e6ae6114162bf5cdde16212bfc6.jpg")
    
    start_date, end_date = st.date_input(
        label='Range Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & (all_df["dteday"] <= str(end_date))]

workday_df = byworkday(main_df)
weather_df = byweather(main_df)
freq_hour_df = byhour(main_df)
work_day, nonwork_day = byworkingday(main_df)

st.title('Data Peminjaman Sepeda :bike:')
st.text("Dashboard ini merupakan hasil visualisasi data Bike Sharing dari tahun 2011-2012.")

col1, col2 = st.columns(2)
#st.write(main_df.columns)
with col1:
    total_registered = main_df["registered_perjam"].sum()
    st.metric("Total Peminjaman (Registered)", value=total_registered)

with col2:
    total_casual = main_df['casual_perjam'].sum()
    st.metric("Total Peminjaman (Casual)", value=total_casual)

#==============================================================================================================
st.subheader('Jumlah Peminjaman berdasarkan Hari Kerja :office_worker:')
total_peminjaman = workday_df['instant_perjam'].values
labels = workday_df['workingday_perjam'].values

total_peminjaman = workday_df['instant_perjam'].values
labels = workday_df['workingday_perjam'].values
colors = ['#4CAF50', '#FF5722']

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#0f0f0f')
ax.set_facecolor('#ffffff')

wedges, texts, autotexts = ax.pie(
    total_peminjaman,
    labels=labels,
    autopct='%1.1f%%',
    startangle=90,
    pctdistance=0.85,
    colors=colors
)

for text in autotexts:
    text.set_color('white')
for text in texts:
    text.set_color('white')

centre_circle = plt.Circle((0, 0), 0.70, fc='white')  # Adjust radius as desired
fig.gca().add_artist(centre_circle)

plt.title("Persentase Peminjaman Sepeda berdasarkan Hari Kerja", fontsize=15, color='white')
plt.axis('equal')
st.pyplot(fig)

#==============================================================================================================
st.subheader('Jumlah Peminjaman berdasarkan Kondisi Cuaca :sun_behind_rain_cloud:')
plt.figure(figsize=(12, 6))
ax = sns.barplot(
    x="Total Peminjaman",
    y="weathersit_perjam",
    data=weather_df.sort_values(by="Total Peminjaman", ascending=False)
)

for container in ax.containers:
    ax.bar_label(container, fmt='%d', label_type='edge', fontsize=10)

plt.title("Jumlah Peminjaman Sepeda berdasarkan Kondisi Cuaca", loc="center", fontsize=15)
plt.xlabel("Total Jumlah Peminjaman")
plt.ylabel("Kondisi Cuaca")
plt.tick_params(axis='y', labelsize=12)
st.pyplot(plt)

#==============================================================================================================
st.subheader('Jumlah Peminjaman berdasarkan Periode Jam :alarm_clock:')
plt.figure(figsize=(10, 5))
plt.plot(freq_hour_df["hr"], freq_hour_df["cnt_perjam"], marker='o')
plt.title("Distribusi Peminjaman Sepeda per Jam", loc="center", fontsize=20)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlabel("Jam (0-23)")
plt.ylabel("Total Peminjaman")
st.pyplot(plt)

#==============================================================================================================
st.subheader('Jumlah Peminjaman berdasarkan Periode Jam dan Hari Kerja :timer_clock:')
plt.figure(figsize=(10, 5))
plt.plot(work_day["hr"], work_day["cnt_perjam"], label="Working Day", color='blue', marker='o')
plt.plot(nonwork_day["hr"], nonwork_day["cnt_perjam"], label="Non-working Day", color='green', marker='o')

plt.title("Distribusi Peminjaman Sepeda per Jam berdasarkan Working Day", loc="center", fontsize=20)
plt.xlabel("Jam (0-23)")
plt.ylabel("Total Peminjaman")
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.legend()

st.pyplot(plt)
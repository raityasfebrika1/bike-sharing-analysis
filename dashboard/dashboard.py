import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi halaman
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_style("whitegrid")

# Warna: biru = nilai tertinggi, abu-abu = lainnya
COLOR_HIGH = "#1f77b4"
COLOR_MID = "#b0b8c1"


def highlight_colors(values):
    """Biru untuk nilai tertinggi, abu-abu untuk sisanya."""
    if not values:
        return []
    vmax = max(values)
    return [COLOR_HIGH if v == vmax else COLOR_MID for v in values]


# Load data
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "main_data.csv")
    df = pd.read_csv(file_path)
    df["dteday"] = pd.to_datetime(df["dteday"])

    # Standardisasi label musim, cuaca, dan tipe hari
    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_map = {
        1: "Clear/Partly Cloudy",
        2: "Mist/Cloudy",
        3: "Light Snow/Rain",
        4: "Heavy Rain/Snow"
    }

    if pd.api.types.is_numeric_dtype(df["season"]):
        df["season_label"] = df["season"].map(season_map)
    else:
        df["season_label"] = df["season"].astype(str).str.title()

    if pd.api.types.is_numeric_dtype(df["weathersit"]):
        df["weather_label"] = df["weathersit"].map(weather_map)
    else:
        df["weather_label"] = df["weathersit"].astype(str)

    if pd.api.types.is_numeric_dtype(df["workingday"]):
        df["day_type"] = df["workingday"].map({0: "Holiday/Weekend", 1: "Working Day"})
    else:
        df["day_type"] = df["workingday"].astype(str)

    # Pengelompokan jam operasional (Binning) - SAMA dengan notebook
    def group_hour(hr):
        if 0 <= hr <= 5:
            return "Dini Hari (00-05)"
        elif 6 <= hr <= 10:
            return "Pagi (06-10)"
        elif 11 <= hr <= 15:
            return "Siang (11-15)"
        elif 16 <= hr <= 19:
            return "Sore (16-19)"
        else:
            return "Malam (20-23)"

    df["time_group"] = df["hr"].apply(group_hour)
    return df


df = load_data()

# ==================== SIDEBAR FILTER ====================
with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.markdown("Pilih rentang tanggal untuk melihat performa penyewaan sepeda:")

    min_date = df["dteday"].min().date()
    max_date = df["dteday"].max().date()

    date_range = st.date_input(
        label="Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0]

# Filter dataset berdasarkan tanggal
main_df = df[(df["dteday"].dt.date >= start_date) & (df["dteday"].dt.date <= end_date)].copy()

# ==================== HEADER & METRIK UTAMA ====================
st.title("Bike Sharing Analytics Dashboard 🚲")
st.markdown(f"Periode Data: **{start_date.strftime('%d %b %Y')}** s.d. **{end_date.strftime('%d %b %Y')}**")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Penyewaan", f"{int(main_df['cnt'].sum()):,}")
with col2:
    st.metric("Pengguna Registered", f"{int(main_df['registered'].sum()):,}")
with col3:
    st.metric("Pengguna Casual", f"{int(main_df['casual'].sum()):,}")

st.divider()

# ==================== GRAFIK TIME SERIES: REGISTERED VS CASUAL ====================
st.subheader("Tren Penyewaan Sepeda: Registered vs Casual")
ts_freq = st.radio(
    label="Agregasi Waktu",
    options=["Bulanan", "Harian"],
    horizontal=True,
    label_visibility="collapsed",
    key="ts_radio"
)

fig_ts, ax_ts = plt.subplots(figsize=(12, 4))

if ts_freq == "Bulanan":
    main_df["year_month"] = main_df["dteday"].dt.to_period("M").astype(str)
    ts_df = main_df.groupby("year_month", as_index=False)[["registered", "casual"]].sum()

    ax_ts.plot(ts_df["year_month"], ts_df["registered"], label="Registered", color="#1f77b4", linewidth=2, marker="o")
    ax_ts.plot(ts_df["year_month"], ts_df["casual"], label="Casual", color="#ff7f0e", linewidth=2, marker="o")
    ax_ts.set_title("Total Penyewaan Bulanan: Registered vs Casual", fontweight="bold")

    # Tampilkan label bulan secara proporsional dan berhenti tepat di akhir filter
    step = max(1, len(ts_df) // 12)
    ax_ts.set_xticks(range(0, len(ts_df), step))
    ax_ts.set_xticklabels(ts_df["year_month"].iloc[::step], rotation=0)
else:
    ts_df = main_df.groupby("dteday", as_index=False)[["registered", "casual"]].sum()

    ax_ts.plot(ts_df["dteday"], ts_df["registered"], label="Registered", color="#1f77b4", linewidth=1.5)
    ax_ts.plot(ts_df["dteday"], ts_df["casual"], label="Casual", color="#ff7f0e", linewidth=1.5)
    ax_ts.set_title("Total Penyewaan Harian: Registered vs Casual", fontweight="bold")
    ax_ts.set_xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))

ax_ts.set_xlabel("Periode")
ax_ts.set_ylabel("Jumlah Penyewaan")
ax_ts.legend(title="Tipe Pengguna")
sns.despine(ax=ax_ts)
st.pyplot(fig_ts)

st.divider()

# ==================== GRAFIK 1: MUSIM & CUACA ====================
st.subheader("1. Pengaruh Musim dan Cuaca terhadap Penyewaan")
unit_p1 = st.radio(
    label="Satuan Poin 1",
    options=["Per Hari", "Per Jam"],
    horizontal=True,
    label_visibility="collapsed",
    key="p1_radio"
)

col_a, col_b = st.columns(2)

with col_a:
    season_order = ["Spring", "Summer", "Fall", "Winter"]

    if unit_p1 == "Per Hari":
        daily_season = main_df.groupby(["dteday", "season_label"], as_index=False)["cnt"].sum()
        season_df = daily_season.groupby("season_label", as_index=False)["cnt"].mean()
        fmt_s = "%.0f"
        unit_label_1 = "per Hari"
    else:
        season_df = main_df.groupby("season_label", as_index=False)["cnt"].mean()
        fmt_s = "%.1f"
        unit_label_1 = "per Jam"

    # Urutan kronologis seperti di notebook
    season_df["season_label"] = pd.Categorical(season_df["season_label"], categories=season_order, ordered=True)
    season_df = season_df.sort_values("season_label").reset_index(drop=True)
    season_df["season_label"] = season_df["season_label"].astype(str)
    palette_s = dict(zip(season_df["season_label"], highlight_colors(season_df["cnt"].tolist())))

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=season_df, x="season_label", y="cnt", hue="season_label",
                palette=palette_s, legend=False, ax=ax1)
    ax1.set_title(f"Rata-rata Penyewaan {unit_label_1} per Musim", fontweight="bold")
    ax1.set_xlabel("Musim")
    ax1.set_ylabel("Rata-rata Penyewaan")
    for c in ax1.containers:
        ax1.bar_label(c, fmt=fmt_s, padding=3)
    sns.despine(ax=ax1)
    st.pyplot(fig1)

with col_b:
    if unit_p1 == "Per Hari":
        # Satu hari = satu cuaca (cuaca dominan hari tersebut), sehingga total harian utuh,
        # bukan potongan jam per kategori cuaca.
        daily_weather = main_df.groupby("dteday").agg(
            cnt=("cnt", "sum"),
            weather_label=("weather_label", lambda s: s.mode().iloc[0])
        )
        weather_stat = daily_weather.groupby("weather_label")["cnt"].agg(["mean", "count"])
        fmt_w = "%.0f"
    else:
        weather_stat = main_df.groupby("weather_label")["cnt"].agg(["mean", "count"])
        fmt_w = "%.1f"

    weather_df = (
        weather_stat.rename(columns={"mean": "cnt", "count": "n"})
        .reset_index()
        .sort_values("cnt", ascending=False)
        .reset_index(drop=True)
    )
    palette_w = dict(zip(weather_df["weather_label"], highlight_colors(weather_df["cnt"].tolist())))

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=weather_df, x="cnt", y="weather_label", hue="weather_label",
                palette=palette_w, legend=False, ax=ax2)
    ax2.set_title(f"Rata-rata Penyewaan {unit_label_1} per Cuaca", fontweight="bold")
    ax2.set_xlabel("Rata-rata Penyewaan")
    ax2.set_ylabel("")
    for c in ax2.containers:
        ax2.bar_label(c, fmt=fmt_w, padding=3)
    sns.despine(ax=ax2)
    st.pyplot(fig2)

    heavy_hours = int((df["weather_label"] == "Heavy Rain/Snow").sum())
    if unit_p1 == "Per Hari":
        if heavy_hours > 0:
            st.caption("Cuaca Heavy Rain/Snow tidak ditampilkan karena tidak ada hari yang kondisi dominannya "
                       f"Heavy Rain/Snow (hanya tercatat {heavy_hours} jam dalam seluruh data).")
    else:
        heavy_row = weather_df[weather_df["weather_label"] == "Heavy Rain/Snow"]
        if len(heavy_row) > 0:
            st.caption(f"Heavy Rain/Snow hanya tercatat {int(heavy_row['n'].iloc[0])} jam, "
                       "sehingga rata-ratanya kurang representatif.")

st.divider()

# ==================== GRAFIK 2: CASUAL VS REGISTERED ====================
st.subheader("2. Perbandingan Pengguna Casual vs Registered berdasarkan kelompok hari")
unit_p2 = st.radio(
    label="Satuan Poin 2",
    options=["Per Hari", "Per Jam"],
    horizontal=True,
    label_visibility="collapsed",
    key="p2_radio"
)

if unit_p2 == "Per Hari":
    daily_user = main_df.groupby(["dteday", "day_type"], as_index=False)[["casual", "registered"]].sum()
    user_df = daily_user.groupby("day_type", as_index=False)[["casual", "registered"]].mean()
    fmt_u = "%.0f"
    unit_label_2 = "per Hari"
else:
    user_df = main_df.groupby("day_type", as_index=False)[["casual", "registered"]].mean()
    fmt_u = "%.1f"
    unit_label_2 = "per Jam"

user_melt = user_df.melt(id_vars="day_type", var_name="Tipe Pengguna", value_name="Rata-rata")

fig3, ax3 = plt.subplots(figsize=(9, 4))
sns.barplot(data=user_melt, x="day_type", y="Rata-rata", hue="Tipe Pengguna", palette=["#ff7f0e", "#1f77b4"], ax=ax3)
ax3.set_title("Rata-rata Penyewaan: Hari Kerja vs Akhir Pekan/Libur", fontweight="bold")
ax3.set_xlabel("Kategori Hari")
ax3.set_ylabel(f"Rata-rata Penyewaan / {unit_p2.replace('Per ', '')}")
for c in ax3.containers:
    ax3.bar_label(c, fmt=fmt_u, padding=3)
sns.despine(ax=ax3)
st.pyplot(fig3)

st.divider()

# ==================== GRAFIK 3: KELOMPOK JAM OPERASIONAL ====================
st.subheader("3. Distribusi Penyewaan Berdasarkan Kelompok Jam")
bin_order = [
    "Dini Hari (00-05)",
    "Pagi (06-10)",
    "Siang (11-15)",
    "Sore (16-19)",
    "Malam (20-23)"
]
bin_df = (
    main_df.groupby("time_group", as_index=False)["cnt"]
    .mean()
    .set_index("time_group")
    .reindex(bin_order)
    .dropna()
    .reset_index()
)
palette_b = dict(zip(bin_df["time_group"], highlight_colors(bin_df["cnt"].tolist())))

fig4, ax4 = plt.subplots(figsize=(9, 4))
sns.barplot(data=bin_df, x="cnt", y="time_group", hue="time_group",
            palette=palette_b, legend=False, ax=ax4)
ax4.set_title("Rata-rata Penyewaan per Kelompok Jam Operasional", fontweight="bold")
ax4.set_xlabel("Rata-rata Penyewaan / Jam")
ax4.set_ylabel("")
for c in ax4.containers:
    ax4.bar_label(c, fmt="%.1f", padding=3)
sns.despine(ax=ax4)
st.pyplot(fig4)

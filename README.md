# Bike Sharing Analytics Dashboard 🚲

Dashboard interaktif untuk menganalisis pola penyewaan sepeda (Capital Bikeshare 2011–2012) berdasarkan musim, cuaca, tipe pengguna, dan jam operasional.

Dashboard online: lihat `url.txt`.

> **Catatan:** Library pada `requirements.txt` membutuhkan **Python 3.11 atau lebih baru**.

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Virtual Environment (`venv`)
> Gunakan langkah ini jika memakai `venv` bawaan Python (bukan Anaconda).

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```bash
mkdir bike_sharing_analysis
cd bike_sharing_analysis
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Menjalankan Dashboard
Jalankan dari folder utama proyek (`submission`):
```bash
streamlit run dashboard/dashboard.py
```

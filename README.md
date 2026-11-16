# Bike Sharing Analytics Dashboard 🚲

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Virtual Environment (`venv`)
> **Catatan:** Gunakan langkah di bawah ini apabila Anda menggunakan `venv` bawaan Python dan **bukan** menggunakan Anaconda/Conda.

```bash
python -m venv venv
venv\Scripts\activate
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

## Run streamlit app
```bash
streamlit run dashboard/dashboard.py
```
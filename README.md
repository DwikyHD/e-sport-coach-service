# e-sport-coach-service

## How to run locally (using Uvicorn)

1. Buat _virtual environment_ dengan menggunakan command ini
   ```
   python -m venv venv
   ```
2. aktifkan virtual environment dengan command berikut
   - Windows
     ```
     source venv/Scripts/activate
     ```
   - Mac & Linux
     ```
     source venv/bin/activate
     ```
3. Install library yang dibutuhkan dengan command berikut
   ```
   pip install -r requirements.txt
   ```
4. Jalankan command dibawah untuk menjalankan API
     ```
     uvicorn main:app
     ```

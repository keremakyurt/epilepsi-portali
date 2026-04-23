import kagglehub
import os
import pandas as pd

print("Amanik Dataset indiriliyor...")
try:
    path = kagglehub.dataset_download("amanik000/epilepsy-disorder-dataset")
    print(f"\nYerel Konum: {path}")

    csv_files = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.csv'):
                csv_files.append(os.path.join(root, f))
    
    print("\n--- DOSYA ICERIGI ---")
    for cf in csv_files:
        df = pd.read_csv(cf)
        print(f"\nCSV '{os.path.basename(cf)}':")
        print("Boyut:", df.shape)
        print("Sutunlar:", list(df.columns))
        print("Ilk 2 Satir:")
        print(df.head(2).to_string())
except Exception as e:
    print("Hata:", e)

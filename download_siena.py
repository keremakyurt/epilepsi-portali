import kagglehub
import os
import pandas as pd

print("Siena Scalp EEG Dataset indiriliyor...")
path = kagglehub.dataset_download("abhishekinnvonix/epilepsy-seizure-dataset-seina-scalp-complete")
print(f"\nYerel Konum: {path}")

print("\n--- DOSYA YAPISI ---")
for root, dirs, files in os.walk(path):
    for f in files:
        if root == path:
            print(f"- {f}")
        else:
            rel = os.path.relpath(root, path)
            print(f"- {rel}\\{f}")

# Eğer icerisinde CSV veya bilgi dosyasi varsa ilk satirlarina bak
csv_files = []
for root, dirs, files in os.walk(path):
    for f in files:
        if f.endswith('.csv'):
            csv_files.append(os.path.join(root, f))

for cf in csv_files[:3]:
    try:
        df = pd.read_csv(cf, nrows=5)
        print(f"\nCSV '{os.path.basename(cf)}' Inceleniyor:")
        print("Sutunlar:", list(df.columns))
        print("Ilk Satir:")
        print(df.head(1).to_string())
    except Exception as e:
        print(f"\nHata okurken {cf}: {e}")

import kagglehub
import pandas as pd
import os

print("Veri Seti 1 indiriliyor: peimandaii/epilepsy-diagnosis-dataset ...")
path1 = kagglehub.dataset_download("peimandaii/epilepsy-diagnosis-dataset")
print("Path 1:", path1)

print("\nVeri Seti 2 indiriliyor: buraktaci/turkish-epilepsy ...")
path2 = kagglehub.dataset_download("buraktaci/turkish-epilepsy")
print("Path 2:", path2)

def explore_csv(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print(f"\n--- {file} İnceleniyor ---")
                try:
                    df = pd.read_csv(file_path)
                    print("Boyut (Satır, Sütun):", df.shape)
                    print("Sütunlar:", list(df.columns))
                    print("Örnek Veri:\n", df.head(2).to_string())
                except Exception as e:
                    print(f"Hata okunurken {file}: {e}")

explore_csv(path1)
explore_csv(path2)

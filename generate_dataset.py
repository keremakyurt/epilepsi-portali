import pandas as pd
import numpy as np
import os

def create_synthetic_dataset(output_path='data/epilepsy_dataset.csv'):
    np.random.seed(42)
    n_samples = 1500

    # 1. KLINIK VERILER (Basit degiskenler)
    yas = np.random.randint(1, 80, n_samples)
    cinsiyet = np.random.choice([0, 1], n_samples)
    aile_oykusu = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    nobet_sikligi = np.random.poisson(lam=0.5, size=n_samples)
    
    # 2. RADYOLOJIK VERILER (Graph Theory & Ag Analizi Metrikleri Ciktilari)
    # Ileride gelistireceginiz goruntu isleme ve ag algoritmalari asagidaki gibi (0 ile 1 arasi vb.) skorlar uretecektir.
    
    # EEG Ag Baglanti Yogunlugu (Connectivity Density) -> Epilepsilerde noronal hiper-senkronizasyon gorulebilir.
    eeg_connectivity = np.random.normal(loc=0.5, scale=0.15, size=n_samples)
    eeg_connectivity = np.clip(eeg_connectivity, 0, 1)
    
    # EEG Ag Modulerligi (Graph Modularity) -> Agin alt bolumlenmesi
    eeg_modularity = np.random.normal(loc=0.4, scale=0.1, size=n_samples)
    
    # fMRI BOLD Sinyali Kumelenme Katsayisi (Clustering Coefficient)
    fmri_clustering = np.random.normal(loc=0.3, scale=0.1, size=n_samples)
    
    # fMRI Global Verimlilik (Global Efficiency) -> Bilgi iletim kapasitesi
    fmri_efficiency = np.random.normal(loc=0.6, scale=0.1, size=n_samples)

    # HASTALIK TANISI - Epilepsi olanlarda genelde belli ag yapilari degiskenlik gosterir
    epilepsi_skoru = (yas * 0.01) + (aile_oykusu * 1.5) + (nobet_sikligi * 1.2) + \
                     (eeg_connectivity * 3.5) + (eeg_modularity * 1.5) + \
                     (fmri_clustering * 2.5) - (fmri_efficiency * 1.5)
                     
    # Eşik degeri tespit edip tani koyalim
    median_skor = np.median(epilepsi_skoru)
    epilepsi_tanisi = (epilepsi_skoru > median_skor + 0.35).astype(int)

    # Veriyi kirletelim (Gercek klinik hayat zorlugu olusturmak adina)
    noise_idx = np.random.choice(n_samples, int(n_samples * 0.15), replace=False)
    epilepsi_tanisi[noise_idx] = 1 - epilepsi_tanisi[noise_idx]

    df = pd.DataFrame({
        'Yas': yas,
        'Cinsiyet': cinsiyet,
        'Aile_Oykusu': aile_oykusu,
        'Nobet_Sikligi': nobet_sikligi,
        'EEG_Baglanti_Yogunlugu': np.round(eeg_connectivity, 4),
        'EEG_Modulerlik': np.round(eeg_modularity, 4),
        'fMRI_Kumelenme_Katsayisi': np.round(fmri_clustering, 4),
        'fMRI_Global_Verimlilik': np.round(fmri_efficiency, 4),
        'Epilepsi_Tanisi': epilepsi_tanisi
    })

    df.to_csv(output_path, index=False)
    print(f"Graph targetli yeni veri seti {n_samples} islem ile hazirlandi: {output_path}")

if __name__ == "__main__":
    work_dir = r"C:\Users\AkyurtPc\epilepsy_project"
    os.makedirs(os.path.join(work_dir, "data"), exist_ok=True)
    create_synthetic_dataset(os.path.join(work_dir, "data", "epilepsy_dataset.csv"))

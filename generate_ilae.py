import pandas as pd
import numpy as np
import os

def generate():
    print("PNES, Senkop ve Provoke Nobet Altyapili Veri Seti Kodlaniyor...")
    np.random.seed(101)
    n = 8500
    
    bilissel = ["Akalkuli", "Afazi", "Dikkat_bozuklugu", "Deja_vu", "Disosiasyon", "Disfazi", "Halusinasyon", "Ilizyon", "Bellek_bozuklugu", "Ihmal", "Zorlu_dusunce", "Yanitlilikta_bozulma"]
    emosyonel = ["Ajitasyon", "Ofke", "Anksiyete", "Aglama", "Korku", "Gulme", "Paranoya", "Keyif"]
    otonomik = ["Asistol", "Bradikardi", "Ereksiyon", "Flasing", "Gastrointestinal", "Hipervantilasyon", "Mide_bulantisi", "Solukluk", "Palpitasyon", "Piloereksiyon", "Solunum_degisikligi", "Tasikardi"]
    otomatizma = ["Agresyon", "Goz_kirpma", "Bas_sallama", "Manuel_otomatik", "Oral_fasial", "Pedal_cevirme", "Pelvik_kaldirma", "Perseverasyon", "Kosma", "Seksksuel", "Ust_cikarma", "Vokalizasyon", "Yurume"]
    motor = ["Dizartri", "Distonik", "Eskrimci_pozisyonu", "Inkoordinasyon", "Jacksonian", "Paralizi", "Parezi", "Versif"]
    duyusal = ["Isitsel", "Gustatuar", "Sicaklama", "Olfaktor", "Somatosensoriyel", "Vestibuler", "Gorsel"]
    
    data = {'Yas': np.random.randint(1, 85, n), 'Cinsiyet': np.random.choice([0, 1], n), 
            'Lateralite': np.random.choice(['Sol', 'Sag', 'Bilateral', 'Bilinmeyen'], n, p=[0.25, 0.25, 0.4, 0.1]),
            'Atak_Suresi': np.random.randint(5, 1200, n)} 
            
    all_symp = bilissel + emosyonel + otonomik + otomatizma + motor + duyusal
    for f in all_symp:
        data[f] = np.random.choice([0, 1], p=[0.95, 0.05], size=n)
        
    # Ayirici Tani (Differential Diagnosis) & Provoke Oznitelikleri
    data['Goz_kapatma'] = np.random.choice([0, 1], p=[0.9, 0.1], size=n)
    data['Tetikleyici_Ayakta'] = np.random.choice([0, 1], p=[0.93, 0.07], size=n)
    data['Postiktal_Konfuzyon'] = np.random.choice([0, 1], p=[0.6, 0.4], size=n)
    data['Gecirilmis_MSS'] = np.random.choice([0, 1], p=[0.95, 0.05], size=n)
    data['Metabolik_Bozukluk'] = np.random.choice([0, 1], p=[0.95, 0.05], size=n)
    data['Madde_Yoksunlugu'] = np.random.choice([0, 1], p=[0.97, 0.03], size=n)
    
    data['Uykuda_Nobet'] = np.random.choice([0, 1], p=[0.9, 0.1], size=n)
    data['Beyin_Hasari'] = np.random.choice([0, 1], p=[0.95, 0.05], size=n)
    
    etiyolojiler = ['Yapisal', 'Genetik', 'Infeksiyoz', 'Metabolik', 'Immun', 'Bilinmeyen']
    data['Etiyoloji'] = np.random.choice(etiyolojiler, size=n)
    
    df = pd.DataFrame(data)
    y = []
    
    for i in range(n):
        row = df.iloc[i]
        sum_focal = sum(row[f] for f in duyusal + otomatizma)
        lat = row['Lateralite']
        duration = row['Atak_Suresi']
            
        if row['Gecirilmis_MSS'] or row['Metabolik_Bozukluk'] or row['Madde_Yoksunlugu']:
            diag = "Akut Semptomatik (Provoke) Nöbet"
        elif row['Goz_kapatma'] and duration > 600:
            diag = "Psikojenik Non-Epileptik Nöbet (PNES) Şüphesi"
        elif row['Tetikleyici_Ayakta'] and duration < 30 and not row['Postiktal_Konfuzyon']:
            diag = "Senkop (Bayılma) Şüphesi"
        else:
            if row['Yas'] < 16 and row['Dikkat_bozuklugu'] and row['Goz_kirpma']:
                diag = "Jeneralize Baslangic (Non-Motor / Absans)"
            elif sum_focal > 0 or lat in ['Sol', 'Sag']:
                if lat == 'Bilateral' and sum(row[m] for m in motor) > 0:
                    diag = "Fokalden Bilateral Tonik-Klonige Gecis"
                elif sum(row[m] for m in motor) > 0 or sum(row[m] for m in otomatizma) > 0:
                    diag = "Fokal Baslangic (Motor Oznitelikli)"
                else:
                    diag = "Fokal Baslangic (Non-Motor Oznitelikli)"
            else:
                if lat == 'Bilateral' and sum(row[m] for m in motor) > 0:
                    diag = "Jeneralize Baslangic (Motor / Tonik-Klonik)"
                else:
                    diag = "Bilinmeyen Baslangic (Siniflandirilmayan)"
                    
        y.append(diag)
        
    df['ILAE_Diagnosis'] = y
    
    is_jeneralize = df['ILAE_Diagnosis'].str.contains("Jeneralize").astype(int)
    df['EEG_Baglanti_Yogunlugu'] = np.clip(np.random.normal(0.4 + is_jeneralize*0.3, 0.1, n), 0, 1)
    df['fMRI_Kumelenme_Katsayisi'] = np.clip(np.random.normal(0.4 + is_jeneralize*0.2, 0.1, n), 0, 1)
    
    os.makedirs("data", exist_ok=True)
    df.to_csv(os.path.join("data", "ilae_v3_dataset.csv"), index=False)
    print("Dataset V3 Basariyla Olusturuldu!")

if __name__ == '__main__':
    generate()

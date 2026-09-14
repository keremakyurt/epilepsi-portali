import pandas as pd
import numpy as np
import os

def generate_exact_survey_dataset(n_samples=8500, output_path=os.path.join("data", "ilae_v3_dataset.csv")):
    """
    TÜBİTAK 2209-A: Epilepsi, PNEN ve Senkop Ayırıcı Tanı Kapsamlı Karar Ağacı Anketi
    Bu veri seti Kerem Akyurt ve Özge Orhan tarafından hazırlanan karar ağacı anket formuna 
    %100 birebir uygun olarak hazırlanmıştır.
    """
    print(f"Resmi Anket Formuna Uygun Klinik Veri Seti Üretiliyor ({n_samples} vaka)...")
    np.random.seed(42)
    
    # Demografik
    yas = np.random.randint(1, 85, n_samples)
    cinsiyet = np.random.choice([0, 1], n_samples) # 0: Kadın, 1: Erkek
    
    # =========================================================================
    # 1. ÖZGEÇMİŞ VE GENEL RİSK FAKTÖRLERİ (Sorular 1 - 8)
    # =========================================================================
    # 1.1 Kafa travması, inme, menenjit öyküsü (Yapısal/Semptomatik Epilepsi)
    s1_gecmis_beyin = np.random.choice([0, 1], n_samples, p=[0.88, 0.12])
    # 1.2 Ailede epilepsi veya çocukluk febril nöbet (Genetik Jeneralize)
    s1_aile_febril = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    # 1.3 Psikiyatrik hastalık (anksiyete, depresyon, konversiyon) veya sekonder kazanç (PNEN)
    s1_psikiyatri = np.random.choice([0, 1], n_samples, p=[0.80, 0.20])
    # 1.4 Bilinen kardiyolojik rahatsızlık (aritmi vb.) (Kardiyojenik Senkop)
    s1_kardiyo = np.random.choice([0, 1], n_samples, p=[0.90, 0.10])
    # 1.5 Sabahları uyanınca ani irkilme/sıçramalar (JME)
    s1_jme_sicrama = np.random.choice([0, 1], n_samples, p=[0.92, 0.08])
    # 1.6 Uykusuzluk, fotik stimülasyon (yanıp sönen ışık) veya ses tetiklemesi (Refleks Epilepsi)
    s1_fotik_tetik = np.random.choice([0, 1], n_samples, p=[0.88, 0.12])
    # 1.7 Geçmişte ağır psikolojik travma / aşırı stres öyküsü (PNEN)
    s1_psikolojik_travma = np.random.choice([0, 1], n_samples, p=[0.82, 0.18])
    # 1.8 Akut Provokasyon (Son 7 günde akut inme/travma, ağır hipoglisemi veya alkol yoksunluğu)
    s1_akut_provokasyon = np.random.choice([0, 1], n_samples, p=[0.92, 0.08])

    # =========================================================================
    # 2. ATAK ÖNCESİ (AURA VE PRODROMAL DÖNEM) - Hastaya Sorulacaklar (Sorular 1 - 6)
    # =========================================================================
    # 2.1 Mideden yukarı yükselme hissi - gastrointestinal aura (Fokal Otonomik)
    s2_aura_gastro = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    # 2.2 Anlamsız korku, kaygı, anlamsız gülme/ağlama (Fokal Emosyonel)
    s2_aura_emosyonel = np.random.choice([0, 1], n_samples, p=[0.88, 0.12])
    # 2.3 Deja vu, yabancı yeri tanıdık sanma, halüsinasyon, zorlu düşünce (Fokal Bilişsel)
    s2_aura_dejavu = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    # 2.4 Yanık lastik kokusu (olfaktör aura) veya görme alanı değişiklikleri (Fokal Duyusal)
    s2_aura_koku_gorme = np.random.choice([0, 1], n_samples, p=[0.90, 0.10])
    # 2.5 Terleme artışı, göz kararması, çarpıntı, solukluk (Vazovagal / Kardiyojenik Senkop)
    s2_presenkop = np.random.choice([0, 1], n_samples, p=[0.82, 0.18])
    # 2.6 Uzun süre ayakta kalma veya aniden ayağa kalkma tetiklemesi (Ortostatik / Refleks Senkop)
    s2_tetik_ayakta = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])

    # =========================================================================
    # 3. ATAK ANI (İKTAL DÖNEM) - Tanıklara ve Hastaya Sorulacaklar (Sorular 1 - 17)
    # =========================================================================
    # 3.1 Ataklar hep yalnızken mi (1: Epilepsi), sadece belli kişilerin yanındayken mi (0: PNEN)
    s3_yalnizken_vs_seyirci = np.random.choice([0, 1], n_samples, p=[0.30, 0.70])
    # 3.2 Uykuda iken (1: Epilepsi/Parasomni) / Sadece uyanıkken (0: PNEN/Senkop)
    s3_uykuda_vs_uyanik = np.random.choice([0, 1], n_samples, p=[0.80, 0.20])
    # 3.3 Başlama şekli: Ani (1: Epilepsi) / Kademeli (0: PNEN)
    s3_baslama_ani = np.random.choice([0, 1], n_samples, p=[0.40, 0.60])
    # 3.4 Atak süresi: Saniyeler (0: Senkop) / 1-5 dk benzer (1: Epilepsi) / >10 dk değişken (2: PNEN)
    s3_sure_kategori = np.random.choice([0, 1, 2], n_samples, p=[0.20, 0.55, 0.25])
    # 3.5 Gözler: Açık/Yukarı sabit (1: Epilepsi) / Kapalı, açmaya dirençli (0: PNEN)
    s3_gozler_durumu = np.random.choice([0, 1], n_samples, p=[0.25, 0.75])
    # 3.6 Yüz rengi: Siyanoz/Mor (1: Epilepsi) / Soluk/Beyaz (0: Senkop/PNEN)
    s3_yuz_rengi = np.random.choice([0, 1], n_samples, p=[0.45, 0.55])
    # 3.7 Kasılma şekli: Koordineli tonik-klonik sıçrama (1: Epilepsi) / Karın atması, bisiklet, çırpınma (0: PNEN)
    s3_kasilma_sekli = np.random.choice([0, 1], n_samples, p=[0.30, 0.70])
    # 3.8 Başın sağa/sola dönmesi (versif) sonrası yaygın kasılma (Fokalden Bilateral Tonik-Kloniğe Geçiş)
    s3_versif_bas_donmesi = np.random.choice([0, 1], n_samples, p=[0.80, 0.20])
    # 3.9 Ağız şapırdatma, çiğneme, etrafı arama - otomatizma (Fokal Motor Başlangıçlı)
    s3_otomatizma = np.random.choice([0, 1], n_samples, p=[0.82, 0.18])
    # 3.10 Dil/Dudak ısırma: Dilin Yan Tarafı (1: Epilepsi) / Dil Ucu veya Dudak (0: PNEN) / Yok (2)
    s3_dil_isirma = np.random.choice([0, 1, 2], n_samples, p=[0.15, 0.25, 0.60])
    # 3.11 İdrar veya gaita kaçırma (inkontinans) (1: Epilepsi, PNEN'de çok nadir)
    s3_inkontinans = np.random.choice([0, 1], n_samples, p=[0.80, 0.20])
    # 3.12 Gece uykudan uyanıp sinirlilik, yataktan inme (Nokturnal Frontal Lob Epilepsisi / NREM Parasomni)
    s3_nokturnal_atak = np.random.choice([0, 1], n_samples, p=[0.93, 0.07])
    # 3.13 Pupiller ışık refleksinin korunması (1: Evet PNEN / 0: Hayır, refleks kayıp Epilepsi / 2: Bilinmiyor)
    s3_pupil_refleks = np.random.choice([0, 1, 2], n_samples, p=[0.20, 0.35, 0.45])
    # 3.14 Pelvik itme (thrusting) hareketi: Evet (0: PNEN) / Hayır (1: Senkopta ASLA görülmez, Epilepside nadir)
    s3_pelvik_itme = np.random.choice([0, 1], n_samples, p=[0.15, 0.85])
    # 3.15 Ses ve solunum: Başlangıçta ani çığlık + hırıltı (1: Epilepsi) / Anlaşılır kelime, inleme, hızlı nefes (0: PNEN)
    s3_ses_solunum = np.random.choice([0, 1], n_samples, p=[0.40, 0.60])
    # 3.16 İnsanların varlığı/ilgisi nöbet şiddetini artırıyor mu: Evet (0: PNEN) / Hayır (1: Epilepsi)
    s3_seyirci_etkisi = np.random.choice([0, 1], n_samples, p=[0.20, 0.80])
    # 3.17 Atak sıklığı: Günde birkaç kez çok sık (0: PNEN) / Seyrek haftada-ayda bir (1: Epilepsi)
    s3_atak_sikligi = np.random.choice([0, 1], n_samples, p=[0.25, 0.75])

    # =========================================================================
    # 4. ATAK SONRASI DÖNEM (POST-İKTAL) - Tanıklara ve Hastaya Sorulacaklar (Sorular 1 - 5)
    # =========================================================================
    # 4.1 Konfüzyon: Atak bitiminde bilinç bulanıklığı var mı (1: Epilepsi) / Anında tanıyor mu (0: PNEN/Senkop)
    s4_postiktal_konfuzyon = np.random.choice([0, 1], n_samples, p=[0.60, 0.40])
    # 4.2 Amnezi: Atağın gerçekleştiği anı hatırlamıyor mu (1: Epilepsi/Senkop) / Hatırlıyor mu (0)
    s4_amnezi = np.random.choice([0, 1], n_samples, p=[0.30, 0.70])
    # 4.3 Atak biter bitmez ağlama krizi yaşanıyor mu (1: PNEN / 0: Hayır)
    s4_aglama_krizi = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    # 4.4 Ciddi travmatik yaralanma (kafa dikişi, kırık vb.) oldu mu (1: Epilepsi / 0: Hayır)
    s4_ciddi_travma = np.random.choice([0, 1], n_samples, p=[0.90, 0.10])
    # 4.5 Peş peşe gelen ataklar arası durum: Normale dönüyor (0: PNEN) / Uyku-sersemlik sürüyor (1: Epilepsi)
    s4_kume_arasi_bilinc = np.random.choice([0, 1], n_samples, p=[0.30, 0.70])

    # DataFrame Oluşturma
    df = pd.DataFrame({
        'Yas': yas,
        'Cinsiyet': cinsiyet,
        'S1_Gecmis_Beyin_Hasari': s1_gecmis_beyin,
        'S1_Aile_Epilepsi_Febril': s1_aile_febril,
        'S1_Psikiyatrik_Hastalik': s1_psikiyatri,
        'S1_Kardiyolojik_Hastalik': s1_kardiyo,
        'S1_JME_Sabah_Sicramalari': s1_jme_sicrama,
        'S1_Fotik_Tetik_Isik': s1_fotik_tetik,
        'S1_Psikolojik_Agir_Travma': s1_psikolojik_travma,
        'S1_Akut_Provokasyon_Neden': s1_akut_provokasyon,
        
        'S2_Aura_Gastrointestinal': s2_aura_gastro,
        'S2_Aura_Emosyonel': s2_aura_emosyonel,
        'S2_Aura_Dejavu_Bilisel': s2_aura_dejavu,
        'S2_Aura_Koku_Gorme_Duyusal': s2_aura_koku_gorme,
        'S2_Prodrom_Terleme_Solukluk': s2_presenkop,
        'S2_Tetik_Ayakta_Ortostatik': s2_tetik_ayakta,
        
        'S3_Yalnizken_vs_Seyirci': s3_yalnizken_vs_seyirci,
        'S3_Uykuda_vs_Uyanik': s3_uykuda_vs_uyanik,
        'S3_Baslama_Ani_vs_Kademeli': s3_baslama_ani,
        'S3_Sure_Kategori': s3_sure_kategori,
        'S3_Gozlerin_Durumu': s3_gozler_durumu,
        'S3_Yuz_Rengi_Siyanoz': s3_yuz_rengi,
        'S3_Kasilma_Sekli': s3_kasilma_sekli,
        'S3_Versif_Bas_Donmesi': s3_versif_bas_donmesi,
        'S3_Otomatizma': s3_otomatizma,
        'S3_Dil_Isirma_Lokalizasyonu': s3_dil_isirma,
        'S3_Inkontinans': s3_inkontinans,
        'S3_Nokturnal_Parasomni_Atak': s3_nokturnal_atak,
        'S3_Pupil_Isik_Refleksi': s3_pupil_refleks,
        'S3_Pelvik_Itme_Hareketi': s3_pelvik_itme,
        'S3_Ses_Solunum_Paterni': s3_ses_solunum,
        'S3_Seyirci_Ilgi_Etkisi': s3_seyirci_etkisi,
        'S3_Atak_Sikligi': s3_atak_sikligi,
        
        'S4_Postiktal_Konfuzyon': s4_postiktal_konfuzyon,
        'S4_Amnezi_Var_mi': s4_amnezi,
        'S4_Aglama_Krizi': s4_aglama_krizi,
        'S4_Ciddi_Travmatik_Yaralanma': s4_ciddi_travma,
        'S4_Kume_Ataklar_Arasi_Durum': s4_kume_arasi_bilinc
    })

    # Algoritmik Yönelim & Etiketleme Mantığı
    labels = []
    for i in range(n_samples):
        row = df.iloc[i]
        
        # 1. Akut Provoke Nöbet Kontrolü
        if row['S1_Akut_Provokasyon_Neden'] == 1:
            tani = "Akut Semptomatik (Provoke) Nöbet"
            
        # 2. PNEN (Psikojenik Non-Epileptik Nöbet) Şüphesi
        # Gözler kapalı/açmaya dirençli (0), pelvik itme (0), kademeli başlama (0), ağlama krizi, seyirci varlığı
        elif (row['S3_Gozlerin_Durumu'] == 0 and (row['S3_Pelvik_Itme_Hareketi'] == 0 or row['S4_Aglama_Krizi'] == 1 or row['S3_Sure_Kategori'] == 2)) or \
             (row['S3_Pelvik_Itme_Hareketi'] == 0 and row['S3_Dil_Isirma_Lokalizasyonu'] != 1 and row['S3_Baslama_Ani_vs_Kademeli'] == 0) or \
             (row['S1_Psikiyatrik_Hastalik'] == 1 and row['S3_Gozlerin_Durumu'] == 0 and row['S3_Atak_Sikligi'] == 0 and row['S4_Kume_Ataklar_Arasi_Durum'] == 0):
            tani = "Psikojenik Non-Epileptik Nöbet (PNEN / Konversiyon)"
            
        # 3. Senkop (Vazovagal / Ortostatik / Kardiyojenik)
        elif (row['S2_Prodrom_Terleme_Solukluk'] == 1 or row['S2_Tetik_Ayakta_Ortostatik'] == 1 or row['S1_Kardiyolojik_Hastalik'] == 1) and \
             row['S3_Sure_Kategori'] == 0 and row['S4_Postiktal_Konfuzyon'] == 0 and row['S3_Dil_Isirma_Lokalizasyonu'] != 1:
            if row['S1_Kardiyolojik_Hastalik'] == 1 and row['S2_Tetik_Ayakta_Ortostatik'] == 0:
                tani = "Kardiyojenik Senkop"
            else:
                tani = "Vazovagal / Ortostatik Senkop"
                
        # 4. Epilepsi Alt Tipleri
        else:
            # JME (Sabah sıçramaları + fotik tetiklenme)
            if row['S1_JME_Sabah_Sicramalari'] == 1 and (row['S1_Fotik_Tetik_Isik'] == 1 or row['Yas'] < 25):
                tani = "Epilepsi - Juvenil Miyoklonik (JME)"
            # Nokturnal Frontal Lob / NREM Parasomni
            elif row['S3_Nokturnal_Parasomni_Atak'] == 1 and row['S3_Uykuda_vs_Uyanik'] == 1:
                tani = "Epilepsi - Nokturnal (Uykuda Gelen Nöbet)"
            # Fokalden Bilateral Tonik-Kloniğe Geçiş
            elif row['S3_Versif_Bas_Donmesi'] == 1 and row['S3_Kasilma_Sekli'] == 1:
                tani = "Epilepsi - Fokalden Bilateral Tonik-Kloniğe Geçiş"
            # Fokal Başlangıçlı (Aura veya Otomatizma ile)
            elif (row['S2_Aura_Gastrointestinal'] == 1 or row['S2_Aura_Emosyonel'] == 1 or 
                  row['S2_Aura_Dejavu_Bilisel'] == 1 or row['S2_Aura_Koku_Gorme_Duyusal'] == 1 or 
                  row['S3_Otomatizma'] == 1):
                tani = "Epilepsi - Fokal Başlangıçlı Nöbet (Auralı/Otomatizmalı)"
            # Jeneralize Tonik-Klonik (Büyük nöbet)
            elif row['S3_Kasilma_Sekli'] == 1 or row['S3_Dil_Isirma_Lokalizasyonu'] == 1 or row['S3_Yuz_Rengi_Siyanoz'] == 1:
                tani = "Epilepsi - Jeneralize Tonik-Klonik (GTC)"
            else:
                tani = "Epilepsi - Sınıflandırılamayan / Belirsiz Başlangıçlı"
                
        labels.append(tani)
        
    df['Karar_Agaci_Tanisi'] = labels
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Resmi anket formuna uygun saf klinik veri seti oluşturuldu: {output_path}")
    print("\n--- Sınıf Dağılımı ---")
    print(df['Karar_Agaci_Tanisi'].value_counts())
    return df

if __name__ == '__main__':
    generate_exact_survey_dataset()

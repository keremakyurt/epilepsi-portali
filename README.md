# TÜBİTAK 2209-A: Epilepsi, PNEN ve Senkop Ayırıcı Tanı Kapsamlı Karar Ağacı Portalı

**Proje Başlığı:** Epilepsi Tanısı İçin Nicel Veri Madenciliği ve Yapay Zeka Algoritmaları  
**Yürütücüler:** Kerem Akyurt, Özge Orhan  
**Danışman:** Doç. Dr. Nermin Tepe *(Balıkesir Üniversitesi Tıp Fakültesi Nöroloji Anabilim Dalı)*  
**Program:** TÜBİTAK 2209-A Üniversite Öğrencileri Araştırma Projeleri Destekleme Programı  

---

## 🎯 Projenin Amacı ve Kapsamı

Epilepsi klinik bir tanıdır. Bu çalışma; hiçbir EEG, fMRI veya laboratuvar tetkikine ihtiyaç duymadan, hastayla ilk karşılaşan **aile hekimleri**, **acil tıp uzmanları** ve **nöroloji hekimlerinin** hasta veya refakatçisinden alacağı **standardize edilmiş klinik karar ağacı anketi ve fiziksel gözlemler** vasıtasıyla:
1. **Gerçek Epileptik Nöbetler** (Fokal Auralı/Otomatizmalı, Jeneralize Tonik-Klonik, JME, Nokturnal vb.),
2. **Senkop** (Vazovagal, Ortostatik, Kardiyojenik),
3. **Psikojenik Non-Epileptik Nöbet** (PNEN / Konversiyon),
4. **Akut Semptomatik (Provoke) Nöbet** (Travma, akut inme, hipoglisemi, yoksunluk)

ayrımını yapmayı, hekime objektif tanı olasılıkları sunmayı, taklitçileri ayırt edici klinik ipuçlarını göstermeyi ve takip/sevk algoritmaları sağlamayı amaçlamaktadır.

---

## 🔬 Karar Ağacı Anket Yapısı (4 Temel Faz)

1. **Bölüm 1: Özgeçmiş ve Genel Risk Faktörleri (Sorular 1 - 8)**
   - Kafa travması/inme/menenjit, ailede epilepsi/febril nöbet, psikiyatrik hastalık/sekonder kazanç, kardiyolojik öykü, sabah JME sıçramaları, fotik/ses stimülasyonu, psikolojik travma ve akut provokasyon kontrolü.
2. **Bölüm 2: Atak Öncesi (Aura ve Prodromal Dönem) - Hastaya Sorulacaklar (Sorular 1 - 6)**
   - Gastrointestinal yükselme aurası, anlamsız korku/kaygı/jelastik-dakristik atak, deja-vu/bilişsel hisler, koku/görme aurası, presenkop (terleme, kararma, solukluk), uzun süre ayakta kalma/ortostatik tetikleyici.
3. **Bölüm 3: Atak Anı (İktal Dönem) - Tanıklara ve Hastaya Sorulacaklar (Sorular 1 - 17)**
   - Yalnızken vs. seyirci varlığı, uykuda vs. uyanık, ani vs. kademeli başlama, atak süresi kategorisi, gözlerin açık/kapalı durumu ve açmaya aktif direnç, siyanoz vs. solukluk, koordineli tonik-klonik vs. düzensiz çırpınma, versif baş dönmesi, otomatizmalar, dilin yan kenarı vs. uç ısırığı, inkontinans, nokturnal atak, pupil ışık refleksi, pelvik itme (thrusting), ses/solunum paterni (iktal çığlık vs. inleme), seyirci ilgisinin nöbete etkisi, atak sıklığı.
4. **Bölüm 4: Atak Sonrası Dönem (Post-iktal) - Tanıklara ve Hastaya Sorulacaklar (Sorular 1 - 5)**
   - Postiktal konfüzyon (>15 dk) vs. anında kendine gelme, amnezi, ağlama krizi, ciddi travmatik yaralanma, peş peşe gelen ataklar arasındaki bilinç durumu.

---

## 📂 Dosya ve Model Yapısı

```
d:/epilepsy_project/
├── data/
│   └── ilae_v3_dataset.csv     # Resmi anket formatında 8.500 vaka kaydı
├── models/
│   ├── rf_epilepsy_model.pkl   # Random Forest Sınıflandırıcısı (%96.18 Doğruluk)
│   ├── knn_epilepsy_model.pkl  # KNN Sınıflandırıcısı (%70.94 Doğruluk)
│   ├── scaler.pkl              # Normalizasyon ölçekleyicisi
│   └── metadata.pkl            # Model sınıfları, özellik adları ve önem skorları
├── .venv/                      # Python 3.12 sanal ortamı
├── app.py                      # 3 Sekmeli Streamlit Karar Destek Portalı
├── model.py                    # Model eğitimi ve öznitelik önem analiz script'i
├── generate_ilae.py            # Resmi ankete uygun veri seti üreteci
├── requirements.txt            # Python bağımlılıkları
└── README.md                   # Proje dokümantasyonu
```

---

## 🚀 Çalıştırma

### Karar Destek Arayüzünü Başlatma:
```powershell
.\.venv\Scripts\streamlit run app.py
```
Tarayıcınızda `http://localhost:8501` adresinden arayüze erişebilirsiniz.

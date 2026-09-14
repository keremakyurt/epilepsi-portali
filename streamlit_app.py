import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="Epilepsi Veri Ambarı ve Hasta Kayıt Portalı",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Koyu / Açık Tema Uyumlu Özel Tasarım (High Contrast)
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        opacity: 0.85;
        margin-bottom: 1.2rem;
    }
    .section-title {
        background: linear-gradient(90deg, #1e3d59, #2b6cb0);
        color: #ffffff !important;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .card-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }
    .card-box p {
        color: inherit !important;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-top: 6px;
    }
    .card-box strong {
        color: inherit !important;
    }
    .card-epilepsy { border-left: 6px solid #ef4444 !important; background-color: rgba(239, 68, 68, 0.12) !important; }
    .card-syncope { border-left: 6px solid #3b82f6 !important; background-color: rgba(59, 130, 246, 0.12) !important; }
    .card-pnes { border-left: 6px solid #a855f7 !important; background-color: rgba(168, 85, 247, 0.12) !important; }
    .metric-title { font-weight: 700; font-size: 1.15rem; margin-bottom: 6px; color: inherit !important; }
    div.stButton > button {
        background-color: #2b6cb0;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.65rem 1.5rem;
        border: none;
    }
    div.stButton > button:hover { background-color: #1e3d59; color: #f7fafc; }
</style>
""", unsafe_allow_html=True)

DATA_PATH = os.path.join("data", "hasta_veri_ambari.csv")
os.makedirs("data", exist_ok=True)

# Google Sheets Yapılandırması (Secrets veya Arayüz Girişi)
def get_gsheets_config():
    webhook_url = ""
    csv_url = ""
    try:
        if "GSHEETS_WEBHOOK_URL" in st.secrets:
            webhook_url = st.secrets["GSHEETS_WEBHOOK_URL"]
        if "GSHEETS_CSV_URL" in st.secrets:
            csv_url = st.secrets["GSHEETS_CSV_URL"]
    except Exception:
        pass
    if not webhook_url and "gsheets_webhook_url" in st.session_state:
        webhook_url = st.session_state["gsheets_webhook_url"]
    if not csv_url and "gsheets_csv_url" in st.session_state:
        csv_url = st.session_state["gsheets_csv_url"]
    return str(webhook_url).strip(), str(csv_url).strip()

# Veri Ambarını Yükleme Yardımcısı (Hibrit: Bulut E-Tablo / Yerel CSV)
def load_warehouse():
    webhook_url, csv_url = get_gsheets_config()
    if csv_url:
        try:
            df_cloud = pd.read_csv(csv_url)
            if not df_cloud.empty:
                return df_cloud
        except Exception:
            pass
    if os.path.exists(DATA_PATH):
        try:
            return pd.read_csv(DATA_PATH)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

# Veri Ambarına Kaydetme Yardımcısı (Yerel CSV + Canlı Google Sheets)
def append_patient_to_warehouse(patient_record):
    df_existing = load_warehouse()
    df_new = pd.DataFrame([patient_record])
    
    if df_existing.empty:
        df_updated = df_new
    else:
        df_updated = pd.concat([df_existing, df_new], ignore_index=True)
        
    df_updated.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
    
    # Canlı Google Sheets Senkronizasyonu
    webhook_url, _ = get_gsheets_config()
    cloud_synced = None
    if webhook_url:
        try:
            resp = requests.post(webhook_url, json=patient_record, timeout=8)
            if resp.status_code in [200, 201, 302]:
                cloud_synced = True
            else:
                cloud_synced = False
        except Exception:
            cloud_synced = False
            
    return len(df_updated), cloud_synced

st.markdown('<div class="main-header">📋 Klinik Karar Ağacı — Hasta Kayıt ve Veri Ambarı Portalı</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">TÜBİTAK 2209-A: Danışıklı Öğrenme (Supervised Learning) Öncesi Standart Hasta Verisi Toplama Sistemi</div>', unsafe_allow_html=True)

df_warehouse = load_warehouse()
vaka_sayisi = len(df_warehouse)

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Hasta Değerlendirme & Veri Girişi",
    f"📦 Hasta Veri Ambarı ({vaka_sayisi} Kayıtlı Hasta)",
    "👁️ Taklitçiler ve Karşılaştırma Rehberi",
    "💊 Tedavi, Takip ve Sevk Protokolü"
])

# ==============================================================================
# SEKME 1: HASTA DEĞERLENDİRME & VERİ AMBARINA KAYIT
# ==============================================================================
with tab1:
    st.info(f"💡 **Veri Toplama Modu Aktif:** Bu form poliklinikte veya serviste değerlendirilen hastaların verilerini standart karar ağacı formatında toplar. Şu ana kadar toplanan vaka sayısı: **{vaka_sayisi}**")
    
    col_meta1, col_meta2, col_meta3 = st.columns(3)
    with col_meta1:
        default_protokol = f"VAKA_{vaka_sayisi + 1:04d}"
        protokol_no = st.text_input("Anonim Protokol / Dosya No", value=default_protokol, help="Hastanın kimlik bilgilerini gizli tutmak için otomatik üretilen kod.")
    with col_meta2:
        hekim_rolleri = [
            "Dr. Kerem Akyurt",
            "Dr. Özge Orhan",
            "Doç. Dr. Nermin Tepe (Danışman / Klinik Sorumlusu)",
            "Nöroloji Poliklinik Hekimi / Asistanı",
            "Acil Tıp Hekimi / Nöbetçi Hekim",
            "Diğer (İsim Giriniz)"
        ]
        secilen_hekim = st.selectbox("Değerlendiren Hekim / Görev", hekim_rolleri, index=0)
        if secilen_hekim == "Diğer (İsim Giriniz)":
            doktor_adi = st.text_input("Hekim Adı ve Ünvanı", placeholder="Örn: Dr. Ahmet Yılmaz")
            if not doktor_adi.strip():
                doktor_adi = "Diğer Hekim"
        else:
            doktor_adi = secilen_hekim
    with col_meta3:
        tarih_saat = st.text_input("Kayıt Tarihi", value=datetime.now().strftime("%d.%m.%Y %H:%M"))

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">👤 Hasta Demografik Bilgileri</div>', unsafe_allow_html=True)
        c_dem1, c_dem2 = st.columns(2)
        with c_dem1:
            yas = st.number_input("Hastanın Yaşı", min_value=1, max_value=105, value=25)
        with c_dem2:
            cins = st.selectbox("Cinsiyet", [1, 0], format_func=lambda x: "Erkek" if x==1 else "Kadın")
            
        st.markdown('<div class="section-title">📋 1. Hastaya Sorulacak Sorular (10 Soru)</div>', unsafe_allow_html=True)
        
        # H1
        h1 = st.radio("1. Atak başlangıcında anlamsız korku oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # H2
        h2 = st.radio("2. Atak başlangıcında anlamsız gülme atağı oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # H3
        h3 = st.radio("3. Atak başlangıcında anlamsız ağlama atağı oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # H4
        h4 = st.radio("4. Atak başlangıcında mideden yemek borusuna doğru yükselme hissi oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # H5 (Evet: 0, Hayır: 1)
        h5_val = st.radio("5. Atak başlangıcında çarpıntı oluyor mu?",
                          [0, 1], format_func=lambda x: "Evet (0 Puan)" if x==0 else "Hayır (1 Puan)", index=1)
        # H6 (Evet: 0, Hayır: 1)
        h6_val = st.radio("6. Atak başlangıcında terleme artışı, gözlerde kararma oluyor mu?",
                          [0, 1], format_func=lambda x: "Evet (0 Puan)" if x==0 else "Hayır (1 Puan)", index=1)
        # H7 (Evet: 0, Hayır: 1)
        h7_val = st.radio("7. Ataklar hep yalnızken, etrafta kimse yokken mi oluyor?",
                          [0, 1], format_func=lambda x: "Evet (0 Puan)" if x==0 else "Hayır (1 Puan)", index=1)
        # H8 (Evet: 0, Hayır: 1)
        h8_val = st.radio("8. Ataklar sonrası ağlama oluyor mu?",
                          [0, 1], format_func=lambda x: "Evet (0 Puan)" if x==0 else "Hayır (1 Puan)", index=1)
        # H9
        h9 = st.radio("9. Sabahları daha çok olmak üzere gün içinde ani irkilme şeklinde sıçramalar oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # H10
        h10 = st.radio("10. Ataklarda düşme sonucu kafaya dikiş atılması, kol-bacak alçıya alınma durumu oldu mu?",
                       [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)

    with col2:
        st.markdown('<div class="section-title">👁️ 2. Atak Anına Tanık Olanlara Sorulacak Sorular (12 Soru)</div>', unsafe_allow_html=True)
        
        # T1
        t1 = st.radio("11. Gözler atak sırasında açık mı?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # T2
        t2 = st.radio("12. Gözler yukarı doğru sabit mi?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # T3 (Evet: 0, Hayır: 1)
        t3_val = st.radio("13. Göz bebekleri hareket ediyor ya da göz kapakları kapalı açmak istenince hasta sıkıyor mu?",
                          [0, 1], format_func=lambda x: "Evet (0 Puan)" if x==0 else "Hayır (1 Puan)", index=1)
        # T4 (Evet: 0, Hayır: 1)
        t4_val = st.radio("14. Atak bitiminde hasta etrafını tanıyor mu, sorulara mantıklı cevap veriyor mu?",
                          [0, 1], format_func=lambda x: "Evet (0 Puan)" if x==0 else "Hayır (1 Puan)", index=1)
        # T5
        t5 = st.radio("15. Atakları hep 1-5 dk mı sürüp sonlanıyor?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # T6
        t6 = st.radio("16. Bütün atakları aynı sürede mi bitiyor?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # T7
        t7 = st.radio("17. Ataklar sırasında ağız şapırdatma, çiğneme, tükürme, boş etrafa bakma veya otomatizma hareketleri var mı?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # T8
        t8 = st.radio("18. Ataklarda gece aniden uykudan uyandırma ve sinirlilik, huzursuzluk, yataktan inme, etrafa zarar verme şeklinde kontrolü zor, bilinç kaybı oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # T9
        t9 = st.radio("19. Ataklar başın sağ veya sola döndüğü, kol ve bacaklarda kasılma ve sonrasında sıçrama şeklinde mi sonlanıyor?",
                      [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)
        # T10 (Evet: 0, Hayır: 1)
        t10_val = st.radio("20. Ataklarda karın/göğüs yukarı aşağı hareketleri, bisiklet çevirme, başı sürekli sağa sola çevirme şeklinde mi?",
                           [0, 1], format_func=lambda x: "Evet (0 Puan)" if x==0 else "Hayır (1 Puan)", index=1)
        # T11 (Evet: 0, Hayır: 1)
        t11_val = st.radio("21. Ataklar sırasında yüzünün rengi bembeyaz veya sarı renkte mi oluyor?",
                           [0, 1], format_func=lambda x: "Evet (0 Puan)" if x==0 else "Hayır (1 Puan)", index=1)
        # T12
        t12 = st.radio("22. Ataklarda dil-dudak ısırma oluyor mu?",
                       [1, 0], format_func=lambda x: "Evet (1 Puan)" if x==1 else "Hayır (0 Puan)", index=1)

    # Toplam Puan Hesaplama
    toplam_epilepsi_puani = (
        h1 + h2 + h3 + h4 + h5_val + h6_val + h7_val + h8_val + h9 + h10 +
        t1 + t2 + t3_val + t4_val + t5 + t6 + t7 + t8 + t9 + t10_val + t11_val + t12
    )
    
    st.markdown("---")
    st.markdown('<div class="section-title">📊 Anlık Klinik Epilepsi Skoru Değerlendirmesi</div>', unsafe_allow_html=True)
    c_sc1, c_sc2 = st.columns([1, 2])
    with c_sc1:
        st.metric("Toplam Epilepsi Skoru", f"{toplam_epilepsi_puani} / 22")
    with c_sc2:
        if toplam_epilepsi_puani >= 15:
            st.success(f"🟢 **Yüksek Olasılıklı Epilepsi Bulguları ({toplam_epilepsi_puani}/22):** Anamnez bulguları kuvvetle epileptik nöbet lehinedir.")
        elif toplam_epilepsi_puani >= 9:
            st.warning(f"🟡 **Orta Düzey / Şüpheli Bulgular ({toplam_epilepsi_puani}/22):** Ayırıcı tanıda Senkop ve PNEN bulgularının detaylı irdelenmesi önerilir.")
        else:
            st.info(f"🔵 **Düşük Epilepsi Skoru ({toplam_epilepsi_puani}/22):** Bulgular Senkop veya Psikojenik Non-Epileptik Nöbet (PNEN) lehine ağırlıktadır.")

    st.markdown("---")
    st.markdown('<div class="section-title">🎯 Kesin Klinik Tanı Etiketi (Danışıklı Öğrenme - Supervised ML İçin)</div>', unsafe_allow_html=True)
    st.caption("İleride karar ağacı modelinin eğitilebilmesi için Nöroloji Uzmanı (Danışman Hoca / Klinik Kurul) tarafından konulan kesinleşmiş altın standart tanıyı seçiniz:")
    
    tani_secenekleri = [
        "Epilepsi - Fokal Başlangıçlı (Auralı/Otomatizmalı)",
        "Epilepsi - Jeneralize Tonik-Klonik (GTC)",
        "Epilepsi - Juvenil Miyoklonik (JME)",
        "Epilepsi - Nokturnal (Uykuda Gelen Nöbet)",
        "Epilepsi - Fokalden Bilateral Tonik-Kloniğe Geçiş",
        "Epilepsi - Sınıflandırılamayan / Belirsiz Başlangıçlı",
        "Vazovagal / Ortostatik Senkop",
        "Kardiyojenik Senkop",
        "Psikojenik Non-Epileptik Nöbet (PNEN / Konversiyon)",
        "Akut Semptomatik (Provoke) Nöbet",
        "Tanı Henüz Netleşmedi / Tetkik Aşamasında"
    ]
    kesin_tani = st.selectbox("Nöroloji Uzmanı Kesin Tanısı (Ground Truth Label)", tani_secenekleri, index=0)
    klinik_not = st.text_area("Klinik Seyir / Açıklama Notu (Opsiyonel)", placeholder="Örn: Hasta ilk kez başvurdu, ailede benzer öykü var, 1 ay sonra kontrole çağrıldı.")

    st.markdown("---")
    if st.button("💾 Bu Hastayı Veri Ambarına Kaydet", type="primary", use_container_width=True):
        yeni_hasta = {
            "Protokol_No": protokol_no,
            "Kayit_Tarihi": tarih_saat,
            "Kaydeden_Hekim": doktor_adi,
            "Yas": yas,
            "Cinsiyet": cins,
            
            # 1. Hastaya Sorulacak Sorular (Puanları)
            "H1_Anlamsiz_Korku": h1,
            "H2_Anlamsiz_Gulme": h2,
            "H3_Anlamsiz_Aglama": h3,
            "H4_Mideden_Yukselme": h4,
            "H5_Carpinti": h5_val,
            "H6_Terleme_Goz_Kararma": h6_val,
            "H7_Hep_Yalnizken": h7_val,
            "H8_Atak_Sonrasi_Aglama": h8_val,
            "H9_Sabah_Sicramalari": h9,
            "H10_Dusme_Dikis_Alci": h10,
            
            # 2. Atak Anına Tanık Olanlara Sorulacak Sorular (Puanları)
            "T1_Gozler_Acik": t1,
            "T2_Gozler_Yukari_Sabit": t2,
            "T3_Goz_Kapak_Sikma": t3_val,
            "T4_Etrafini_Tanima": t4_val,
            "T5_Hep_1_5_Dk": t5,
            "T6_Ayni_Surede_Bitis": t6,
            "T7_Agiz_Sapurdatma_Otomatizma": t7,
            "T8_Gece_Huzursuz_Uyanma": t8,
            "T9_Bas_Donmesi_Kasilma_Sicrama": t9,
            "T10_Karin_Gogus_Bisiklet_Hareket": t10_val,
            "T11_Yuz_Bembeyaz_Sari": t11_val,
            "T12_Dil_Dudak_Isirma": t12,
            
            "Toplam_Epilepsi_Skoru": toplam_epilepsi_puani,
            "Kesin_Klinik_Tani": kesin_tani,
            "Klinik_Not": klinik_not
        }
        
        toplam, cloud_ok = append_patient_to_warehouse(yeni_hasta)
        if cloud_ok is True:
            st.success(f"🎉 **{protokol_no}** başarıyla kaydedildi ve **Google E-Tabloya canlı aktarıldı!** (Skor: {toplam_epilepsi_puani}/22 | Toplam Vaka: **{toplam}**)")
        elif cloud_ok is False:
            st.warning(f"💾 **{protokol_no}** yerel ambarına kaydedildi (Bulut bağlantısına ulaşılamadı). (Skor: {toplam_epilepsi_puani}/22 | Toplam Vaka: **{toplam}**)")
        else:
            st.success(f"🎉 **{protokol_no}** başarıyla Veri Ambarına kaydedildi! (Skor: {toplam_epilepsi_puani}/22 | Toplam Vaka: **{toplam}**)")
        st.balloons()

# ==============================================================================
# SEKME 2: HASTA VERİ AMBARI VE İSTATİSTİKLERİ
# ==============================================================================
with tab2:
    st.markdown("### 📦 Toplanan Gerçek Hasta Veri Ambarı")
    st.caption("Danışıklı öğrenme (Supervised Machine Learning) için klinikte toplanan standardize hasta verileri.")
    
    webhook_url, csv_url = get_gsheets_config()
    if webhook_url:
        st.success("🟢 **Canlı Bulut Senkronizasyonu Aktif:** Tüm hekimlerin girdiği yeni hastalar ortak Google E-Tablosuna anında kaydedilmektedir.")
    else:
        st.info("💡 **Yerel Çalışma Modu:** Hasta kayıtları şu an bu sistemdeki yerel veri ambarında toplanmaktadır. Diğer hekimlerle 7/24 ortak Google E-Tablo kullanmak için aşağıdaki kurulum panelini açabilirsiniz.")
        
    with st.expander("⚙️ Canlı Google E-Tablo (Google Sheets) Bulut Bağlantı Ayarları & Kurulumu"):
        st.markdown("""
        Diğer hekimlerin poliklinikten veya akıllı telefonlarından girdikleri vakaların doğrudan ortak bir Google E-Tabloya (Google Sheets) canlı akması için:
        
        **1 Dakikalık Kurulum Adımları:**
        1. [Google Drive](https://drive.google.com) üzerinde yeni ve boş bir **Google E-Tablo** oluşturun (Örn: `Epilepsi_Hasta_Veri_Ambari`).
        2. E-Tablo açıkken üst menüden **Uzantılar (Extensions) ➔ Apps Script** seçeneğine tıklayın.
        3. Açılan kod penceresine aşağıdaki 10 satırlık kodu yapıştırıp kaydedin:
        ```javascript
        function doPost(e) {
          var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
          var data = JSON.parse(e.postData.contents);
          if (sheet.getLastRow() === 0) {
            sheet.appendRow(Object.keys(data));
          }
          sheet.appendRow(Object.values(data));
          return ContentService.createTextOutput(JSON.stringify({"status": "success"})).setMimeType(ContentService.MimeType.JSON);
        }
        ```
        4. Sağ üstteki mavi **Dağıt (Deploy) ➔ Yeni Dağıtım (New deployment)** butonuna basın.
        5. Tür olarak **Web Uygulaması (Web app)** seçin:
           * *Yürütücü (Execute as):* **Ben (E-posta adresiniz)**
           * *Erişimi olanlar (Who has access):* **Herkes (Anyone)**
        6. **Dağıt** deyin ve size verilen **Web Uygulaması URL'sini (Web app URL)** kopyalayıp aşağıdaki kutucuğa yapıştırın:
        """)
        
        cfg_col1, cfg_col2 = st.columns(2)
        with cfg_col1:
            in_webhook = st.text_input("Google Apps Script Webhook URL", value=webhook_url, placeholder="https://script.google.com/macros/s/.../exec")
            if in_webhook.strip() != webhook_url:
                st.session_state["gsheets_webhook_url"] = in_webhook.strip()
                st.rerun()
        with cfg_col2:
            in_csv = st.text_input("Google E-Tablo CSV Linki (İsteğe Bağlı - Tabloyu Canlı Okumak İçin)", value=csv_url, placeholder="https://docs.google.com/spreadsheets/d/.../export?format=csv")
            if in_csv.strip() != csv_url:
                st.session_state["gsheets_csv_url"] = in_csv.strip()
                st.rerun()
                
    st.markdown("---")
    df_current = load_warehouse()
    
    if df_current.empty:
        st.warning("⚠️ Henüz veri ambarında kayıtlı hasta bulunmamaktadır. 1. Sekmeden hasta kaydı oluşturabilirsiniz.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam Kayıtlı Vaka", len(df_current))
        m2.metric("Yaş Ortalaması", f"{df_current['Yas'].mean():.1f}")
        erkek_oran = (df_current['Cinsiyet'] == 1).mean() * 100
        m3.metric("Erkek / Kadın Dağılımı", f"%{erkek_oran:.0f} Erkek")
        kesinlesen = (df_current['Kesin_Klinik_Tani'] != "Tanı Henüz Netleşmedi / Tetkik Aşamasında").sum()
        m4.metric("Kesin Tanısı Konan", f"{kesinlesen} / {len(df_current)}")
        
        st.markdown("#### 📋 Veri Ambarı Tablosu")
        st.dataframe(df_current, use_container_width=True)
        
        c_down1, c_down2 = st.columns(2)
        with c_down1:
            csv_data = df_current.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                label="📥 Veri Ambarını CSV Olarak İndir (Excel Uyumlu)",
                data=csv_data,
                file_name=f"epilepsi_veri_ambari_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_down2:
            st.info("💡 **Danışıklı Öğrenme Notu:** Yeterli sayıda vaka (örneğin 50-100 hasta) toplandığında, bu veri ambarı doğrudan Random Forest ve Karar Ağacı eğitiminde kullanılarak projenin makine öğrenmesi tamamlanacaktır.")

# ==============================================================================
# SEKME 3: TAKLİTÇİLER VE KARŞILAŞTIRMA REHBERİ
# ==============================================================================
with tab3:
    st.markdown("### 👁️ Epilepsi, PNEN ve Senkop Ayırıcı Tanı Kılavuzu")
    st.caption("Klinikte hasta değerlendirirken yararlanabileceğiniz karşılaştırmalı referans tablosu.")
    
    comp_df = pd.DataFrame({
        "Klinik Parametre": [
            "Atak Başlangıcı / Hızı",
            "Ortam ve Seyirci Etkisi",
            "Uykuda Gerçekleşme",
            "Gözlerin Durumu (İktal)",
            "Dil Isırma Bölgesi",
            "Kasılma / Hareket Paterni",
            "Pelvik İtme (Thrusting)",
            "Ses ve Solunum",
            "Atak Süresi",
            "Pupil Işık Refleksi",
            "Ataklar Arası Durum (Küme)"
        ],
        "Gerçek Epileptik Nöbet": [
            "Ani başlar (saniyeler içinde)",
            "Seyirciden bağımsız, yalnızken de olur",
            "Sık görülür (özellikle uykuda/uyanırken)",
            "GÖZLER AÇIK, yukarı/yana fiksasyon",
            "DİLİN YAN (LATERAL) KENARI derin ısırılır",
            "Senkron, ritmik, koordineli tonik-klonik",
            "Çok nadir / Gözlenmez",
            "Başlangıçta iktal feryat (çığlık) + hırıltı",
            "Genellikle 1 - 2 dakika",
            "Genellikle kaybolur / pupil dilate",
            "Konfüzyon, uyku ve sersemlik devam eder"
        ],
        "Vazovagal / Ortostatik Senkop": [
            "Kademeli (göz kararması, bulantı prodromu)",
            "Ayakta durma, sıcak ortam, kan görme tetikler",
            "Uykuda ASLA görülmez",
            "Gözler açık veya hafif kaymış, gevşek",
            "Genellikle ısırık YOK (nadiren dil ucu)",
            "Ani tonus kaybı (yığılma), kısa multifokal miyokloni",
            "ASLA GÖRÜLMEZ",
            "Sessiz / Solukluk ve terleme",
            "Çok kısa (< 30-60 saniye)",
            "Korunmuştur",
            "Hasta hızla normale döner"
        ],
        "PNEN (Psikojenik / Konversiyon)": [
            "Kademeli, dalgalı başlangıç",
            "Sıklıkla seyirci varken veya stres sonrası",
            "Uykuda bildirilse de gerçekte uyanıklıkta",
            "GÖZLER SIKI KAPALI, AÇMAYA AKTİF DİRENÇ",
            "Dil ucu, dudak ısırığı veya ısırık yok",
            "Asenkron çırpınma, başı sallama, karın atması",
            "Sıklıkla gözlemlenir (patognomonik)",
            "Anlaşılır kelimeler, inleme, hızlı nefes",
            "Uzun (>10-30 dakika veya saatler)",
            "KORUNMUŞTUR (Normal ışık refleksi)",
            "Hasta atak biter bitmez konuşur, çay içer"
        ]
    })
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("#### 🎯 Altın Klinik Bulgular")
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown("""
        <div class="card-box card-epilepsy">
            <div class="metric-title">👅 Dil Lateral Kenar Isırığı</div>
            <p>Çene kaslarının istemsiz tonik spazmı dili dişler arasına sıkıştırır. <strong>Lateral (yan) kenar ısırığı, epilepsi için %95'in üzerinde tanısal özgüllüğe sahiptir.</strong></p>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown("""
        <div class="card-box card-pnes">
            <div class="metric-title">👁️ Göz Kapalılığı ve Direnç</div>
            <p>PNEN hastaları gözlerini sıklıkla sıkıca kapatır. Klinisyen göz kapağını açmak istediğinde <strong>hastanın aktif direnç gösterdiği</strong> gözlenir.</p>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown("""
        <div class="card-box card-syncope">
            <div class="metric-title">⏱️ Süre ve Toparlanma Hızı</div>
            <p>Senkopta beyin kan akımı hasta yere yığılınca hemen düzelir; 1-2 dakikada tam toparlanma olur. Epilepside ise <strong>en az 15-30 dk derin postiktal konfüzyon</strong> yaşanır.</p>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# SEKME 4: TEDAVİ VE SEVK KILAVUZU
# ==============================================================================
with tab4:
    st.markdown("### 💊 Tedavi, Takip ve Sevk Protokolü")
    st.caption("Klinikte hasta takibinde başvurulacak rehber.")
    
    t_col1, t_col2 = st.columns([1.1, 1])
    with t_col1:
        st.markdown("#### 1. İlk Nöbet Sonrası Antiepileptik İlaç (ASM) Başlama Kriterleri")
        st.markdown("""
        ILAE kılavuzlarına göre tek bir provoke olmayan nöbette hemen ilaç başlanması şart değildir.
        * **Tedavi Endikasyonu:** Gelecek 10 yılda tekrarlama riskinin **>%60** olması durumudur.
        
        **Tekrarlama Riskini >%60 Yapan Durumlar:**
        1. **Geçmiş Yapısal Beyin Hasarı:** Eski inme, kafa travması, menenjit öyküsü.
        2. **Nöbetin Uykuda Gerçekleşmesi:** Gece nöbetlerinde tekrarlama riski gündüze göre belirgin yüksektir.
        3. **Fokal Nöbet Bulguları:** Tek taraflı başlangıç veya belirgin aura varlığı.
        4. **Aralıklı Küme Nöbet:** 24 saat içinde birden fazla nöbet geçirilmesi.
        """)
        
    with t_col2:
        st.markdown("#### 2. Kırmızı Bayraklar (Derhal 112 / Acil Sevk)")
        st.error("""
        * **Nöbet süresinin 5 dakikayı geçmesi** (Status Epilepticus tehlikesi!)
        * Nöbet sonrası bilincin **30 dakikada açılmaması**
        * Bilinç açılmadan **ikinci bir nöbetin gelmesi**
        * Nöbet anında ciddi **kafa travması / yaralanma**
        * Hastanın **gebe** olması (Eklampsi riski)
        * Nöbet sonrası kalıcı **fokal motor kayıp (Todd parezisi)**
        """)

    st.markdown("---")
    st.markdown("#### 3. Hasta Yakını İçin İlk Yardım Kuralları")
    g1, g2 = st.columns(2)
    with g1:
        st.success("""
        ##### ✅ Nöbet Sırasında YAPILMASI Gerekenler:
        * Sakin olun, hastayı yere yatırıp yan çevirin (**Koma/İyileşme pozisyonu**).
        * Başının altına yumuşak bir şey koyun, kravat/yakayı gevşetin.
        * Çevredeki sert ve kesici eşyaları uzaklaştırın.
        * Nöbetin başlama saatini not edin.
        """)
    with g2:
        st.warning("""
        ##### ❌ KESİNLİKLE YAPILMAMASI Gerekenler:
        * **Ağzına kaşık, bez, tahta sokmaya ÇALIŞMAYIN!** (Çene kırığı ve boğulma riski).
        * Kasılmaları zorla durdurmaya çalışmayın.
        * Soğan, kolonya, amonyak koklatmayın.
        * Ağızdan su veya hap vermeye çalışmayın.
        """)

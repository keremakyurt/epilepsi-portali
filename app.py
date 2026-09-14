import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="TÜBİTAK 2209 Projesi: Epilepsi Teşhisi İçin Nicel Veri Madenciliği ve Yapay Zeka Algoritmaları",
    page_icon="🧠",
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

DEFAULT_GSHEETS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycby8tmvpDOC7Mlbgml9IFj9Cg6c8z5M0iPvncJ5PpXpWOQf8aAFyUfLjpD7gYOvyRrga/exec"

# Google Sheets Yapılandırması (Varsayılan URL, Secrets veya Arayüz Girişi)
def get_gsheets_config():
    webhook_url = DEFAULT_GSHEETS_WEBHOOK_URL
    csv_url = ""
    try:
        if "GSHEETS_WEBHOOK_URL" in st.secrets:
            webhook_url = st.secrets["GSHEETS_WEBHOOK_URL"]
        if "GSHEETS_CSV_URL" in st.secrets:
            csv_url = st.secrets["GSHEETS_CSV_URL"]
    except Exception:
        pass
    if "gsheets_webhook_url" in st.session_state and st.session_state["gsheets_webhook_url"]:
        webhook_url = st.session_state["gsheets_webhook_url"]
    if not csv_url and "gsheets_csv_url" in st.session_state:
        csv_url = st.session_state["gsheets_csv_url"]
    return str(webhook_url).strip(), str(csv_url).strip()

# Veri Ambarını Yükleme Yardımcısı (Hibrit: Canlı Google E-Tablo / Yerel CSV)
def load_warehouse():
    webhook_url, csv_url = get_gsheets_config()
    
    # 1. Google Apps Script doGet ile Canlı Okuma (İki Yönlü Canlı Senkronizasyon)
    if webhook_url:
        try:
            resp = requests.get(webhook_url, timeout=5)
            if resp.status_code == 200 and resp.text.strip().startswith("["):
                raw_data = resp.json()
                if isinstance(raw_data, list):
                    if len(raw_data) > 1:
                        raw_header = raw_data[0]
                        raw_rows = [r for r in raw_data[1:] if any(str(c).strip() for c in r)]
                        if raw_rows:
                            max_len = max(len(raw_header), max(len(r) for r in raw_rows))
                            clean_headers = []
                            for i in range(max_len):
                                col_name = str(raw_header[i]).strip() if i < len(raw_header) else ""
                                if not col_name:
                                    col_name = f"Sutun_{i+1}"
                                elif col_name in clean_headers:
                                    col_name = f"{col_name}_{i+1}"
                                clean_headers.append(col_name)
                                
                            padded_rows = [r + [''] * (max_len - len(r)) for r in raw_rows]
                            df_live = pd.DataFrame(padded_rows, columns=clean_headers)
                            return df_live
                        else:
                            return pd.DataFrame()
                    elif len(raw_data) <= 1:
                        return pd.DataFrame()
        except Exception:
            pass

    if csv_url:
        try:
            df_cloud = pd.read_csv(csv_url)
            if not df_cloud.empty:
                return df_cloud
        except Exception:
            pass
            
    if os.path.exists(DATA_PATH):
        try:
            df_local = pd.read_csv(DATA_PATH)
            return df_local
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

st.markdown('<div class="main-header">🧠 TÜBİTAK 2209 Projesi: Epilepsi Teşhisi İçin Nicel Veri Madenciliği ve Yapay Zeka Algoritmaları</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Klinik Karar Ağacı ve Danışıklı Öğrenme (Supervised Learning) Hasta Kayıt Portalı</div>', unsafe_allow_html=True)

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
            "Kerem Akyurt",
            "Özge Orhan",
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
        st.markdown('<div class="section-title">👤 Hasta Kimlik ve Fiziksel Bilgileri</div>', unsafe_allow_html=True)
        hasta_ad_soyad = st.text_input("Hasta Adı ve Soyadı", placeholder="Örn: Ayşe Yılmaz")
        
        c_dem1, c_dem2, c_dem3, c_dem4 = st.columns(4)
        with c_dem1:
            yas = st.number_input("Yaş", min_value=1, max_value=110, value=25)
        with c_dem2:
            cins = st.selectbox("Cinsiyet", [1, 0], format_func=lambda x: "Erkek" if x==1 else "Kadın")
        with c_dem3:
            boy = st.number_input("Boy (cm)", min_value=40, max_value=230, value=170)
        with c_dem4:
            kilo = st.number_input("Kilo (kg)", min_value=3, max_value=250, value=70)
            
        vki = round(kilo / ((boy / 100) ** 2), 1)
            
        st.markdown('<div class="section-title">📋 1. Hastaya Sorulacak Sorular (10 Soru)</div>', unsafe_allow_html=True)
        
        # H1
        h1 = st.radio("1. Atak başlangıcında anlamsız korku oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # H2
        h2 = st.radio("2. Atak başlangıcında anlamsız gülme atağı oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # H3
        h3 = st.radio("3. Atak başlangıcında anlamsız ağlama atağı oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # H4
        h4 = st.radio("4. Atak başlangıcında mideden yemek borusuna doğru yükselme hissi oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # H5 (Evet: 0, Hayır: 1)
        h5_val = st.radio("5. Atak başlangıcında çarpıntı oluyor mu?",
                          [0, 1], format_func=lambda x: "Evet" if x==0 else "Hayır", index=1)
        # H6 (Evet: 0, Hayır: 1)
        h6_val = st.radio("6. Atak başlangıcında terleme artışı, gözlerde kararma oluyor mu?",
                          [0, 1], format_func=lambda x: "Evet" if x==0 else "Hayır", index=1)
        # H7 (Evet: 0, Hayır: 1)
        h7_val = st.radio("7. Ataklar hep yalnızken, etrafta kimse yokken mi oluyor?",
                          [0, 1], format_func=lambda x: "Evet" if x==0 else "Hayır", index=1)
        # H8 (Evet: 0, Hayır: 1)
        h8_val = st.radio("8. Ataklar sonrası ağlama oluyor mu?",
                          [0, 1], format_func=lambda x: "Evet" if x==0 else "Hayır", index=1)
        # H9
        h9 = st.radio("9. Sabahları daha çok olmak üzere gün içinde ani irkilme şeklinde sıçramalar oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # H10
        h10 = st.radio("10. Ataklarda düşme sonucu kafaya dikiş atılması, kol-bacak alçıya alınma durumu oldu mu?",
                       [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)

    with col2:
        st.markdown('<div class="section-title">👁️ 2. Atak Anına Tanık Olanlara Sorulacak Sorular (12 Soru)</div>', unsafe_allow_html=True)
        
        # T1
        t1 = st.radio("11. Gözler atak sırasında açık mı?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # T2
        t2 = st.radio("12. Gözler yukarı doğru sabit mi?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # T3 (Evet: 0, Hayır: 1)
        t3_val = st.radio("13. Göz bebekleri hareket ediyor ya da göz kapakları kapalı açmak istenince hasta sıkıyor mu?",
                          [0, 1], format_func=lambda x: "Evet" if x==0 else "Hayır", index=1)
        # T4 (Evet: 0, Hayır: 1)
        t4_val = st.radio("14. Atak bitiminde hasta etrafını tanıyor mu, sorulara mantıklı cevap veriyor mu?",
                          [0, 1], format_func=lambda x: "Evet" if x==0 else "Hayır", index=1)
        # T5
        t5 = st.radio("15. Atakları hep 1-5 dk mı sürüp sonlanıyor?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # T6
        t6 = st.radio("16. Bütün atakları aynı sürede mi bitiyor?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # T7
        t7 = st.radio("17. Ataklar sırasında ağız şapırdatma, çiğneme, tükürme, boş etrafa bakma veya otomatizma hareketleri var mı?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # T8
        t8 = st.radio("18. Ataklarda gece aniden uykudan uyandırma ve sinirlilik, huzursuzluk, yataktan inme, etrafa zarar verme şeklinde kontrolü zor, bilinç kaybı oluyor mu?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # T9
        t9 = st.radio("19. Ataklar başın sağ veya sola döndüğü, kol ve bacaklarda kasılma ve sonrasında sıçrama şeklinde mi sonlanıyor?",
                      [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)
        # T10 (Evet: 0, Hayır: 1)
        t10_val = st.radio("20. Ataklarda karın/göğüs yukarı aşağı hareketleri, bisiklet çevirme, başı sürekli sağa sola çevirme şeklinde mi?",
                           [0, 1], format_func=lambda x: "Evet" if x==0 else "Hayır", index=1)
        # T11 (Evet: 0, Hayır: 1)
        t11_val = st.radio("21. Ataklar sırasında yüzünün rengi bembeyaz veya sarı renkte mi oluyor?",
                           [0, 1], format_func=lambda x: "Evet" if x==0 else "Hayır", index=1)
        # T12
        t12 = st.radio("22. Ataklarda dil-dudak ısırma oluyor mu?",
                       [1, 0], format_func=lambda x: "Evet" if x==1 else "Hayır", index=1)

    # Toplam Puan Hesaplama (Arka Planda Model/Kayıt İçin)
    toplam_epilepsi_puani = (
        h1 + h2 + h3 + h4 + h5_val + h6_val + h7_val + h8_val + h9 + h10 +
        t1 + t2 + t3_val + t4_val + t5 + t6 + t7 + t8 + t9 + t10_val + t11_val + t12
    )

    st.markdown("---")
    st.markdown('<div class="section-title">🎯 Kesin Klinik Tanı Etiketi (Danışıklı Öğrenme - Supervised ML İçin)</div>', unsafe_allow_html=True)
    st.caption("İleride karar ağacı modelinin eğitilebilmesi için Nöroloji Uzmanı (Danışman Hoca / Klinik Kurul) tarafından konulan kesinleşmiş altın standart tanıyı seçiniz:")
    
    tani_secenekleri = [
        "Epilepsi (Epileptik Nöbet)",
        "Psikojenik Non-Epileptik Nöbet (PNEN)",
        "Senkop",
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
            "Hasta_Adi_Soyadi": hasta_ad_soyad,
            "Yas": yas,
            "Cinsiyet": cins,
            "Boy_cm": boy,
            "Kilo_kg": kilo,
            "VKI": vki,
            
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
            st.success(f"🎉 **{protokol_no}** başarıyla kaydedildi ve **Google E-Tabloya canlı aktarıldı!** (Sistemdeki Toplam Vaka: **{toplam}**)")
        elif cloud_ok is False:
            st.warning(f"💾 **{protokol_no}** yerel ambarına kaydedildi (Bulut bağlantısına ulaşılamadı). (Sistemdeki Toplam Vaka: **{toplam}**)")
        else:
            st.success(f"🎉 **{protokol_no}** başarıyla Veri Ambarına kaydedildi! (Sistemdeki Toplam Vaka: **{toplam}**)")
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
                
    st.markdown("---")
    df_current = load_warehouse()
    
    if df_current.empty:
        st.warning("⚠️ Henüz veri ambarında kayıtlı hasta bulunmamaktadır. 1. Sekmeden hasta kaydı oluşturabilirsiniz.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam Kayıtlı Vaka", len(df_current))
        
        # Yaş ortalaması (sayısal dönüştürme ile hatasız)
        yas_mean = "-"
        if "Yas" in df_current.columns:
            yas_numeric = pd.to_numeric(df_current["Yas"], errors="coerce")
            if not yas_numeric.dropna().empty:
                yas_mean = f"{yas_numeric.mean():.1f}"
        m2.metric("Yaş Ortalaması", yas_mean)
        
        # Cinsiyet oranı (güvenli)
        erkek_str = "-"
        if "Cinsiyet" in df_current.columns:
            cins_numeric = pd.to_numeric(df_current["Cinsiyet"], errors="coerce")
            if not cins_numeric.dropna().empty:
                erkek_oran = (cins_numeric == 1).mean() * 100
                erkek_str = f"%{erkek_oran:.0f} Erkek"
        m3.metric("Erkek / Kadın Dağılımı", erkek_str)
        
        # Kesin tanı sayısı (güvenli)
        kesin_str = f"0 / {len(df_current)}"
        if "Kesin_Klinik_Tani" in df_current.columns:
            kesinlesen = (df_current["Kesin_Klinik_Tani"].astype(str).str.strip() != "Tanı Henüz Netleşmedi / Tetkik Aşamasında").sum()
            kesin_str = f"{kesinlesen} / {len(df_current)}"
        m4.metric("Kesin Tanısı Konan", kesin_str)
        
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

        with st.expander("🛠️ Veri Ambarı Yönetimi (Yalnızca Yetkili Araştırmacı)"):
            c_adm1, c_adm2 = st.columns([1, 2])
            with c_adm1:
                if st.button("🗑️ Yerel Veri Ambarını Sıfırla (Test Kayıtlarını Sil)", type="secondary"):
                    header = "Protokol_No,Kayit_Tarihi,Kaydeden_Hekim,Hasta_Adi_Soyadi,Yas,Cinsiyet,Boy_cm,Kilo_kg,VKI,H1_Anlamsiz_Korku,H2_Anlamsiz_Gulme,H3_Anlamsiz_Aglama,H4_Mideden_Yukselme,H5_Carpinti,H6_Terleme_Goz_Kararma,H7_Hep_Yalnizken,H8_Atak_Sonrasi_Aglama,H9_Sabah_Sicramalari,H10_Dusme_Dikis_Alci,T1_Gozler_Acik,T2_Gozler_Yukari_Sabit,T3_Goz_Kapak_Sikma,T4_Etrafini_Tanima,T5_Hep_1_5_Dk,T6_Ayni_Surede_Bitis,T7_Agiz_Sapurdatma_Otomatizma,T8_Gece_Huzursuz_Uyanma,T9_Bas_Donmesi_Kasilma_Sicrama,T10_Karin_Gogus_Bisiklet_Hareket,T11_Yuz_Bembeyaz_Sari,T12_Dil_Dudak_Isirma,Toplam_Epilepsi_Skoru,Kesin_Klinik_Tani,Klinik_Not\n"
                    with open(DATA_PATH, "w", encoding="utf-8-sig") as f:
                        f.write(header)
                    st.success("Test kayıtları yerel ambardan temizlendi!")
                    st.rerun()
            with c_adm2:
                st.caption("💡 **Bilgi:** Gerçek hasta kayıtlarınız Google E-Tablonuzda güvenle saklanmaktadır. Buradaki buton sadece sistemdeki yerel test kayıtlarını temizler.")

# ==============================================================================
# SEKME 3: TAKLİTÇİLER VE KARŞILAŞTIRMA REHBERİ
# ==============================================================================
with tab3:
    st.markdown("### 👁️ Klinik Karar Ağacı Sorularının Patofizyolojik Nedenleri ve Ayırıcı Tanı Sonuçları")
    st.caption("TÜBİTAK 2209-A projesinde hekimler tarafından değerlendirilen 22 sorunun nörolojik arka planı, klinik mekanizması (Neden) ve ayırıcı tanıdaki karşılığı (Sonuç: Epilepsi vs. Senkop / PNEN).")
    
    sorular_rehberi = [
        # 1. HASTAYA SORULAN SORULAR (H1 - H10)
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H1",
            "Klinik Soru ve Bulgu": "Aniden gelen sebepsiz korku, panik hissi (Aura)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Amigdala ve mezial temporal lob kaynaklı fokal epileptik deşarjlar, bilinç kapanmadan önce ani emosyonel psişik aura yaratır.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Panik atak gibi yavaş gelişmez; ortamdan bağımsız, saniyeler içinde aniden başlar.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H2",
            "Klinik Soru ve Bulgu": "Mideden yukarı yükselen tuhaf his (Epigastrik Aura)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "İnsular korteks ve mezial temporal yapıların otonomik aktivasyonudur. MTLE (Mezial Temporal Lob Epilepsisi) için en klasik bulgudur.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Senkoptaki bulantıdan farklıdır; epigastriumdan boğaza doğru yükselen bir dalga hissidir.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H3",
            "Klinik Soru ve Bulgu": "Etrafta olmayan kötü koku/tat veya görsel halüsinasyon",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Unkus (koku korteksi - unsinat nöbet) veya oksipital/temporal assosiasyon alanlarındaki fokal elektriksel paroksizmal deşarjlardır.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Yanık lastik veya metalik koku/tat doğrudan fokal kortikal odak kanıtıdır; senkop veya PNEN'de olmaz.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H4",
            "Klinik Soru ve Bulgu": "Daha önce yaşamışlık (Déjà vu) veya yabancılaşma hissi",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Hipokampus ve parahipokampal girusun disfonksiyonu sonucu hafıza ve algı devrelerinin geçici senkronizasyon kaybıdır.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Sağlıklı insanlardaki déjà vu'dan farklı olarak, korkutucu, rüya benzeri ve yabancılaşma hissiyle gelir.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H5",
            "Klinik Soru ve Bulgu": "Ayakta dururken göz kararması, baş dönmesi, soğuk terleme",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Geçici serebral hipoperfüzyona bağlı retino-kortikal iskemi (tünel vizyonu) ve otonom sempatik/parasempatik dengesizliktir.",
            "Tanısal Sonuç ve Klinik Anlamı": "Vazovagal / Ortostatik Senkop lehinedir. Gerçek epilepside kademeli göz kararması ve soğuk terleme prodromu görülmez.",
            "Klinik Yönelim": "Taklitçi (Senkop) Lehine"
        },
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H6",
            "Klinik Soru ve Bulgu": "Ayağa kalkma, sıcak ortam, uzun süre ayakta kalma, kan görme",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Venöz göllenme, vazodepresör refleks veya sempatik yetmezliğe bağlı hemodinamik kan basıncı düşüşüdür.",
            "Tanısal Sonuç ve Klinik Anlamı": "Refleks Senkop lehinedir. Ortam ve postür tetikleyicileri elektriksel nöbetten ziyade kardiyovasküler instabiliteyi gösterir.",
            "Klinik Yönelim": "Taklitçi (Senkop) Lehine"
        },
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H7",
            "Klinik Soru ve Bulgu": "Olay sonrası toparlanmanın >15 dk sürmesi, konfüzyon",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Jeneralize deşarj sonrası korteksin enerji tükenmesi ve nörotransmitter deplesyonuna bağlı postiktal serebral depresyondur.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Senkopta kan akımı düzelince hasta 1-2 dakikada berraklaşır; PNEN'de ise hemen konuşur.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H8",
            "Klinik Soru ve Bulgu": "Uyanınca belirgin yaygın kas ağrısı, yorgunluk ve bitkinlik",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Tonik-klonik fazda tüm iskelet kaslarının yoğun, kontrolsüz ve anaerobik kasılması sonucu laktik asit birikimi ve mikroyırtıklardır.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Senkopta kas tonusu kaybolup hasta gevşek yığıldığı için ertesi gün şiddetli kas ağrısı oluşmaz.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H9",
            "Klinik Soru ve Bulgu": "Dilin özellikle yan (lateral) kenarının derin ısırılması",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Masseter ve temporal kasların tonik spazmı dili diş sıraları arasına sıkıştırır. Özgüllüğü %95'in üzerindedir.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Senkopta ısırık olmaz. PNEN'de ise ısırık varsa dil ucu veya dudakta olur; yan kenar ısırığı epilepsidir.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Hastaya Sorulan",
            "Soru Kodu": "H10",
            "Klinik Soru ve Bulgu": "Olay sırasında veya sonrasında idrar kaçırma (enürezis)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Tonik fazdaki aşırı intraabdominal basınç ve ardından gelen otonomik sfinkter tonusunun depresyonudur.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Bilinç kaybı ve konvülziyonla birlikte görülen sfinkter kontrol kaybı nöbet olasılığını belirgin artırır.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        
        # 2. TANIĞA SORULAN SORULAR (T1 - T12)
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T1",
            "Klinik Soru ve Bulgu": "Yere yığılmadan önce ani çığlık / ses (İktal Feryat)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Tonik spazmla toraks ve diyaframın kasılması sonucu havanın spazm halindeki daralmış kordonlardan dışarı fırlamasıdır.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. İstemli bir çığlık değil mekanik ses tellerinin spazmıdır. Senkop sessizdir; PNEN'de ise sözel feryat olur.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T2",
            "Klinik Soru ve Bulgu": "Baş veya gözlerin bir yöne kilitlenmesi (Deviasyon)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Frontal göz alanı (FEF) veya kortikal odağın başı ve gözleri zorla karşı yöne çevirmesidir (versif deviasyon).",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Fokal motor lateralizasyonun en kesin belirtisidir; senkopta veya PNEN'de tek yöne tonik deviasyon görülmez.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T3",
            "Klinik Soru ve Bulgu": "Olay sırasında gözlerin açık olması",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Kortikal nöronal eksitasyon sırasında levator palpebra kas tonusunun açık kalması ve gözlerin yukarı/yana fikse olmasıdır.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Nöbette gözler açıktır. PNEN'de ise hastaların >%90'ında gözler sıkı kapalıdır ve açmaya aktif direnç vardır.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T4",
            "Klinik Soru ve Bulgu": "Önce kaskatı kesilme (tonik), ardından ritmik sıçrama (klonik)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Kortikal jeneralize deşarj önce sürekli eksitasyon (tonik faz), ardından inhibitör devrelerin aralıklı devreye girmesiyle klonik fazı üretir.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Gerçek tonik-klonik nöbetin evrensel ve stereotipik nörofizyolojik sıralamasıdır.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T5",
            "Klinik Soru ve Bulgu": "Kasılma ve sıçramaların her iki tarafta düzenli ve ritmik olması",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Korpus kallozum üzerinden iki hemisfer arasında senkronize deşarj yayılımı ve frekansın giderek yavaşlamasıdır.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. PNEN'de ise hareketler ritmik değil asenkron, amaca yönelik olmayan çırpınma ve dalgalanmadır.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T6",
            "Klinik Soru ve Bulgu": "Dudaklarda morarma (siyanoz) veya solunumun durması",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "İnterkostal kaslar ve diyaframın tonik kasılması ventilasyonu durdurur (iktal apne) ve parsiyel oksijen basıncı hızla düşer.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Gerçek siyanoz objektif hipoksi göstergesidir. Senkopta solukluk ön plandadır; PNEN'de siyanoz oluşmaz.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T7",
            "Klinik Soru ve Bulgu": "Pelvik itme (kalçayı vurma) veya başı iki yana sallama",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Kortikal elektriksel deşarj dışı, psikojenik kaynaklı kompleks disosiyatif motor hareketlerdir.",
            "Tanısal Sonuç ve Klinik Anlamı": "PNEN lehinedir. Pelvik thrusting ve başı sağa-sola rotasyonel sallama PNEN için son derece yüksek özgüllüğe sahip negatif bulgudur.",
            "Klinik Yönelim": "Taklitçi (PNEN) Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T8",
            "Klinik Soru ve Bulgu": "Olay sırasında ağlama, çığlık atma veya anlamlı kelimeler",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Kortikal bilinç merkezlerinin tamamen kapanmadığını ve limbik-emosyonel motor kontrolün devrede olduğunu gösterir.",
            "Tanısal Sonuç ve Klinik Anlamı": "PNEN lehinedir. Gerçek jeneralize nöbette korteks baskılandığı için hasta anlamlı kelime telaffuz edemez veya ağlayamaz.",
            "Klinik Yönelim": "Taklitçi (PNEN) Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T9",
            "Klinik Soru ve Bulgu": "Kasılma ve sıçramaların süresi (1-2 dakika vs >5-10 dakika)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Epileptik nöbetler intrensek GABAerjik inhibitör devrelerle 1-2 dakikada sonlanır. PNEN ise dalgalı olarak uzar.",
            "Tanısal Sonuç ve Klinik Anlamı": "1-2 dk sürmesi Epilepsi; 5-10 dakikadan uzun, dalgalı azalıp artan kasılmalar ise PNEN lehinedir.",
            "Klinik Yönelim": "1-2 Dk: Epilepsi / >5 Dk: PNEN"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T10",
            "Klinik Soru ve Bulgu": "Olayın uykuda gerçekleşmesi (Noktürnal)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "NREM uykusunun senkronizan etkisi epileptojenik odakları tetikler (özellikle frontal ve mezial temporal lob).",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Vazovagal veya ortostatik senkop yatay pozisyonda ve uykuda ASLA görülmez. Uykuda olan ataklar epilepsidir.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T11",
            "Klinik Soru ve Bulgu": "Toparlandıktan sonra kolda/bacakta geçici güçsüzlük (Todd Felci)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "Nöbeti başlatan fokal motor korteksin yoğun deşarj sonrası nöronal tükenmesi ve geçici hiperpolarizasyonudur.",
            "Tanısal Sonuç ve Klinik Anlamı": "Epilepsi lehinedir. Atak sonrasında ekstremitede dakikalarca süren geçici felç fokal başlangıçlı epilepsinin kesin kanıtıdır.",
            "Klinik Yönelim": "Epilepsi Lehine"
        },
        {
            "Grup": "Tanığa Sorulan",
            "Soru Kodu": "T12",
            "Klinik Soru ve Bulgu": "Hastanın olay anını hatırlamaması (İktal Amnezi)",
            "Neden Sorulur? (Patofizyolojik Mekanizma)": "İktal deşarjın hafıza devrelerini (hipokampal assosiasyon korteksi) tamamen bloke ederek yeni kayıt almasını engellemesidir.",
            "Tanısal Sonuç ve Klinik Anlamı": "Hatırlamama Epilepsi; atak anını ve etraftaki konuşmaları baştan sona net hatırlama ise PNEN lehinedir.",
            "Klinik Yönelim": "Hatırlamıyor: Epilepsi / Hatırlıyor: PNEN"
        }
    ]
    
    df_rehber = pd.DataFrame(sorular_rehberi)
    
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        kategori_filtre = st.selectbox(
            "Filtreleme Seçeneği:",
            [
                "Tüm Sorular (22 Soru - Kapsamlı Rehber)",
                "🧑‍🦱 Sadece Hastaya Sorulan Sorular (10 Soru)",
                "👥 Sadece Tanığa Sorulan Sorular (12 Soru)",
                "⚡ Sadece Epilepsi Lehine Olan Bulgular",
                "🛑 Sadece Taklitçi (Senkop / PNEN) Lehine Olan Bulgular"
            ]
        )
    with f_col2:
        st.caption("🔍 **Not:** Sorular araştırma projesinde hekimler tarafından değerlendirilen klinik sorularla birebir eşleşmektedir.")
        
    if "Sadece Hastaya" in kategori_filtre:
        df_goster = df_rehber[df_rehber["Grup"] == "Hastaya Sorulan"]
    elif "Sadece Tanığa" in kategori_filtre:
        df_goster = df_rehber[df_rehber["Grup"] == "Tanığa Sorulan"]
    elif "Epilepsi Lehine" in kategori_filtre:
        df_goster = df_rehber[df_rehber["Klinik Yönelim"].str.contains("Epilepsi")]
    elif "Taklitçi" in kategori_filtre:
        df_goster = df_rehber[df_rehber["Klinik Yönelim"].str.contains("Taklitçi|PNEN|Senkop")]
    else:
        df_goster = df_rehber
        
    # Tablo olarak göster
    st.dataframe(
        df_goster[["Soru Kodu", "Klinik Soru ve Bulgu", "Neden Sorulur? (Patofizyolojik Mekanizma)", "Tanısal Sonuç ve Klinik Anlamı", "Klinik Yönelim"]],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    with st.expander("📌 Soruların Klinik Neden-Sonuç Mekanizmaları ve Ayrım Kartları (Detaylı Görünüm)", expanded=False):
        c_reh1, c_reh2 = st.columns(2)
        with c_reh1:
            st.markdown("#### 🧑‍🦱 1. Hastaya Sorulan Sorular (Aura ve Prodrom)")
            for item in [x for x in sorular_rehberi if x["Grup"] == "Hastaya Sorulan"]:
                st.markdown(f"""
                **[{item['Soru Kodu']}] {item['Klinik Soru ve Bulgu']}**  
                * **Neden (Mekanizma):** {item['Neden Sorulur? (Patofizyolojik Mekanizma)']}  
                * **Sonuç (Ayırıcı Tanı):** {item['Tanısal Sonuç ve Klinik Anlamı']}  
                * **Klinik Yönelim:** `{item['Klinik Yönelim']}`
                ---
                """)
        with c_reh2:
            st.markdown("#### 👥 2. Tanığa Sorulan Sorular (İktal ve Motor Patern)")
            for item in [x for x in sorular_rehberi if x["Grup"] == "Tanığa Sorulan"]:
                st.markdown(f"""
                **[{item['Soru Kodu']}] {item['Klinik Soru ve Bulgu']}**  
                * **Neden (Mekanizma):** {item['Neden Sorulur? (Patofizyolojik Mekanizma)']}  
                * **Sonuç (Ayırıcı Tanı):** {item['Tanısal Sonuç ve Klinik Anlamı']}  
                * **Klinik Yönelim:** `{item['Klinik Yönelim']}`
                ---
                """)

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

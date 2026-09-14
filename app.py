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
        st.markdown('<div class="section-title">1. Özgeçmiş ve Genel Risk Faktörleri</div>', unsafe_allow_html=True)
        yas = st.number_input("Hastanın Yaşı", min_value=1, max_value=105, value=25)
        cins = st.selectbox("Cinsiyet", [0, 1], format_func=lambda x: "Erkek" if x==1 else "Kadın")
        
        q1_1 = st.radio("1.1 Daha önce kafa travması, inme veya menenjit (santral sinir sistemi enfeksiyonu) öyküsü var mı?", 
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q1_2 = st.radio("1.2 Ailede epilepsi veya çocukluk çağı ateşli havale (febril nöbet) öyküsü var mı?", 
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q1_3 = st.radio("1.3 Eşlik eden psikiyatrik hastalık (anksiyete, depresyon, konversiyon) veya sekonder kazanç var mı?", 
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q1_4 = st.radio("1.4 Eşlik eden bilinen bir kardiyolojik rahatsızlık (aritmi vb.) var mı?", 
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q1_5 = st.radio("1.5 Sabahları uyanınca daha sık olmak üzere, gün içinde ani irkilme şeklinde sıçramalar oluyor mu?", 
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q1_6 = st.radio("1.6 Ataklar uykusuzluk, yanıp sönen ışıklar (fotik stimülasyon) veya ani ses ile tetikleniyor mu?", 
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q1_7 = st.radio("1.7 Geçmişte veya atak döneminde hastayı derinden etkileyen ağır psikolojik travma / aşırı stres öyküsü var mı?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q1_8 = st.radio("1.8 Akut Provokasyon: Son 7 günde kafa travması, inme, ağır hipoglisemi veya alkol/madde yoksunluğu var mı?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)

        st.markdown('<div class="section-title">2. Atak Öncesi (Aura ve Prodromal Dönem)</div>', unsafe_allow_html=True)
        q2_1 = st.radio("2.1 Atak başlamadan önce mideden yemek borusuna doğru yükselme hissi (gastrointestinal aura) oluyor mu?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q2_2 = st.radio("2.2 Atak başlangıcında anlamsız bir korku, kaygı veya anlamsız gülme (jelastik) / ağlama (dakristik) atağı oluyor mu?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q2_3 = st.radio("2.3 Atak öncesinde yabancı yeri tanıdık sanma (deja vu), halüsinasyon veya zorlu düşünce gibi hisler oluyor mu?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q2_4 = st.radio("2.4 Atak öncesinde yanık lastik kokusu (olfaktör) veya görme alanı değişiklikleri/halüsinasyonlar oluyor mu?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q2_5 = st.radio("2.5 Atak başlangıcında terleme artışı, gözlerde kararma, çarpıntı veya solukluk oluyor mu?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q2_6 = st.radio("2.6 Ataklardan önce uzun süre ayakta kalma veya aniden ayağa kalkma (ortostatik) durumu var mı?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)

    with col2:
        st.markdown('<div class="section-title">3. Atak Anı (İktal Dönem) - Fiziksel Bulgular</div>', unsafe_allow_html=True)
        q3_1 = st.radio("3.1 Ataklar hep yalnızken mi (1), sadece seyirci / belli kişilerin yanındayken mi (0) oluyor?",
                        [1, 0], format_func=lambda x: "Yalnızken de olabiliyor (1)" if x==1 else "Sadece seyirci varken (0)", index=0)
        q3_2 = st.radio("3.2 Ataklar uykuda iken mi (1), yoksa sadece uyanıkken mi (0) gerçekleşiyor?",
                        [0, 1], format_func=lambda x: "Uykuda da oluyor (1)" if x==1 else "Sadece uyanıkken (0)", index=0)
        q3_3 = st.radio("3.3 Atakların başlama şekli nasıldır?",
                        [1, 0], format_func=lambda x: "Ani (1)" if x==1 else "Kademeli / Yavaş Yavaş (0)", index=0)
        q3_4 = st.radio("3.4 Atakların süresi ortalama ne kadardır ve stereotipik midir?",
                        [0, 1, 2], format_func=lambda x: "Saniyeler (<1 dk) (0)" if x==0 else ("1 - 5 dk benzer süre (1)" if x==1 else "10 - 15 dk veya değişken saatler (2)"), index=1)
        q3_5 = st.radio("3.5 Atak sırasında gözlerin durumu nasıldır?",
                        [1, 0], format_func=lambda x: "Açık / Yukarı Sabit Fiksasyon (1)" if x==1 else "Sıkı Kapalı, Açmaya Karşı Dirençli (0)", index=0)
        q3_6 = st.radio("3.6 Ataklarda yüzün rengi morarıyor mu (siyanoz), yoksa bembeyaz/soluk mu oluyor?",
                        [1, 0], format_func=lambda x: "Siyanoz / Dudaklarda Morarma (1)" if x==1 else "Soluk / Bembeyaz (0)", index=0)
        q3_7 = st.radio("3.7 Atak sırasında kasılmaların şekli nasıldır?",
                        [1, 0], format_func=lambda x: "Koordineli tonik-klonik kasılma (1)" if x==1 else "Karın atması, bisiklet, çırpınma (0)", index=0)
        q3_8 = st.radio("3.8 Ataklar başın sağ/sola döndüğü (versif), kol-bacakta kasılma ve sıçrama şeklinde mi sonlanıyor?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q3_9 = st.radio("3.9 Ağız şapırdatma, çiğneme, tükürme, üzerini arama (otomatizma) hareketleri var mı?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q3_10 = st.radio("3.10 Ataklarda dil veya dudak ısırılması gerçekleşiyor mu? Ne şekilde?",
                         [1, 0, 2], format_func=lambda x: "Dilin YAN (Lateral) Kenarı (1)" if x==1 else ("Dilin Ucu veya Dudak (0)" if x==0 else "Isırık Yok (2)"), index=2)
        q3_11 = st.radio("3.11 Atak anında idrar veya gaita (büyük abdest) kaçırma durumu (inkontinans) oluyor mu?",
                         [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q3_12 = st.radio("3.12 Gece aniden uykudan uyanıp sinirlilik, yataktan inme, etrafa zarar verme oluyor mu?",
                         [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q3_13 = st.radio("3.13 Sağlık personeli/112 tarafından pupiller ışık refleksinin korunduğu tespit edildi mi?",
                         [0, 1, 2], format_func=lambda x: "Evet, Korunmuş (1)" if x==1 else ("Hayır, Refleks Kayıp (0)" if x==0 else "Bilinmiyor / Bakılmadı (2)"), index=2)
        q3_14 = st.radio("3.14 Atak sırasında gövdede ve kalçada öne doğru şiddetli itme (pelvik itme) hareketi var mı?",
                         [1, 0], format_func=lambda x: "Evet (0) [Pelvik İtme Var]" if x==0 else "Hayır (1)", index=0)
        q3_15 = st.radio("3.15 Atak esnasındaki ses çıkarma ve solunum düzeni hangisine daha çok uyuyor?",
                         [1, 0], format_func=lambda x: "Başlangıçta ani çığlık (iktal feryat) ve hırıltılı solunum (1)" if x==1 else "Anlaşılır kelimeler, inleme ve hızlı nefes (0)", index=0)
        q3_16 = st.radio("3.16 Çevredeki insanların varlığı veya ilgisi nöbetin şiddetini artırıyor mu?",
                         [1, 0], format_func=lambda x: "Evet, ilgiyle artıyor (0)" if x==0 else "Hayır, bağımsız (1)", index=0)
        q3_17 = st.radio("3.17 Atakların sıklığı genellikle nasıldır?",
                         [1, 0], format_func=lambda x: "Haftada, ayda veya yılda bir gibi seyrek (1)" if x==1 else "Günde birkaç defa ve çok sık aralarla (0)", index=0)

        st.markdown('<div class="section-title">4. Atak Sonrası (Post-iktal Dönem)</div>', unsafe_allow_html=True)
        q4_1 = st.radio("4.1 Atak bitiminde hasta etrafını anında tanıyor mu, yoksa bir süre bilinç bulanıklığı (konfüzyon) yaşıyor mu?",
                        [1, 0], format_func=lambda x: "Konfüzyon Var, Uyku Hali Sürüyor (1)" if x==1 else "Anında Kendine Geliyor (0)", index=0)
        q4_2 = st.radio("4.2 Hasta atağın gerçekleştiği ana dair hiçbir şey hatırlamıyor mu (amnezi var mı)?",
                        [1, 0], format_func=lambda x: "Evet, Hiç Hatırlamıyor (1)" if x==1 else "Hayır, Olayları Hatırlıyor (0)", index=0)
        q4_3 = st.radio("4.3 Atak bittikten hemen sonra ağlama sesleri veya ağlama krizi yaşanıyor mu?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q4_4 = st.radio("4.4 Ataklarda düşme sonucu kafaya dikiş atılması, kemik kırılması gibi ciddi travmatik yaralanmalar oldu mu?",
                        [0, 1], format_func=lambda x: "Evet (1)" if x==1 else "Hayır (0)", index=0)
        q4_5 = st.radio("4.5 Ataklar peş peşe geliyorsa, iki atak arasındaki dinlenme süresinde hastanın durumu nasıldır?",
                        [1, 0], format_func=lambda x: "Uyku hali, sersemlik devam ediyor (1)" if x==1 else "Tamamen normale dönüyor, konuşabiliyor (0)", index=0)

    st.markdown("---")
    st.markdown('<div class="section-title">🎯 5. Danışıklı Öğrenme (Supervised ML) İçin Kesin Tanı Etiketi</div>', unsafe_allow_html=True)
    st.caption("İleride makine öğrenmesi karar ağacının eğitilebilmesi için Nöroloji Uzmanı (Danışman Hoca / Klinik Kurul) tarafından konulan kesinleşmiş altın standart tanıyı seçiniz:")
    
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
            
            "S1_Gecmis_Beyin_Hasari": q1_1,
            "S1_Aile_Epilepsi_Febril": q1_2,
            "S1_Psikiyatrik_Hastalik": q1_3,
            "S1_Kardiyolojik_Hastalik": q1_4,
            "S1_JME_Sabah_Sicramalari": q1_5,
            "S1_Fotik_Tetik_Isik": q1_6,
            "S1_Psikolojik_Agir_Travma": q1_7,
            "S1_Akut_Provokasyon_Neden": q1_8,
            
            "S2_Aura_Gastrointestinal": q2_1,
            "S2_Aura_Emosyonel": q2_2,
            "S2_Aura_Dejavu_Bilisel": q2_3,
            "S2_Aura_Koku_Gorme_Duyusal": q2_4,
            "S2_Prodrom_Terleme_Solukluk": q2_5,
            "S2_Tetik_Ayakta_Ortostatik": q2_6,
            
            "S3_Yalnizken_vs_Seyirci": q3_1,
            "S3_Uykuda_vs_Uyanik": q3_2,
            "S3_Baslama_Ani_vs_Kademeli": q3_3,
            "S3_Sure_Kategori": q3_4,
            "S3_Gozlerin_Durumu": q3_5,
            "S3_Yuz_Rengi_Siyanoz": q3_6,
            "S3_Kasilma_Sekli": q3_7,
            "S3_Versif_Bas_Donmesi": q3_8,
            "S3_Otomatizma": q3_9,
            "S3_Dil_Isirma_Lokalizasyonu": q3_10,
            "S3_Inkontinans": q3_11,
            "S3_Nokturnal_Parasomni_Atak": q3_12,
            "S3_Pupil_Isik_Refleksi": q3_13,
            "S3_Pelvik_Itme_Hareketi": q3_14,
            "S3_Ses_Solunum_Paterni": q3_15,
            "S3_Seyirci_Ilgi_Etkisi": q3_16,
            "S3_Atak_Sikligi": q3_17,
            
            "S4_Postiktal_Konfuzyon": q4_1,
            "S4_Amnezi_Var_mi": q4_2,
            "S4_Aglama_Krizi": q4_3,
            "S4_Ciddi_Travmatik_Yaralanma": q4_4,
            "S4_Kume_Ataklar_Arasi_Durum": q4_5,
            
            "Kesin_Klinik_Tani": kesin_tani,
            "Klinik_Not": klinik_not
        }
        
        toplam, cloud_ok = append_patient_to_warehouse(yeni_hasta)
        if cloud_ok is True:
            st.success(f"🎉 **{protokol_no}** başarıyla kaydedildi ve **Google E-Tabloya canlı aktarıldı!** (Veri Tabanındaki Toplam Vaka: **{toplam}**)")
        elif cloud_ok is False:
            st.warning(f"💾 **{protokol_no}** yerel ambarına kaydedildi, ancak Google E-Tablo bağlantısına ulaşılamadı. (Toplam Vaka: **{toplam}**)")
        else:
            st.success(f"🎉 **{protokol_no}** başarıyla Veri Ambarına kaydedildi! (Veri Tabanındaki Toplam Vaka: **{toplam}**)")
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

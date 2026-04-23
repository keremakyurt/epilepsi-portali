import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

st.set_page_config(page_title="TAM UYUMLU ILAE Karar Destek", page_icon="🔬", layout="wide")

st.markdown("""
<style>
    div.stButton > button {
        background-color: #2c3e50;
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #1a252f;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_assets():
    model_path = os.path.join("models", "knn_epilepsy_model.pkl")
    scaler_path = os.path.join("models", "scaler.pkl")
    metadata_path = os.path.join("models", "metadata.pkl")
    
    if os.path.exists(model_path):
        return joblib.load(model_path), joblib.load(scaler_path), joblib.load(metadata_path)
    return None, None, None

model, scaler, meta = load_assets()

st.title("🔬 Tıbbi Karar Destek Arayüzü (ILAE Kapsamlı)")
st.markdown("Bu sistem Jeneralize/Fokal sınıflandırmasına ek olarak; **PNES, Senkop ve Provoke Nöbetleri ayırdetmek** üzere etiyoloji filtreleriyle donatılmıştır.")
st.markdown("---")

c1, c2, c3 = st.columns([1.2, 1, 1.2])

with c1:
    with st.expander("📌 Temel Klinik ve Başlangıç Bilgileri", expanded=True):
        yas = st.number_input("Yaş", min_value=0, max_value=120, value=30)
        cins = st.selectbox("Cinsiyet", [0, 1], format_func=lambda x: "Erkek" if x==1 else "Kadın")
        lat = st.selectbox("Nöbet Başlangıç Lateralitesi", ["Bilinmeyen", "Sol", "Sag", "Bilateral"])
        eti = st.selectbox("Etiyoloji (Kök Neden)", ["Bilinmeyen", "Yapisal", "Genetik", "Infeksiyoz", "Metabolik", "Immun"])
        
    with st.expander("🛑 Nöbet Tekrarlama Risk Faktörleri"):
        uykuda = st.checkbox("Uykuda Nöbet Geçirme Öyküsü")
        beyin = st.checkbox("Önceden Geçirilmiş Beyin Hasarı")

with c2:
    with st.expander("⚖️ Ayırıcı Tanı (PNES/Senkop) Gözlemleri", expanded=True):
        atak = st.number_input("Atak Süresi (Saniye)", min_value=1, max_value=3600, value=90)
        goz = st.checkbox("Atak Anında Gözleri Sıkıca Kapatma / Açmaya Direnç")
        teti = st.checkbox("Tetikleyici: Uzun süre ayakta kalma / Ağrı")
        konf = st.checkbox("Postiktal Konfüzyon (Atak sonrası bilinç bulanıklığı)")
        
    with st.expander("💉 Akut Semptomatik (Provoke) Kontrolü"):
        mss = st.checkbox("Son 7 günde inme, travma veya MSS Enfeksiyonu")
        met = st.checkbox("Ağır metabolik bozukluk (Akut hipoglisemi vb.)")
        mad = st.checkbox("Alkol veya madde yoksunluğu/intoksikasyonu")

bilissel = ["Akalkuli", "Afazi", "Dikkat_bozuklugu", "Deja_vu", "Disosiasyon", "Disfazi", "Halusinasyon", "Ilizyon", "Bellek_bozuklugu", "Ihmal", "Zorlu_dusunce", "Yanitlilikta_bozulma"]
emosyonel = ["Ajitasyon", "Ofke", "Anksiyete", "Aglama", "Korku", "Gulme", "Paranoya", "Keyif"]
otonomik = ["Asistol", "Bradikardi", "Ereksiyon", "Flasing", "Gastrointestinal", "Hipervantilasyon", "Mide_bulantisi", "Solukluk", "Palpitasyon", "Piloereksiyon", "Solunum_degisikligi", "Tasikardi"]
otomatizma = ["Agresyon", "Goz_kirpma", "Bas_sallama", "Manuel_otomatik", "Oral_fasial", "Pedal_cevirme", "Pelvik_kaldirma", "Perseverasyon", "Kosma", "Seksksuel", "Ust_cikarma", "Vokalizasyon", "Yurume"]
motor = ["Dizartri", "Distonik", "Eskrimci_pozisyonu", "Inkoordinasyon", "Jacksonian", "Paralizi", "Parezi", "Versif"]
duyusal = ["Isitsel", "Gustatuar", "Sicaklama", "Olfaktor", "Somatosensoriyel", "Vestibuler", "Gorsel"]

with c3:
    with st.expander("📋 Çoklu Seçimli Semptom Havuzu", expanded=True):
        st.caption("Aynı nöbette birden fazla görülebilecek bulguları seçiniz:")
        sec_bilissel = st.multiselect("Bilişsel Olaylar", bilissel)
        sec_emosyonel = st.multiselect("Emosyonel (Afektif)", emosyonel)
        sec_otonomik = st.multiselect("Otonomik Belirtiler", otonomik)
        sec_otomatizma = st.multiselect("Otomatizma Belirtileri", otomatizma)
        sec_motor = st.multiselect("Motor Belirtiler", motor)
        sec_duyusal = st.multiselect("Duyusal Belirtiler", duyusal)

st.markdown("---")
if st.button("Teşhis Algoritmasını Çalıştır ve Değerlendir", type="primary"):
    if model is None:
        st.error("Model Bulunamadı!")
    else:
        # Algoritmalar
        input_data = {
            'Yas': yas, 'Cinsiyet': cins, 'Atak_Suresi': atak,
            'Goz_kapatma': 1 if goz else 0,
            'Tetikleyici_Ayakta': 1 if teti else 0,
            'Postiktal_Konfuzyon': 1 if konf else 0,
            'Gecirilmis_MSS': 1 if mss else 0,
            'Metabolik_Bozukluk': 1 if met else 0,
            'Madde_Yoksunlugu': 1 if mad else 0,
            'Uykuda_Nobet': 1 if uykuda else 0,
            'Beyin_Hasari': 1 if beyin else 0,
            # Varsayilan Graph
            'EEG_Baglanti_Yogunlugu': 0.5,
            'fMRI_Kumelenme_Katsayisi': 0.5
        }
        
        all_s = bilissel + emosyonel + otonomik + otomatizma + motor + duyusal
        secilenler = sec_bilissel + sec_emosyonel + sec_otonomik + sec_duyusal + sec_motor + sec_otomatizma
        
        for f in all_s:
            input_data[f] = 1 if f in secilenler else 0
            
        lat_map = {"Sol": "Lateralite_Sol", "Sag": "Lateralite_Sag", "Bilateral": "Lateralite_Bilateral"}
        for k,v in lat_map.items():
            input_data[v] = 1 if lat == k else 0
            
        eti_map = {"Genetik": "Etiyoloji_Genetik", "Immun": "Etiyoloji_Immun", "Infeksiyoz": "Etiyoloji_Infeksiyoz", "Metabolik": "Etiyoloji_Metabolik", "Yapisal": "Etiyoloji_Yapisal"}
        for k,v in eti_map.items():
            input_data[v] = 1 if eti == k else 0
            
        vals = []
        for col in meta['features']:
            vals.append(input_data.get(col, 0))
            
        feat_scaled = scaler.transform(np.array([vals]))
        pred = model.predict(feat_scaled)[0]
        prob = model.predict_proba(feat_scaled)[0]
        max_prob = max(prob) * 100
        diagnosis = meta['encoder'].inverse_transform([pred])[0]
        
        c_sonuc, c_bar = st.columns([1, 1])
        with c_sonuc:
            st.subheader("🎯 Sistem Kararı")
            if "Provoke" in diagnosis or "PNES" in diagnosis or "Senkop" in diagnosis:
                st.warning(f"⚠️ DİKKAT (Ayırıcı Tanı): **{diagnosis}** — Güven Oranı: %{max_prob:.1f}")
            else:
                st.success(f"📌 ILAE TESPİTİ: **{diagnosis}** — Güven Oranı: %{max_prob:.1f}")
            
            # Risk Kural Motoru (Model Disi Mantik)
            if uykuda or beyin or eti != "Bilinmeyen":
                st.error("💊 RİSK UYARISI: Tek nöbet geçirilmiş olsa dahi belirlenen risk faktörlerine istinaden hastalarda İlaç Tedavisine Başlama Endikasyonu bulunabilir.")
                
        with c_bar:
            st.markdown("### 📊 Ayırıcı Olasılık Analizi")
            prob_df = pd.DataFrame({"Klinik Çıktı": meta['encoder'].classes_, "İhtimal (%)": prob * 100})
            st.bar_chart(prob_df.set_index("Klinik Çıktı"), height=300)

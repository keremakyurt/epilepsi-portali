import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

def train_survey_models():
    """
    TÜBİTAK 2209-A: Karar Ağacı Anketi Soruları ile Model Eğitimi
    Random Forest ve KNN modellerini eğitir, öznitelik önem analizlerini çıkarır ve kaydeder.
    """
    data_path = os.path.join("data", "ilae_v3_dataset.csv")
    print(f"Resmi Anket Veri Seti Okunuyor: {data_path}")
    df = pd.read_csv(data_path)
    
    X = df.drop(columns=['Karar_Agaci_Tanisi'])
    y_raw = df['Karar_Agaci_Tanisi']
    feature_cols = X.columns.tolist()
    
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 1. Random Forest Modeli
    print("\n--- 1. Random Forest Sınıflandırıcısı Eğitiliyor ---")
    rf = RandomForestClassifier(n_estimators=180, max_depth=18, random_state=42, class_weight='balanced')
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    acc_rf = accuracy_score(y_test, y_pred_rf)
    print(f"Random Forest Test Doğruluğu: %{acc_rf * 100:.2f}")
    
    # 2. KNN Modeli
    print("\n--- 2. K-Nearest Neighbors (KNN) Eğitiliyor ---")
    knn = KNeighborsClassifier(n_neighbors=7, weights='distance')
    knn.fit(X_train_scaled, y_train)
    y_pred_knn = knn.predict(X_test_scaled)
    acc_knn = accuracy_score(y_test, y_pred_knn)
    print(f"KNN Test Doğruluğu: %{acc_knn * 100:.2f}")
    
    # Öznitelik Önem Düzeyleri (Feature Importance)
    importances = rf.feature_importances_
    feat_imp = pd.DataFrame({
        'Soru_Parametre': feature_cols,
        'Onem_Skoru': importances
    }).sort_values(by='Onem_Skoru', ascending=False)
    
    print("\nEn Belirleyici İlk 12 Klinik Soru:")
    print(feat_imp.head(12).to_string(index=False))
    
    # Model ve Varlıkların Kaydedilmesi
    os.makedirs("models", exist_ok=True)
    joblib.dump(rf, os.path.join("models", "rf_epilepsy_model.pkl"))
    joblib.dump(knn, os.path.join("models", "knn_epilepsy_model.pkl"))
    joblib.dump(scaler, os.path.join("models", "scaler.pkl"))
    
    metadata = {
        'encoder': le,
        'features': feature_cols,
        'classes': list(le.classes_),
        'rf_accuracy': acc_rf,
        'knn_accuracy': acc_knn,
        'feature_importances': feat_imp.to_dict(orient='records')
    }
    joblib.dump(metadata, os.path.join("models", "metadata.pkl"))
    print("\nTüm anket modelleri başarıyla kaydedildi!")

if __name__ == '__main__':
    train_survey_models()

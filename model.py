import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import joblib

def train_model():
    print("V3 ILAE Ayirici Tani Dataseti Yukleniyor...")
    data_path = os.path.join("data", "ilae_v3_dataset.csv")
    df = pd.read_csv(data_path)
    
    X_raw = df.drop(columns=['ILAE_Diagnosis'])
    y_raw = df['ILAE_Diagnosis']
    
    # Etiyoloji ve Lateralite text icerir
    X = pd.get_dummies(X_raw, columns=['Lateralite', 'Etiyoloji'], drop_first=True)
    
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    train_cols = X.columns.tolist()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Filtreli (PNES+Senkop) KNN Modeli Egitiliyor...")
    knn = KNeighborsClassifier(n_neighbors=9, weights='distance')
    knn.fit(X_train_scaled, y_train)
    
    y_pred = knn.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"ILAE Model Dogruluk Orani: %{acc*100:.2f}")
    
    os.makedirs("models", exist_ok=True)
    joblib.dump(knn, os.path.join("models", "knn_epilepsy_model.pkl"))
    joblib.dump(scaler, os.path.join("models", "scaler.pkl"))
    joblib.dump({'encoder': le, 'features': train_cols}, os.path.join("models", "metadata.pkl"))
    print("Senkop ve Provoke Destekli Model Kaydedildi!")

if __name__ == '__main__':
    train_model()

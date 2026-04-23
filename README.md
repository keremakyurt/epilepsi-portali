# Epilepsy Decision Support System

A comprehensive decision support system for epilepsy diagnosis and classification based on ILAE (International League Against Epilepsy) criteria, with support for differential diagnosis of PNES (Psychogenic Non-Epileptic Seizures), syncope, and provoked seizures.

## Project Structure

```
epilepsy_project/
├── data/                          # Dataset files (CSVs)
│   ├── epilepsy_dataset.csv       # Synthetic epilepsy dataset
│   └── ilae_v3_dataset.csv        # ILAE v3 differential diagnosis dataset
├── models/                        # Trained models and scalers
│   ├── knn_epilepsy_model.pkl     # KNN classifier model
│   ├── scaler.pkl                 # StandardScaler for feature normalization
│   └── metadata.pkl               # Model metadata (encoder, features)
├── logs/                          # Application logs
├── notebooks/                     # Jupyter notebooks for exploration
├── tests/                         # Unit tests
├── .venv/                         # Python virtual environment
├── .gitignore                     # Git ignore rules
├── app.py                         # Streamlit web application
├── model.py                       # Model training script
├── generate_dataset.py            # Synthetic dataset generation
├── generate_ilae.py               # ILAE dataset generation
├── explore_data.py                # Data exploration script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Features

- **Clinical Input Interface**: Comprehensive symptom and clinical data collection
- **ML-Based Classification**: KNN classifier trained on ILAE criteria
- **Differential Diagnosis**: Support for PNES, syncope, and provoked seizure identification
- **Risk Assessment**: Integrated risk stratification rules
- **Probabilistic Output**: Confidence scores for classification decisions
- **Interactive Web UI**: Streamlit-based user interface

## Setup and Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation Steps

1. Navigate to the project directory:
   ```bash
   cd C:\Users\AkyurtPc\epilepsy_project
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Generate Datasets
```bash
# Generate synthetic epilepsy dataset
python generate_dataset.py

# Generate ILAE v3 differential diagnosis dataset
python generate_ilae.py
```

### Train Model
```bash
python model.py
```

### Run Web Application
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Explore Data
```bash
python explore_data.py
```

## Dataset Information

### epilepsy_dataset.csv
- 1500 synthetic patient records
- Clinical features, EEG network metrics, fMRI connectivity measures
- Binary epilepsy diagnosis target

### ilae_v3_dataset.csv
- 8500 detailed seizure records
- Comprehensive symptom profiles (cognitive, emotional, autonomic, automatisms, motor, sensory)
- ILAE diagnosis classifications including differential diagnoses

## Model Details

- **Algorithm**: K-Nearest Neighbors (KNN) with distance weighting
- **n_neighbors**: 9
- **Features**: 50+ clinical and imaging features
- **Accuracy**: See training output for current model performance
- **Preprocessing**: StandardScaler normalization

## Clinical Classification System

The system supports the following diagnoses:

1. **Generalized Onset Seizures**
   - Motor (Tonic-Clonic, etc.)
   - Non-Motor (Absences)

2. **Focal Onset Seizures**
   - Motor features
   - Non-Motor features
   - Focal to Bilateral Tonic-Clonic

3. **Differential Diagnoses**
   - PNES (Psychogenic Non-Epileptic Seizures)
   - Syncope (Vasovagal fainting)
   - Provoked Seizures (Acute symptomatic)

4. **Unknown/Unclassified Onset**

## Dependencies

See `requirements.txt` for the complete list of Python dependencies.

Key packages:
- pandas: Data manipulation
- numpy: Numerical computing
- scikit-learn: Machine learning
- streamlit: Web application framework
- joblib: Model serialization

## Contributing

For improvements or bug reports, please contact the development team.

## License

This project is intended for medical research and educational purposes.

## Disclaimer

This is a decision support system and should not be used as a sole diagnostic tool. Clinical judgment and professional medical assessment are required for all patient diagnoses.

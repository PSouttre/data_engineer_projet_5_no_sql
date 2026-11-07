import pytest
import pandas as pd

# --- CONFIGURATION ---
# Chemin vers le fichier de données
CHEMIN_CSV = "../projet_5_donnees/healthcare_dataset.csv"

# Colonnes du dataset de départ
COLONNES_ATTENDUES = ['Name', 'Age', 'Gender', 'Blood Type', 'Medical Condition',
       'Date of Admission', 'Doctor', 'Hospital', 'Insurance Provider',
       'Billing Amount', 'Room Number', 'Admission Type', 'Discharge Date',
       'Medication', 'Test Results']

# --- FIXTURE ---
@pytest.fixture(scope="module")
def dataset():
    """
    Charge le CSV une seule fois pour tout le module de test.
    Tous les tests utiliseront ce  DataFrame.
    """
    df = pd.read_csv(CHEMIN_CSV)
    return df

# --- TESTS D'INTÉGRITÉ ---

def test_presence_colonnes(dataset):
    """Vérifie que toutes les colonnes requises sont bien présentes."""
    colonnes_actuelles = dataset.columns.tolist()
    for col in COLONNES_ATTENDUES:
        # L'instruction 'assert' vérifie si la condition est vraie.
        # Si elle est fausse, pytest affiche le message situé après la virgule.
        assert col in colonnes_actuelles, f"ERREUR : La colonne obligatoire '{col}' est manquante dans le CSV."

def test_valeurs_manquantes(dataset):
    """Identifie la présence de valeurs nulles ou NaN dans le dataset."""
    # sum().sum() compte le total absolu de cellules vides dans tout le DataFrame
    total_nan = dataset.isnull().sum().sum()
    assert total_nan == 0, f"ERREUR D'INTÉGRITÉ : Le fichier contient {total_nan} valeurs manquantes."

def test_types_variables(dataset):
    """Contrôle que les types de données sont prêts pour MongoDB."""
    # Vérification des colonnes numériques
    colonnes_numeriques = ['Age', 'Billing Amount', 'Room Number']
    for col in colonnes_numeriques:
        assert pd.api.types.is_numeric_dtype(dataset[col]), f"ERREUR DE TYPE : la colonne {col} doit être numérique."

    # Vérification des colonnes dates (en objet dans le csv, on vérifie qu'elles sont convertibles en datetime sans erreur)
    colonnes_dates = ['Date of Admission', 'Discharge Date']
    for col in colonnes_dates:
        try:
            #on essaie la conversion
            pd.to_datetime(dataset[col])
        except Exception as e:
            pytest.fail(f"ERREUR DE TYPE : Le contenu de {col} n'est pas convertible en date. Détail : {e}")

    # Vérification des colonnes textes
    colonnes_texte = ['Name', 'Gender', 'Blood Type', 'Medical Condition','Doctor', 'Hospital', 'Insurance Provider',
       'Admission Type', 'Medication', 'Test Results']
    for col in colonnes_texte:
        assert pd.api.types.is_object_dtype(dataset[col]), f"ERREUR DE TYPE : le contenu de {col} doit être du texte."



def test_doublons(dataset):
    """Traque les lignes strictement identiques (doublons)."""
    nombre_doublons = dataset.duplicated().sum()
    assert nombre_doublons == 0, f"ERREUR DE DOUBLON : Le fichier contient {nombre_doublons} lignes en double."
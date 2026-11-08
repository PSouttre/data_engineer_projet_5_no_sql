import pytest
import pandas as pd
from pymongo import MongoClient
import datetime

# --- CONFIGURATION ---
URI_MONGODB = "mongodb://localhost:27017/"
NOM_DB = "healthcare_db"
NOM_COLLECTION = "patients"
CHEMIN_CSV = "../../projet_5_donnees/healthcare_dataset.csv"


# --- FIXTURES ---

@pytest.fixture(scope="module")
def db_collection():
    """Établit la connexion à MongoDB et retourne la collection cible."""
    client = MongoClient(URI_MONGODB)
    db = client[NOM_DB]
    collection = db[NOM_COLLECTION]
    yield collection
    client.close()


@pytest.fixture(scope="module")
def total_attendu():
    """Calcule le nombre de lignes attendues après nettoyage du CSV."""
    df = pd.read_csv(CHEMIN_CSV)
    df = df.drop_duplicates()
    return len(df)


# --- TESTS POST-MIGRATION ---

def test_volumetrie_documents(db_collection, total_attendu):
    """Vérifie que le nombre de documents en base correspond au nombre de lignes nettoyées."""
    total_mongodb = db_collection.count_documents({})
    assert total_mongodb == total_attendu, f"ERREUR VOLUMÉTRIE : Nombre de documents attendu {total_attendu}, mais nombre trouvé {total_mongodb}."


def test_types_donnees_mongodb(db_collection):
    """Vérifie l'intégrité des types BSON sur un échantillon de documents."""
    # On prend un document au hasard pour vérifier son typage
    doc_sample = db_collection.find_one()

    assert doc_sample is not None, "La collection est vide !"

    # Vérification que la date d'admission est bien un objet datetime (ISODate dans MongoDB)
    assert isinstance(doc_sample.get("Date of Admission"),
                      datetime.datetime), "ERREUR DE TYPE : 'Date of Admission' n'est pas un format Date."

    # Vérification que l'âge est bien un nombre (int ou float)
    assert isinstance(doc_sample.get("Age"), (int, float)), "ERREUR DE TYPE : 'Age' n'est pas un format numérique."

    # Vérification que le montant de la facture est un nombre (idéalement float)
    assert isinstance(doc_sample.get("Billing Amount"),
                      (int, float)), "ERREUR DE TYPE : 'Billing Amount' n'est pas un format numérique."


def test_presence_index(db_collection):
    """Vérifie que les index pertinents ont bien été créés."""
    index_info = db_collection.index_information()

    # Les clés du dictionnaire renvoyé par index_information() sont les noms des index.
    # pymongo nomme automatiquement les index selon les clés (ex: "Medical Condition_1")
    index_noms = list(index_info.keys())

    # On vérifie la présence de sous-chaînes dans les noms d'index
    index_maladie_present = any("Medical Condition" in nom for nom in index_noms)
    index_date_present = any("Date of Admission" in nom for nom in index_noms)

    assert index_maladie_present, "L'index sur 'Medical Condition' est manquant."
    assert index_date_present, "L'index sur 'Date of Admission' est manquant."
import pandas as pd
from pymongo import MongoClient
import pymongo

# --- CONFIGURATION ---
CHEMIN_CSV = "../../projet_5_donnees/healthcare_dataset.csv"
URI_MONGODB = "mongodb://localhost:27017/"
NOM_DB = "healthcare_db"
NOM_COLLECTION = "patients"


def run_migration():
    print("Démarrage de la migration vers MongoDB...")

    # Extraction
    print(f"Lecture du fichier {CHEMIN_CSV}...")
    df = pd.read_csv(CHEMIN_CSV)

    # Transformation
    # Conversion des chaînes de caractères en objets datetime (format BSON ISODate)
    print("Transformation des types de données (dates)...")
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])

    # Conversion du DataFrame Pandas en liste de dictionnaires Python (équivalent des documents JSON/BSON)
    documents = df.to_dict(orient='records')

    # Chargement
    print("Connexion à MongoDB local...")
    client = MongoClient(URI_MONGODB)
    db = client[NOM_DB]
    collection = db[NOM_COLLECTION]

    # Sécurité : On vide la collection avant l'import pour éviter de doubler les données
    # si on relance le script plusieurs fois pendant les tests.
    collection.drop()

    print(f"Insertion de {len(documents)} documents dans la collection '{NOM_COLLECTION}'...")
    # insert_many() est la méthode PyMongo la plus performante pour insérer en masse (Bulk insert)
    resultat = collection.insert_many(documents)

    print(f"Migration terminée ! {len(resultat.inserted_ids)} documents insérés avec succès.")

    # Indexation
    # Un index accélère la lecture. On cible ici la pathologie et la date d'admission.
    print("Création des index pertinents...")
    collection.create_index([("Medical Condition", pymongo.ASCENDING)])
    collection.create_index([("Date of Admission", pymongo.DESCENDING)])
    print("Index créés.")

    # Fermeture de la connexion
    client.close()


if __name__ == "__main__":
    run_migration()
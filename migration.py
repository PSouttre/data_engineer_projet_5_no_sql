import os
import pandas as pd
from pymongo import MongoClient
import pymongo

# --- CONFIGURATION (Docker ou locale) ---
CHEMIN_CSV = os.getenv("CSV_PATH",  "../../projet_5_donnees/healthcare_dataset.csv")
URI_MONGODB = os.getenv("MONGO_URI","mongodb://localhost:27017/")
NOM_DB = "healthcare_db"
NOM_COLLECTION = "patients"

def charger_csv(chemin):
    '''
    Reçoit le chemin du fichier de données csv et retourne un dataframe
    :return: df
    '''
    print(f"Lecture du fichier {chemin}...")
    df = pd.read_csv(chemin)
    return df

def nettoyer_donnees(df):
    '''
    Supprime les doublons du dataframe.
    :param df: dataframe issue des données csv
    :return: dataframe sans doublons
    '''
    print("Suppression des doublons...")
    df_clean = df.drop_duplicates()
    return df_clean

def convertir_dates(df):
    '''
    Conversion des chaînes de caractères de df_clean en objets datetime (format BSON ISODate)
    :param df: dataframe nettoyés des doublons.
    :return: dataframe final
    '''
    print("Transformation des types de données (dates)...")
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    return df

def connecter_mongodb(uri):
    '''
    Ouvre la connexion à MongoDB et retourne le client et la collection cible.
    :param uri: uri de connexion MongoDB
    :return: tuple (client, collection) : le client pour fermer la connexion à la fin,
             la collection pour insérer les documents
    '''
    print("Connexion à MongoDB...")
    client = MongoClient(uri)
    db = client[NOM_DB]
    collection = db[NOM_COLLECTION]
    return client,collection

def inserer_documents(collection, documents):
    '''
    Vide la collection puis insère tous les documents en une seule opération (insert_many).
    La collection est vidée avant l'import pour éviter les doublons si le script est relancé.
    :param collection: collection MongoDB cible
    :param documents: liste de dictionnaires (un dictionnaire = un document patient)
    :return: nombre de documents insérés
    '''
    # Sécurité : On vide la collection avant l'import pour éviter de doubler les données
    # si on relance le script plusieurs fois pendant les tests.
    collection.drop()
    print(f"Insertion de {len(documents)} documents dans la collection '{collection.name}'...")

    # insert_many() est la méthode PyMongo la plus performante pour insérer en masse (Bulk insert)
    resultat = collection.insert_many(documents)
    return len(resultat.inserted_ids)

def creer_index(collection):
    '''
    Crée les index sur la pathologie et la date d’admission.
    Un index accélère la lecture.
    :param collection: collection MongoDB sur laquelle créer les index
    :return: None
    '''
    print("Création des index pertinents...")
    collection.create_index([("Medical Condition", pymongo.ASCENDING)])
    collection.create_index([("Date of Admission", pymongo.DESCENDING)])
    print("Index créés.")


def run_migration():
    '''
    Enchaîne les étapes Extract -> Transform -> Load -> Index.
    '''
    print("Démarrage de la migration vers MongoDB...")

    # Extraction
    df = charger_csv(CHEMIN_CSV)

    # Transformation
    df = nettoyer_donnees(df)
    df = convertir_dates(df)
    # Conversion du DataFrame en liste de dictionnaires (équivalent des documents JSON/BSON)
    documents = df.to_dict(orient='records')

    # Chargement
    client, collection = connecter_mongodb(URI_MONGODB)
    try:
        nb_documents = inserer_documents(collection, documents)
        print(f"Migration terminée ! {nb_documents} documents insérés avec succès.")
        creer_index(collection)
    finally :
        # Fermeture de la connexion
        client.close()


if __name__ == "__main__":
    run_migration()
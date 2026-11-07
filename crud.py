from pymongo import MongoClient
from datetime import datetime

# Connexion à la base de données
URI_MONGODB = "mongodb://localhost:27017/"
client = MongoClient(URI_MONGODB)
db = client["healthcare_db"]
collection = db["patients"]


def run_crud():

    # CREATE : Créer et insérer un nouveau document
    # On recrée la structure exacte d'un patient du dataset, avec les bons types
    nouveau_patient = {
        "Name": "Test_Patient_DataEngineer",
        "Age": 42,
        "Gender": "Female",
        "Blood Type": "O+",
        "Medical Condition": "Asthma",
        "Date of Admission": datetime(2026, 11, 7),  # Type datetime attendu
        "Doctor": "Dr. Smith",
        "Hospital": "OpenClassrooms General",
        "Insurance Provider": "Medicare",
        "Billing Amount": 1250.50,
        "Room Number": 101,
        "Admission Type": "Emergency",
        "Discharge Date": datetime(2026, 11, 10),
        "Medication": "Albuterol",
        "Test Results": "Inconclusive"
    }

    print("[CREATE] Insertion du patient test...")
    resultat_insertion = collection.insert_one(nouveau_patient)
    # On récupère son id
    id_patient = resultat_insertion.inserted_id
    print(f"Patient inséré avec l'ID BSON : {id_patient}\n")

    # READ : Rechercher le document dans la base
    print("[READ] Recherche du patient dans la base...")
    # On cherche le document dont le nom correspond
    patient_trouve = collection.find_one({"Name": "Test_Patient_DataEngineer"})
    print(f"Patient trouvé ! Son diagnostic initial est : {patient_trouve['Medical Condition']}\n")

    # UPDATE : Mettre à jour une information du document
    print("[UPDATE] Mise à jour du diagnostic et de la facture...")
    # L'opérateur $set est obligatoire dans MongoDB pour modifier des champs spécifiques
    # sans écraser le reste du document
    collection.update_one(
        {"_id": id_patient},
        {"$set": {
            "Medical Condition": "Asthma - Treated",
            "Billing Amount": 1500.00
        }}
    )

    # On relit pour vérifier la modification
    patient_maj = collection.find_one({"_id": id_patient})
    print(
        f"Mise à jour réussie. Nouveau diagnostic : {patient_maj['Medical Condition']}, Nouvelle facture : {patient_maj['Billing Amount']}\n")

    # DELETE : Supprimer le document
    print("[DELETE] Suppression du patient test...")
    collection.delete_one({"_id": id_patient})

    # On vérifie qu'il a bien disparu
    verification_suppression = collection.find_one({"_id": id_patient})
    if verification_suppression is None:
        print("Le patient a été définitivement supprimé de la base.\n")

    print("--- FIN DES OPÉRATIONS CRUD ---")
    client.close()


if __name__ == "__main__":
    run_crud()
"""
Tests de sécurité : vérifient que l'authentification et les rôles MongoDB fonctionnent.
À lancer après la migration (la collection patients doit contenir des données).
"""
import os

import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure

# --- CONFIGURATION ---
HOTE = os.getenv("MONGO_HOST", "localhost")
NOM_DB = os.getenv("MONGO_DB", "healthcare_db")
URI_APP = os.getenv("MONGO_URI")
ANALYSTE_USER = os.getenv("MONGO_ANALYSTE_USER")
ANALYSTE_PASSWORD = os.getenv("MONGO_ANALYSTE_PASSWORD")


def creer_client(uri):
    """Crée un client MongoDB qui abandonne après 3 secondes si la base ne répond pas."""
    return MongoClient(uri, serverSelectionTimeoutMS=3000)


# --- FIXTURES ---
@pytest.fixture
def client_analyste():
    """Connexion avec le compte analyste (lecture seule)."""
    client = creer_client(
        f"mongodb://{ANALYSTE_USER}:{ANALYSTE_PASSWORD}@{HOTE}:27017/{NOM_DB}?authSource={NOM_DB}"
    )
    yield client
    client.close()


@pytest.fixture
def client_app():
    """Connexion avec le compte de l'application (lecture + écriture)."""
    client = creer_client(URI_APP)
    yield client
    client.close()


# --- TESTS ---
def test_acces_refuse_sans_identifiants():
    """Sans identifiants, la lecture des données est refusée."""
    client = creer_client(f"mongodb://{HOTE}:27017/")
    with pytest.raises(OperationFailure):   # pytest.raises(OperationFailure) : le test réussit si l’erreur se produit.
                                            # OperationFailure est l’erreur que pymongo lève quand MongoDB refuse une opération (pas authentifié, pas autorisé).
                                            # C’est l’inverse d’un test classique : on vérifie que la porte reste fermée.
        client[NOM_DB]["patients"].find_one()
    client.close()


def test_acces_refuse_mauvais_mot_de_passe():
    """Un mauvais mot de passe est rejeté."""
    client = creer_client(
        f"mongodb://{ANALYSTE_USER}:mauvais_mdp@{HOTE}:27017/{NOM_DB}?authSource={NOM_DB}"
    )
    with pytest.raises(OperationFailure):
        client[NOM_DB]["patients"].find_one()
    client.close()


def test_analyste_peut_lire(client_analyste):
    """Le compte analyste (read) peut consulter les données."""
    assert client_analyste[NOM_DB]["patients"].find_one() is not None


def test_analyste_ne_peut_pas_ecrire(client_analyste):
    """Le compte analyste (read) ne peut pas insérer de document."""
    with pytest.raises(OperationFailure):
        client_analyste[NOM_DB]["patients"].insert_one({"Name": "Intrus"})


def test_app_peut_lire(client_app):
    """Le compte app (readWrite) peut consulter les données."""
    assert client_app[NOM_DB]["patients"].find_one() is not None


def test_app_ne_peut_pas_creer_utilisateur(client_app):
    """Le compte app ne peut pas créer de compte : c'est réservé à l'administrateur."""
    with pytest.raises(OperationFailure):
        client_app[NOM_DB].command("createUser", "pirate", pwd="pirate", roles=["readWrite"])
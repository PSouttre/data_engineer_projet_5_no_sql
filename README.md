# Projet 5 - Migration d'une base de données vers MongoDB

Ce projet s'inscrit dans le cadre de la formation Data Engineer. Il a pour objectif de migrer un jeu de données médicales (CSV) vers une base de données NoSQL orientée documents (MongoDB), en garantissant l'intégrité des données à l'aide de tests automatisés et la sécurité de la base grâce à l'authentification et à des rôles utilisateurs.

L'ensemble du projet tourne dans des conteneurs Docker : il fonctionne de la même façon sous Windows, macOS et Linux, sans installer Python ni MongoDB sur la machine.

## Sommaire

1. [Concepts clés de MongoDB](#concepts-clés-de-mongodb-nosql)
2. [Architecture](#architecture)
3. [Pipeline ETL et qualité des données](#pipeline-etl-et-qualité-des-données)
4. [Authentification et rôles](#authentification-et-rôles)
5. [Installation](#installation)
6. [Utilisation](#utilisation)
7. [Sauvegarde et restauration](#sauvegarde-et-restauration)
8. [Structure du projet](#structure-du-projet)
9. [Dépannage](#dépannage)

## Concepts clés de MongoDB (NoSQL)

Contrairement aux bases de données relationnelles (SQL) qui utilisent des tables rigides, MongoDB repose sur une architecture plus flexible :

*   **Base de données (Database) :** C'est le conteneur de plus haut niveau pour les données. Une instance MongoDB peut héberger plusieurs bases de données indépendantes.
*   **Collection :** L'équivalent d'une "Table" en SQL. C'est un regroupement de documents. Contrairement à une table, une collection ne force pas un schéma strict : les documents qu'elle contient peuvent avoir des champs différents.
*   **Document :** L'équivalent d'une "Ligne" (Row) en SQL. C'est l'unité de base du stockage dans MongoDB. Les données y sont représentées sous forme de paires clé/valeur au format BSON (une représentation binaire du JSON), permettant d'imbriquer des tableaux ou d'autres sous-documents.
*   **Index :** Structure qui accélère les recherches sur un ou plusieurs champs.

Dans ce projet :
- Base de données : `healthcare_db`
- Collection : `patients` (un document = une admission d'un patient)

## Architecture

Le fichier `docker-compose.yml` définit deux conteneurs :

| Conteneur | Rôle |
|---|---|
| `mongodb_projet5` | Serveur MongoDB avec authentification activée. Les données sont conservées dans un volume persistant (`mongodb_data`). |
| `python_etl_projet5` | Environnement Python 3.12 (image construite à partir du `Dockerfile`) qui exécute les tests, la migration et le script CRUD. |

Le conteneur Python communique avec MongoDB par le réseau interne de Docker (`mongodb:27017`), avec un compte dédié. Les identifiants sont lus dans un fichier `.env` qui n'est jamais versionné.

## Pipeline ETL et qualité des données

La migration est conçue de manière défensive : seules des données validées sont insérées en base. Le script `pipeline.py` enchaîne trois étapes et s'arrête à la première erreur.

1. **Tests pré-migration (`test_pre_migration.py`)**
   Le fichier CSV source est audité avec `pytest` et `pandas` :
   - présence des colonnes obligatoires ;
   - absence de valeurs manquantes ;
   - conformité des types (numériques, dates convertibles, textes) ;
   - absence de doublons après nettoyage.

2. **Migration (`migration.py`)**
   Exécutée uniquement si les tests pré-migration réussissent. Le script est découpé en fonctions, une par étape :

   | Étape | Fonction | Rôle |
   |---|---|---|
   | Extract | `charger_csv()` | Lecture du fichier CSV avec pandas |
   | Transform | `nettoyer_donnees()` | Suppression des doublons |
   | Transform | `convertir_dates()` | Conversion des dates en `datetime` (type BSON ISODate) |
   | Load | `connecter_mongodb()` | Connexion authentifiée à la collection |
   | Load | `inserer_documents()` | Purge de la collection puis insertion en masse (`insert_many`) |
   | Indexation | `creer_index()` | Index sur `Medical Condition` (croissant) et `Date of Admission` (décroissant) |
   | | `run_migration()` | Enchaîne toutes les étapes |

   La collection est vidée avant chaque import pour éviter les doublons en cas de relance. Les tests réutilisent ces fonctions : ils vérifient exactement le même nettoyage que celui appliqué pendant la migration.

3. **Tests post-migration (`test_post_migration.py`)**
   - le nombre de documents en base correspond au nombre de lignes nettoyées ;
   - les types BSON sont corrects (dates, entiers, décimaux) ;
   - les index sont bien présents.

### Schéma d'un document

| Champ | Type BSON |
|---|---|
| `_id` | ObjectId (généré par MongoDB) |
| `Name`, `Gender`, `Blood Type`, `Medical Condition`, `Doctor`, `Hospital`, `Insurance Provider`, `Admission Type`, `Medication`, `Test Results` | String |
| `Age`, `Room Number` | Int |
| `Billing Amount` | Double |
| `Date of Admission`, `Discharge Date` | Date (ISODate) |

## Authentification et rôles

L'authentification MongoDB est activée : sans identifiants, aucune donnée n'est accessible. Chaque compte ne dispose que des droits nécessaires à son usage (principe du moindre privilège).

| Compte (variables du `.env`) | Rôle MongoDB | Périmètre | Usage |
|---|---|---|---|
| `MONGO_ROOT_USER` | `root` | Toutes les bases | Administration uniquement (gestion des comptes). Jamais utilisé par les scripts. |
| `MONGO_APP_USER` | `readWrite` | `healthcare_db` | Application Python : migration, CRUD, tests. |
| `MONGO_ANALYSTE_USER` | `read` | `healthcare_db` | Consultation et exports. Aucune modification possible. |

Mise en place :
- Les variables `MONGO_INITDB_ROOT_USERNAME` et `MONGO_INITDB_ROOT_PASSWORD` activent l'authentification et créent le compte administrateur au premier démarrage.
- Le script `mongo-init/01-creation-utilisateurs.js` est exécuté automatiquement au premier démarrage (volume vide) et crée les comptes application et analyste.
- Les mots de passe sont stockés dans `.env`, exclu du dépôt par le `.gitignore`. Seul le modèle `.env.example` est versionné.
- Le port MongoDB n'est exposé que sur `127.0.0.1` : la base n'est pas accessible depuis le réseau.
- Les données patients (CSV, sauvegardes) sont exclues du dépôt.

Le fichier `test_authentification.py` vérifie ces règles automatiquement :
- accès refusé sans identifiants ou avec un mauvais mot de passe ;
- le compte analyste peut lire mais pas écrire ;
- le compte application peut lire mais ne peut pas créer d'utilisateur.

## Installation

### Prérequis

- **Windows / macOS :** [Docker Desktop](https://www.docker.com/products/docker-desktop/), démarré.
- **Linux :** Docker Engine et le plugin Docker Compose.
- Git.
- Le fichier `healthcare_dataset.csv` ([Healthcare Dataset sur Kaggle](https://www.kaggle.com/datasets/prasad22/healthcare-dataset)).

> Les commandes utilisent `docker compose` (Compose v2). Avec une ancienne version de Docker (Compose v1), remplacer `docker compose` par `docker-compose`.

### 1. Cloner le dépôt

```bash
git clone https://github.com/PSouttre/data_engineer_projet_5_no_sql.git
cd data_engineer_projet_5_no_sql
```

### 2. Ajouter les données

Créer un dossier `data` à la racine du projet et y copier `healthcare_dataset.csv`.

macOS / Linux / Git Bash :
```bash
mkdir -p data
```
Windows (PowerShell) :
```powershell
New-Item -ItemType Directory -Force data
```

Pour utiliser un autre dossier, modifier la variable `CSV_DIR` dans le fichier `.env`.

### 3. Créer le fichier `.env`

macOS / Linux / Git Bash :
```bash
cp .env.example .env
```
Windows (PowerShell) :
```powershell
Copy-Item .env.example .env
```

Ouvrir `.env` et remplacer toutes les valeurs des mots de passe. Utiliser uniquement des lettres et des chiffres : les caractères `@ : / ? # %` rendent l'adresse de connexion invalide.

### 4. Démarrer l'infrastructure

```bash
docker compose up -d --build
```

Vérifier que les deux conteneurs sont lancés :
```bash
docker compose ps
```

## Utilisation

Toutes les commandes se lancent depuis la racine du projet et sont identiques sous Windows, macOS et Linux.

| Action | Commande |
|---|---|
| Pipeline complet (tests, migration, tests) | `docker compose exec python_app python pipeline.py` |
| Tests pré-migration | `docker compose exec python_app python -m pytest test_pre_migration.py -v` |
| Migration seule | `docker compose exec python_app python migration.py` |
| Tests post-migration | `docker compose exec python_app python -m pytest test_post_migration.py -v` |
| Tests d'authentification (après la migration) | `docker compose exec python_app python -m pytest test_authentification.py -v` |
| Démonstration CRUD | `docker compose exec python_app python crud.py` |
| Arrêter les conteneurs (données conservées) | `docker compose down` |

### Opérations CRUD (`crud.py`)

Script qui montre la manipulation d'un document :
*  **Create :** Insertion d'un nouveau document patient (`insert_one`).
*  **Read :** Recherche du patient via un critère spécifique (`find_one`).
*  **Update :** Mise à jour du diagnostic et de la facturation avec l'opérateur ciblé `$set` (`update_one`).
*  **Delete :** Suppression du document pour nettoyer la base de test (`delete_one`).

### Consulter la base avec MongoDB Compass

Se connecter avec le compte analyste (lecture seule), en remplaçant le mot de passe par celui du `.env` :
```
mongodb://analyste:MOT_DE_PASSE@localhost:27017/healthcare_db?authSource=healthcare_db
```

## Sauvegarde et restauration

Les outils `mongoexport` et `mongoimport` sont lancés dans le conteneur MongoDB. L'option `-p` sans valeur demande le mot de passe de façon masquée.

**Exportation (sauvegarde)** avec le compte analyste, la lecture suffit :
```bash
docker compose exec mongodb mongoexport -u analyste -p --authenticationDatabase healthcare_db --db healthcare_db --collection patients --jsonArray --out /tmp/backup_patients.json
docker cp mongodb_projet5:/tmp/backup_patients.json ./backup_patients.json
```

**Importation (restauration)** dans une nouvelle collection, avec le compte application (droits d'écriture nécessaires) :
```bash
docker cp ./backup_patients.json mongodb_projet5:/tmp/backup_patients.json
docker compose exec mongodb mongoimport -u app_etl -p --authenticationDatabase healthcare_db --db healthcare_db --collection patients_restaures --jsonArray --file /tmp/backup_patients.json
```

Le format JSON étendu de `mongoexport` conserve les types BSON (les dates restent au format `$date`). Le fichier de sauvegarde contient des données patients : il est exclu du dépôt.

## Structure du projet

```
.
├── docker-compose.yml               # Définition des conteneurs MongoDB et Python
├── Dockerfile                       # Image de l'application Python
├── requirements.txt                 # Dépendances Python
├── .env.example                     # Modèle des variables d'environnement
├── mongo-init/
│   └── 01-creation-utilisateurs.js  # Création des comptes application et analyste
├── pipeline.py                      # Orchestration : tests, migration, tests
├── migration.py                     # Migration ETL du CSV vers MongoDB
├── crud.py                          # Démonstration des opérations CRUD
├── test_pre_migration.py            # Qualité des données sources
├── test_post_migration.py           # Vérification des données en base
└── test_authentification.py         # Vérification des droits par rôle
```

## Dépannage

**Les comptes ne sont pas créés / « Authentication failed »**
Le script `mongo-init` ne s'exécute que si le volume de données est vide. Si la base a été créée avant l'activation de l'authentification, ou si les identifiants du `.env` ont été modifiés, supprimer le volume (attention : les données sont effacées, relancer ensuite le pipeline) :
```bash
docker compose down -v
docker compose up -d --build
```

**« ports are not available » au démarrage**
Le port 27017 est déjà utilisé, en général par un serveur MongoDB installé directement sur la machine. L'arrêter, ou modifier le port côté machine dans `docker-compose.yml` (par exemple `"127.0.0.1:27018:27017"`).

**`FileNotFoundError` sur le fichier CSV**
Vérifier que `healthcare_dataset.csv` se trouve bien dans le dossier `data/` (ou dans le dossier indiqué par `CSV_DIR` dans `.env`).

**Échec de la migration juste après le premier démarrage**
Au premier lancement, MongoDB redémarre une fois après la création des comptes. Attendre une dizaine de secondes puis relancer la commande.
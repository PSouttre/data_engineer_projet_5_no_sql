# Projet 5 - Migration d'une base de données vers MongoDB

Ce projet s'inscrit dans le cadre de la formation Data Engineer. Il a pour objectif de migrer un jeu de données tabulaire (CSV) vers une base de données NoSQL orientée documents (MongoDB) hébergée en local, en garantissant l'intégrité des données à l'aide de tests unitaires.

## Concepts clés de MongoDB (NoSQL)

Contrairement aux bases de données relationnelles (SQL) qui utilisent des tables rigides, MongoDB repose sur une architecture plus flexible :

*   **Base de données (Database) :** C'est le conteneur physique de plus haut niveau pour les données. Une instance MongoDB peut héberger plusieurs bases de données indépendantes.
*   **Collection :** L'équivalent d'une "Table" en SQL. C'est un regroupement de documents. Contrairement à une table, une collection ne force pas un schéma strict : les documents qu'elle contient peuvent avoir des champs différents.
*   **Document :** L'équivalent d'une "Ligne" (Row) en SQL. C'est l'unité de base du stockage dans MongoDB. Les données y sont représentées sous forme de paires clé/valeur au format BSON (une représentation binaire du JSON), permettant d'imbriquer des tableaux ou d'autres sous-documents.

## Prérequis et installation (Environnement Windows)

Le projet nécessite Python 3 et une instance de MongoDB Community Server tournant en local (port 27017). 

1. Cloner le dépôt et se placer à la racine du projet.
2. Créer l'environnement virtuel :
   `python -m venv venv`
3. Activer l'environnement virtuel :
   `.\venv\Scripts\activate`
4. Installer les dépendances strictes :
   `pip install -r requirements.txt`

## Logique de la migration et qualité des données

La migration est conçue de manière défensive pour garantir que seules des données propres sont insérées en base.

1. **Tests Pré-migration (`test_pre_migration.py`) :** 
   Avant toute manipulation, le fichier CSV source est audité via le framework `pytest` et `pandas`. Les tests vérifient automatiquement :
   - La présence des colonnes obligatoires.
   - L'absence de valeurs manquantes (NaN/Null).
   - La conformité du typage des variables (ex: numériques, dates).
   - L'absence de doublons stricts.
   

   *Pour lancer les tests d'intégrité :*
   `pytest test_pre_migration.py -v`
Messages d'erreur à voir dans le terminal.


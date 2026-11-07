import subprocess
import sys

# Script qui lance pytest en arrière-plan et qui déclenche la migration si, et seulement si, les tests passent à 100%
def run_pipeline():
    print("Début du pipeline de données...")

    # Test : Audit des données sources
    print("\n Étape 1 : Lancement des tests d'intégrité (pytest)...")
    # subprocess lance une commande terminal depuis Python
    result_tests = subprocess.run(["pytest", "test_pre_migration.py", "-v"])

    # Le returncode est 0 si tous les tests sont verts (PASSED)
    if result_tests.returncode != 0:
        print("\n ERREUR : Les tests d'intégrité ont échoué.")
        print("Arrêt du pipeline. Le fichier de migration n'a pas été exécuté.")
        sys.exit(1)  # Arrêt forcé avec code d'erreur

    print("\nTests validés ! Les données sources sont saines.")

    # Chargement : Exécution de la migration
    print("\nÉtape 2 : Lancement de la migration MongoDB...")
    result_migration = subprocess.run(["python", "migration.py"])

    if result_migration.returncode == 0:
        print("\nPipeline exécuté et terminé avec succès !")
    else:
        print("\nERREUR lors de l'exécution de la migration.")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
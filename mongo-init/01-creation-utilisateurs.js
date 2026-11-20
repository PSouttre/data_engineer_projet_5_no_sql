// Script exécuté automatiquement par l'image MongoDB au PREMIER démarrage (volume vide),
// avec le compte administrateur défini dans .env.
// Principe du moindre privilège : chaque compte n'a que les droits nécessaires.

// process.env permet de lire les variables d'environnement du conteneur
const nomDb = process.env.MONGO_DB;

// On se place sur la base healthcare_db : les comptes y seront enregistrés
const base = db.getSiblingDB(nomDb);

// Compte de l'application Python : lecture + écriture sur healthcare_db uniquement
base.createUser({
  user: process.env.MONGO_APP_USER,
  pwd: process.env.MONGO_APP_PASSWORD,
  roles: [{ role: "readWrite", db: nomDb }],
});

// Compte analyste : lecture seule sur healthcare_db
base.createUser({
  user: process.env.MONGO_ANALYSTE_USER,
  pwd: process.env.MONGO_ANALYSTE_PASSWORD,
  roles: [{ role: "read", db: nomDb }],
});

print("Comptes app et analyste créés sur la base " + nomDb);
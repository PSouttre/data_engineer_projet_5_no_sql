# On part d'une image Python officielle, légère (slim), correspondant à ta version
FROM python:3.12-slim

# On définit le dossier de travail à l'intérieur du conteneur
WORKDIR /app

# On copie le fichier des dépendances dans le conteneur
COPY requirements.txt .

# On installe les librairies (pandas, pymongo, pytest)
RUN pip install --no-cache-dir -r requirements.txt

# On garde le conteneur allumé en arrière-plan pour pouvoir y lancer nos scripts manuellement
CMD ["tail", "-f", "/dev/null"]
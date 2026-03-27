# Utiliser Python slim
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Exposer le port
EXPOSE 5000

# Lancer l'application
CMD ["python", "app.py"]
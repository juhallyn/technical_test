# Documentation du Projet

Ce document fournit des instructions pour lancer le projet.

## Structure du Projet

├── Dockerfile
├── Pipfile
├── Pipfile.lock
├── init.py
├── alembic
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── afac7fe86058_initial.py
├── alembic.ini
├── config
│   ├── init.py
│   └── database.py
├── docker-compose.yml
├── main.py
├── models.py
├── subject
└── tests
    ├── init.py
    └── test_main.py

  
## Prérequis

- [Docker](https://www.docker.com/)

- [Docker Compose](https://docs.docker.com/compose/)

- [Python](https://www.python.org/) (pour utiliser Pipenv)

  

## Instructions pour lancer le Projet

  

1.  **Cloner le Projet**

 ```bash

git clone <url_du_projet.git>

cd <nom_du_projet>
```
2. **Configurer les Variables d'Environnement**

Assurez-vous que le fichier .env contient les bonnes valeurs pour les variables d'environnement PostgreSQL :

```bash

POSTGRES_USER=psql

POSTGRES_PASSWORD=psql

POSTGRES_DB=rpn

```
3.  **Lancer les Conteneurs Docker**

  Utilisez Docker Compose pour construire et lancer les conteneurs.

(pour récuperer le shell ajouter l'option `-d`)

```bash
docker-compose up
```
4.  **Accéder au Shell Pipenv**
Accédez au shell Pipenv dans le conteneur.
```bash
docker-compose  exec  app  pipenv  shell
```
5. Installer les Dépendances Python
Dans le shell Pipenv, utilisez la commande suivante pour installer les dépendances Python spécifiées dans le fichier Pipfile :

```pipenv install```
  

6. **Appliquer les Migrations**
Dans le shell Pipenv, utilisez la commande suivante pour appliquer les migrations de base de données avec Alembic :
```bash
alembic  upgrade  head
```

6.  **Redémarrer les Conteneurs Docker**

  ```bash
docker-compose restart
```
L'application sera accessible à l'adresse http://127.0.0.1:8000.

  
-----------------------------------------------------------------------------------------------------------------------------------

# API Endpoints

## 1. Évaluation d'une Expression RPN

-  **URL :**  `/eval_rpn/`

-  **Méthode :** POST

-  **Paramètres :**

-  `rpn` : Expression RPN à évaluer

-  **Exemple :**

```bash
curl  -X  POST  -H  "Content-Type: application/json"  -d  '{"expr": "2 2 * 3 + 1.2 +"}'  http://localhost:8000/eval_rpn/
```
## 2. Exporter les Données en CSV

-  **URL :**  `/export_csv/`

-  **Méthode :** GET

-  **Exemple :**

```bash
curl  http://localhost:8000/export_csv/  >  export.csv
```
------------------------------------------------------------------------------------------------------
# Tests unitaires 
Exécutez les tests unitaires :
```bash
docker-compose  exec  app  python  -m  unittest  discover  -s  tests
```
------------------------------------------------------------------------------------------------------

# Paquets Utilisés

- FastAPI : Framework web moderne pour les API avec Python 3.7+.
- Uvicorn : Serveur ASGI pour exécuter des applications FastAPI.
- SQLAlchemy : Bibliothèque SQL pour Python.
- Psycopg2-binary : Adaptateur PostgreSQL pour Python.
- Alembic : Outil de migration de base de données pour SQLAlchemy.
- HTTPX : Bibliothèque client HTTP asynchrone pour Python.
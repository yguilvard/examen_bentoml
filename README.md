# Examen BentoML
<https://github.com/yguilvard/examen_bentoml>

## Mise en place
```bash
# Decompression de l'archive
mkdir ~/examen_bentoml && tar xzf admission_service_submission.tar.gz -C ~/examen_bentoml
cd ~/examen_bentoml
```

Cette archive contient:
- `admission_service_docker_image.tar.gz`
- `requirements.txt`
- `README.md`
- `tests/`

## Lancer le service

### 1. Charger l'image Docker

```bash
# Chargement de l'image
docker load -i admission_service_docker_image.tar.gz
```

L'image de rendu est construite pour `linux/amd64`.

### 2. Initialiser le stockage persistant local

```bash
# Creation du répertoire de fonctionnement des api
mkdir data/ 2>/dev/null

# Création du secret
docker run --rm \
  --user root \
  -e PYTHONPATH=/home/bentoml/bento/src \
  -v "$(pwd)/data:/data" \
  --entrypoint sh \
  admission_service:latest \
  -lc '/app/.venv/bin/python -m src.api.create_jwt_secret_file -o /data/.jwt_secret.key'

# Donne accès à l'utilisateur BentoML (default 1034)
docker run --rm \
  --user root \
  -v "$(pwd)/data:/data" \
  --entrypoint sh \
  admission_service:latest \
  -lc "chown -R 1034:1034 /data"

# Récupération de la clé
export JWT_SECRET_KEY="$(cat data/.jwt_secret.key)"


# Initialisation de la base des tokens depuis le container
docker run --rm \
  -v "$(pwd)/data:/data" \
  --entrypoint sh \
  admission_service:latest \
  -lc 'mkdir -p /data/api && printf "[]\n" > /data/api/tokens.db.json'

# Creation de l'utilisateur admin
docker run --rm \
  -e ADMISSION_DATA_DIRECTORY=/data \
  -e JWT_SECRET_KEY="$JWT_SECRET_KEY" \
  -e PYTHONPATH=/home/bentoml/bento/src \
  -v "$(pwd)/data:/data" \
  --entrypoint sh \
  admission_service:latest \
  -lc '/app/.venv/bin/python -m src.adapters.users_fs --user admin --password admin'

```

Notes :
- `data/.jwt_secret.key` est persistant et peut etre conservé entre les runs.
- `data/api/users.db.json` et `data/api/tokens.db.json` sont persistés via le point de montage `/data`.

### 3. Démarrer le service

> Dans un premier terminal :

```bash
# Démarrage avec exposition du port et volume
docker run --rm -p 3000:3000 \
  -e ADMISSION_DATA_DIRECTORY=/data \
  -e JWT_SECRET_KEY="$JWT_SECRET_KEY" \
  -v "$(pwd)/data:/data" \
  admission_service:latest
```

## Lancer les tests

### Tests automatiques

> Dans un second terminal

```bash
cd ~/examen_bentoml
# Installation de pip
sudo apt-get update && sudo apt-get install python3-pip python3.12-venv

# Création de l'environnement virtuel
python3 -m venv .venv

# Récupération de la clé (tests avec payload)
export JWT_SECRET_KEY="$(cat data/.jwt_secret.key)"

# Activation
source .venv/bin/activate

# Installation des pré-requis
pip install -r requirements.txt

# Lancement des tests
TEST_API_USERNAME=admin TEST_API_PASSWORD=admin TEST_API_PORT=3000 JWT_SECRET_KEY="$JWT_SECRET_KEY" pytest -v tests/
```

### Tests en console

```console
# Récupération d'un token
user@host:~$ TOKEN=$(curl -s -X POST http://localhost:3000/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' | jq -r '.access_token')

# Envoi d'une requête de prediction
user@host:~$ curl -s -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"request":{"gre_score":320,"toefl_score":110,"rating":4,"sop":4,"lor":4,"cgpa":8.5,"research_xp":1}}'
  | jq
{
  "prediction": 0.7557780264929408
}
```

Le endpoint `/predict` attend des valeurs brutes metier. La normalisation est appliquee dans le service avant l'appel au modele.

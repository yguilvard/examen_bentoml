# Examen BentoML

Cette archive contient:
- `admission_service_docker_image.tar.gz`
- `requirements.txt`
- `README.md`
- `tests/`

## Lancer le service

### 1. Charger l'image Docker

```bash
docker load -i admission_service_docker_image.tar.gz
```

### 2. Initialiser le stockage persistant local

```bash
mkdir -p data/api
docker run --rm \
  -v "$(pwd)/data:/data" \
  admission_service:latest \
  python -m src.api.create_jwt_secret_file -o /data/jwt_secret.key
export JWT_SECRET_KEY="$(cat data/jwt_secret.key)"
docker run --rm \
  -e ADMISSION_DATA_DIRECTORY=/data \
  -e JWT_SECRET_KEY="$JWT_SECRET_KEY" \
  -v "$(pwd)/data:/data" \
  admission_service:latest \
  python -m src.adapters.users_fs --user admin --password admin
```

Notes :
- `data/jwt_secret.key` est persistant et peut etre conservé entre les runs.
- `data/api/users.db.json` et `data/api/tokens.db.json` sont persistés via le point de montage `/data`.

### 3. Démarrer le service

Dans un premier terminal :

```bash
docker run --rm -p 3000:3000 \
  -e ADMISSION_DATA_DIRECTORY=/data \
  -e JWT_SECRET_KEY="$JWT_SECRET_KEY" \
  -v "$(pwd)/data:/data" \
  admission_service:latest
```

## Lancer les tests

Dans un second terminal :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
TEST_API_USERNAME=admin TEST_API_PASSWORD=admin TEST_API_PORT=3000 JWT_SECRET_KEY="$JWT_SECRET_KEY" pytest -v tests/
```

# Malicious Text Feature Engineering System (MTFES)

MTFES is a FastAPI service that fetches texts from MongoDB, extracts features (rarest word, sentiment, weapon mention), and exposes the processed data via HTTP endpoints.

## Features
- Data fetch from MongoDB Atlas (or any MongoDB) via connection string
- Text processing with NLTK VADER sentiment, rarest word, and weapon blacklist match
- FastAPI service with `/health`, `/data`, `/refresh`, and OpenAPI docs at `/docs`

## Tech Stack
- Python 3.11, FastAPI, Uvicorn
- PyMongo, Pandas, NLTK (VADER)
- Docker, OpenShift (optional deployment)

## Project Layout
```
MTFES/
  app/
    main.py        # FastAPI app and endpoints
    manager.py     # Orchestrates fetch and processing
    fetcher.py     # MongoDB fetch logic (env-driven)
    processor.py   # Text feature engineering
  data/
    weapons.txt    # Weapon blacklist used by processor
  Dockerfile
  requirements.txt
```

## Configuration
Set environment variables (locally or in OpenShift):
- `MONGODB_URI` (required): e.g. `mongodb+srv://<user>:<pass>@<cluster>/<db>`
  - To avoid long hangs, you can append `?serverSelectionTimeoutMS=5000&connectTimeoutMS=5000`.
- `DB_NAME` (required): e.g. `IranMalDB`

## Local Development
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment
export MONGODB_URI="mongodb+srv://IRGC:iraniraniran@iranmaldb.gurutam.mongodb.net/"
export DB_NAME="IranMalDB"

# Run API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test
curl http://127.0.0.1:8000/health
open http://127.0.0.1:8000/docs
```

## Docker
The Dockerfile pre-installs NLTK resources and CA certificates. Build for x86_64 if your cluster is x86.
```bash
# Enable buildx (once)
docker buildx create --use 2>/dev/null || true

# Build and push (amd64)
docker buildx build --platform linux/amd64 -t <dockerhub_user>/mtfes:latest --push .

# Optional: multi-arch
# docker buildx build --platform linux/amd64,linux/arm64 -t <dockerhub_user>/mtfes:latest --push .

# Image variant with NLTK + dnspython baked in (recommended)
docker buildx build --platform linux/amd64 -t <dockerhub_user>/mtfes:nltk-dns --push .
```

## OpenShift (deploy from Docker Hub)
```bash
# Login and select project
oc login https://api.<cluster>:6443
oc new-project <project> || true
oc project <project>

# ConfigMap for DB settings (short timeouts recommended)
oc create configmap mtfes-config \
  --from-literal=MONGODB_URI="mongodb+srv://IRGC:iraniraniran@iranmaldb.gurutam.mongodb.net/?serverSelectionTimeoutMS=5000&connectTimeoutMS=5000" \
  --from-literal=DB_NAME="IranMalDB" || true

# Create app from your Docker Hub image
och new-app docker.io/<dockerhub_user>/mtfes:nltk-dns --name=mtfes || true
oc set env deploy/mtfes --from=configmap/mtfes-config

# Expose service and create a public Route
oc expose svc/mtfes

# Optional: extend route timeout for long DB fetches
oc annotate route mtfes haproxy.router.openshift.io/timeout=120s --overwrite

# Wait and get URL
oc rollout status deploy/mtfes
oc get route mtfes -o jsonpath='{.spec.host}{"\n"}'
```

## Endpoints
- `GET /health` – service liveness
- `GET /data` – processed records as JSON (404 if no data)
- `GET /refresh` – re-fetch from MongoDB and re-process
- `GET /docs` – interactive API docs

## Troubleshooting
- 404 at `/` is expected; use `/health` or `/docs`.
- If `/data` returns 404 or `/refresh` times out:
  - Verify env vars in the deployment.
  - Ensure network egress to MongoDB Atlas and that Atlas network access allows the cluster egress IPs.
  - Add connection timeouts to `MONGODB_URI` as shown above.
- On OpenShift, if the pod fails with “exec format error”, rebuild the image for `linux/amd64` or push a multi-arch image.

## License
MIT

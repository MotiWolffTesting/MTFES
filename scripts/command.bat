# 0) Navigate to project root
cd "/Users/mordechaywolff/Desktop/IDF/8200 Training/Data/Week-8/MTFES"

# 1) Local development (Windows)
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set MONGODB_URI=mongodb+srv://IRGC:iraniraniran@iranmaldb.gurutam.mongodb.net/
set DB_NAME=IranMalDB
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test locally
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/docs

# 2) Docker - build and push
docker login

docker buildx create --use

docker buildx build --platform linux/amd64 -t motiwolff/mtfes:latest --push .

docker buildx build --platform linux/amd64,linux/arm64 -t motiwolff/mtfes:latest --push .

docker buildx build --platform linux/amd64 -t motiwolff/mtfes:nltk-dns --push .

docker buildx imagetools inspect motiwolff/mtfes:latest

# 3) OpenShift - deploy from Docker Hub (no YAML)
oc login https://api.<cluster>:6443 --username=<user> --password=<pass>

oc new-project motiwolff-dev
oc project motiwolff-dev

oc create configmap mtfes-config \
  --from-literal=MONGODB_URI="mongodb+srv://IRGC:iraniraniran@iranmaldb.gurutam.mongodb.net/?serverSelectionTimeoutMS=5000&connectTimeoutMS=5000" \
  --from-literal=DB_NAME="IranMalDB"

oc new-app docker.io/motiwolff/mtfes:nltk-dns --name=mtfes

oc set env deploy/mtfes --from=configmap/mtfes-config

oc expose svc/mtfes

oc annotate route mtfes haproxy.router.openshift.io/timeout=120s --overwrite

oc rollout status deploy/mtfes
oc get route mtfes -o jsonpath="{.spec.host}\n"

# Test via route
curl http://<ROUTE_HOST>/health
curl http://<ROUTE_HOST>/docs
curl http://<ROUTE_HOST>/refresh
curl http://<ROUTE_HOST>/data

# 3.1) Pin image digest / force amd64 (optional)
oc set triggers deploy/mtfes --remove-all
oc annotate deploy/mtfes image.openshift.io/triggers- --overwrite

oc set image deploy/mtfes mtfes=docker.io/motiwolff/mtfes@sha256:0c801f5b12085843934d3477ef5274e7beb7af4c34b7398ea7984037e3141488

oc patch deploy/mtfes --type='json' -p='[{"op":"add","path":"/spec/template/spec/containers/0/imagePullPolicy","value":"Always"}]'

oc rollout restart deploy/mtfes
oc rollout status deploy/mtfes

# 4) Troubleshooting
oc set env deploy/mtfes --list | grep -E 'MONGODB_URI|DB_NAME'

oc get pods -l deployment=mtfes
oc describe pod <POD_NAME> | sed -n '/Image:/,/Image ID:/p'

oc logs -f deploy/mtfes

POD=$(oc get pod -n motiwolff-dev -l deployment=mtfes -o name | head -n1)
oc exec -i -n motiwolff-dev "$POD" -- python - <<'PY'
from pymongo import MongoClient
import os
c = os.environ["MONGODB_URI"]
try:
    print(MongoClient(c, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000).admin.command("ping"))
except Exception as e:
    print("Ping failed:", e)
PY

# 5) Cleanup
oc delete project motiwolff-dev

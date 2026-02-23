# 🚀 Deployment Checklist

Follow these steps to get your application running on OpenShift with GitHub Actions CI/CD.

## ✅ Prerequisites

- [ ] GitHub account with the two repositories pushed
- [ ] Docker Hub account
- [ ] OpenShift Developer Sandbox account (free)

---

## 📋 Step 1: GitHub Secrets (2 minutes)

Add these to your `python-task-api` repository:

**Settings → Secrets and variables → Actions → New repository secret**

1. **DOCKERHUB_USERNAME**
   - Value: Your Docker Hub username
   - Example: `john_doe`

2. **DOCKERHUB_TOKEN**
   - Value: Your Docker Hub access token
   - Get it: Docker Hub → Account Settings → Security → New Access Token
   - Name it: `github-actions`
   - Permissions: Read, Write, Delete

3. **OPENSHIFT_SERVER**
   - Value: Your OpenShift API server URL
   - Get it: OpenShift Dashboard → Copy Login Command → Extract the server URL
   - Example: `https://api.sandbox.openshift.com:6443`

4. **OPENSHIFT_TOKEN**
   - Value: Your OpenShift login token
   - Get it: OpenShift Dashboard → Copy Login Command → Extract the token

---

## 📋 Step 2: Setup OpenShift Cluster (5 minutes)

### 2a. Create OpenShift Sandbox Account
```bash
https://developers.redhat.com/developer-sandbox
```

### 2b. Create New Project
```bash
oc new-project task-api
```

### 2c. Setup PostgreSQL Database
```bash
oc new-app postgresql-persistent \
  -p POSTGRESQL_USER=taskapi \
  -p POSTGRESQL_PASSWORD=SecurePass123 \
  -p POSTGRESQL_DATABASE=taskdb \
  -n task-api
```

### 2d. Setup Redis Cache
```bash
oc apply -f k8s-manifests/infrastructure/redis/redis.yaml -n task-api
```

### 2e. Create Docker Hub Secret
```bash
oc create secret docker-registry dockerhub-secret \
  --docker-server=docker.io \
  --docker-username=YOUR_DOCKERHUB_USERNAME \
  --docker-password=YOUR_DOCKERHUB_TOKEN \
  -n task-api
```

---

## 📋 Step 3: Configure Image Registry (3 minutes)

Update the Kustomize configuration to use your Docker Hub username:

```bash
cd k8s-manifests/apps/task-api/base
kustomize edit set image task-api=YOUR_DOCKERHUB_USERNAME/task-api:latest
cd /home/dera_kings20/AZURE_devops
git add k8s-manifests/apps/task-api/base/kustomization.yaml
git commit -m "Configure Docker Hub image registry"
git push
```

Replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username.

---

## 📋 Step 4: Trigger First Deployment (1 minute)

Push any change to trigger GitHub Actions pipeline:

```bash
cd python-task-api
git commit --allow-empty -m "Trigger initial deployment"
git push origin main
```

---

## 📋 Step 5: Watch Pipeline Run (2 minutes)

1. Go to: `https://github.com/YOUR_USERNAME/python-task-api`
2. Click **Actions** tab
3. Watch the workflow run
4. Should see:
   - ✅ **CI** workflow: Tests, lint, type-checking
   - ✅ **Build & Deploy** workflow: Build image, push to Docker Hub, deploy to OpenShift

---

## 📋 Step 6: Expose Application (2 minutes)

After deployment succeeds, expose the service:

```bash
oc expose service task-api -n task-api
```

Get the public URL:

```bash
oc get route task-api -n task-api
# Copy the route URL from the output
```

---

## 📋 Step 7: Test Application (2 minutes)

```bash
# Get the route URL
ROUTE=$(oc get route task-api -n task-api -o jsonpath='{.spec.host}')

# Test health endpoint
curl -X GET http://$ROUTE/health

# Get API documentation
curl -X GET http://$ROUTE/docs

# Or open in browser:
# http://$ROUTE/docs
```

---

## 🎯 Expected Workflow After Setup

```
1. Push code to GitHub
   ↓
2. GitHub Actions CI runs (tests, lint, type-check)
   ↓
3. If CI passes, Build & Deploy runs
   ├─ Builds Docker image
   ├─ Pushes to Docker Hub
   ├─ Deploys to OpenShift
   ↓
4. Application automatically updated on OpenShift
```

---

## 🛠️ Troubleshooting

### Workflow fails in CI step
- Check Python syntax errors
- Run locally: `pytest` tests
- Check linting: `black --check app/` and `flake8 app/`

### Workflow fails in Build & Deploy step
1. Verify DOCKERHUB_TOKEN is correct (not username)
2. Verify OPENSHIFT_TOKEN hasn't expired
3. Check OpenShift resource limits haven't been exceeded

### Application doesn't deploy to OpenShift
1. Verify postgres and redis are running:
   ```bash
   oc get pods -n task-api
   ```
2. Check pod logs:
   ```bash
   oc logs -n task-api --all-containers -l app=task-api
   ```

### Can't connect to application
1. Verify route is exposed:
   ```bash
   oc get route -n task-api
   ```
2. Test internal service:
   ```bash
   oc port-forward -n task-api svc/task-api 8000:8000
   curl http://localhost:8000/health
   ```

---

## 📞 Quick Command Reference

```bash
# OpenShift login
oc login --token=TOKEN --server=SERVER

# View logs
oc logs -n task-api -l app=task-api -f

# Scale replicas
oc scale deployment task-api --replicas=3 -n task-api

# Delete and redeploy
oc delete deployment task-api -n task-api
# Then push a new commit to trigger GitHub Actions

# Get all resources
oc get all -n task-api

# Describe a pod
oc describe pod POD_NAME -n task-api

# Execute command in pod
oc exec -it POD_NAME -n task-api -- /bin/bash
```

---

## ✅ Verification Checklist

After all steps:

- [ ] GitHub Secrets are configured (4 secrets: DOCKERHUB_USERNAME, DOCKERHUB_TOKEN, OPENSHIFT_SERVER, OPENSHIFT_TOKEN)
- [ ] OpenShift project exists: `task-api`
- [ ] PostgreSQL database is running
- [ ] Redis cache is running
- [ ] Docker Hub secret is created in OpenShift
- [ ] Kustomize configuration updated with your Docker username
- [ ] Initial commit pushed, GitHub Actions workflow completed successfully
- [ ] Application route is exposed
- [ ] Can access application at public URL
- [ ] `/health` endpoint returns success
- [ ] Can view API docs at `/docs`

---

## 🎓 For Your CV

**You can now say:**

> "Implemented a complete CI/CD pipeline using GitHub Actions that automatically tests, builds, and deploys a Python FastAPI microservice to OpenShift Kubernetes cluster. Docker images are pushed to Docker Hub registry, and deployments are managed through Kustomize infrastructure-as-code."

**This demonstrates:**
- ✅ CI/CD automation (GitHub Actions)
- ✅ Containerization (Docker)
- ✅ Container registries (Docker Hub)
- ✅ Kubernetes/Container orchestration (OpenShift)
- ✅ Infrastructure-as-Code (Kustomize)
- ✅ Automated testing and quality checks
- ✅ Python backend development (FastAPI)

---

## 📚 Key Files

- `.github/workflows/ci.yml` - Automated testing and linting
- `.github/workflows/deploy.yml` - Build, push, and deploy
- `k8s-manifests/apps/task-api/base/` - Base Kubernetes manifests
- `k8s-manifests/infrastructure/redis/` - Redis cache infrastructure
- `python-task-api/Dockerfile` - Multi-stage Docker build
- `python-task-api/requirements.txt` - Python dependencies

---

## ❓ Need Help?

Refer to:
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed architecture overview
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Feature documentation
- [k8s-manifests/README.md](k8s-manifests/README.md) - Kubernetes details

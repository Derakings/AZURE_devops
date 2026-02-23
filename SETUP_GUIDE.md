 # 🚀 Production CI/CD Project Setup Guide

**🔴 IMPORTANT: Project Name Substitution**

Throughout this guide, you'll see `-n task-api` in command examples. **Always replace `task-api` with your actual OpenShift project name.**

```bash
# Check your project name:
oc get projects

# You'll see something like:
# NAME              DISPLAY NAME    STATUS
# derakings-dev     derakings-dev   Active
```

**Example substitution:**
- See: `oc get pods -n task-api`
- Replace with: `oc get pods -n derakings-dev` (use YOUR project name)

For convenience, you can set an environment variable:
```bash
MY_PROJECT=$(oc project -q)  # Gets your current project name
# Then use: oc get pods -n $MY_PROJECT
```

---

Complete guide to deploy the Task Management API using GitHub Actions and OpenShift.

## 📊 Project Overview

**What You're Building:**
- FastAPI microservice with PostgreSQL and Redis
- Containerized with Docker, deployed to OpenShift
- CI pipeline with GitHub Actions (test, lint, type-check)
- CD pipeline with GitHub Actions (build, push, deploy)
- Production-ready with monitoring, health checks, and auto-scaling

**Technologies:**
- **Application**: Python 3.11, FastAPI, PostgreSQL, Redis
- **CI/CD**: GitHub Actions
- **Container**: Docker, Docker Hub
- **Orchestration**: OpenShift/Kubernetes
- **IaC**: Kustomize for manifest management

## 📋 Prerequisites Checklist

### Required Accounts
- [ ] GitHub account (for code repositories & CI/CD)
- [ ] Docker Hub account (for container registry)
- [ ] Red Hat account (for OpenShift Developer Sandbox)

### Local Tools (Optional for local testing)
- [ ] Docker Desktop
- [ ] Python 3.11+
- [ ] kubectl or oc CLI
- [ ] Git

---

## 🎯 Phase 1: Repository Setup (15 minutes)

### Step 1.1: Initialize Application Repository

```bash
cd /home/dera_kings20/AZURE_devops/python-task-api

# Initialize Git repository
git init
git add .
git commit -m "Initial commit: FastAPI Task Management API"

# Create GitHub repository (via GitHub CLI or web interface)
gh repo create python-task-api --public --source=. --remote=origin

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 1.2: Initialize Deployment Repository

```bash
cd /home/dera_kings20/AZURE_devops/k8s-manifests

# Initialize Git repository
git init
git add .
git commit -m "Initial commit: Kubernetes manifests for Task API"

# Create GitHub repository
gh repo create k8s-manifests --public --source=. --remote=origin

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🔐 Phase 2: Docker Hub & GitHub Secrets Setup (10 minutes)

### Step 2.1: Create Docker Hub Account & Repository

1. **Sign up for Docker Hub** (if you don't have an account)
   - Go to https://hub.docker.com/signup
   - Create free account
   - Verify email

2. **Create Docker Hub Access Token**
   - Login to Docker Hub
   - Go to **Account Settings** → **Security**
   - Click **"New Access Token"**
   - Name: `github-actions`
   - Permissions: Read, Write, Delete
   - **Copy the token and save it securely**

### Step 2.2: Add GitHub Secrets

In your **python-task-api** GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** and add these:

| Secret Name | Value |
|------------|-------|
| `DOCKERHUB_USERNAME` | derakings |
| `DOCKERHUB_TOKEN` |  |
| `OPENSHIFT_SERVER` | Your OpenShift cluster URL |
| `OPENSHIFT_TOKEN` | Your OpenShift API token |

**How to get OpenShift credentials:**
```bash
# Login to OpenShift web console: https://console-openshift-console.apps.<cluster>.openshiftapps.com
# Click your username (top right) → "Copy login command"
# A new tab opens showing:
# oc login --token=sha256~xxx --server=https://api.xxx.openshiftapps.com:6443

# Extract token and server from that command and add as GitHub secrets
```

---

## ☸️ Phase 3: OpenShift Setup (15 minutes)

### Step 3.1: Sign Up for OpenShift Developer Sandbox

1. Visit https://developers.redhat.com/developer-sandbox
2. Click "Start your sandbox for free"
3. Login with Red Hat account (create if needed)
4. Verify email and phone number
5. Wait for sandbox provisioning (~2 minutes)

### Step 3.2: Login to OpenShift & Get Token

```bash
# Login to OpenShift web console
# Click your username (top right) → "Copy login command"
# A new tab opens → Click "Display Token"
# You'll see the full login command

# Copy and run in terminal:
oc login --token=<your-token> --server=https://api.<cluster>.openshiftapps.com:6443

# Verify login
oc whoami
oc whoami --show-server
```

### Step 3.3: Use Your Pre-Created Project

**✅ OpenShift Developer Sandbox automatically creates a project for you!**

You don't need to create a new project. Your sandbox comes with a pre-created project:

```bash
# Check your existing projects
oc get projects

# You'll see something like:
# NAME              DISPLAY NAME    STATUS
# derakings-dev     derakings-dev   Active
```

**Use your existing project (replace `derakings-dev` with your actual project name):**

```bash
# Switch to your project
oc project derakings-dev

# Verify you're in the right project
oc whoami --show-project
```

**Throughout this guide, whenever you see `-n task-api`, replace it with your actual project name** (`-n derakings-dev`).

### Step 3.4: Deploy PostgreSQL

```bash
# First, switch to your project
oc project derakings-dev   # Use YOUR project name here

# Deploy PostgreSQL
oc new-app postgresql-persistent \
  -p POSTGRESQL_USER=taskapi \
  -p POSTGRESQL_PASSWORD=SecurePass123 \
  -p POSTGRESQL_DATABASE=taskdb \
  -p VOLUME_CAPACITY=1Gi

# Wait for PostgreSQL to be ready
oc wait --for=condition=ready pod -l name=postgresql --timeout=300s
```

### Step 3.5: Deploy Redis

```bash
# Deploy Redis to your project
oc apply -f k8s-manifests/infrastructure/redis/redis.yaml
```

---

## 🔑 Phase 4: Configure Docker Registry Secret (5 minutes)

```bash
# Create Docker Hub secret for pulling images
oc create secret docker-registry dockerhub-secret \
  --docker-server=docker.io \
  --docker-username=$DOCKERHUB_USERNAME \
  --docker-password=$DOCKERHUB_TOKEN \
  --docker-email=ignored@example.com
```

---

## 🚀 Phase 5: Deploy with GitHub Actions (5 minutes)

### Step 5.1: Update Kubernetes Manifest

```bash
cd k8s-manifests/apps/task-api/base

# Update image name with your Docker Hub username
kustomize edit set image task-api=<your-dockerhub-username>/task-api:latest

# Commit changes
git add .
git commit -m "Update image registry to Docker Hub"
git push
```

### Step 5.2: Trigger Deployment

Make a test commit to trigger the GitHub Actions workflow:

```bash
cd python-task-api

# Make a small change
echo "# Updated README" >> README.md

# Commit and push
git add .
git commit -m "Trigger CI/CD deployment"
git push
```

### Step 5.3: Monitor GitHub Actions

1. Go to your **python-task-api** GitHub repository
2. Click **"Actions"** tab
3. Click the workflow run to view details
4. Watch the stages:
   - ✅ **CI Pipeline**: Runs tests, linting, type-checking
   - ✅ **Build & Push**: Builds Docker image and pushes to Docker Hub
   - ✅ **Deploy**: Deploys to OpenShift using Kustomize

---

## 🧪 Phase 6: Verify Deployment (5 minutes)

### Step 6.1: Check Deployment Status

```bash
# Check if pods are running
oc get pods -n task-api

# Check deployments
oc get deployment -n task-api

# Check services
oc get svc -n task-api

# Wait for deployment to be ready
oc rollout status deployment/task-api -n task-api --timeout=5m
```

### Step 6.2: Expose Application

```bash
# Create a route to expose the application
oc expose service task-api -n task-api

# Get the application URL
echo "Application URL:"
oc get route task-api -n task-api -o jsonpath='{.spec.host}'
```

### Step 6.3: Test API Endpoints

```bash
# Set the API URL
API_URL="https://$(oc get route task-api -n task-api -o jsonpath='{.spec.host}')"

# Health check
curl -k $API_URL/health

# Access Swagger UI
echo "Swagger Docs: $API_URL/docs"

# Register a user
curl -k -X POST $API_URL/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'

# Login
TOKEN=$(curl -k -X POST $API_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }' | jq -r .access_token)

# Create a task
curl -k -X POST $API_URL/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing the API",
    "priority": "high",
    "status": "todo"
  }'

# List tasks
curl -k -H "Authorization: Bearer $TOKEN" \
  $API_URL/api/v1/tasks
```

---

## 📊 Phase 7: Monitor Application (5 minutes)

### Step 7.1: View Logs

```bash
# Application logs
oc logs -f deployment/task-api -n task-api --all-containers

# PostgreSQL logs
oc logs -f deployment/postgresql -n task-api

# Redis logs (if running)
oc logs -f statefulset/redis -n task-api || echo "Redis not found"
```

### Step 7.2: Check Metrics

```bash
# Get application metrics endpoint
API_URL="https://$(oc get route task-api -n task-api -o jsonpath='{.spec.host}')"
curl -k $API_URL/metrics | head -20
```

---

## 🔄 Phase 8: Test CI/CD Pipeline End-to-End (5 minutes)

### Step 8.1: Make a Code Change

```bash
cd python-task-api

# Update version
sed -i 's|1.0.0|1.0.1|g' app/__init__.py

# Commit and push
git add .
git commit -m "Bump version to 1.0.1"
git push
```

### Step 8.2: Watch GitHub Actions

1. Go to GitHub repository → **"Actions"** tab
2. Click on the running workflow
3. View real-time logs as:
   - Tests run
   - Docker image builds
   - Image pushes to Docker Hub
   - Deployment updates OpenShift

### Step 8.3: Verify New Deployment

```bash
# Check new image is deployed
oc get deployment task-api -n task-api -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check pod status
oc get pods -n task-api

# Verify application is still running
API_URL="https://$(oc get route task-api -n task-api -o jsonpath='{.spec.host}')"
curl -k $API_URL/health
```

### Step 8.3: Verify New Deployment

```bash
# Check new image is deployed
oc get deployment task-api -n task-api -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check pod status
oc get pods -n task-api

# Verify application is still running
API_URL="https://$(oc get route task-api -n task-api -o jsonpath='{.spec.host}')"
curl -k $API_URL/health
```

---

## ✅ Success Criteria

Your project is complete when:

- ✅ Code repositories on GitHub (python-task-api & k8s-manifests)
- ✅ GitHub Actions workflows created (CI & CD)
- ✅ Docker Hub repository created
- ✅ GitHub Secrets configured (Docker Hub & OpenShift tokens)
- ✅ OpenShift Developer Sandbox project created
- ✅ PostgreSQL & Redis running in OpenShift
- ✅ Application deployed from GitHub Actions
- ✅ API accessible via OpenShift Route
- ✅ Health checks passing
- ✅ CI/CD pipeline end-to-end functional
- ✅ Code changes automatically trigger deployment

---

## 📝 CV/Resume Points

### What to Include:

**Project Description:**
> Designed and implemented a production-grade CI/CD pipeline for a Python FastAPI microservice, leveraging Azure DevOps, ArgoCD, and OpenShift. Established GitOps workflows with automated deployment across dev, staging, and production environments.

## 📝 CV/Resume Points

### What to Include:

**Project Description:**
> Designed and implemented a production-grade CI/CD pipeline for a Python FastAPI microservice using GitHub Actions for continuous integration and deployment to OpenShift. Established automated testing, containerization, and deployment workflows that enable code changes to automatically trigger build, test, and deployment processes. Leveraged Kubernetes manifests with Kustomize for declarative infrastructure-as-code across environments.

**Technologies & Skills:**
- **Languages**: Python 3.11, SQL, Bash, YAML
- **Frameworks**: FastAPI, SQLAlchemy, Pydantic
- **Databases**: PostgreSQL, Redis
- **Containers**: Docker, Docker Hub, multi-stage builds
- **Orchestration**: Kubernetes, OpenShift, Kustomize
- **CI/CD**: GitHub Actions (test, build, push, deploy)
- **Version Control**: Git, GitHub
- **Security**: JWT authentication, API tokens, RBAC
- **Monitoring**: Health checks, metrics endpoints

**Key Achievements:**
- Automated CI/CD pipeline triggering on every code push
- Integrated comprehensive testing (pytest, linting, type-checking) in CI phase
- Containerized application with multi-stage Docker builds
- Automated deployment to Kubernetes/OpenShift with zero downtime
- Implemented health checks and readiness probes for reliable deployments
- Used Kustomize for maintainable infrastructure-as-code

**GitHub Repositories:**
- Application: `github.com/[USERNAME]/python-task-api`
- Manifests: `github.com/[USERNAME]/k8s-manifests`

---

## 🐛 Troubleshooting

### Issue: `oc new-project task-api` fails with "Forbidden"

**Root Cause:** OpenShift Developer Sandbox restricts project creation. Your sandbox comes with a **pre-created project** for you.

**Solution:** Use your existing project instead. Check what project you have:
```bash
oc get projects
# Shows your pre-created project (e.g., derakings-dev)
```

Switch to it:
```bash
oc project derakings-dev
# or whatever your project name is
```

**Update all commands in this guide:** Replace `-n task-api` with `-n <your-project-name>`

For example:
```bash
# Instead of:
oc new-app postgresql-persistent ... -n task-api

# Run:
oc new-app postgresql-persistent ... -n derakings-dev
```

### Issue: Pod not starting

```bash
# Check pod status
oc describe pod <pod-name> -n task-api

# Check logs
oc logs <pod-name> -n task-api

# Check events
oc get events -n task-api --sort-by='.lastTimestamp'
```

### Issue: GitHub Actions workflow fails

1. Go to GitHub repository **"Actions"** tab
2. Click the failed workflow run
3. Check the logs section
4. Common issues:
   - Docker Hub credentials not set → Add to GitHub Secrets
   - OpenShift token expired → Generate new token and update GitHub Secrets
   - Network issues → Retry the workflow

### Issue: Cannot connect to database

```bash
# Check PostgreSQL is running
oc get pods -n task-api | grep postgres

# Check PostgreSQL service
oc get service postgres -n task-api

# Test connection from app pod
oc exec -it <app-pod-name> -n task-api -- psql -h postgresql -U taskapi -d taskdb
```

### Issue: Docker Hub push fails

```bash
# Verify credentials
docker login -u $DOCKERHUB_USERNAME

# Check GitHub Secret is set correctly
# Go to Settings → Secrets and variables → Actions
# Verify DOCKERHUB_USERNAME and DOCKERHUB_TOKEN are correct
```

### Issue: OpenShift deployment not updating

```bash
# Force rollout
oc rollout restart deployment/task-api -n task-api

# Check deployment status
oc rollout status deployment/task-api -n task-api

# Check current image
oc get deployment task-api -n task-api -o jsonpath='{.spec.template.spec.containers[0].image}'
```

---

## 📚 Next Steps

After completing this setup:

1. **Monitor Your Deployments:**
   - Check GitHub Actions logs on every commit
   - Monitor OpenShift pods and resources
   - Set up OpenShift alerts for pod failures

2. **Add More Features:**
   - Implement background tasks with Celery
   - Add email notifications
   - Implement file uploads to cloud storage

3. **Enhance Security:**
   - Implement OAuth2 providers
   - Add rate limiting
   - Implement request authentication stricter validation

4. **Improve Testing:**
   - Add integration tests
   - Add end-to-end tests
   - Increase code coverage

5. **Scale Further:**
   - Add horizontal pod autoscaling
   - Implement caching strategies
   - Add CDN for static assets
   - Set up multi-region deployments

---

## 🎉 Congratulations!

You've successfully built a production-ready CI/CD pipeline demonstrating:

- ✅ Modern Python development practices with FastAPI
- ✅ Cloud-native architecture on Kubernetes/OpenShift
- ✅ Automated CI pipeline with comprehensive testing
- ✅ Containerization with Docker
- ✅ Automated CD pipeline with zero-downtime deploys
- ✅ Infrastructure-as-code with Kustomize
- ✅ Security best practices (JWT, RBAC, secrets)
- ✅ Monitoring and health checks

This project showcases enterprise-level DevOps and cloud engineering skills!

**Estimated Total Setup Time**: 1-2 hours  
**Resume Impact**: High ⭐⭐⭐⭐⭐  
**Interview Appeal**: Excellent

The skills demonstrated here are in high demand:
- GitHub Actions (widely used across industries)
- Container orchestration (Kubernetes skills valued everywhere)
- CI/CD automation (essential for DevOps roles)
- Python backend development (fullstack candidates)
- Infrastructure-as-code (cloud efficiency gain)

Good luck! 🚀

# Kubernetes Deployment Reference

This directory contains reference manifests for deploying the Document AI Processing Pipeline to a Kubernetes cluster.

## Files

| File | Description |
|------|-------------|
| `backend-deployment.yaml` | FastAPI backend — 2 replicas, resource limits, liveness/readiness probes, HPA |
| `backend-service.yaml` | ClusterIP service + HorizontalPodAutoscaler (2–8 replicas, 70% CPU target) |
| `frontend-deployment.yaml` | Next.js frontend deployment + LoadBalancer service |

## Local Testing with minikube

```bash
# 1. Start minikube
minikube start

# 2. Build images into minikube's Docker daemon
eval $(minikube docker-env)
docker build -f services/ai-api/Dockerfile -t document-ai-backend:latest services/ai-api/
docker build -f Dockerfile.frontend -t document-ai-frontend:latest .

# 3. Create secret for OPENAI_API_KEY
kubectl create secret generic document-ai-secrets \
  --from-literal=openai-api-key="your-openai-api-key"

# 4. Apply manifests
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# 5. Check pods
kubectl get pods
kubectl get services

# 6. Access the frontend
minikube service document-ai-frontend
```

## Local Testing with kind

```bash
kind create cluster --name document-ai
kind load docker-image document-ai-backend:latest --name document-ai
kind load docker-image document-ai-frontend:latest --name document-ai
kubectl apply -f k8s/
```

## Production Notes

- **SQLite is not suitable for multi-replica deployments.** Replace `DATABASE_URL` with a durable relational database connection string and use a `PersistentVolumeClaim` only for local or single-node testing.
- **Secrets** should be managed with an external secrets manager, not plain Kubernetes Secrets in production.
- **HPA** requires the Kubernetes metrics server. Install with: `minikube addons enable metrics-server`
- **Ingress** is not included. Add an `nginx-ingress` or `traefik` ingress controller for hostname-based routing.

## Key Design Choices

The `/health` endpoint is used for both `livenessProbe` and `readinessProbe`. This is intentional:
- Liveness checks prevent restart loops caused by a wedged process.
- Readiness checks prevent routing traffic to a pod that hasn't finished initializing.

The FastAPI backend runs 2 replicas minimum to demonstrate zero-downtime rolling updates. The HPA can scale to 8 replicas under CPU load — matching a realistic invoice processing burst.

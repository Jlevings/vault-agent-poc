## Postgres (Kubernetes) Deployment

The Postgres database that powers the demo runs inside the local Kubernetes cluster. We currently manage it via the manifests in `k8s/postgres/` rather than Terraform, because most developers prefer to apply the YAML directly with `kubectl`.

### Steps

1. Ensure your local cluster (Rancher Desktop or Minikube) is running and the `vault-ai` namespace exists.
2. Apply the manifests:
   ```bash
   kubectl apply -n vault-ai -f k8s/postgres/
   kubectl rollout status -n vault-ai statefulset/postgres
   ```
3. Seed the sample data:
   ```bash
   kubectl -n vault-ai exec -it postgres-0 -- \
     psql -U postgres -d postgres -f /docker-entrypoint-initdb.d/seed.sql
   ```

### Why no Terraform?

You can certainly manage these Kubernetes resources with Terraform’s `kubernetes` provider or Helm charts. For the POC we kept the database simple and local to avoid coupling Terraform to cluster credentials. If you’d like to codify it, this directory is the natural place to add those configurations.

# Command reference — ML Model Serving project build

Every command used to build, deploy, and monitor this project, in order.

## 1. Local development

```bash
# Create and activate a Python 3.12 virtual environment
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Train the model
python train_model.py

# Run the API locally
uvicorn app.main:app --reload
```

## 2. Git / GitHub

```bash
git init
git add .
git commit -m "Initial commit: model serving API + Helm chart"
git remote add origin git@github.com:nishav98/ml-model-serving-on-Kubernetes-with-CI-CD.git
git branch -M main
git push -u origin main
```

## 3. Docker

```bash
docker build -t ml-serving:local .
docker run -p 8000:8000 ml-serving:local
```

## 4. AWS CLI setup

```bash
aws configure
aws sts get-caller-identity
```

## 5. ECR (container registry)

```bash
aws ecr create-repository --repository-name ml-serving --region ap-south-1

aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

docker tag ml-serving:local <account-id>.dkr.ecr.ap-south-1.amazonaws.com/ml-serving:v1
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/ml-serving:v1

aws ecr describe-images --repository-name ml-serving --region ap-south-1
```

## 6. EKS (Kubernetes cluster)

```bash
eksctl create cluster --name ml-serving --region ap-south-1 --nodes 2 --node-type t3.medium --managed

kubectl get nodes
kubectl get pods -A
```

## 7. Helm (app deployment)

```bash
helm install ml-serving ./helm/ml-serving
helm upgrade ml-serving ./helm/ml-serving

kubectl get pods
kubectl get deployment,service,hpa
kubectl describe pod <pod-name>

# Test locally via port-forward
kubectl port-forward service/ml-serving-ml-serving 8080:80
```

## 8. Monitoring (Prometheus + Grafana)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

kubectl get pods -n monitoring
kubectl get servicemonitors -A

# Port-forward Prometheus
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090

# Port-forward Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80

# Get Grafana admin password (Git Bash)
kubectl get secret -n monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d
```

## 9. Teardown (stop AWS billing)

```bash
helm uninstall monitoring -n monitoring
helm uninstall ml-serving

kubectl get pods -A   # confirm clean

eksctl delete cluster --name ml-serving --region ap-south-1

aws eks list-clusters --region ap-south-1   # confirm empty
```

## 10. GitHub Actions CI/CD setup

```bash
# 1. Create an IAM OIDC identity provider for GitHub Actions (one-time, per AWS account)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# 2. Create an IAM role GitHub Actions can assume (trust policy scoped to your repo)
#    Save this as trust-policy.json first, replacing <account-id> and <github-username>:
#    {
#      "Version": "2012-10-17",
#      "Statement": [{
#        "Effect": "Allow",
#        "Principal": {"Federated": "arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com"},
#        "Action": "sts:AssumeRoleWithWebIdentity",
#        "Condition": {
#          "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
#          "StringLike": {"token.actions.githubusercontent.com:sub": "repo:<github-username>/ml-model-serving-on-Kubernetes-with-CI-CD:*"}
#        }
#      }]
#    }
aws iam create-role --role-name github-actions-ml-serving --assume-role-policy-document file://trust-policy.json

# 3. Attach permissions the role needs (ECR push + EKS access)
aws iam attach-role-policy --role-name github-actions-ml-serving --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess
aws iam attach-role-policy --role-name github-actions-ml-serving --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy

# 4. Grab the role ARN to add as a GitHub secret
aws iam get-role --role-name github-actions-ml-serving --query 'Role.Arn' --output text
```

Then in GitHub: repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret** → name it `AWS_ROLE_ARN`, paste the role ARN from step 4.

**Status: workflow file written and committed, IAM/OIDC trust wiring documented above — not yet run end-to-end since it requires an active EKS cluster.** Next time a cluster is spun up, push a commit to `main` and watch the Actions tab.

## Tools installed along the way

| Tool | Purpose |
|---|---|
| Python 3.12 | Runtime (3.14 lacked scikit-learn wheels) |
| Git + Git Bash | Version control |
| Docker Desktop | Containerization |
| AWS CLI | AWS resource management |
| eksctl | EKS cluster creation |
| kubectl | Kubernetes control |
| Helm | Kubernetes package management |

## Real issues hit and fixed (good interview material)

1. **Python 3.14 had no scikit-learn wheels** → installed Python 3.12 in a dedicated venv.
2. **`python` command not found on Windows** → Microsoft Store alias was shadowing the real install; disabled the alias.
3. **Docker Desktop wouldn't start** → WSL was outdated; fixed with `wsl --update`.
4. **Helm chart deployed but created zero resources** → the `templates/` folder didn't actually exist on disk despite showing in the editor; recreated it directly.
5. **Prometheus never found the app's `/metrics` endpoint** → the Kubernetes Service had a pod *selector* but no *labels* of its own, so the ServiceMonitor (which matches on Service labels) couldn't find it. Added `metadata.labels` to `service.yaml`.

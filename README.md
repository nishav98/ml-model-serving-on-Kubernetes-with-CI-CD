# ML Model Serving on Kubernetes with CI/CD

A scikit-learn model (RandomForest, Iris dataset) served via FastAPI, containerized,
and deployed on Amazon EKS with autoscaling, health probes, and Prometheus/Grafana
monitoring. GitHub Actions builds and deploys on every push to `main`.

## Stack
Python · FastAPI · Docker · Amazon EKS · Helm · GitHub Actions · Prometheus · Grafana

## Local development

```bash
pip install -r requirements.txt
python train_model.py          # trains model, saves app/model.joblib
uvicorn app.main:app --reload  # http://localhost:8000
```

Test it:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

## Docker

```bash
docker build -t ml-serving:local .
docker run -p 8000:8000 ml-serving:local
```

## Endpoints

| Method | Path      | Purpose                          |
|--------|-----------|-----------------------------------|
| GET    | /health   | K8s liveness/readiness probe      |
| POST   | /predict  | Run inference                     |
| GET    | /metrics  | Prometheus scrape target          |

## Roadmap (this repo will grow to include)
- [ ] `helm/` chart: Deployment, Service, HPA, probes
- [ ] EKS cluster provisioning (`eksctl` config)
- [ ] `.github/workflows/deploy.yml`: build → push to ECR → `helm upgrade`
- [ ] Grafana dashboard JSON + screenshot
- [ ] Load test results (`hey`/`locust`) showing HPA scaling

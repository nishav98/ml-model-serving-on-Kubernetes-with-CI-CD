Spent today building and deploying a full ML inference pipeline on Kubernetes — training a model, serving it via FastAPI, containerizing it, deploying to AWS EKS with autoscaling and health checks, and wiring up real monitoring with Prometheus and Grafana.

What's in it:
🐳 Docker + AWS ECR for the container pipeline
☸️ EKS + a hand-written Helm chart (Deployment, Service, HPA, liveness/readiness probes)
📊 Prometheus scraping app-specific metrics, visualized in Grafana

The part I'm actually proud of: Prometheus wasn't picking up my app's metrics, and it took real debugging to find why — my Kubernetes Service had a pod *selector* but no *labels* of its own, and the ServiceMonitor matches on Service labels, not selectors. Small distinction, easy to miss, good lesson.

Repo (with full architecture, screenshots, and command history): [link]

#DevOps #Kubernetes #MLOps #AWS #Prometheus #Grafana

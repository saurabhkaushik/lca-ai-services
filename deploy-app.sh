# GCP Account and Project Setup
gcloud config set account 'legaltest200@gmail.com'
gcloud config set project 'genuine-wording-362504'

# Docker Build - Local 
docker build -t law-service-app . 
#docker run -p 8080:8080 -it law-service-app 

# Image Push
gcloud auth configure-docker asia-south1-docker.pkg.dev
docker tag law-service-app asia-south1-docker.pkg.dev/genuine-wording-362504/lca-service-app/lca-ai-service
docker push asia-south1-docker.pkg.dev/genuine-wording-362504/lca-service-app/lca-ai-service

# EKS Setup
gcloud container clusters get-credentials "autopilot-cluster-2" --region asia-south1
kubectl rollout restart deployment lca-service-app-gke
#kubectl apply -f deployment.yaml 
#kubectl apply -f service.yaml
#docker system prune

# Validation 
kubectl get deployments
kubectl get services
kubectl get pods
kubectl get nodes
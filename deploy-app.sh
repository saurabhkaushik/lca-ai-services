# GCP Account and Project Setup
gcloud config set account 'lcakumar004@gmail.com'
gcloud config set project 'lca-prod-379123'

# Docker Build - Local 
docker build -t law-service-app . 
#docker run -p 8081:8080 -it law-service-app 

# Repo in Artifactory 
gcloud artifacts repositories create lca-service-app --repository-format=docker --location=us-central1 

# Image Push
gcloud auth configure-docker us-central1-docker.pkg.dev
docker tag law-service-app us-central1-docker.pkg.dev/lca-prod-379123/lca-service-app/lca-ai-service
docker push us-central1-docker.pkg.dev/lca-prod-379123/lca-service-app/lca-ai-service

export USE_GKE_GCLOUD_AUTH_PLUGIN=True
# EKS Setup
gcloud container clusters create-auto "lca-prod-cluster" --region=us-central1
gcloud container clusters get-credentials "lca-prod-cluster" --region us-central1
kubectl apply -f deployment.yaml 
kubectl apply -f service.yaml
kubectl rollout restart deployment lca-service-app-gke

# Validation 
kubectl get deployments
kubectl get services
kubectl get pods
kubectl get nodes
#docker system prune
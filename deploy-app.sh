
# GCP Account and Project Setup
gcloud config set account 'lcakumar002@gmail.com'
gcloud config set project 'lca-prod-372208'

# Docker Build - Local 
docker build -t law-service-app . 
#docker run -p 8080:8080 -it law-service-app 

# Repo in Artifactory 
gcloud artifacts repositories create lca-service-app --repository-format=docker --location=asia-south1 
export USE_GKE_GCLOUD_AUTH_PLUGIN=True
# Image Push
gcloud auth configure-docker asia-south1-docker.pkg.dev
docker tag law-service-app asia-south1-docker.pkg.dev/lca-prod-372208/lca-service-app/lca-ai-service
docker push asia-south1-docker.pkg.dev/lca-prod-372208/lca-service-app/lca-ai-service

# EKS Setup
gcloud container clusters create-auto "lca-prod-cluster" --region=asia-south1
gcloud container clusters get-credentials "lca-prod-cluster" --region asia-south1
kubectl apply -f deployment.yaml 
kubectl apply -f service.yaml
kubectl rollout restart deployment lca-service-app-gke

# Validation 
kubectl get deployments
kubectl get services
kubectl get pods
kubectl get nodes
#docker system prune
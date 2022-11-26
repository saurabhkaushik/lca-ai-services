docker build -t law-service-app . 

gcloud auth configure-docker asia-south1-docker.pkg.dev
docker tag law-service-app asia-south1-docker.pkg.dev/genuine-wording-362504/lca-service-app/lca-ai-service
docker push asia-south1-docker.pkg.dev/genuine-wording-362504/lca-service-app/lca-ai-service

gcloud run deploy lca-ai-services --memory 16Gi --cpu 4 --region asia-south1 --image asia-south1-docker.pkg.dev/genuine-wording-362504/lca-service-app/lca-ai-service

#docker run -p 8080:8080 -it law-service-app 

#docker compose build 
#docker compose up -d 

#docker tag lca-ai-service saurabhkaushik/lca-ai-service
#docker push saurabhkaushik/lca-ai-service
#docker pull saurabhkaushik/lca-ai-service


#docker login saurabhkaushik/imtp@2012
#docker container ls
#docker images 
#gcloud artifacts repositories list
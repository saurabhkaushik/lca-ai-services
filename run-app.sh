#python3 -m venv env
source env/bin/activate 
export LCA_APP_ENV='development'  
#export LCA_APP_ENV='production'  
export GOOGLE_APPLICATION_CREDENTIALS='./config/gcp/lca-prod-key.json'
export PORT=8081
#python3 -m pip install --upgrade pip
#pip3 install -r requirements.txt --upgrade
#python3 -m spacy download en_core_web_md
#pip3 install lexnlp --no-deps regex 
#python3 -m nltk.downloader punkt
python3 app-run.py 
# deactivate
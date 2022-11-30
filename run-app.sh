# python3 -m venv env
export LCA_APP_ENV='development'  
#export LCA_APP_ENV='production'  
export GOOGLE_APPLICATION_CREDENTIALS='./store/genuine-wording-key.json'
export PORT=8081
source env/bin/activate
#python3 -m pip install --upgrade pip
#pip3 install -r requirements.txt --upgrade
#python3 -m spacy download en_core_web_md
#python3 -m nltk.downloader stopwords
python3 app-run.py 
# deactivate
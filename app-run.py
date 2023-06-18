import app
import config
from waitress import serve
import os

app = app.create_app(config)

if __name__ == '__main__': 
    port = os.getenv('PORT')
    app_env = os.getenv('LCA_APP_ENV')
    if port == None: 
        port = 8080
    if app_env == 'production': 
        serve(app, host="0.0.0.0", port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)

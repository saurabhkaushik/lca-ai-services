import app
import config
from waitress import serve
import os

app = app.create_app(config)
cert_file = "./config/ssl/certificate.crt"
key_file = "./config/ssl/private.key"

if __name__ == '__main__': 
    port = os.getenv('PORT')
    app_env = os.getenv('LCA_APP_ENV')
    if port == None: 
        port = 8080
    app.run(debug=True, host='0.0.0.0', port=port, ssl_context=(cert_file, key_file))
    ''' if app_env == 'production': 
        app.run(debug=True, host='0.0.0.0', port=port)
        #serve(app, host="0.0.0.0", port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)
    '''

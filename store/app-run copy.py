import app
import config
from waitress import serve
import os
import ssl 

app = app.create_app(config)
ca_file = "./config/ssl/ca_bundle.crt"
cert_file = "./config/ssl/certificate.crt"
key_file = "./config/ssl/private.key"

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(ca_file)
context.load_cert_chain(cert_file, key_file)

if __name__ == '__main__': 
    port = os.getenv('PORT')
    app_env = os.getenv('LCA_APP_ENV')
    if port == None: 
        port = 8080
    app.run(debug=True, host='0.0.0.0', port=port, ssl_context=context)
    ''' if app_env == 'production': 
        app.run(debug=True, host='0.0.0.0', port=port)
        #serve(app, host="0.0.0.0", port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)
    '''

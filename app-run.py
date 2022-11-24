import app
import config
from waitress import serve

app = app.create_app(config)

if __name__ == '__main__': 
    #serve(app, host="0.0.0.0", port=8081)
    app.run(debug=True, host='0.0.0.0', port=8080)

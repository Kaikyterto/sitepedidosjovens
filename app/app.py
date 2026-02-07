from flask import Flask
from controllers.routes import cliente
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

app.register_blueprint(cliente)

if __name__ == "__main__":
    app.run(debug=True)

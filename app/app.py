from flask import Flask
from flask_cors import CORS
from app.controllers.routes import cliente

app = Flask(__name__)
CORS(app)

app.register_blueprint(cliente)

if __name__ == "__main__":
    app.run()

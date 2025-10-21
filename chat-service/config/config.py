import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy


load_dotenv()

db = SQLAlchemy()


def create_app(): 
    # Initialize server app like tom cat
    app = Flask(__name__)
    CORS(app)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    db.init_app(app)
    
    
    # set up API documentation
    api = Api(
        app,
        title="Chat Service API",
        version="1.0",
        description="API documentation for the Chat Service",
        doc="/swagger-ui"
    )  # Swagger UI available at /docs

    return app, api
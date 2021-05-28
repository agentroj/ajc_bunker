"""FlaskのConfigを提供する"""
"""Provide Config of Flask"""
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class DevelopmentConfig:

    # Flask
    DEBUG = True

    # SQLAlchemy
      # EXERCISE: SQLALCHEMY_DATABASE_URIを実装しましょう ============
    # EXERCISE: Let's implement SQLALCHEMY_DATABASE_URI ==========
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
        'user': os.environ.get("MYSQL_USER") or "root",
        'password': os.environ.get("MYSQL_PASSWORD") or "password",
        'host': os.environ.get("DB_HOST") or "localhost",
        'db_name': os.environ.get("MYSQL_DATABASE") or "docker_pytweet",
    })
    # ============================================================
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.urandom(24)

    IMG_UPLOAD_URL = 'https://api.imgur.com/3/image'
    IMGUR_CLI_ID = os.environ.get("IMGUR_CLI_ID")
Config = DevelopmentConfig

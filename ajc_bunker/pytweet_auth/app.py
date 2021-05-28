# flask appの初期化を行い、flask appオブジェクトの実体を持つ
# Initialize flask app and get an instance of flask app object 
from flask import Flask
from pytweet_auth.database import init_db
from pytweet_auth.config import Config
import os
import pytweet_auth.models
from flask_login import LoginManager


def create_app():
    # インスタンスの立ち上げ
     # Start up instance application
    _app = Flask(__name__)
    # Flaskのconfigが 設定ファイルを読み込む処理
     # Import settings for config of Flask
    _app.config.from_object(Config)

    # DBのセットアップ
   # Set up DB
    _app.secret_key = os.urandom(24)
    init_db(_app)

    return _app


app = create_app()

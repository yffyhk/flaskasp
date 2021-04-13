import os

from flask import Flask, render_template, redirect


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = '4136489ea93036a02da1d21b910437de5176ff0f8b193fb7',
        DATABASE=os.path.join(app.instance_path,'flaskasp.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py',silent=True)
    else:
        app.config.from_mapping(test_config)


    try:
        os.mkdir(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
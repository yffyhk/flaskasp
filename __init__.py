import os
import json

from flask import Flask, render_template, redirect, url_for


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = '',
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
        return redirect(url_for('article.page',title="home"))

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import article
    app.register_blueprint(article.bp)

    from . import log
    app.register_blueprint(log.bp)

    from . import forum
    app.register_blueprint(forum.bp)

    from . import video
    app.register_blueprint(video.bp)

    from . import profile
    app.register_blueprint(profile.bp)


    return app
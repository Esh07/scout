# -*- coding: utf-8 -*-
from flask import Flask

from . import extensions
from .blueprints import public, genes


def create_app(config_file):
    """Flask app factory function."""
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.config.from_pyfile(config_file)

    configure_extensions(app)
    register_blueprints(app)
    return app


def configure_extensions(app):
    """Configure Flask extensions."""
    extensions.toolbar.init_app(app)
    extensions.bootstrap.init_app(app)
    extensions.mongo.init_app(app)
    extensions.store.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.public_bp)
    app.register_blueprint(genes.genes_bp)

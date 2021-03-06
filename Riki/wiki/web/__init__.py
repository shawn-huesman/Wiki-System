import os

from flask import current_app
from flask import Flask
from flask import g
from flask import send_from_directory
from flask_login import LoginManager
from werkzeug.local import LocalProxy
import platform

from wiki.core import Wiki
from wiki.web.user import UserManager

class WikiError(Exception):
    pass

def get_wiki():
    wiki = getattr(g, '_wiki', None)
    if wiki is None:
        wiki = g._wiki = Wiki(current_app.config['CONTENT_DIR'])
    return wiki

current_wiki = LocalProxy(get_wiki)

def get_users():
    users = getattr(g, '_users', None)
    if users is None:
        users = g._users = UserManager(current_app.config['USER_DIR'])
    return users

current_users = LocalProxy(get_users)

def create_app(directory):
    '''
    The create_app method verifies the platform on which the application
    is accessed to configure the path for the “uploads” folder.

    The create_app method verifies whether the “uploads” folder exists
    and creates it otherwise.
    '''
    app = Flask(__name__)
    app.config['CONTENT_DIR'] = directory
    app.config['TITLE'] = 'wiki'

    if platform.system() == 'Windows':
        app.config['UPLOAD_FOLDER'] = os.getcwd()+'\\uploads'
    else:
        app.config['UPLOAD_FOLDER'] = os.getcwd()+'/uploads'

    if not os.path.exists( app.config['UPLOAD_FOLDER'] ):
        os.makedirs( app.config['UPLOAD_FOLDER'] )

    try:
        app.config.from_pyfile(
            os.path.join(app.config.get('CONTENT_DIR'), 'config.py')
        )
    except IOError:
        msg = "You need to place a config.py in your content directory."
        raise WikiError(msg)

    loginmanager.init_app(app)

    from wiki.web.routes import bp
    app.register_blueprint(bp)

    return app


loginmanager = LoginManager()
loginmanager.login_view = 'wiki.user_login'

@loginmanager.user_loader
def load_user(name):
    return current_users.get_user(name)

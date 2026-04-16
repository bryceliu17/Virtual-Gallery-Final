from flask import Flask, render_template
from flask_mysqldb import MySQL
import secrets

mysql = MySQL()

def createApp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_urlsafe(32)


    #Upload folder
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
  

    # MySQL config
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '123456'
    app.config['MYSQL_DB'] = 'virtual_gallery'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config["MYSQL_AUTOCOMMIT"] = False


    mysql.init_app(app)

    from .views import bpView
    app.register_blueprint(bpView)

    #Error handler routes
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500
    return app
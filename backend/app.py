from flask import Flask, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from core.config import APP_CONFIG
from routers import auth, dashboard


def create_app():
    app = Flask(__name__)
    app.config.from_object(APP_CONFIG)
    app.json.sort_keys = False

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    
    script_name = APP_CONFIG.BASE_URL
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        script_name: app
    })
    
    @app.route("/")
    def app_info():
        
        return render_template('index.html')

    return app

    
app = create_app()

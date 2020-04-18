from web.controllers.main import main as main_blueprint
from web import app

app.register_blueprint(main_blueprint)

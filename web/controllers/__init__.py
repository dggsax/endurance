from web.controllers.main import main as main_blueprint
from web import app, db
from flask import render_template, abort


app.register_blueprint(main_blueprint)

@app.errorhandler(404)
def not_found_error(error):
    print("yee haw")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

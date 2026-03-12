from flask import Flask

from routes.authroutes import auth_bp
from routes.userRoutes import user_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True)

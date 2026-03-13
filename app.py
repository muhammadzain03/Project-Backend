from flask import Flask

from routes.authroutes import auth_bp
from routes.GetUserInfoRoutes import user_bp
from routes.UpdateUserInfo import update_user_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(update_user_bp)

if __name__ == "__main__":
    app.run(debug=True)

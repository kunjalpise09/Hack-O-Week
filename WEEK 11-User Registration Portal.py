from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret123"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
app.config['JWT_SECRET_KEY'] = "jwt-secret"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/signup_page')
def signup_page():
    return render_template("signup.html")

@app.route('/signup', methods=['POST'])
def signup():

    username = request.form['username']
    password = request.form['password']

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(username=username, password=hashed_pw)

    db.session.add(user)
    db.session.commit()

    return "User Registered Successfully"

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):

        token = create_access_token(identity=username)

        return jsonify({
            "message": "Login Successful",
            "JWT Token": token
        })

    return "Invalid Credentials"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
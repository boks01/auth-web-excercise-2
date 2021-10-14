from enum import unique
from logging import debug
from flask import Flask, render_template, redirect, request, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, current_user, UserMixin, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, check_password_hash, generate_password_hash
import flask
import sqlalchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SECRET_KEY'] = "miegorengenak"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UserData(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    email = db.Column(db.String(1000), unique=True)
    token = db.Column(db.String(1000))
    password = db.Column(db.String(1000))

db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return UserData.query.get(user_id)

@app.route("/")
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        hashed = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        if request.form.get('token') != "authweb":
            flash('Incorrect token, plese check again.')
            return redirect(url_for('register'))
        else:
            new_data = UserData(
                name = request.form.get('name') ,
                email = request.form.get('email') ,
                token = request.form.get('token') ,
                password = hashed ,
            )
            try:
                db.session.add(new_data)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError:
                flash('Account already exist, please use another account.')
                return redirect(url_for('register'))
            return redirect(url_for('secrets'))
    return render_template("register.html", logged_in=current_user.is_authenticated)

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        username = UserData.query.filter_by(email=email).first()
        if username == None:
            flash('Unknown account, pelase check again.')
            return redirect(url_for('login'))
        elif check_password_hash(username.password, password):
            login_user(username)
            return redirect(url_for('secrets'))
        else:
            flash('Incorrect password, plese check again')
            return redirect(url_for('login'))
    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/secrets")
@login_required
def secrets():
    name = current_user.name
    return render_template('secrets.html', name=name)

@app.route("/download")
@login_required
def download():
    return send_from_directory("static", "files/Dasar Desain Grafis Modul 1.pdf")


if  __name__ == "__main__":
    app.run(debug=True)

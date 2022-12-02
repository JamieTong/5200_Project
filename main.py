from flask import Flask, render_template, request,url_for, redirect, make_response, jsonify
from google.cloud.sql.connector import Connector
import pymysql
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField
from wtforms.validators import InputRequired, Length, ValidationError
from sqlalchemy import Column, Integer, String, Sequence
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)


def connect_db():
    connector = Connector()
    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            "wide-cathode-362521:us-central1:team13",
            "pymysql",
            user="root",
            password="1234",
            db="project"
        )
        return conn
    try:
        pool = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=getconn,
        )
        return pool.connect()
    except Exception as e:
        return str(e)

#databse connection
connection = connect_db()
#NUID and role for logged-in user
userID = 0
userRole = ''


app.config['SECRET_KEY'] = 'mysecretekey'
# bcrypt = Bcrypt(app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# @login_manager.user_loader
# def load_user(user_id):
#     return Users.query.get(int(user_id))
 
# class Users(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key = True, nullable = False)
#     email = db.Column(db.String(50), nullable = False, unique = True)
#     password = db.Column(db.String(50), nullable = False)
#     role = db.Column(db.String(80))


class LoginForm(FlaskForm):
    id = StringField(
        validators=[
            InputRequired(), 
            Length(min=4, max=20)], render_kw={"placeholder": "NUID"}
    )
    password = PasswordField(
        validators=[
            InputRequired(), 
            Length(min=8, max=20)], render_kw={"placeholder": "Password"}
    )
    submit = SubmitField('Login')    

@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/login", methods = ['GET', 'POST'])
def login():
    global userRole, userID
    form = LoginForm()
    if form.validate_on_submit():
        input_id = form.id.data
        input_password = form.password.data
        # with connection as db_conn:
        result = connection.execute(f"select password from Users where id = {input_id}").fetchone()[0]
        print(result)
        role = connection.execute(f"select role from Users where id = {input_id}").fetchone()[0]
        # user = Users.query.filter_by(id=form.id.data).first()
        if result:
            userID = input_id
            userRole = role
            if (input_password == form.password.data):
                if(userRole == 'student'):
                    return redirect(url_for('studentDashboard'))
                elif(userRole == 'admin'):
                    return redirect(url_for('adminDashboard'))
    return render_template('login.html', form=form)


@app.route('/studentDashboard', methods=['GET'])
def studentDashboard():
    sql = ('SELECT name FROM Student WHERE NUID = {id}').format(id = userID)
    result = connection.execute(sql)
    name = [row[0] for row in result]
    return render_template('studentDashboard.html')

@app.route('/adminDashboard', methods=['GET'])
def adminDashboard():
    return render_template('adminDashboard.html')

@app.route('/semester', methods=['GET','POST'])
def semester():
    dropdown_list = ['Spring 2023','Fall 2022','Summer 2022']
    return render_template('semester.html',list = dropdown_list)

@app.route('/browse', methods=['GET'])
def browse():
    return render_template("browseClasses.html")
    
@app.route('/view_register', methods=['GET'])
def view():
    return render_template("view.html")    


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
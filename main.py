from flask import Flask, render_template, request,url_for, redirect, make_response,flash
from google.cloud.sql.connector import Connector
import pymysql
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from data import major_list

app = Flask(__name__)

# Google Cloud SQL 
PASSWORD ="1234"
USER = "root"
PUBLIC_IP_ADDRESS ="35.235.120.25"
DBNAME ="project"
INSTANCE_NAME ="wide-cathode-362521:us-west2:newdb"
MY_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{user}:{password}@{ip}/{database}').format(
    user=USER, password=PASSWORD, ip = PUBLIC_IP_ADDRESS, database=DBNAME
)
 
# configuration
app.config['SECRET_KEY'] = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"]= MY_SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

db=SQLAlchemy(app)
# bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# database models
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    password = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(50), nullable = False, unique = True)
    role = db.Column(db.String(50), nullable = False)

class Student(db.Model):
    __tablename__ = 'student'
    nuid = db.Column('nuid',db.Integer, primary_key = True, nullable = False)
    name = db.Column('name',db.String(50), nullable = False)
    entry_year = db.Column(db.Integer, nullable = False)
    type = db.Column(db.String(50), nullable = False)
    min_credit = db.Column(db.Integer, nullable = False)
    department_id = db.Column(db.Integer, nullable = False)
    campus_name = db.Column(db.String(50), nullable = False)
    major = db.Column(db.String(50), nullable = False)

class Course(db.Model):
    __tablename__ = 'course'

class Campus(db.Model):
    __tablename__ = 'campus'
    name = db.Column(db.String(50),primary_key = True, nullable = False)
    location = db.Column(db.String(50), nullable = False)

class Major(db.Model):
    __tablename__ = 'major'
    name = db.Column(db.String(50),primary_key = True, nullable = False)
    department_id = db.Column(db.Integer, nullable = False)

class LoginForm(FlaskForm):
    id = StringField(
        validators=[
            InputRequired(), 
            Length(min=4, max=20)], render_kw={"placeholder": "WUID"}
    )
    password = PasswordField(
        validators=[
            InputRequired(), 
            Length(min=8, max=20)], render_kw={"placeholder": "Password"}
    )
    submit = SubmitField('Login')    

class CriteriaForm(FlaskForm):
    major = SelectField('major')
    number = StringField(render_kw={"placeholder": "example: CS5200"})
    CRN = StringField(render_kw={"placeholder": "CRN"})
    level = SelectField('level',choices=('graduate','undergraduate'))
    campus = SelectField('campus')
    type = SelectField('type', choices=('offline','online','hybrid'))

class ProfessorForm(FlaskForm):
    major = SelectField('major')
    number = StringField(render_kw={"placeholder": "example: CS5200"})
    CRN = StringField(render_kw={"placeholder": "CRN"})
    level = SelectField('level')
    campus = SelectField('campus')
    type = SelectField('type', choices=('offline','online','hybrid'))    

@app.route("/")
def homepage(methods = ['GET', 'POST']):
    # (test db connection purpose)response list all data in a table
    # campus = Campus.query.all()
    response = list()
    # for cam in campus:
    #     response.append({
    #         "name" : cam.name,
    #         "location": cam.location
    #     })
    # return make_response({
    #     'status' : 'success',
    #     'message': response
    # }, 200)
    # campus = Campus.query.with_entities(Campus.name)
    # majors = Major.query.with_entities(Major.name)
    # for cam in campus:
    #     response.append({
    #         "name" : maj.name,
    #     })
    # return make_response({
    #     'status' : 'success',
    #     'message': response
    # }, 200)
    form = LoginForm()
    return render_template("home.html", form = form)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    global userID, userRole
    form = LoginForm()
    # if form.validate_on_submit():
    user = Users.query.filter_by(id=form.id.data).first()
    if user:
        if (user.password == form.password.data):
            login_user(user)
            if user.role == "student":
                return redirect(url_for('studentDashboard'))
            if user.role == "admin":
                return redirect(url_for('adminDashboard'))
        else:
            flash("The password you entered is incorrect. Please try again.")
            return redirect(request.url)    
    else:
        flash("The id you entered is incorrect. Please try again")          
    return render_template('login.html',form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))    

@app.route('/studentDashboard', methods=['GET'])
def studentDashboard():
    id = current_user.id
    student = Student.query.filter_by(nuid=id).first()
    name = student.name
    return render_template('studentDashboard.html',name=name)

@app.route('/adminDashboard', methods=['GET'])
def adminDashboard():
    return render_template('adminDashboard.html')

@app.route('/semester', methods=['GET','POST'])
def semester():
    dropdown_list = ['Spring 2023','Fall 2022','Summer 2022']
    return render_template('semester.html',list=dropdown_list)

@app.route('/criteria', methods=['GET','POST'])
def criteria():
    form = CriteriaForm()
    majors = [x[0] for x in Major.query.with_entities(Major.name)]
    campus = [x[0] for x in Campus.query.with_entities(Campus.name)]
    form.major.choices = majors
    form.campus.choices = campus
    return render_template('criteria.html',form = form)    


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

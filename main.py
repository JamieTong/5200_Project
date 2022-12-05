from flask import Flask, render_template, request,url_for, redirect, make_response,flash
from google.cloud.sql.connector import Connector
import pymysql
import sqlalchemy 
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField,widgets
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from data import major_list
from sqlalchemy.sql import text, select
# from flask_table import Table, Col

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
    role = db.Column(db.String(50), nullable = False)
    min_credit = db.Column(db.Integer, nullable = False)
    department_id = db.Column(db.Integer, nullable = False)
    campus_name = db.Column(db.String(50), nullable = False)
    major = db.Column(db.String(50), nullable = False)

class Course(db.Model):
    __tablename__ = 'course'
    number = db.Column('number',db.Integer, primary_key = True, nullable = False)
    seats_available = db.Column(db.Integer, nullable = False)
    total_seats = db.Column(db.Integer, nullable = False)
    wl_available = db.Column(db.Integer, nullable = False)
    total_wl = db.Column(db.Integer, nullable = False)
    pre_requisite = db.Column(db.String(50), nullable = False)
    crn = db.Column(db.Integer, nullable = False)
    name = db.Column(db.String(50), nullable = False)
    type = db.Column(db.String(50), nullable = False)
    level = db.Column(db.String(50), nullable = False)
    semester = db.Column(db.String(50), nullable = False)
    time_from = db.Column(db.String(50), nullable = False)
    time_to = db.Column(db.String(50), nullable = False)
    days = db.Column(db.String(50), nullable = False)
    date = db.Column(db.String(50), nullable = False)
    campus_name = db.Column(db.String(50), nullable = False)
    credit = db.Column(db.Integer, nullable = False)
    major = db.Column(db.String(50), nullable = False)

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

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CriteriaForm(FlaskForm):
    semester = SelectField('semester', choices=('Spring 2023','Fall 2022','Summer 2022'))
    major = SelectField('major')
    number = StringField('number',render_kw={"placeholder": "example: CS5200"})
    keyword = StringField('keyword',render_kw={"placeholder": "class contains the word"})
    CRN = StringField('CRN',render_kw={"placeholder": "CRN"})
    level = SelectField('level', choices=('','graduate','undergraduate'))
    campus = SelectField('campus')
    type = SelectField('type', choices=('','offline','online','hybrid'))
    days = MultiCheckboxField('days', choices=('MON','TUE','WED','THU','FRI','SAT','SUN'))
    time_from = SelectField('time_from',choices=('','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00',
    '18:00','19:00','20:00','21:00','22:00','23:00','00:00'))
    time_to = SelectField('time_to',choices=('','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00',
    '18:00','19:00','20:00','21:00','22:00','23:00','00:00'))
    submit = SubmitField('Search')    

# class ProfessorForm(FlaskForm):
#     name = StringField(render_kw={"placeholder": "name"})
#     field = SelectField('filed', choices=('teaching courses','working field'))

# class CourseTable(Table)

@app.route("/")
def homepage(methods = ['GET', 'POST']):
    name = 'Spring 2023'
    semester_courses = Course.query.filter_by(semester = 'Spring 2023',campus_name = 'Boston',credit = 4)
    # # (test db connection purpose)response list all data in a table

    response = list()

    # response.append({
    #         "name" : student.name,
    #         "major": student.major
    #     })
    for course in semester_courses:
        response.append({
            "name" : course.name,
            "total_wl": course.total_wl,
            "level": course.level
        })
    return make_response({
        'status' : 'success',
        'message': response
    }, 200)
    form = LoginForm()
    return render_template("home.html", form = form)

# To login, I only added one user to Users: please use: id=938372796, password=02031f84
@app.route("/login", methods = ['GET', 'POST'])
def login():
    global userID, userRole
    form = LoginForm()
    # if form.validate_on_submit():
    user = Users.query.filter_by(id=form.id.data).first()
    print('user found')
    if user:
        if (user.password == form.password.data):
            print('password found')
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
    major = [x[0] for x in Major.query.with_entities(Major.name)]
    major.insert(0, "")
    campus = [x[0] for x in Campus.query.with_entities(Campus.name)]
    campus.insert(0, "")
    form.major.choices = major
    form.campus.choices = campus
    return render_template('criteria.html',form = form)    

@app.route('/search',  methods=['GET','POST'])
def searchCourse():
    form = request.form
    semester = form['semester']
    number = form['number'] 
    CRN = form['CRN']
    major = form['major']  
    campus = form['campus'] 
    keyword = form['keyword'] 
    type = form['type'] 
    level = form['level']
    days = request.form.getlist('days')
    time_from = form['time_from'] 
    time_to = form['time_to'] 
    equal_conditions = [('number',number),('CRN',CRN),('major',major),('campus_name',campus),
    ('type',type),('level',level)] * 1

    valid_equal_conditions = list()
    valid_other_conditions = list()
    for row in equal_conditions:
        if (row[1] == '' or row[1] == ' ' or row[1] is None or not row[1]) == False:
            valid_equal_conditions.append(row) 
    for row in equal_conditions:
        if (row[1] == '' or row[1] == ' ' or row[1] is None or not row[1]) == False:
            valid_other_conditions.append(row)         
    query_string = ('select * from course where semester = "{s}"').format(s=semester)
    for row in valid_equal_conditions:
        if row[0] == 'CRN':
            query_string += (' and {a} = {b}').format(a = row[0],b = row[1])
        else:
            query_string += (" and {a} = '{b}'").format(a = row[0],b = row[1])
    if keyword != '':
        query_string += (" and name like '%{k}%'").format(k = keyword)
    if not days:
        for day in days:
            query_string += (" and days like '{d}'").format(d = day)    
    if time_from != '':
        query_string += (" and time_from >= '{f}'").format(f = time_from)
    if time_to != '':
        query_string += (" and time_to <= '{t}'").format(t = time_to)  
    if len(days) > 0:
        for day in days:
            query_string += (" and days like '%{d}%'").format(d = day)   
    # SELECT * FROM course WHERE days LIKE '%FRI%' and days LIKE '%WED%';
    print(query_string)   
    courses = db.session.execute(select(Course).from_statement(text(query_string))).scalars().all()
    # response = list()
    # for course in courses:
    #     response.append({
    #         "name" : course.name,
    #         "number": course.number,
    #         "major": course.major
    #     })
    # return make_response({
    #     'status' : 'success',
    #     'message': response
    # }, 200)

    return render_template('browseClasses.html',courses = courses)   

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

from flask import Flask, render_template, request,url_for, redirect, make_response,flash
from google.cloud.sql.connector import Connector
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField,widgets
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from data import major_list
from sqlalchemy.sql import text, select
from datetime import datetime
# from flask_table import Table, Col

app = Flask(__name__)

# Google Cloud SQL 
PASSWORD ="1234"
USER = "root"
PUBLIC_IP_ADDRESS ="10.17.176.3"
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


class Registration(db.Model):
    __tablename__ = 'registration'
    crn = db.Column(db.Integer, primary_key = True,nullable = False)
    nuid = db.Column(db.Integer, primary_key = True, nullable = False)
    course_number = db.Column(db.String(50), nullable = False)
    permission = db.Column(db.String(50), nullable = True)
    registration_time = db.Column(db.String(50), nullable = True)


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

# login details
@app.route("/")
def homepage(methods = ['GET', 'POST']):

    # response = list()

    # # response.append({
    # #         "name" : student.name,
    # #         "major": student.major
    # #     })
    # for course in semester_courses:
    #     response.append({
    #         "name" : course.name,
    #         "total_wl": course.total_wl,
    #         "level": course.level
    #     })
    # return make_response({
    #     'status' : 'success',
    #     'message': response
    # }, 200)
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


# student dashboard
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

@app.route('/filter', methods=['GET','POST'])
def filter():
    form = CriteriaForm()
    major = [x[0] for x in Major.query.with_entities(Major.name)]
    major.insert(0, "")
    campus = [x[0] for x in Campus.query.with_entities(Campus.name)]
    campus.insert(0, "")
    form.major.choices = major
    form.campus.choices = campus
    return render_template('browse_criteria.html',form = form)  

@app.route('/search',  methods=['GET','POST'])
def search():
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

    return render_template('browseClasses.html',courses = courses)   

@app.route('/searchCourse',  methods=['GET','POST'])
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

    return render_template('classes.html',courses = courses)   

@app.route('/register',  methods=['POST'])
def register():
    form = request.form
    nuid = current_user.get_id()
    crn = form['crn']
    course_number = form['number']
    permission = "Allowed"
    registration_time = datetime.now()

    # sql_query = ('insert into registration VALUES({crn},{nuid},{course_number},"{permission}","{registration_time}")').format(crn=crn, nuid=nuid, course_number=course_number, permission=permission,registration_time=registration_time)
    registration = Registration(crn=crn, nuid=nuid, course_number=course_number, permission=permission, registration_time=registration_time)
    db.session.add(registration)
    db.session.commit()
    return(redirect('/semester'))
    return "Success", 200, {"Access-Control-Allow-Origin": "*"}

@app.route('/semester', methods=['GET','POST'])
def semester():
    id = current_user.get_id()
    # reg = Registration.query.join(Student).filter(Registration,nuid = Registration.nuid)

    regs = db.session.query(
         Registration.crn, Registration.course_number,Course.name, Registration.nuid, Registration.registration_time, Registration.permission
    ).filter(
         Registration.crn == Course.crn
    ).filter_by(
         nuid = id
    ).all()
    print(regs)

    # myCourses = db.session.execute(select(Registration).filter_by(nuid=nuid)).scalars().all()
    # terms = ['Spring 2023','Fall 2022','Summer 2022']
    return render_template('student_view.html', regs=regs)

@app.route('/dropClass', methods = ['POST'])
def dropClass():
    form = request.form
    crn = form['crn']
    nuid = form['nuid']
    Registration.query.filter_by(crn=crn, nuid=nuid).delete()
    # print(reg.permission)
    # reg.permission = permission
    db.session.commit()
    return(redirect('/semester'))
# admin dashboard
@app.route('/selectSemester', methods=['GET','POST'])
def selectSemester():
    terms = ['','Spring 2023','Fall 2022','Summer 2022']
    return render_template('adminSemester.html', list=terms)

@app.route('/selectSemester1', methods=['GET','POST'])
def selectSemester1():
    terms = ['','Spring 2023','Fall 2022','Summer 2022']
    return render_template('adminSemester1.html', list=terms)    

@app.route('/viewRegistration', methods=['GET','POST'])
def viewRegistration():
    semester = request.form.get('semester')
    regs = db.session.query(
         Registration.crn, Registration.course_number,Course.name,Student.name, Registration.nuid, Registration.registration_time, Registration.permission
    ).filter(
         Registration.crn == Course.crn,
    ).filter(
         Registration.nuid == Student.nuid,
    ).all()
    return render_template('viewRegistration.html',semester = semester,regs = regs)    

@app.route('/editPermission', methods=['GET','POST'])
def editPermission():
    semester = request.form.get('semester')
    regs = db.session.query(
         Registration.crn, Registration.course_number,Course.name,Student.name, Registration.nuid, Registration.registration_time, Registration.permission
    ).filter(
         Registration.crn == Course.crn,
    ).filter(
         Registration.nuid == Student.nuid,
    ).all()
    return render_template('editPermission.html',semester = semester,regs = regs)   

@app.route('/updatePermission', methods = ['POST'])
def updatePermission():
    form = request.form
    crn = form['crn']
    nuid = form['nuid']
    permission = form['permission']
    reg = Registration.query.filter_by(crn=crn, nuid=nuid).first()
    print(reg.permission)
    reg.permission = permission
    db.session.commit()

    return(redirect('/editPermission'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

from flask import Flask,request,render_template,request,redirect,url_for,session,flash
from wtforms import Form, StringField, TextAreaField, PasswordField, validators,EmailField,SelectField
import ibm_db
from prettytable import from_db_cursor
import re
import uuid
import ibm_boto3
from ibm_botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired

app = Flask(__name__)
app.secret_key='a'


#connect db2
conn=ibm_db.connect("DATABASE=;HOSTNAME=;PORT=;SECURITY=;SSLServerCertificate=;UID;PWD=",'','')

def log_done():
    print("DONE!\n")
def log_client_error(e):
    print("CLIENT ERROR: {0}\n".format(e))

def log_error(msg):
    print("UNKNOWN ERROR: {0}\n".format(msg))

def get_uuid():
    return str(uuid.uuid4().hex)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/jobseeker_login',methods=['GET','POST'])
def jobseeker_login():
    global userid
    if request.method == 'POST':
        form_type=request.form['type']
        if(form_type=="login"):
            email = request.form['email']
            password = request.form['password']
            sql = "SELECT * FROM jobseekers WHERE email=? AND password=?"
            st=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(st,1,email)
            ibm_db.bind_param(st,2,password)
            ibm_db.execute(st)
            account=ibm_db.fetch_assoc(st)
            print(account)
            if account:
                msg="Logged In Successfully"
                session['logged_in']=True
                session['id']=account['USERNAME']
                session['useremail']=account['EMAIL']
                session['userType']="jobseeker"
                print(session['userType'])
                userid=account["USERNAME"]
                session['username']=account['USERNAME']
                flash('Login Successful','success')
                return redirect(url_for('jobseeker_dashboard',uname=userid))
            else:
                print("nope")
                flash('Email or Password Incorrect','danger')
                return render_template('login_jobseeker.html')
        else:
            username=request.form['username']
            email=request.form['email']
            password=request.form['password']
            confirm_password=request.form['confirm_password']
            if password!=confirm_password:
                msg="Password & Confirm password is not same"
                flash('Password & Confirm password doesnt match, Try Login ','danger')
                print(msg)
            sql="SELECT * FROM jobseekers WHERE email=?"
            st=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(st,1,email)
            ibm_db.execute(st)
            account=ibm_db.fetch_assoc(st)
            print(account)
            if account:
                msg="account already exixt"
                flash('Account is already exist, Try Login ','danger')
                print(msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
                msg="invalid email"
                flash('Email format is Incorrect','danger')
                print(msg)
            elif not re.match(r'[A-Za-z0-9]+',username):
                msg="shld contain oly alpha"
                flash('Username must contain only Alphabets and Numbers','danger')
                print(msg)
            else:
                insert_sql="INSERT INTO jobseekers VALUES(?,?,?)"
                prep_stmt=ibm_db.prepare(conn,insert_sql)
                ibm_db.bind_param(prep_stmt,1,username)
                ibm_db.bind_param(prep_stmt,2,email)
                ibm_db.bind_param(prep_stmt,3,password)
                ibm_db.execute(prep_stmt)
                flash('Account created successfully, Login to Continue !','success')
                msg="you have successfully Registered, Login to continue"
                print(msg)
    print("entered normal call")
    return render_template('login_jobseeker.html')

@app.route("/recruiter_login",methods=["GET","POST"])
def recruiter_login():
    global userid
    if request.method == 'POST':
        form_type=request.form['type']
        if(form_type=="login"):
            print("enetered login")
            email = request.form['email']
            password = request.form['password']
            sql = "SELECT * FROM recruiters WHERE email=? AND password=?"
            st=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(st,1,email)
            ibm_db.bind_param(st,2,password)
            ibm_db.execute(st)
            account=ibm_db.fetch_assoc(st)
            print(account)
            if account:
                msg="Logged In Successfully"
                session['logged_in']=True
                session['id']=account['USERNAME']
                session['useremail']=account['EMAIL']
                session['userType']="recruiter"
                print(session['userType'])
                userid=account["USERNAME"]
                session['username']=account['USERNAME']
                flash('Login Successful','success')
                return redirect(url_for('recruiter_dashboard',uname=userid))
            else:
                print("nope")
                flash('Email or Password Incorrect','danger')
                return render_template('login_recruiter.html')
        else:
            username=request.form['username']
            email=request.form['email']
            password=request.form['password']
            company=request.form['commpany_name']
            designation=request.form['designation']
            confirm_password=request.form['confirm_password']
            if password!=confirm_password:
                msg="Password & Confirm password is not same"
                flash('Password & Confirm password doesnt match, Try Login ','danger')
                print(msg)
            sql="SELECT * FROM recruiters WHERE email=?"
            st=ibm_db.prepare(conn,sql)
            ibm_db.bind_param(st,1,email)
            ibm_db.execute(st)
            account=ibm_db.fetch_assoc(st)
            print(account)
            if account:
                msg="account already exixt"
                flash('Account is already exist, Try Login ','danger')
                print(msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
                msg="invalid email"
                flash('Email format is Incorrect','danger')
                print(msg)
            elif not re.match(r'[A-Za-z0-9]+',username):
                msg="shld contain oly alpha"
                flash('Username must contain only Alphabets and Numbers','danger')
                print(msg)
            else:
                insert_sql="INSERT INTO recruiters VALUES(?,?,?,?,?)"
                prep_stmt=ibm_db.prepare(conn,insert_sql)
                ibm_db.bind_param(prep_stmt,1,username)
                ibm_db.bind_param(prep_stmt,2,email)
                ibm_db.bind_param(prep_stmt,3,company)
                ibm_db.bind_param(prep_stmt,4,designation)
                ibm_db.bind_param(prep_stmt,5,password)
                ibm_db.execute(prep_stmt)
                flash('Account created successfully, Login to Continue !','success')
                msg="you have successfully Registered, Login to continue"
                print(msg)
    
    return render_template('login_recruiter.html')

@app.route('/jobseeker_dashboard/<uname>')
def jobseeker_dashboard(uname):
    return render_template('home_jobseeker.html',userName=uname)

@app.route('/recruiter_dashboard/<uname>')
def recruiter_dashboard(uname):
    return render_template('home_recruiter.html',userName=uname)


@app.route('/jobseeker_profile')
def jobseeker_profile():
    print("profile account .......... ",account)
    return render_template('profile_jobseeker.html',item=account)

@app.route('/recruiter_profile')
def recruiter_profile():
    return render_template('profile_recruiter.html',item=account)

@app.route('/jobseeker_profile_setup',methods=["GET","POST"])
def jobseeker_profile_setup():
    if request.method == 'POST':
        email=request.form['q20_email']
        name=request.form['q59_name']
        headline=request.form['q66_headline']
        phone=request.form['q60_phoneNumber[full]']
        gender=request.form['q13_gender']

        mnth=request.form['q15_dateOf[month]']
        day=request.form['q15_dateOf[day]']
        year=request.form['q15_dateOf[year]']
        
        dob=day+"-"+mnth+"-"+year
        nationality=request.form['q16_nationality']
        city=request.form['q18_address[city]']
        state=request.form['q18_address[state]']
        postal=request.form['q18_address[postal]']
        degree=request.form['q27_degree']
        dept=request.form['q26_areaOf']
        graduation=request.form['q42_yearOf']
        institute=request.form['q43_nameOf43']
        cgpa=request.form['q44_overallCgpa']
        skill=request.form['q51_typeA']
        company=request.form['q31_nameOf']
        designation=request.form['q33_designation']
        salary=request.form['q32_salary']
        experience=request.form['q45_yearOf45']
        linkedin=request.form['q68_linkedinProfile']
        website=request.form['q69_websiteUrl']
        otherlink=request.form['q70_otherUsefull']

        insert_sql="INSERT INTO JOBSEEKERPROFILES VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        prep_stmt=ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(prep_stmt,1,email)
        ibm_db.bind_param(prep_stmt,2,name)
        ibm_db.bind_param(prep_stmt,3,headline)
        ibm_db.bind_param(prep_stmt,4,phone)
        ibm_db.bind_param(prep_stmt,5,gender)
        ibm_db.bind_param(prep_stmt,6,dob)
        ibm_db.bind_param(prep_stmt,7,nationality)
        ibm_db.bind_param(prep_stmt,8,city)
        ibm_db.bind_param(prep_stmt,9,state)
        ibm_db.bind_param(prep_stmt,10,postal)
        ibm_db.bind_param(prep_stmt,11,degree)
        ibm_db.bind_param(prep_stmt,12,dept)
        ibm_db.bind_param(prep_stmt,13,graduation)
        ibm_db.bind_param(prep_stmt,14,institute)
        ibm_db.bind_param(prep_stmt,15,cgpa)
        ibm_db.bind_param(prep_stmt,16,skill)
        ibm_db.bind_param(prep_stmt,17,company)
        ibm_db.bind_param(prep_stmt,18,designation)
        ibm_db.bind_param(prep_stmt,19,salary)
        ibm_db.bind_param(prep_stmt,20,experience)
        ibm_db.bind_param(prep_stmt,23,linkedin)
        ibm_db.bind_param(prep_stmt,24,website)
        ibm_db.bind_param(prep_stmt,25,otherlink)
        
        ibm_db.execute(prep_stmt)
        
        return render_template("profile_jobseeker_setup.html",form=form)
        
    return render_template("profile_jobseeker_setup.html",form=form)

@app.route('/recruiter_profile_setup',methods=["GET","POST"])
def recruiter_profile_setup():
    if request.method == 'POST':
        companyname=request.form['q42_companyName']
        headline=request.form['q43_headline']
        about=request.form['q45_aboutYour']
        email=request.form['q20_email']
        website=request.form['q17_website']
        location=request.form['q16_location']
        insert_sql="INSERT INTO RECRUITERPROFILES VALUES(?,?,?,?,?,?,?)"
        prep_stmt=ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(prep_stmt,1,companyname)
        ibm_db.bind_param(prep_stmt,2,headline)
        ibm_db.bind_param(prep_stmt,3,logofilename)
        ibm_db.bind_param(prep_stmt,4,about)
        ibm_db.bind_param(prep_stmt,5,email)
        ibm_db.bind_param(prep_stmt,6,website)
        ibm_db.bind_param(prep_stmt,7,location)
        
        ibm_db.execute(prep_stmt)
        
        return render_template("profile_recruiter_setup.html",form=form)
        
    return render_template("profile_recruiter_setup.html",form=form)


@app.route('/jobseeker_profile_update',methods=["GET","POST"])
def jobseeker_profile_update():
    if request.method == 'POST':
        email=request.form['q20_email']
        name=request.form['q59_name']
        headline=request.form['q66_headline']
        phone=request.form['q60_phoneNumber[full]']
        gender=request.form['q13_gender']

        mnth=request.form['q15_dateOf[month]']
        day=request.form['q15_dateOf[day]']
        year=request.form['q15_dateOf[year]']
        
        dob=day+"-"+mnth+"-"+year
        nationality=request.form['q16_nationality']
        city=request.form['q18_address[city]']
        state=request.form['q18_address[state]']
        postal=request.form['q18_address[postal]']
        degree=request.form['q27_degree']
        dept=request.form['q26_areaOf']
        graduation=request.form['q42_yearOf']
        institute=request.form['q43_nameOf43']
        cgpa=request.form['q44_overallCgpa']
        skill=request.form['q51_typeA']
        company=request.form['q31_nameOf']
        designation=request.form['q33_designation']
        salary=request.form['q32_salary']
        experience=request.form['q45_yearOf45']
        linkedin=request.form['q68_linkedinProfile']
        website=request.form['q69_websiteUrl']
        otherlink=request.form['q70_otherUsefull']
        insert_sql="UPDATE JOBSEEKERPROFILES SET name =?, headline =?, phone=?,gender=?,dob=?,nationality=?,city=?,state=?,pincode=?,degree=?,areaofstudy=?,graduation=?,institute=?,cgpa=?,skills=?,company=?,designation=?,salary=?,experience=?,resume=?,profilepicture=?,linkedinlink=?,websitelink=?,otherlink=? WHERE email=? "
        prep_stmt=ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(prep_stmt,1,name)
        ibm_db.bind_param(prep_stmt,2,headline)
        ibm_db.bind_param(prep_stmt,3,phone)
        ibm_db.bind_param(prep_stmt,4,gender)
        ibm_db.bind_param(prep_stmt,5,dob)
        ibm_db.bind_param(prep_stmt,6,nationality)
        ibm_db.bind_param(prep_stmt,7,city)
        ibm_db.bind_param(prep_stmt,8,state)
        ibm_db.bind_param(prep_stmt,9,postal)
        ibm_db.bind_param(prep_stmt,10,degree)
        ibm_db.bind_param(prep_stmt,11,dept)
        ibm_db.bind_param(prep_stmt,12,graduation)
        ibm_db.bind_param(prep_stmt,13,institute)
        ibm_db.bind_param(prep_stmt,14,cgpa)
        ibm_db.bind_param(prep_stmt,15,skill)
        ibm_db.bind_param(prep_stmt,16,company)
        ibm_db.bind_param(prep_stmt,17,designation)
        ibm_db.bind_param(prep_stmt,18,salary)
        ibm_db.bind_param(prep_stmt,19,experience)
        ibm_db.bind_param(prep_stmt,20,resume)
        ibm_db.bind_param(prep_stmt,21,profilepicture)
        ibm_db.bind_param(prep_stmt,22,linkedin)
        ibm_db.bind_param(prep_stmt,23,website)
        ibm_db.bind_param(prep_stmt,24,otherlink)
        ibm_db.bind_param(prep_stmt,25,email)
        ibm_db.execute(prep_stmt)
        return render_template('profile_jobseeker.html',item=account)
    return render_template('profile_jobseeker_update.html',form=form,item=account)

@app.route('/recruiter_profile_update',methods=["GET","POST"])
def recruiter_profile_update():
    if request.method == 'POST':
        companyname=request.form['q42_companyName']
        headline=request.form['q43_headline']
        about=request.form['q45_aboutYour']
        email=request.form['q20_email']
        website=request.form['q17_website']
        location=request.form['q16_location']
        insert_sql="UPDATE RECRUITERPROFILES SET headline =?, companylogo=?,about=?,email=?,website=?,location=? where companyname=? "
        prep_stmt=ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(prep_stmt,1,headline)
        ibm_db.bind_param(prep_stmt,2,logofilename)
        ibm_db.bind_param(prep_stmt,3,about)
        ibm_db.bind_param(prep_stmt,4,email)
        ibm_db.bind_param(prep_stmt,5,website)
        ibm_db.bind_param(prep_stmt,6,location)
        ibm_db.bind_param(prep_stmt,7,companyname)
        ibm_db.execute(prep_stmt)
        return render_template('profile_recruiter.html',item=account)
    return render_template('profile_recruiter_update.html',item=account)

@app.route('/logout')
def logout():
    session['logged_in']=False
    session.pop('Loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


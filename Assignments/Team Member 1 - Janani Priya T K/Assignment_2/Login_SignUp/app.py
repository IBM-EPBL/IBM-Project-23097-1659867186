from flask import Flask,request,render_template,request,redirect,url_for,session,flash
from wtforms import Form, StringField, TextAreaField, PasswordField, validators,EmailField,SelectField
import ibm_db
import re

app = Flask(__name__)
app.secret_key=' '

#connect db2
conn=ibm_db.connect("DATABASE=;HOSTNAME=;PORT=;SECURITY=;SSLServerCertificate=;UID=;PWD=",'','')

@app.route('/')
def hello():
    return render_template('index.html')

class LoginForm(Form):  # Create Login Form
    email = StringField('', [validators.length(min=1)],
                           render_kw={'autofocus': True, 'placeholder': 'Email'})                    
    password = PasswordField('', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})

@app.route('/login',methods=['GET','POST'])
def login():
    global userid
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # GEt user form
        email = form.email.data
        # email = request.form.get("email")
        password = form.password.data
        sql = "SELECT * FROM users WHERE email=? AND password=?"
        st=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(st,1,email)
        ibm_db.bind_param(st,2,password)
        ibm_db.execute(st)
        account=ibm_db.fetch_assoc(st)
        print(account)
        if account:
            print("yes iit is")
            msg="Logged In Successfully"
            session['logged_in']=True
            session['id']=account['USERNAME']
            userid=account["USERNAME"]
            session['username']=account['USERNAME']
            flash('Login Successful','success')
            return redirect(url_for('dashboard',uname=userid))
        else:
            print("nope")
            flash('Email or Password Incorrect','danger')
            return render_template('login.html',form=form)
    return render_template('login.html', form=form)

class RegisterForm(Form):
    username = StringField('', [validators.length(min=3, max=25)], render_kw={'placeholder': 'Username'})
    email = EmailField('', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})
    password = PasswordField('', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})
    roll=StringField('', [validators.length(min=3, max=25)], render_kw={'placeholder': 'Roll Number'})
@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method=="POST":
        username=form.username.data
        email=form.email.data
        password=form.password.data
        roll=form.roll.data
        # password=request.form['password']
        sql="SELECT * FROM users WHERE email=?"
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
            insert_sql="INSERT INTO users VALUES(?,?,?,?)"
            prep_stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,username)
            ibm_db.bind_param(prep_stmt,2,email)
            ibm_db.bind_param(prep_stmt,3,password)
            ibm_db.bind_param(prep_stmt,4,roll)
            ibm_db.execute(prep_stmt)
            flash('Account created successfully, Login to Continue !','success')
            msg="you have successfully Registered, Login to continue"
            print(msg)
    elif request.method=="POST":
        msg="please fill out form"
        print(msg)
        return render_template('register.html',form=form)
    return render_template('register.html',form=form)

@app.route('/dashboard/<uname>')
def dashboard(uname):
    return render_template('dashboard.html',userName=uname)

@app.route('/logout')
def logout():
    session['logged_in']=False
    session.pop('Loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

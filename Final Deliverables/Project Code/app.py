from flask import Flask,request,render_template,request,redirect,url_for,session,flash
from wtforms import Form, StringField, TextAreaField, PasswordField, validators,EmailField,SelectField
import ibm_db
import re
import uuid
import ibm_boto3
from ibm_botocore.client import Config
from ibm_botocore.exceptions import ClientError
import ibm_s3transfer.manager
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
import random
import requests
from flask import Flask, jsonify, request
import base64
from datetime import date

#connect db2
conn=ibm_db.connect("DATABASE=;HOSTNAME=;SECURITY=;SSLServerCertificate=;UID=;PWD=",'','')

class UploadFileForm(FlaskForm):
    resume = FileField("File", validators=[InputRequired()])
    profilepic=FileField("File", validators=[InputRequired()])

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/joblisting')
def joblisting():
    sql = "SELECT * FROM JOBPOSTINGS"
    stmt = ibm_db.exec_immediate(conn, sql)
    tuple = ibm_db.fetch_tuple(stmt)
    items=[]
    while tuple != False:
        tuple = ibm_db.fetch_tuple(stmt)
    return render_template('job_listing.html',items=items)

@app.route('/jobdetails',methods=["GET","POST"])
def jobdetails():
    jobid=request.form['jobid']
    sql = "SELECT * FROM JOBPOSTINGS where jobid=?"
    st=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(st,1,jobid)
    ibm_db.execute(st)
    account=ibm_db.fetch_assoc(st)
    req=[]
    req=account["REQUIREMENTS"].splitlines( )
    account["REQUIREMENTS"]=req
    company_name=account["COMPANYNAME"]
    sql = "SELECT * FROM RECRUITERPROFILES where COMPANYNAME=?"
    st=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(st,1,company_name)
    ibm_db.execute(st)
    return render_template('job_details.html',item=account,company_item=companyaccount)

# Profile Setup
@app.route('/jobseeker_profile')
def jobseeker_profile():
    
    account=fetchjprofiledata()
    return render_template('profile_jobseeker.html',item=account)

@app.route('/recruiter_profile')
def recruiter_profile():
    account=fetchrprofiledata()
    
    return render_template('profile_recruiter.html',item=account)


# Posting Jobs
@app.route('/posting_job',methods=["GET","POST"])
def posting_job():
    if request.method == 'POST':
        company_name=request.form['q42_typeA42']
        recruiter_email=request.form['q20_recruiterEmail']
        job_role=request.form['q43_jobRole']
        job_type=request.form['q47_jobType47']
        job_description=request.form['q48_jobDescription']
        job_requirements=request.form['q49_requirements']
        job_location=request.form['q44_jobLocation']
        salary=request.form['q45_salary']
        vaccancy=request.form['q51_vaccancy']

        jobid="JBID"+company_name[0]+company_name[len(company_name)-1]+str(random.randint(1000,9999))
        jobid=jobid.upper()
        
        insert_sql="INSERT INTO JOBPOSTINGS VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"
        stmt=ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(stmt,1,jobid)
        ibm_db.bind_param(stmt,2,job_role)
        ibm_db.bind_param(stmt,3,company_name)
        ibm_db.bind_param(stmt,4,job_location)
        ibm_db.bind_param(stmt,5,job_type)
        ibm_db.bind_param(stmt,6,job_description)
        ibm_db.execute(stmt)
        return render_template('profile_recruiter.html',item=account)
    return render_template('post_jobs.html',useremail=session['useremail'],companyname=session['companyname'])

@app.route('/joblistingviaapi',methods=["GET","POST"])
def joblistingviaapi():
    if request.method == 'POST':
        query=request.form['query']
        url1 = 'https://www.reed.co.uk/api/1.0/search?keywords='+query
        result=response.json()
        items=result["results"]
        myitems=[]
        t=0
        return render_template('job_listing_via_apis.html',items=myitems)

@app.route('/jobdetailsviaapis',methods=["GET","POST"])
def jobdetailsviaapis():
    if request.method == 'POST':
        jobid=request.form['jobid']
        url1 = 'https://www.reed.co.uk/api/1.0/search?keywords='+jobid
        result=response.json()
        result=result["results"]
        result=result[0]
        return render_template('job_details_via_apis.html',item=result)

@app.route('/courseApiSearch',methods=["GET","POST"])
def courseApiSearch():
    if request.method == 'POST':
        query=request.form['query']
        url1 = 'https://www.udemy.com/api-2.0/courses/?language=en&search='+query
        response = requests.get(url1,headers=headers)
        result=response.json()
        result=result["results"]
        myitems=[]
        t=0
        count=len(result)
        while(t<len(result)):
            item=result[t]
            myitem={}
            myitem["courseName"]=item["title"]
            myitem["headline"]=item["headline"]
            myitem["price"]=item["price"]
            myitem["view"]="https://www.udemy.com"+item["url"]
            myitem["image"]=item["image_480x270"]
            myitems.append(myitem)
            t=t+1
        return render_template('courseSearchResults.html',items=myitems,count=count)

@app.route('/courseFetch')
def courseFetch():
    url1 = 'https://www.udemy.com/api-2.0/courses/?&language=en&search=java'
    result=response.json()
    result=result["results"]
    myitems=[]
    t=0
    while(t<8):
        item=result[t]
        myitem={}
        myitem["courseName"]=item["title"]
        myitem["headline"]=item["headline"]
        myitem["price"]=item["price"]
        myitem["image"]=item["image_480x270"]
        myitems.append(myitem)
        t=t+1
    return render_template('courseFetch.html',items=myitems)

@app.route('/submit_application',methods=["GET","POST"])
def submit_application():
    today = date.today()
    if request.method == 'POST':
        account=fetchjprofiledata()
        if request.form['task']=='Edit Profile':
            form = UploadFileForm()
            return render_template('profile_jobseeker_update.html',form=form,item=account)
        else:
            stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(stmt,1,appln_number)
            return redirect(url_for('jobseeker_applications'))

@app.route('/jobseeker_applications')
def jobseeker_applications():
    
    current_user_email=session["useremail"]
    sql = "SELECT * FROM APPLICATIONS"
    stmt = ibm_db.exec_immediate(conn, sql)
    tuple = ibm_db.fetch_tuple(stmt)
    items=[]
    tuple = ibm_db.fetch_tuple(stmt)
    return render_template('applications_jobseeker.html',items=items)

@app.route('/recruiter_applications')
def recruiter_applications():
    sql = "SELECT * FROM APPLICATIONS"
    stmt = ibm_db.exec_immediate(conn, sql)
    tuple = ibm_db.fetch_tuple(stmt)
    return render_template('applications_recruiter.html',items=items)
@app.route('/joblisting')
def joblisting():
    sql = "SELECT * FROM JOBPOSTINGS"
    stmt = ibm_db.exec_immediate(conn, sql)
    tuple = ibm_db.fetch_tuple(stmt)
    items=[]
    while tuple != False:
        tuple = ibm_db.fetch_tuple(stmt)
    return render_template('job_listing.html',items=items)

@app.route('/jobdetails',methods=["GET","POST"])
def jobdetails():
    jobid=request.form['jobid']
    sql = "SELECT * FROM JOBPOSTINGS where jobid=?"
    st=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(st,1,jobid)
    ibm_db.execute(st)
    account=ibm_db.fetch_assoc(st)
    req=[]
    req=account["REQUIREMENTS"].splitlines( )
    account["REQUIREMENTS"]=req
    company_name=account["COMPANYNAME"]
    sql = "SELECT * FROM RECRUITERPROFILES where COMPANYNAME=?"
    st=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(st,1,company_name)
    ibm_db.execute(st)
    return render_template('job_details.html',item=account,company_item=companyaccount)

# Profile Setup
@app.route('/jobseeker_profile')
def jobseeker_profile():
    
    account=fetchjprofiledata()
    return render_template('profile_jobseeker.html',item=account)

@app.route('/recruiter_profile')
def recruiter_profile():
    account=fetchrprofiledata()
    
    return render_template('profile_recruiter.html',item=account)


# Posting Jobs
@app.route('/posting_job',methods=["GET","POST"])
def posting_job():
    if request.method == 'POST':
        company_name=request.form['q42_typeA42']
        recruiter_email=request.form['q20_recruiterEmail']
        job_role=request.form['q43_jobRole']
        job_type=request.form['q47_jobType47']
        job_description=request.form['q48_jobDescription']
        job_requirements=request.form['q49_requirements']
        job_location=request.form['q44_jobLocation']
        salary=request.form['q45_salary']
        vaccancy=request.form['q51_vaccancy']

        jobid="JBID"+company_name[0]+company_name[len(company_name)-1]+str(random.randint(1000,9999))
        jobid=jobid.upper()
        
        insert_sql="INSERT INTO JOBPOSTINGS VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"
        stmt=ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(stmt,1,jobid)
        ibm_db.bind_param(stmt,2,job_role)
        ibm_db.bind_param(stmt,3,company_name)
        ibm_db.bind_param(stmt,4,job_location)
        ibm_db.bind_param(stmt,5,job_type)
        ibm_db.bind_param(stmt,6,job_description)
        ibm_db.execute(stmt)
        return render_template('profile_recruiter.html',item=account)
    return render_template('post_jobs.html',useremail=session['useremail'],companyname=session['companyname'])

@app.route('/joblistingviaapi',methods=["GET","POST"])
def joblistingviaapi():
    if request.method == 'POST':
        query=request.form['query']
        url1 = 'https://www.reed.co.uk/api/1.0/search?keywords='+query
        result=response.json()
        items=result["results"]
        myitems=[]
        t=0
        return render_template('job_listing_via_apis.html',items=myitems)

@app.route('/jobdetailsviaapis',methods=["GET","POST"])
def jobdetailsviaapis():
    if request.method == 'POST':
        jobid=request.form['jobid']
        url1 = 'https://www.reed.co.uk/api/1.0/search?keywords='+jobid
        result=response.json()
        result=result["results"]
        result=result[0]
        return render_template('job_details_via_apis.html',item=result)

@app.route('/courseApiSearch',methods=["GET","POST"])
def courseApiSearch():
    if request.method == 'POST':
        query=request.form['query']
        url1 = 'https://www.udemy.com/api-2.0/courses/?language=en&search='+query
        response = requests.get(url1,headers=headers)
        result=response.json()
        result=result["results"]
        myitems=[]
        t=0
        count=len(result)
        while(t<len(result)):
            item=result[t]
            myitem={}
            myitem["courseName"]=item["title"]
            myitem["headline"]=item["headline"]
            myitem["price"]=item["price"]
            myitem["view"]="https://www.udemy.com"+item["url"]
            myitem["image"]=item["image_480x270"]
            myitems.append(myitem)
            t=t+1
        return render_template('courseSearchResults.html',items=myitems,count=count)

@app.route('/courseFetch')
def courseFetch():
    url1 = 'https://www.udemy.com/api-2.0/courses/?&language=en&search=java'
    result=response.json()
    result=result["results"]
    myitems=[]
    t=0
    while(t<8):
        item=result[t]
        myitem={}
        myitem["courseName"]=item["title"]
        myitem["headline"]=item["headline"]
        myitem["price"]=item["price"]
        myitem["image"]=item["image_480x270"]
        myitems.append(myitem)
        t=t+1
    return render_template('courseFetch.html',items=myitems)

@app.route('/submit_application',methods=["GET","POST"])
def submit_application():
    today = date.today()
    if request.method == 'POST':
        account=fetchjprofiledata()
        if request.form['task']=='Edit Profile':
            form = UploadFileForm()
            return render_template('profile_jobseeker_update.html',form=form,item=account)
        else:
            stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(stmt,1,appln_number)
            return redirect(url_for('jobseeker_applications'))

@app.route('/jobseeker_applications')
def jobseeker_applications():
    
    current_user_email=session["useremail"]
    sql = "SELECT * FROM APPLICATIONS"
    stmt = ibm_db.exec_immediate(conn, sql)
    tuple = ibm_db.fetch_tuple(stmt)
    items=[]
    tuple = ibm_db.fetch_tuple(stmt)
    return render_template('applications_jobseeker.html',items=items)

@app.route('/recruiter_applications')
def recruiter_applications():
    sql = "SELECT * FROM APPLICATIONS"
    stmt = ibm_db.exec_immediate(conn, sql)
    tuple = ibm_db.fetch_tuple(stmt)
    return render_template('applications_recruiter.html',items=items)

@app.route('/view_applicantProfile',methods=["GET","POST"])
def view_applicantProfile():
    applicant_email=request.form["applicant_email"]
    st=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(st,1,applicant_email)
    ibm_db.execute(st)
    return render_template('view_profile.html',item=account)

@app.route('/view_applicantProfile',methods=["GET","POST"])
def view_applicantProfile():
    applicant_email=request.form["applicant_email"]
    st=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(st,1,applicant_email)
    ibm_db.execute(st)
    return render_template('view_profile.html',item=account)

@app.route('/logout')
def logout():
    session['logged_in']=False
    session.pop('Loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0')


from flask import render_template, url_for, request, redirect
from flask_pymongo import pymongo
import pyrebase
import requests
import json
import sys
import re
import os
import time
from app import app
from app import rds_db as db

config = {
    "apiKey": "AIzaSyAcxxRO8Sqf7m8F9NkUI6-9MPdWrZkYgGs",
    "authDomain": "savemygpa-7912d.firebaseapp.com",
    "databaseURL": "https://savemygpa-7912d.firebaseio.com",
    "projectId": "savemygpa-7912d",
    "storageBucket": "savemygpa-7912d.appspot.com",
    "messagingSenderId": "781502539376",
    "appId": "1:781502539376:web:7618817f841ef51f9b36b5"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

CONNECTION_STRING = 'mongodb://admin:ForTeam107@cluster0-shard-00-00.skio4.mongodb.net:27017,cluster0-shard-00-01.skio4.mongodb.net:27017,cluster0-shard-00-02.skio4.mongodb.net:27017/<saveMyGpa>?ssl=true&replicaSet=atlas-fvgrlg-shard-0&authSource=admin&retryWrites=true&w=majority'
client = pymongo.MongoClient(CONNECTION_STRING)
# print("server version:", client.server_info()["version"])
mdb = client.get_database('<saveMyGpa>')
# mongodb connected here
# print(mdb.list_collection_names())

@app.route('/')
@app.route('/index')
def index():
    if auth.current_user:
        subjects = db.get_subjects()
        student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]

        return render_template('index.html', records=student['courses'], subjects=subjects)
    else:
        return redirect('/account')

@app.route('/grade', methods=['POST', 'GET'])
def grade():
    subjects = db.get_subjects()
    selected_subject = request.form['subject']
    CRNs = db.get_CRNs(selected_subject)
    if 'CRN' not in request.form:
        return render_template('index.html', subjects=subjects, CRNs=CRNs, selected_subject=selected_subject)
    elif 'CRN' in request.form:
        selected_CRN = request.form['CRN']
        grade = db.get_grade(selected_subject, selected_CRN)
        return render_template('index.html', subjects=subjects, CRNs=CRNs, selected_subject=selected_subject, selected_CRN=selected_CRN, grade=grade)
    else:
        return None

@app.route('/read', methods=['POST', 'GET'])
def read():
    subjects = db.get_subjects()
    selected_subject = request.form['subject']
    CRNs = db.get_CRNs(selected_subject)
    if 'CRN' not in request.form:
        return render_template('index.html', subjects=subjects, CRNs=CRNs, selected_subject=selected_subject)
    elif 'CRN' in request.form:
        selected_CRN = request.form['CRN']
        sectionInfos = db.get_sectionInfos(selected_subject, selected_CRN)
        # print(type(selected_CRN), file=sys.stderr)
        return render_template('index.html', subjects=subjects, CRNs=CRNs, selected_subject=selected_subject, selected_CRN=selected_CRN, sectionInfos=sectionInfos)
    else:
        return None

@app.route('/increment', methods=['POST', 'GET'])
def increment():
    subjects = db.get_subjects()
    subjectI = request.form['subjectI']
    courseNumberI = request.form['courseNumberI']
    sectionIdI = request.form['sectionIdI']
    termI = request.form['termI']
    gradeI = request.form['gradeI']
    wRes = ""
    if subjectI not in subjects:
        wRes = "Put correct subject"
        return render_template('index.html', subjects=subjects, wRes=wRes)    
    if courseNumberI not in db.get_CRNs(subjectI):
        wRes = "Put correct course number"
        return render_template('index.html', subjects=subjects, wRes=wRes)
    if sectionIdI.isnumeric() == False:
        wRes = "Put correct section ID"
        return render_template('index.html', subjects=subjects, wRes=wRes)
    termPattern = re.compile(r'^20..-[fa, sp, su, wt]')
    if re.match(termPattern, termI) == None:
        wRes = "Put correct term (20xx-yy, yy = sp, fa, etc.)"
        return render_template('index.html', subjects=subjects, wRes=wRes)
    if gradeI not in ['A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W']:
        wRes = "Put correct grade ('A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W')"
        return render_template('index.html', subjects=subjects, wRes=wRes)
    res = db.increment_section(subjectI, courseNumberI, sectionIdI, termI, gradeI)
    if res == 1: 
        wRes = "Successfully incremented grade"
    elif res == -1: 
        wRes = "Such section does not exist. Change sectionId"
    else:
        wRes = "Such course does not exist. Change subject or course number"
    return render_template('index.html', subjects=subjects, wRes=wRes)

@app.route('/decrement', methods=['POST', 'GET'])
def decrement():
    subjects = db.get_subjects()
    subjectD = request.form['subjectD']
    courseNumberD = request.form['courseNumberD']
    sectionIdD = request.form['sectionIdD']
    termD = request.form['termD']
    gradeD = request.form['gradeD']
    dRes = ""
    if subjectD not in subjects:
        dRes = "Put correct subject"
        return render_template('index.html', subjects=subjects, dRes=dRes)    
    if courseNumberD not in db.get_CRNs(subjectD):
        dRes = "Put correct course number"
        return render_template('index.html', subjects=subjects, dRes=dRes)
    if sectionIdD.isnumeric() == False:
        dRes = "Put correct section ID"
        return render_template('index.html', subjects=subjects, dRes=dRes)
    termPattern = re.compile(r'^20..-[fa, sp, su, wt]')
    if re.match(termPattern, termD) == None:
        dRes = "Put correct term (20xx-yy, yy = sp, fa, etc.)"
        return render_template('index.html', subjects=subjects, dRes=dRes)
    if gradeD not in ['A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W']:
        dRes = "Put correct grade ('A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W')"
        return render_template('index.html', subjects=subjects, dRes=dRes)
    res = db.decrement_section(subjectD, courseNumberD, sectionIdD, termD, gradeD)
    if res == 1: 
        dRes = "Successfully decremented grade"
    elif res == -1: 
        dRes = "Such section does not exist. Change sectionId"
    else:
        dRes = "Such course does not exist. Change subject or course number"
    return render_template('index.html', subjects=subjects, dRes=dRes)

@app.route('/addProf', methods=['POST'])
def addProf():
    subjects = db.get_subjects()
    firstName = request.form['profFN']
    lastName = request.form['profLN']
    if firstName.isalpha() == False or lastName.isalpha() == False:
        apRes = "Put correct name"
        return render_template('index.html', subjects=subjects, apRes=apRes)
    db.add_professor(firstName, lastName)
    apRes = "Professor successfully added"
    return render_template('index.html', subjects=subjects, apRes=apRes)

@app.route('/deleteProf', methods=['POST'])
def deleteProf():
    subjects = db.get_subjects()
    firstName = request.form['profFND']
    lastName = request.form['profLND']
    if firstName.isalpha() == False or lastName.isalpha() == False:
        dpRes = "Put correct name"
        return render_template('index.html', subjects=subjects, dpRes=dpRes)
    db.delete_professor(firstName, lastName)
    dpRes = "Professor successfully deleted"
    return render_template('index.html', subjects=subjects, dpRes=dpRes)

@app.route('/account', methods=['GET'])
def account():
    return render_template('account.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return redirect('/')
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']
        print(error)
        return render_template('account.html', login_error=True, error_message=error['message'])

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']

    try:
        user = auth.create_user_with_email_and_password(email, password)
        user = auth.sign_in_with_email_and_password(email, password)

        department = request.form['department']
        year = int(request.form['class'])

        db.create_student(email, year, department)
        mdb.students.insert({ "studentEmail": email, "courses": [] }, {})

        return redirect('/')
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']
        print(error)
        return render_template('account.html', reg_error=True, error_message=error['message'])

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

term_frequencies = db.build_term_frequencies()

subj_list = []
f = open("subjects.txt", "r")
for x in f:
    subj_list.append(x.split('|||'))
f.close()

@app.route('/')
@app.route('/index')
def index():
    if auth.current_user:
        student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]

        return render_template('index.html', subj_list=subj_list, records=student['courses'])
    else:
        return redirect('/account')

@app.route('/getCrsNum', methods=['POST'])
def getCrsNum():
    sel_subj = request.form.get('sel_subj')
    CRNs = db.get_CRNs(sel_subj)
    return render_template('index.html', subj_list=subj_list, sel_subj=sel_subj, CRNs=CRNs)

@app.route('/grade', methods=['POST'])
def grade():
    sel_subj = request.form.get('sel_subj_pred')
    CRNs = db.get_CRNs(sel_subj)

    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']

    if 'CRN' not in request.form:
        return render_template('index.html', subj_list=subj_list, records=courses, CRNs=CRNs)
    elif 'CRN' in request.form:
        selected_CRN = request.form['CRN']
        grade = db.get_grade(sel_subj, selected_CRN)
        description = db.get_description(sel_subj, selected_CRN)
        academic_history = student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]['courses']
        return render_template('index.html', subj_list=subj_list, records=courses, CRNs=CRNs, sel_subj=sel_subj, selected_CRN=selected_CRN, grade=grade)
    else:
        return None

@app.route('/read', methods=['POST', 'GET'])
def read():
    sel_subj = request.form.get('sel_subj')
    CRNs = db.get_CRNs(sel_subj)

    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']

    if 'sel_CRN' not in request.form:
        return render_template('index.html', subj_list=subj_list, records=courses, CRNs=CRNs, sel_subj=sel_subj)
    elif 'sel_CRN' in request.form:
        sel_CRN = request.form.get('sel_CRN')
        sectionInfos = db.get_sectionInfos(sel_subj, sel_CRN)
        # print(type(selected_CRN), file=sys.stderr)
        return render_template('index.html', subj_list=subj_list, records=courses, CRNs=CRNs, sel_subj=sel_subj, sel_CRN=sel_CRN, sectionInfos=sectionInfos)
    else:
        return None

@app.route('/increment', methods=['POST', 'GET'])
def increment():
    subjectI = request.form['subjectI']
    courseNumberI = request.form['courseNumberI']
    sectionIdI = request.form['sectionIdI']
    termI = request.form['termI']
    gradeI = request.form['gradeI']
    wRes = ""
    subjects = []
    for x in subj_list:
        subjects.append(x[0])
    if subjectI not in subjects:
        wRes = "Put correct subject"
        return render_template('index.html', subj_list=subj_list, records=courses, wRes=wRes)    
    if courseNumberI not in db.get_CRNs(subjectI):
        wRes = "Put correct course number"
        return render_template('index.html', subj_list=subj_list, records=courses, wRes=wRes)
    if sectionIdI.isnumeric() == False:
        wRes = "Put correct section ID"
        return render_template('index.html', subj_list=subj_list, records=courses, wRes=wRes)
    termPattern = re.compile(r'^20..-[fa, sp, su, wt]')
    if re.match(termPattern, termI) == None:
        wRes = "Put correct term (20xx-yy, yy = sp, fa, etc.)"
        return render_template('index.html', subj_list=subj_list, records=courses, wRes=wRes)
    if gradeI not in ['A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W']:
        wRes = "Put correct grade ('A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W')"
        return render_template('index.html', subj_list=subj_list, records=courses, wRes=wRes)
    res = db.increment_section(subjectI, courseNumberI, sectionIdI, termI, gradeI)
    if res == 1:
        wRes = "Successfully incremented grade"
    elif res == -1:
        wRes = "Such section does not exist. Change sectionId"
    else:
        wRes = "Such course does not exist. Change subject or course number"
    
    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']

    return render_template('index.html', subj_list=subj_list, records=courses, wRes=wRes)

@app.route('/decrement', methods=['POST', 'GET'])
def decrement():
    subjectD = request.form['subjectD']
    courseNumberD = request.form['courseNumberD']
    sectionIdD = request.form['sectionIdD']
    termD = request.form['termD']
    gradeD = request.form['gradeD']
    dRes = ""
    subjects = []
    for x in subj_list:
        subjects.append(x[0])
    if subjectD not in subjects:
        dRes = "Put correct subject"
        return render_template('index.html', subj_list=subj_list, records=courses, dRes=dRes)    
    if courseNumberD not in db.get_CRNs(subjectD):
        dRes = "Put correct course number"
        return render_template('index.html', subj_list=subj_list, records=courses, dRes=dRes)
    if sectionIdD.isnumeric() == False:
        dRes = "Put correct section ID"
        return render_template('index.html', subj_list=subj_list, records=courses, dRes=dRes)
    termPattern = re.compile(r'^20..-[fa, sp, su, wt]')
    if re.match(termPattern, termD) == None:
        dRes = "Put correct term (20xx-yy, yy = sp, fa, etc.)"
        return render_template('index.html', subj_list=subj_list, records=courses, dRes=dRes)
    if gradeD not in ['A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W']:
        dRes = "Put correct grade ('A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','W')"
        return render_template('index.html', subj_list=subj_list, records=courses, dRes=dRes)
    res = db.decrement_section(subjectD, courseNumberD, sectionIdD, termD, gradeD)
    if res == 1:
        dRes = "Successfully decremented grade"
    elif res == -1:
        dRes = "Such section does not exist. Change sectionId"
    else:
        dRes = "Such course does not exist. Change subject or course number"
    
    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']

    return render_template('index.html', subj_list=subj_list, records=courses, dRes=dRes)

@app.route('/addProf', methods=['POST'])
def addProf():
    firstName = request.form['profFN']
    lastName = request.form['profLN']
    db.add_professor(firstName, lastName)
    apRes = "Professor successfully added"
    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']
    return render_template('index.html', subj_list=subj_list, apRes=apRes)

@app.route('/deleteProf', methods=['POST'])
def deleteProf():
    firstName = request.form['profFND']
    lastName = request.form['profLND']
    db.delete_professor(firstName, lastName)
    dpRes = "Professor Successfully Deleted"

    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']
    return render_template('index.html', subj_list=subj_list, dpRes=dpRes)

@app.route('/changeProf', methods=['POST'])
def changeProf():
    newFirstName = request.form['newProfF']
    newLastName = request.form['newProfL']
    oldFirstName = request.form['oldProfF']
    oldLastName = request.form['oldProfL']
    sectionId = request.form['changeSecId']
    if sectionId.isnumeric() == False:
        cpRes = "Put Correct Section ID"
        return render_template('index.html', subj_list=subj_list, cpRes=cpRes)
    db.change_professor(newFirstName, newLastName, oldFirstName, oldLastName, sectionId)
    cpRes = "Completed"
    return render_template('index.html', subj_list=subj_list, cpRes=cpRes)


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


@app.route('/add', methods=['POST'])
def add():
    term = request.form['termA']
    subject = request.form['subjectA']
    courseNumber = request.form['courseNumberA']
    instructor = request.form['instructorA']
    grade = request.form['gradeA']

    print(subject + " " + courseNumber + " " + term + " " + instructor + " " + grade)

    mdb.students.update_one({"studentEmail": auth.current_user['email']}, {"$addToSet": { "courses": {"courseNumber": float(courseNumber), "departmentCode": str(subject), "grade": str(grade), "professorName": str(instructor), "term": str(term)}}})
    
    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']
    return render_template('index.html', subj_list=subj_list, records=courses)

  
from flask import render_template, url_for, request, redirect, flash
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
import numpy as np

app.secret_key = "very secret"

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

term_frequencies, num_courses = db.build_term_frequencies()

grades = {'A+' : 4.00, 'A' : 4.00, 'A-' : 3.67,
'B+' : 3.33, 'B' : 3.00, 'B-' : 2.67,
'C+' : 2.33, 'C' : 2.00, 'C-' : 1.67,
'D+' : 1.33, 'D' : 1.00, 'D-' : 0.67,
'F' : 0}

subj_list = db.build_subject_list()

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
    sel_subj = request.form.get('sel_subj')
    CRNs = db.get_CRNs(sel_subj)

    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    academic_history = student['courses']

    if 'sel_CRN' not in request.form:
        return render_template('index.html', subj_list=subj_list, records=courses, CRNs=CRNs)
    elif 'sel_CRN' in request.form:
        try:
            selected_CRN = request.form.get('sel_CRN')
            selected_average = db.get_grade(sel_subj, selected_CRN)
            selected_description = db.get_description(sel_subj, selected_CRN)
            selected_description_word_frequencies = db.build_individual_document_frequency(selected_description)
            total_difference = 0
            num_courses = 0
            total_similarity = 0
            if selected_average == 0:
                total_gpa_points = 0
                num_courses = 0
                for course in academic_history:
                    if course['grade'] != 'W':
                        num_courses += 1
                        total_gpa_points += grade_to_gpa(course['grade'])
                if num_courses == 0:
                    projected_gpa = 2.0
                else:
                    projected_gpa = total_gpa_points / num_courses
            else:
                for course in academic_history:
                    course_description = db.get_description(course['departmentCode'], int(course['courseNumber']))
                    course_average = db.get_grade(course['departmentCode'], int(course['courseNumber']))
                    if course_description != None and course['grade'] != 'W':
                        course_description_word_frequencies = db.build_individual_document_frequency(course_description)
                        total_difference += (grade_to_gpa(course['grade']) - course_average) * get_similarity(selected_description_word_frequencies, course_description_word_frequencies)**2
                        total_similarity += get_similarity(selected_description_word_frequencies, course_description_word_frequencies)**2
                    num_courses += 1
                if num_courses == 0 or total_similarity == 0:
                    projected_gpa = selected_average
                else:
                    projected_gpa = selected_average + total_difference / total_similarity
            return render_template('index.html', subj_list=subj_list, records=academic_history, CRNs=CRNs, sel_subj=sel_subj, sel_CRN=selected_CRN, grade=predicted_gpa_to_letter_grade(projected_gpa))
        except TypeError:
            return render_template('index.html', subj_list=subj_list, records=academic_history, CRNs=CRNs, sel_subj=sel_subj)
    return render_template('index.html', subj_list=subj_list, records=academic_history, CRNs=CRNs, sel_subj=sel_subj)

@app.route('/read', methods=['POST', 'GET'])
def read():
    sel_subj = request.form.get('sel_subj')
    CRNs = db.get_CRNs(sel_subj)
    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']

    if 'sel_CRN' not in request.form:
        return render_template('index.html', subj_list=subj_list, records=courses, CRNs=CRNs, sel_subj=sel_subj)
    elif 'sel_CRN' in request.form:
        try:
            sel_CRN = request.form.get('sel_CRN')
            sectionInfos = db.get_sectionInfos(sel_subj, sel_CRN)
            sections = []
            for section in sectionInfos:
                section_list = list(section)
                print(section_list)
                section_list[0], section_list[1] = section_list[1], section_list[0]
                section_list[1] = section_list[-2] + " " + section_list[-1]
                section_list.pop(-1)
                section_list.pop(-1)
                sections.append(tuple(section_list))

            sections = tuple(sections)
            # print(type(selected_CRN), file=sys.stderr)
            return render_template('index.html', subj_list=subj_list, records=courses, CRNs=CRNs, sel_subj=sel_subj, sel_CRN=sel_CRN, sectionInfos=sections)
        except TypeError:
            return render_template('index.html', subj_list=subj_list, records=courses, CRNs=CRNs, sel_subj=sel_subj)
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
    subjects = db.get_subjects()
    term = request.form['termA']
    subject = request.form['sel_subj']
    courseNumber = request.form['courseNumberA']
    instructor = request.form['instructorA']
    grade = request.form['gradeA']

    print(subject + " " + courseNumber + " " + term + " " + instructor + " " + grade)

    existing = mdb.students.find({"studentEmail": auth.current_user['email'], "courses": {"$elemMatch": {"courseNumber": float(courseNumber), "departmentCode": str(subject), "term": str(term)}}})

    if len(list(existing)) == 0:
        mdb.students.update_one({"studentEmail": auth.current_user['email']}, {"$addToSet": { "courses": {"courseNumber": float(courseNumber), "departmentCode": str(subject), "grade": str(grade), "professorName": str(instructor), "term": str(term)}}})
    else:
        flash("Error: Course already exists")

    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']

    return redirect("/")

@app.route('/remove', methods=['POST'])
def remove():
    subjects = db.get_subjects()
    term = request.form['termA']
    subject = request.form['sel_subj']
    courseNumber = request.form['courseNumberA']

    mdb.students.update_one({"studentEmail": auth.current_user['email']}, {"$pull": { "courses": {"courseNumber": float(courseNumber), "departmentCode": str(subject), "term": str(term)}}})

    student = mdb.students.find({"studentEmail": auth.current_user['email']})[0]
    courses = student['courses']
    return redirect("/")

def grade_to_gpa(grade):
    return grades[grade]

def predicted_gpa_to_letter_grade(predicted_gpa):
    closest_grade = 'A+'
    closest_distance = abs(grades['A+'] + 0.33 - predicted_gpa)
    for grade in grades.keys():
        if grade == 'A+':
            continue
        elif abs(grades[grade] - predicted_gpa) < closest_distance:
            closest_grade = grade
            closest_distance = abs(grades[grade] - predicted_gpa)
    return closest_grade

def get_similarity(course1, course2):
    similarity = 0
    for word in course1:
        if word in course2:
            similarity += (1 + np.log2(course1[word] * course2[word])) * np.log2((num_courses + 1) / term_frequencies[word])
    return similarity

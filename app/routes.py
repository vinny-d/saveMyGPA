from flask import render_template, url_for, request
import sys
import re
from app import app
from app import rds_db as db

@app.route('/')
@app.route('/index')
def index():
    subjects = db.get_subjects()
    return render_template('index.html', subjects=subjects)

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

@app.route('/addProf', methods=['POST', 'GET'])
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

@app.route('/deleteProf', methods=['POST', 'GET'])
def deleteProf():
    subjects = db.get_subjects()
    firstName = request.form['profFND']
    lastName = request.form['profLND']
    if firstName.isalpha() == False or lastName.isalpha() == False:
        dpRes = "Put correct name"
        return render_template('index.html', subjects=subjects, dpRes=dpRes)
    db.delete_professor(firstName, lastName)
    dpRes = "Professor successfully added"
    return render_template('index.html', subjects=subjects, dpRes=dpRes)
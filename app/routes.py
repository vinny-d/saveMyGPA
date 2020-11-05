from flask import render_template, url_for, request
import sys
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
        # print(type(selected_CRN), file=sys.stderr)
        return render_template('index.html', subjects=subjects, CRNs=CRNs, selected_subject=selected_subject, selected_CRN=selected_CRN, grade=grade)
    else:
        return None
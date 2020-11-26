import pymysql
import pyrebase
import sys

conn = pymysql.connect(
    host = 'savemygpa.coi7sdcjbaeb.us-east-1.rds.amazonaws.com',
    port = 3306,
    user = 'admin',
    password = 'ForTeam107',
    db = 'savemygpa',
)

firebaseConfig = {
    "apiKey": "AIzaSyAcxxRO8Sqf7m8F9NkUI6-9MPdWrZkYgGs",
    "authDomain": "savemygpa-7912d.firebaseapp.com",
    "databaseURL": "https://savemygpa-7912d.firebaseio.com",
    "projectId": "savemygpa-7912d",
    "storageBucket": "savemygpa-7912d.appspot.com",
    "messagingSenderId": "781502539376",
    "appId": "1:781502539376:web:7618817f841ef51f9b36b5"
}

def get_subjects():
    cur = conn.cursor()
    cur.execute("select departmentCode from Course")
    details = cur.fetchall()
    details = sorted(set(details))
    subjects = []
    for subject_tuple in details:
        subjects.append(subject_tuple[0])
    return subjects

def get_CRNs(deptCode):
    cur = conn.cursor()
    cur.execute("select courseNumber from Course where departmentCode = %s", deptCode)
    details = cur.fetchall()
    CRNs = []
    for CRN_tuple in details:
        CRNs.append(str(CRN_tuple[0]))
    return CRNs

def get_grade(deptCode, CRN):
    cur = conn.cursor()
    cur.execute("select courseId from Course where departmentCode = %s and courseNumber = %s", (deptCode, CRN))
    details = cur.fetchall()
    if len(details) == 0:
        return 0.0
    # print(details, file=sys.stderr)
    cur.execute("select * from Section where courseId = %s", details[0][0])
    details = cur.fetchall()
    avg_grade = 0.0
    num_total = 0
    for section in details:
        avg_grade += section[4] * 4.0 # A
        avg_grade += section[5] * 3.67 # A-
        avg_grade += section[6] * 3.33 # B+
        avg_grade += section[7] * 3.0 # B
        avg_grade += section[8] * 2.67 # B-
        avg_grade += section[9] * 2.33 # C+
        avg_grade += section[10] * 2.0 # C
        avg_grade += section[11] * 1.67 # C-
        avg_grade += section[12] * 1.33 # D+
        avg_grade += section[13] * 1.0 # D
        avg_grade += section[14] * .67 # D-
        for i in range(4,16):
             num_total += section[i]
    if num_total:
        avg_grade = round(avg_grade / num_total, 2)
    return avg_grade

def get_sectionInfos(deptCode, CRN):
    cur = conn.cursor()
    cur.execute("select courseId from Course where departmentCode = %s and courseNumber = %s", (deptCode, CRN))
    details = cur.fetchall()
    if len(details) == 0:
        return None
    # print(details, file=sys.stderr)
    cur.execute("select * from Section where courseId = %s", details[0][0])
    sectionInfos = cur.fetchall()
    return sectionInfos

def increment_section(subject, courseNumber, sectionId, term, grade):
    cur = conn.cursor()
    cur.execute("select courseId from Course where departmentCode = %s and courseNumber = %s", (subject, courseNumber))
    details = cur.fetchall()
    if len(details) == 0:
        return 0
    cur.execute("select courseId, professorId from Section where courseId = %s and sectionId = %s and term = %s", (details[0][0], sectionId, term))
    secDetails = cur.fetchall()
    if len(secDetails) == 0:
        return -1
    else:
        gradeStr = grade.replace('-', 'Minus')
        gradeStr = gradeStr.replace('+', 'Plus')
        gradeStr = 'Grade' + gradeStr
        cur.execute("update Section set {} = {} + 1 where courseId = %s and professorId = %s and sectionId = %s and term = %s".format(gradeStr, gradeStr),(secDetails[0][0], secDetails[0][1], sectionId, term))
        conn.commit()
    return 1

def decrement_section(subject, courseNumber, sectionId, term, grade):
    cur = conn.cursor()
    cur.execute("select courseId from Course where departmentCode = %s and courseNumber = %s", (subject, courseNumber))
    details = cur.fetchall()
    if len(details) == 0:
        return 0
    cur.execute("select courseId, professorId from Section where courseId = %s and sectionId = %s and term = %s", (details[0][0], sectionId, term))
    secDetails = cur.fetchall()
    if len(secDetails) == 0:
        return -1
    else:
        gradeStr = grade.replace('-', 'Minus')
        gradeStr = gradeStr.replace('+', 'Plus')
        gradeStr = 'Grade' + gradeStr
        cur.execute("update Section set {} = {} - 1 where courseId = %s and professorId = %s and sectionId = %s and term = %s".format(gradeStr, gradeStr),(secDetails[0][0], secDetails[0][1], sectionId, term))
        conn.commit()
    return 1

def add_professor(firstName, lastName):
    cur = conn.cursor()
    cur.execute("insert into Professor (firstName, lastName) values (%s, %s)", (firstName, lastName))
    conn.commit()

def delete_professor(firstName, lastName):
    cur = conn.cursor()
    cur.execute("delete from Professor where firstName = %s and lastName = %s", (firstName, lastName))
    conn.commit()

def access_data():
    cur = conn.cursor()
    cur.execute("describe Section")
    details = cur.fetchall()
    return details

def check_professor():
    cur = conn.cursor()
    cur.execute("select * from Professor where firstName = 'Steven' and lastName = 'Pan'")
    details = cur.fetchall()
    return details

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
# newuser = auth.create_user_with_email_and_password('gchoi17@illinois.edu', 'Team107')
user = auth.sign_in_with_email_and_password('gchoi17@illinois.edu', 'Team107')

# print(get_subjects())
# get_subjects()
# print(access_data())
# print(get_CRNs('IS'))
# get_grade('ECE', 110)
# print(check_professor())
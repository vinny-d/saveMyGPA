import pandas as pd
import mysql.connector

df = pd.read_csv("uiuc-gpa-dataset.csv").dropna()

host = 'savemygpa.coi7sdcjbaeb.us-east-1.rds.amazonaws.com'
user = 'admin'
password = 'ForTeam107'
db = 'savemygpa'

connection = mysql.connector.connect(host=host, user=user, password=password, database=db)
cursor = connection.cursor()

print("Connected")

for index, row in df.iterrows():
    if row['YearTerm'] == '2019-fa':
        ## Populate the "Section" table ##
        course_query = "SELECT courseId FROM Course WHERE departmentCode = %s AND courseNumber = %s"
        cursor.execute(course_query, (row['Subject'], row['Number']))

        course_id = 0

        for course in cursor:
            course_id = course[0]

        names = row['Primary Instructor'].split(', ')
        last_name = names[0]
        first_name = names[1]

        course_query = "SELECT professorId FROM Professor WHERE firstName = %s AND lastName = %s"
        cursor.execute(course_query, (first_name, last_name))

        professor_id = 0

        for professor in cursor:
            professor_id = professor[0]

        sql = "INSERT INTO Section(courseId, professorId, term, GradeA, GradeAMinus, GradeBPlus, GradeB, GradeBMinus," \
              " GradeCPlus, GradeC, GradeCMinus, GradeDPlus, GradeD, GradeDMinus, GradeF, GradeW) VALUES(%s, %s, %s, " \
             "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        cursor.execute(sql, (course_id, professor_id, row['YearTerm'], row['A+'] + row['A'], row['A-'], row['B+'], row['B'], row['B-'], row['C+'], row['C'], row['C-'], row['D+'], row['D'], row['D-'], row['F'], row['W']))

        ## Populate the "Course" table ##
        course_name = row['Course Title']
        course_subject = row['Subject']
        course_number = row['Number']

        sql = "INSERT IGNORE INTO Course(courseName, courseSubject, courseNumber) VALUES(%s, %s, %s)"
        cursor.execute(sql, (course_name, course_subject, course_number))
    else:
        break

connection.commit()

cursor.close()
connection.close()

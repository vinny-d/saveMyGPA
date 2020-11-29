import pandas as pd
import mysql.connector

df = pd.read_csv("fa2019Courses.csv").dropna()

host = 'savemygpa.coi7sdcjbaeb.us-east-1.rds.amazonaws.com'
user = 'admin'
password = 'ForTeam107'
db = 'savemygpa'

connection = mysql.connector.connect(host=host, user=user, password=password, database=db)
cursor = connection.cursor()

print("Connected")

for index, row in df.iterrows():
    ## Insert the description field
    sql = "UPDATE Course SET description = %s WHERE departmentCode = %s AND courseNumber = %s"
    cursor.execute(sql, (row['description'], row['deptCode'], row['courseNum']))

connection.commit()

cursor.close()
connection.close()

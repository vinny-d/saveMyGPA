import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd

# helper functin to get individual course website data, and return in dictionary form
def getCourseInfo(url) :
    courseReq = requests.get(url)
    courseSoup = BeautifulSoup(courseReq.text, 'html.parser')
    courseFullID = courseSoup.find(class_ = "app-inline")
    deptCode = courseFullID.next_element.split()[0]
    courseNum = courseFullID.next_element.split()[1]
    
    print (deptCode + ' ' + courseNum + '\n')

    descriptionStep = courseSoup.find(class_ = "col-sm-12")

    description =  descriptionStep.find_all('p')[1].next_element
    # conditional for "same as <deptcode> <courseNum>"
    if str(description).isspace() :
        description = descriptionStep.find_all('p')[2].next_element
        for link in descriptionStep.find_all('p')[2].find_all('a') :
            description += link.next_element
            description += link.next_element.next_element
    elif str(description)[0] == '<' :
        description =  descriptionStep.find_all('p')[1].next_element.next_element
        i = 0
        for link in descriptionStep.find_all('p')[1].find_all('a') :
            if i != 0 :
                description += link.next_element
            description += link.next_element.next_element
            i += 1
    
    # conditional for "continutation of ___ "
    else : #str(description).split()[0] == 'Continuation' : 
        description = descriptionStep.find_all('p')[1].next_element
        for link in descriptionStep.find_all('p')[1].find_all('a') :
            description += str(link.next_element)
            description += link.next_element.next_element


    courseInfo = {'deptCode' : deptCode, 'courseNum' : courseNum, 'description' : description}

    return courseInfo



def generateCSV() :
    # fall link, we gonna go from big picture to small to loading csv.
    fall2019 = 'https://courses.illinois.edu/schedule/2019/fall/'
    baseURL = 'https://courses.illinois.edu'

    r = requests.get(fall2019)
    soup = BeautifulSoup(r.text, 'html.parser')

    departmentTable = soup.find('table', class_ = 'table table-striped table-bordered table-condensed')

    deptLinks = []

    for link in departmentTable.find_all('a') :
        # print(link)
        deptLinks.append(link.get('href'))

    i = 0
    while i < len(deptLinks) :
        deptLinks[i] = baseURL + deptLinks[i]
        i += 1

    # now we have a list of links to all the department pages, links stored in deptLinks
    # these pages hold the links to all of the department courses
    # we now repeat a similar process, this time on each dept page
    # for each dept page, we get a list of course links, and for each course link we run a function to return 
    # dictionary key (ex . {'DeptCode' : 'CS', 'CourseNum' : '225', 'Description' : 'some nerd stuff'})
    courseLinks = []
    finalDicts = []
    for link in deptLinks :
        r2 = requests.get(link)
        deptSoup = BeautifulSoup(r2.text, 'html.parser')
        courseTable = deptSoup.find('table', class_ = 'table table-striped table-bordered table-condensed')
        for link in courseTable.find_all('a') :
            courseURL = baseURL + link.get('href')
            courseLinks.append(courseURL)
            finalDicts.append(getCourseInfo(courseURL))

    df = pd.DataFrame(finalDicts)
    df.to_csv('REALfall2019Courses.csv')

    print ('saved to file')
    # data = getCourseInfo('https://courses.illinois.edu/schedule/2019/fall/AFRO/243')
    #print (data)

# testURL = 'https://courses.illinois.edu/schedule/2019/fall/ECE/205'
# print(getCourseInfo(testURL))

generateCSV()

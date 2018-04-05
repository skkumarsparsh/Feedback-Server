from flask import Flask,request,Response
import json
import sqlite3

app = Flask(__name__)

@app.route('/teachers',methods = ['POST'])
def get_teachers():
    with open('data.json', 'r') as f:
        data = json.load(f)
    resp = Response(json.dumps(data))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/get-s3t',methods = ['POST'])
def get_stuff():
    with open('data.json', 'r') as f:
        data = json.load(f)
    semesters = []
    sections = {}
    teachers = []
    subjects = {}
    for t in data:
        semesters.append(t)
        tp = []
        d = data[t]
        for temp in d:
            tp.append(temp)
        sections[t] = tp
    for temp in sections:
        for s in sections[temp]:
            d = data[temp][s]
            for t in d:
                if t not in teachers:
                    teachers.append(t)
    for tea in teachers:
        xyz = []
        for temp in sections:
            for s in sections[temp]:
                d = data[temp][s]
                for t in d:
                    if tea == t:
                        if d[t] not in xyz:
                            xyz.append(d[t])
        subjects[tea] = xyz
    resp = {}
    print(subjects)
    resp["semesters"] = semesters
    resp["sections"] = sections
    resp["teachers"] = teachers
    resp["subjects"] = subjects
    resp = Response(json.dumps(resp))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/response',methods = ['POST'])
def responses():
    data = json.loads(request.get_data());
    resp = Response(json.dumps(data))
    subjects = data['subjects']
    usn = data['usn']
    i = 0;
    z = [];
    for key, value in data.items():
        if not(key == 'subjects' or key == 'usn'):
            print(key, len(value), subjects[i])
            z.append([str(key),str(subjects[i]),int(value[0]),int(value[1]),int(value[2]),int(value[3]),int(value[4]),int(value[5]),int(value[6]),int(value[7]),int(value[8]),int(value[9]),int(value[10]),int(value[11])])
            i = i + 1;
    conn = sqlite3.connect('responses.db');
    c = conn.cursor()
    c.execute('CREATE table if not exists Responses(TeacherName varchar(50), Subject varchar(50), Q1 integer, Q2 integer, Q3 integer, Q4 integer, Q5 integer, Q6 integer, Q7 integer, Q8 integer, Q9 integer, Q10 integer, Q11 integer, Q12 integer)')
    c.executemany("INSERT into Responses (TeacherName, Subject, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", z);
    conn.commit()
    conn.close()

    # adding the usn of the student (into the database) that has completed the feedback
    conn = sqlite3.connect('usn_done_feedback.db')
    c = conn.cursor()
    c.execute('CREATE table if not exists usn(u varchar(10))')
    c.execute("INSERT into usn values('" + usn + "')")
    conn.commit()
    conn.close()
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/check',methods = ['POST'])
def usn_check():
    conn = sqlite3.connect('usn_done_feedback.db')
    c = conn.cursor()
    c.execute('CREATE table if not exists usn(u varchar(10))')
    content = json.loads(request.get_data())
    print(content)
    c.execute("SELECT * from usn where u = '" + content['usn'] + "'")
    data = c.fetchone()
    if data is None:
        resp = Response(json.dumps({'allowed': True}))
    else:
        resp = Response(json.dumps({'allowed': False}))
    conn.commit()
    conn.close()
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == '__main__':
   app.run("0.0.0.0", 8080)
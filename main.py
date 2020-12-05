from flask import Flask, render_template, request, redirect, url_for, g, session
from markupsafe import escape
import logging
from logging import FileHandler
import os
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def sql_query_connection_select(sqlstr):
    try:
        conn = sqlite3.connect('main.db')
        cursor = conn.execute(sqlstr)
        ret = cursor.fetchall()
        if len(ret) == 0:
            print('None value has been returned')
            # TODO if time institute a logger here
            return ret
        else:
            return ret
    except:
        print('an error has occurred')
        # TODO if time institute a logger here
    return None


def sql_query_connection_insert(sqlstr):
    try:
        conn = sqlite3.connect('main.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sqlstr)
        conn.commit()
        conn.close()
    except:
        print('an error has occurred')
        # TODO if time institute a logger here
    return None


def edit_workorder(sessioninfo):
    sqlstr = 'SELECT * FROM machine WHERE machine_location = {}'.format("'" + sessioninfo['machine_location'] + "'")
    sqlreturn = sql_query_connection_select(sqlstr)
    if len(sqlreturn) is 0:
        print('Game does not exist, Please try again')
        return redirect(url_for('workorder_confirm_edit', closeorder=False, confirmedit=True,workorderid=sessioninfo['workorder_id'],
                               error='Game does not exist, Please try again.'))
    else:
        if sessioninfo['part_id'] is not '':
            sqlstr = 'SELECT * FROM part WHERE part_id = {}'.format("'" + str(sessioninfo["part_id"]) + "'")
            sqlreturn = sql_query_connection_select(sqlstr)
            if len(sqlreturn) is None:
                return redirect(url_for('workorder_confirm_edit', closeorder=False, confirmedit=True,
                                        workorderid=sessioninfo['workorder_id'],
                                        error='Invalid part number, Please try again.'))
            else:
                sqlstr = "UPDATE workorder SET workorder_description = {}, machine_location = {},part_id = {} WHERE  \
                         workorder_id = {}" .format(
                    "'" + sessioninfo['workorder_description'] + "'",
                    "'" + sessioninfo['machine_location'] + "'",
                    "'" + str(sessioninfo['part_id']) + "'",
                    "'" + str(sessioninfo['workorder_id']) + "'")
                a = sql_query_connection_insert(sqlstr)
                print(a)
                successmsg = 'Successful workorder edit!'
                return render_template("workorder_final_edit.html", confirmedit=True,workorderid=sessioninfo['workorder_id'],success=successmsg)


@app.route('/', methods=['GET'])
def index():
    if len(session) == 0:
        return redirect(url_for('login'))
    elif session['username'] == 'root':
        return render_template("dashboard.html", session_user=session['username'])
    else:
        return render_template("dashboard.html", session_user=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'GET':
        return render_template('login.html', error=error)
    if request.method == 'POST':
        username = "'" + request.form['username'] + "'"
        password = "'" + request.form['password'] + "'"
        # TODO : perhaps a more secure string
        sqlstr = "SELECT tech_id, tech_name FROM tech WHERE tech_name = {} AND tech_password = {}".format(username,
                                                                                                          password)
        sqlreturn = sql_query_connection_select(sqlstr)
        # Todo: better if statement
        if len(sqlreturn) == 0:
            return render_template('login.html', error='Invalid Username or Password, please try again!')
        else:
            session['uid'] = sqlreturn[0][0]
            session['username'] = sqlreturn[0][1]
            return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return 'you have been logged out'


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template("dashboard.html")


@app.route('/workorder/add', methods=['GET', 'POST'])
def workorder_add():
    if request.method == 'POST':
        if request.form.get("Return"):
            return redirect(url_for('index'))
        else:
            pass
    if request.method == 'POST':
        req = request.form
        if req["location"] is '' or req["problem"] is '':
            print('Invalid blank item, please try again')
            return render_template("workorder.html", neworder=True, editorder=False,
                                   error='Invalid blank item, please try again.')
        else:
            pass
        sqlstr = 'SELECT * FROM machine WHERE machine_location = {}'.format("'" + req["location"] + "'")
        sqlreturn = sql_query_connection_select(sqlstr)
        if len(sqlreturn) is 0:
            print('Game does not exist, Please try again')
            return render_template("workorder.html", neworder=True, editorder=False,
                                   error='Game does not exist, Please try again.')
        else:
            pass
        if req["part_needed_text"] is not '':
            sqlstr = 'SELECT * FROM part WHERE part_id = {}'.format("'" + req["part_needed_text"] + "'")
            sqlreturn = sql_query_connection_select(sqlstr)
            if len(sqlreturn) is None:
                return render_template("workorder.html", neworder=True, editorder=False,
                                       error='Invalid part number, Please try again.')
            else:
                pass
        sqlstr = "SELECT workorder_id FROM workorder WHERE workorder_id=(SELECT max(workorder_id) FROM workorder)"
        int_workorder_id = sql_query_connection_select(sqlstr)[0][0]
        sqlstr = "INSERT INTO workorder(workorder_id,workorder_description,machine_location,part_id) VALUES({}, " \
                 "{}, {}, {})".format(
            int_workorder_id + 1,
            "'" + req["problem"] + "'",
            "'" + req["location"] + "'",
            "'" + req["part_needed_text"] + "'")
        sql_query_connection_insert(sqlstr)
        try:
            sqlstr = "SELECT workorder_id FROM workorder WHERE workorder_id=(SELECT max(workorder_id) FROM workorder)"
            int_workorder_id = sql_query_connection_select(sqlstr)[0][0]
            successmsg = 'Successful workorder creation! Workorder ID {} created!'.format(int_workorder_id)
            return render_template("workorder.html", neworder=True, editorder=False, success=successmsg)
        except:
            print('an error has occurred')
    return render_template("workorder.html", neworder=True, editorder=False)


@app.route('/workorder/edit', methods=['GET', 'POST'])
def workorder_lookup():
    if request.method == 'POST':
        req = request.form
        sqlstr = 'SELECT * FROM workorder WHERE workorder_id = {}'.format("'" + req["WorkorderID"] + "'")
        sqlreturn = sql_query_connection_select(sqlstr)
        if len(sqlreturn) is 0:
            # TODO: logger
            print('Workorder ID does not exist, try again.')
            return render_template("workorder.html", neworder=False, editorder=True, lookuporder=True,
                                   error='Workorder ID does not exist, try again.')
        else:
            keys = ('workorder_id', 'workorder_description', 'machine_location', 'part_id', 'status')
            session['sqlreturndict'] = dict(zip(keys, sqlreturn[0]))
            return redirect(url_for('workorder_editor', workorderid=session['sqlreturndict']['workorder_id']))
    return render_template("workorder.html", neworder=False, editorder=True, lookuporder=True)


@app.route('/workorder/edit/<workorderid>', methods=['GET', 'POST'])
def workorder_editor(workorderid):
    workorderid = session['sqlreturndict']['workorder_id']
    if request.method == 'POST':
        if request.form.get("Return"):
            return redirect(url_for('index'))
        else:
            pass
        if request.form.get("closeorder"):
            return redirect(url_for('workorder_close', workorderid=workorderid))
        else:
            pass
        if request.form.get('Submit'):
            req = request.form
            print(req[0]['location'])
            if req["location"] is '' or req["problem"] is '':
                print('Invalid blank item, please try again')
                return render_template("workorder.html", neworder=True, editorder=False,
                                       error='Invalid blank item, please try again.')
            keys = ('workorder_id', 'workorder_description', 'machine_location', 'part_id', 'status')
            values=(workorderid, req[0]['location'])
            session['sqlreturndict'] = dict(zip(keys, sqlreturn[0]))
            return redirect(url_for('workorder_confirm_edit', closeorder=False, confirmedit=True,workorderid=workorderid))
        else:
            pass
    if session['sqlreturndict']['part_id'] == '':
        return render_template("workorder_final_edit.html", editorder=True)
    else:
        return render_template("workorder_final_edit.html", partadded=True , editorder=True)


@app.route('/workorder/edit/<workorderid>/close', methods=['GET', 'POST'])
def workorder_close(workorderid):
    if request.method == 'POST':
        print(request.form)
        if request.form.get("Submit"):
            pass
    else:
        pass
    if request.form.get("Return"):
        return redirect(url_for('index'))
    else:
        pass
    if request.method == 'GET':
        if session['sqlreturndict']['part_id'] == '':
            return render_template("workorder_final_edit.html", closeorder=True,workorderid=workorderid)
        else:
            return render_template("workorder_final_edit.html", partadded=True, closeorder=True,workorderid=workorderid)


@app.route('/workorder/edit/<workorderid>/confirm', methods=['GET', 'POST'])
def workorder_confirm_edit(workorderid):
    """print(session['sqlreturndict']) print("'" + session['sqlreturndict']['machine_location'] + "'")"""
    if request.method == 'POST':
        if request.form.get('Submit'):
            sessioninfo = session['sqlreturndict']

            sqlstr = 'SELECT * FROM machine WHERE machine_location = {}'.format(
                "'" + sessioninfo['machine_location'] + "'")
            sqlreturn = sql_query_connection_select(sqlstr)
            if len(sqlreturn) is 0:
                print('Game does not exist, Please try again')
                return redirect(url_for('workorder_confirm_edit', closeorder=False, confirmedit=True,
                                        workorderid=sessioninfo['workorder_id'],
                                        error='Game does not exist, Please try again.'))
            else:
                if sessioninfo['part_id'] is not '':
                    sqlstr = 'SELECT * FROM part WHERE part_id = {}'.format("'" + str(sessioninfo["part_id"]) + "'")
                    sqlreturn = sql_query_connection_select(sqlstr)
                    if len(sqlreturn) is None:
                        return redirect(url_for('workorder_confirm_edit', closeorder=False, confirmedit=True,
                                                workorderid=sessioninfo['workorder_id'],
                                                error='Invalid part number, Please try again.'))
                    else:
                        sqlstr = "UPDATE workorder SET workorder_description = {}, machine_location = {},part_id = {} WHERE  \
                                 workorder_id = {}".format(
                            "'" + sessioninfo['workorder_description'] + "'",
                            "'" + sessioninfo['machine_location'] + "'",
                            "'" + str(sessioninfo['part_id']) + "'",
                            "'" + str(sessioninfo['workorder_id']) + "'")
                        a = sql_query_connection_insert(sqlstr)
                        print(a)
                        successmsg = 'Successful workorder edit!'
                        return render_template("workorder_final_edit.html", confirmedit=True,
                                               workorderid=sessioninfo['workorder_id'], success=successmsg)
        else:
            pass
        if request.form.get('Return'):
            return redirect(url_for('index'))
        else:
            pass
    else:
        if session['sqlreturndict']['part_id'] == '':
            return render_template("workorder_final_edit.html",confirmedit=True,workorderid=workorderid)
        else:
            return render_template("workorder_final_edit.html", partadded=True,confirmedit=True,workorderid=workorderid)


@app.route('/parts', methods=['GET', 'POST'])
def parts():
    pass




"""
@app.route('/student/add', methods=['GET', 'POST'])
def add():
    con = sqlite3.connect('main.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT student_id FROM student WHERE student_id=(SELECT max(student_id) FROM student)")
    sid = [dict(id=row[0]) for row in cur.fetchall()][0]["id"] + 1
    con.close()
    if request.method == 'POST':
        if request.form['student_name'] is not None:
            try:
                student_name = request.form['student_name']
                student_name = student_name.split(' ')
                sfn, sln = '"' + student_name[0].strip() + '"', '"' + student_name[1].strip() + '"'
                con = sqlite3.connect('main.db')
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO student (student_id, student_first_name, student_last_name) VALUES ({}, {}, {})".format(
                        sid, sfn, sln))
                con.commit()
                con.close()
                return redirect('/dashboard')
                return redirect('/dashboard')
            except:
                error = 'Invalid Name. Please try again.'
                return render_template('OLDstudentadd.html', error=error)
        else:
            return redirect(url_for('dashboard'))
    else:
        return render_template("OLDstudentadd.html")


@app.route('/quiz/add', methods=['GET', 'POST'])
def quizadd():
    con = sqlite3.connect('main.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT quiz_id FROM quizzes WHERE quiz_id=(SELECT max(quiz_id) FROM quizzes)")
    quiz_id = [dict(id=row[0]) for row in cur.fetchall()][0]["id"] + 1
    con.close()
    if request.method == 'POST':
        if request.form['quiz_subject'] is not None:
            try:
                subject = '"' + request.form['quiz_subject'].strip() + '"'
                q_amt = request.form['quiz_question_amount'].strip()
                q_date = request.form['quiz_date'].strip()
                q_date = '"' + datetime.datetime.strptime(q_date, '%Y-%m-%d').strftime('%B %d,%Y') + '"'
                q_date = q_date
                print('quiz_id {}, subject {}, q_amt {} q_date {}'.format(quiz_id, subject, q_amt, q_date))
                con = sqlite3.connect('main.db')
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO quizzes (quiz_id, quiz_subject, quiz_question_amount, quiz_date) VALUES ({}, {}, {}, {})".format(
                        quiz_id, subject, q_amt, q_date))
                con.commit()
                con.close()
                return redirect('/dashboard')
            except:
                error = 'Invalid Name. Please try again.'
                return render_template('OLDquizadd.html', error=error)
        else:
            return redirect(url_for('dashboard'))
    else:
        return render_template("OLDquizadd.html")


@app.route('/student/<studentid>', methods=['GET', 'POST'])
def studentidpass(studentid=None):
    print(studentid)
    error = 'Error, user not found'
    con = sqlite3.connect('main.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        "SELECT score_id,score_total FROM score WHERE student_id= {}".format(studentid))
    con.commit()
    rowscur = cur.fetchall()
    con.close()

    return render_template("OLDstudentsearch.html", rows=rowscur, error=error)
"""

if __name__ == '__main__':
    app.run(debug=True)

# \/\/\/ Linux
# export FLASK_APP=main.py
# export FLASK_ENV=development
# flask run
# \/\/\/ Windows
# set FLASK_APP=main.py
# set FLASK_ENV=development
# python -m flask run
#
# root abc123
# bob technician abc123

"""def logfile_start():
    file_handler = FileHandler(os.getcwd() + "/log.txt")
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)"""

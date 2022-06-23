from flask import Flask, request, render_template, redirect, session, jsonify
from flask_mysqldb import MySQL
import bcrypt
import re

app = Flask(__name__)
app.secret_key = 'nushmods'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'nushmods'
mysql = MySQL(app)

ROUNDS = 12
REGEX = re.compile(r'h\d{7}')
WEIGHTAGE_REGEX = re.compile(r'^\d{1,2}(\.\d)?$')
NAME_MAX_LENGTH = 50
PW_MIN_LENGTH = 8
PW_MAX_LENGTH = 50
GENDER_LIST = ['M', 'F', 'X']
LEVEL_LIST = [x+1 for x in range(6)]
TYPE_LIST = ['Core', 'Elective', 'Enrichment', 'Honours', 'Other']
ITEM_TYPE_LIST = ['Homework', 'Assignment', 'Event', 'Important', 'Test']

GET_STUDENT_PW = 'SELECT password FROM student WHERE s_id = %s'
GET_TEACHER_PW = 'SELECT password FROM teacher WHERE t_id = %s'
REGISTER = 'INSERT INTO student (s_id, name, password, gender) VALUES (%s, %s, %s, %s)'

GET_STUDENT_NAME = 'SELECT name FROM student WHERE s_id = %s'
GET_ITEMS = """
SELECT i_id, m_code, title, description, CONCAT(date, "") "date", weightage, type
FROM   item i1
       NATURAL JOIN module_item mi
WHERE  TRUE = %s
       AND is_dated = TRUE
       AND title LIKE %s
       AND type IN %s
       AND m_code IN %s
       AND m_code IN (SELECT m_code
                      FROM   takes
                      WHERE  s_id = %s
                      UNION
                      SELECT m_code
                      FROM   teaches
                             NATURAL JOIN offered_module
                      WHERE  t_id = %s
                      UNION
                      SELECT m_code
                      FROM   offered_module
                      WHERE  coord_id = %s
                     )
UNION
SELECT i_id, m_code, title, description, CONCAT(date, "") "date", weightage, type
FROM   item i2
       NATURAL JOIN class_item ci
WHERE  TRUE = %s
       AND is_dated = TRUE
       AND title LIKE %s
       AND type IN %s
       AND m_code IN %s
       AND (m_code, c_name) IN (SELECT m_code, c_name
                                FROM   takes
                                WHERE  s_id = %s
                                UNION
                                SELECT m_code, c_name
                                FROM   teaches
                                WHERE  t_id = %s
                               )
ORDER BY date;
"""
GET_ITEM_BY_CODE = """
SELECT i_id, m_code, title, description, CONCAT(date, ""), weightage, type, "", is_class, name
FROM   item i1
       NATURAL JOIN module_item mi
       NATURAL JOIN offered_module
       LEFT JOIN teacher ON offered_module.coord_id = teacher.t_id
WHERE  is_dated = TRUE
       AND i_id = %s
       AND m_code IN (SELECT m_code
                      FROM   takes
                      WHERE  s_id = %s
                      UNION
                      SELECT m_code
                      FROM   teaches
                             NATURAL JOIN offered_module
                      WHERE  t_id = %s
                      UNION
                      SELECT m_code
                      FROM   offered_module
                      WHERE  coord_id = %s
                     )
UNION
SELECT i_id, m_code, title, description, CONCAT(date, ""), weightage, type,  c_name, is_class, name
FROM   item i2
       NATURAL JOIN class_item ci
       INNER JOIN teacher ON ci.t_id = teacher.t_id
WHERE  is_dated = TRUE
       AND i_id = %s
       AND (m_code, c_name) IN (SELECT m_code, c_name
                                FROM   takes
                                WHERE  s_id = %s
                                UNION
                                SELECT m_code, c_name
                                FROM   teaches
                                WHERE  t_id = %s
                               );
"""
GET_ANNOUNCEMENTS = """
SELECT i_id, m_code, title, description, CONCAT(date, "") "date", priority
FROM   item i1
       NATURAL JOIN module_item mi
WHERE  is_dated = FALSE
       AND m_code IN (SELECT m_code
                      FROM   takes
                      WHERE  s_id = %s
                      UNION
                      SELECT m_code
                      FROM   offered_module
                      WHERE  coord_id = %s
                     )
UNION
SELECT i_id, m_code, title, description, CONCAT(date, "") "date", priority
FROM   item i2
       NATURAL JOIN class_item ci
WHERE  is_dated = FALSE
       AND (m_code, c_name) IN (SELECT m_code, c_name
                                FROM   takes
                                WHERE  s_id = %s
                                UNION
                                SELECT m_code, c_name
                                FROM   teaches
                                WHERE  t_id = %s
                               )
ORDER BY priority DESC, date DESC;
"""

GET_DEPARTMENTS = """
SELECT   d.d_code, d.hod_id, CONCAT(t.prefix, ". ", t.name), d.name, description
FROM     department d
         LEFT JOIN teacher t ON d.hod_id = t.t_id
ORDER BY d.name;
"""

GET_QUERIED_MODULES_1 = """
SELECT   m_code, title, semesters, CONCAT(prefix, ". ", c.name), type
FROM     module AS m
         NATURAL
"""
GET_QUERIED_MODULES_2 = """
         JOIN offered_module
         LEFT JOIN teacher AS c ON coord_id = t_id
         LEFT JOIN department AS d ON m.d_code = d.d_code
WHERE    (m_code LIKE %s OR title LIKE %s)
         AND m.d_code IN %s
         AND type IN %s
ORDER BY m_code;
"""

GET_MODULE_BY_CODE = """
SELECT m_code, title, CONCAT(prefix, ". ", c.name), d.name, type, semesters, mc, hours, m.description, d.d_code, coord_id, (hod_id = %s),
       EXISTS(SELECT *
              FROM   offered_module
              WHERE  m_code = %s
             )
FROM   module AS m
       NATURAL LEFT JOIN offered_module
       LEFT JOIN teacher AS c ON coord_id = t_id
       LEFT JOIN department AS d ON m.d_code = d.d_code
WHERE  m_code = %s;
"""
GET_GUEST_MODULE_BY_CODE = """
SELECT m_code, title, CONCAT(prefix, ". ", c.name), d.name, type, semesters, mc, hours, m.description, d.d_code, coord_id, FALSE,
       EXISTS(SELECT *
              FROM   offered_module
              WHERE  m_code = %s
             )
FROM   module AS m
       NATURAL LEFT JOIN offered_module
       LEFT JOIN teacher AS c ON coord_id = t_id
       LEFT JOIN department AS d ON m.d_code = d.d_code
WHERE  m_code = %s;
"""

GET_DEPARTMENT_BY_CODE = """
SELECT d.name, d.d_code, CONCAT(prefix, ". ", t.name), description, (hod_id = %s)
FROM   department d
       LEFT JOIN teacher t ON d.hod_id = t.t_id
WHERE  d.d_code = %s;
"""
GET_GUEST_DEPARTMENT_BY_CODE = """
SELECT d.name, d.d_code, CONCAT(prefix, ". ", t.name), description, FALSE
FROM   department d
       LEFT JOIN teacher t ON d.hod_id = t.t_id
WHERE  d.d_code = %s;
"""

GET_OFFERED_MODULE_BY_CODE = """
SELECT m_code,
       CONCAT(prefix, ". ", name),
       title,
       overview,
       (coord_id = %s)
FROM   offered_module
       NATURAL JOIN module
       LEFT JOIN teacher ON coord_id = t_id
WHERE  m_code = %s
       AND (coord_id = %s
            OR m_code IN (SELECT DISTINCT m_code
                          FROM   teaches
                          WHERE  t_id = %s
                          UNION
                          SELECT DISTINCT m_code
                          FROM   takes
                          WHERE  s_id = %s
                     )
           );
"""

GET_QUERIED_TEACHERS = """
SELECT   t_id, CONCAT(prefix, ". ", name), email, phone
FROM     teacher
WHERE    d_code IN %s
         AND (t_id LIKE %s
              OR CONCAT(prefix, ". ", name) LIKE %s
             )
ORDER BY t_id;
"""

GET_QUERIED_TEACHERS_SAFE = """
SELECT   d_code, t_id, CONCAT(prefix, ". ", name)
FROM     teacher
WHERE    d_code IN %s
         AND (t_id LIKE %s
              OR CONCAT(prefix, ". ", name) LIKE %s
             )
ORDER BY d_code, t_id;
"""

ITEM_CHECK = """
SELECT t_id
       FROM item
       NATURAL JOIN class_item
WHERE  i_id = %s
       AND (m_code, c_name) IN (SELECT m_code, c_name
                                FROM   teaches
                                WHERE  t_id = %s
                               )
UNION
SELECT coord_id
       FROM item
       NATURAL JOIN module_item
       NATURAL JOIN offered_module
WHERE  i_id = %s
       AND coord_id = %s;
"""

@app.route('/')
def index():
    return render_template('index.html', greeting_1='The ', greeting_2='comprehensive', greeting_3=' NUSH curriculum directory.', logged_in=logged_in())

@app.route('/<name>')
def named_index(name):
    return render_template('index.html', greeting_1='Hello, ', greeting_2=name, logged_in=logged_in())

@app.route('/search')
def search():
    try:
        try:
            cur = mysql.connection.cursor()
            cur.execute(GET_DEPARTMENTS)
            depts = cur.fetchall()
            return render_template('search.html', departments=depts, levels=LEVEL_LIST, types=TYPE_LIST, hod_of=hod_of(), logged_in=logged_in())
        except Exception as e:
            return 'MySQL Error [%d]: %s' % (e.args[0], e.args[1])
    except:
        pass
    return 'There is an error in the system. Please try again later.'

@app.route('/search/teacher')
def search_teacher():
    try:
        try:
            cur = mysql.connection.cursor()
            cur.execute(GET_DEPARTMENTS)
            depts = cur.fetchall()
            id = session['id'] if 'id' in session else ''
            return render_template('search-teacher.html', departments=depts, id=id, logged_in=logged_in())
        except Exception as e:
            return 'MySQL Error [%d]: %s' % (e.args[0], e.args[1])
    except:
        pass
    return 'There is an error in the system. Please try again later.'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'id' in session:
        return redirect('/account')
    if request.method == 'POST':
        try:
            cur = mysql.connection.cursor()
            id = request.form['id']
            password = request.form['password']
            if 'login' in request.form:
                if REGEX.fullmatch(id) == None:
                    cur.execute(GET_TEACHER_PW, (id,))
                else:
                    cur.execute(GET_STUDENT_PW, (id,))
                row = cur.fetchone()
                if row == None or not bcrypt.checkpw(password.encode('utf-8'), row[0].encode('utf-8')):
                    return error('Invalid ID or password')
                session['id'] = id
                return redirect('/account')
            else:
                # ID
                if REGEX.fullmatch(id) == None:
                    return error('Invalid ID')
                cur.execute(GET_STUDENT_PW, (id,))
                row = cur.fetchone()
                if row != None:
                    return error('ID already exists')
                
                # Password
                if (len(password) < PW_MIN_LENGTH):
                    return error(f'Password needs at least {PW_MIN_LENGTH} characters')
                if (len(password) > PW_MAX_LENGTH):
                    return error(f'Please limit password to {PW_MAX_LENGTH} characters')
                
                # Name
                name = request.form['name']
                if (len(name) == 0):
                    return error('Please enter your name')
                if (len(name) > NAME_MAX_LENGTH):
                    return error(f'Please limit name to {NAME_MAX_LENGTH} characters')
                
                # Confirm Password
                confirm = request.form['confirm']
                if password != confirm:
                    return error('Passwords don\'t match')

                # Gender
                gender = request.form['gender']
                if gender not in GENDER_LIST:
                    return error('Please select your gender')

                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=ROUNDS))
                cur.execute(REGISTER, (id, name, hashed, gender))
                mysql.connection.commit()
                session['id'] = id
                return redirect('/account')
        except Exception as e:
            return error('MySQL Error [%d]: %s' % (e.args[0], e.args[1]))
    return render_template('login.html', message='')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html', logged_in=logged_in())

@app.route('/account')
def account():
    if 'id' not in session:
        return redirect('/login')
    
    try:
        try:
            id = session['id']
            cur = mysql.connection.cursor()
            if 'q' in request.args:
                q = '%' + request.args['q'] + '%'
                item_of = request.args['itemof'].split(',')
                types = request.args['types'].split(',')
                modules = request.args['modules'].split(',')
                cur.execute(GET_ITEMS, (('M' in item_of), q, types, modules, id, id, id, ('C' in item_of), q, types, modules, id, id))
                return jsonify(cur.fetchall())
            
            if is_teacher():
                return render_template('account.html', teacher=True, name='Teacher', types=ITEM_TYPE_LIST, class_list=get_raw_class_list())
            cur.execute(GET_STUDENT_NAME, (id,))
            name = cur.fetchone()[0]
            return render_template('account.html', teacher=False, name=name, types=ITEM_TYPE_LIST, class_list=get_raw_class_list())
        except Exception as e:
            return 'MySQL Error [%d]: %s' % (e.args[0], e.args[1])
    except:
        pass
    return 'There is an error in the system. Please try again later.'

@app.route('/class')
def class_page():
    return render_template('class.html')

@app.route('/consult')
def consult():
    if 'id' not in session:
        return redirect('/login')
    if is_teacher():
        return render_template('consult.html', student=False)
    return render_template('consult.html', student=True)

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect('/login')

def error(message):
    return render_template('login.html', message=message)

def get_hod_of(cur):
    hod = ''
    if is_teacher():
        cur.execute('select d_code from teacher where t_id = %s and is_hod = true;', (session['id'],))
        row = cur.fetchone()
        if row != None:
            hod = row[0]
    return hod

@app.route('/interact/get/announcements')
def get_announcements():
    try:
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute(GET_ANNOUNCEMENTS, (id, id, id, id))
        return jsonify(cur.fetchall())
    except:
        pass
    return jsonify(None)

@app.route('/interact/get/item')
def get_item():
    try:
        i_id = request.args['id']
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute(GET_ITEM_BY_CODE, (i_id, id, id, id, i_id, id, id))
        row = list(cur.fetchone())
        row.append(item_perm(i_id))
        return jsonify(row)
    except:
        return jsonify(None)

@app.route('/interact/edit/item', methods=['POST'])
def edit_item():
    try:
        if request.form['title'] == '':
            return reject('Please enter a title')
        if request.form['date'] == '':
            return reject('Please select a date')
        if request.form['module'] == '':
            return reject('Please select a valid module')
        if request.form['type'] not in ITEM_TYPE_LIST:
            return reject('Please select a valid type')
        weightage = request.form['weightage']
        if weightage == '':
            weightage = '0'
        if WEIGHTAGE_REGEX.fullmatch(weightage) == None:
            return reject('Please enter a valid weightage')
        if request.form['id'] != '':
            assert item_perm(request.form['id'])

        try:
            cur = mysql.connection.cursor()
            if request.form['isclass'] == '1':
                if request.form['class'] == '':
                    return reject('Please select a valid class')
                if request.form['id'] == '':
                    cur.execute('CALL add_class_item (%s, %s, %s, %s, %s, %s, %s, %s)', (request.form['title'], request.form['description'], request.form['date'], weightage, request.form['type'], session['id'], request.form['module'], request.form['class']))
                else:
                    cur.execute('CALL edit_class_item(%s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['title'], request.form['description'], request.form['date'], weightage, request.form['type'], request.form['id'], session['id'], request.form['module'], request.form['class']))
            else:
                if request.form['id'] == '':
                    if not is_coord_of_module(request.form['module']):
                        return reject('You are not a coordinator; Please select a class')
                    cur.execute('CALL add_module_item (%s, %s, %s, %s, %s, %s)', (request.form['title'], request.form['description'], request.form['date'], weightage, request.form['type'], request.form['module']))
                else:
                    if not is_coord_of_item(request.form['id']):
                        return reject('You are not a coordinator')
                    cur.execute('CALL edit_module_item(%s, %s, %s, %s, %s, %s, %s)', (request.form['title'], request.form['description'], request.form['date'], weightage, request.form['type'], request.form['id'], request.form['module']))
            mysql.connection.commit()
        except Exception as e:
            return reject('MySQL Error [%d]: %s' % (e.args[0], e.args[1]))
        return jsonify(success=True)
    except:
        pass
    return reject('There is an error in the system. Please try again later.')

@app.route('/interact/add/announcement', methods=['POST'])
def add_announcement():
    try:
        if request.form['title'] == '':
            return reject('Please enter a title')
        if request.form['module'] == '':
            return reject('Please select a valid module')
        if request.form['priority'] == '':
            return reject('Please enter a priority')

        try:
            cur = mysql.connection.cursor()
            if request.form['isclass'] == '1':
                if request.form['class'] == '':
                    return reject('Please select a valid class')
                cur.execute('CALL add_class_announcement (%s, %s, %s, %s, %s, %s)', (request.form['title'], request.form['description'], request.form['priority'], session['id'], request.form['module'], request.form['class']))
            else:
                if not is_coord_of_module(request.form['module']):
                    return reject('You are not a coordinator; Please select a class')
                cur.execute('CALL add_module_announcement (%s, %s, %s, %s)', (request.form['title'], request.form['description'], request.form['priority'], request.form['module']))
            mysql.connection.commit()
        except Exception as e:
            return reject('MySQL Error [%d]: %s' % (e.args[0], e.args[1]))
        return jsonify(success=True)
    except:
        pass
    return reject('There is an error in the system. Please try again later.')

@app.route('/interact/delete/item', methods=['POST'])
def delete_item():
    try:
        cur = mysql.connection.cursor()
        cur.execute('CALL delete_item(%s, %s)', (request.form['id'], session['id']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        pass
    return reject('')

@app.route('/interact/get/class-list')
def get_class_list():
    return jsonify(get_raw_class_list())
def get_raw_class_list():
    try:
        cur = mysql.connection.cursor()
        if 'edit' in request.args:
            assert is_teacher()
            cur.execute("SELECT m_code, c_name FROM teaches WHERE t_id = %s", (session['id'],))
        else:
            if is_teacher():
                cur.execute("SELECT m_code, c_name FROM teaches WHERE t_id = %s UNION SELECT c.m_code, c_name FROM class c LEFT JOIN offered_module o ON c.m_code = o.m_code WHERE coord_id = %s", (session['id'], session['id']))
            else:
                cur.execute("SELECT m_code, c_name FROM takes WHERE s_id = %s", (session['id'],))
        rows = cur.fetchall()
        class_list = {}
        for row in rows:
            if row[0] in class_list:
                class_list[row[0]].append(row[1])
            else:
                class_list[row[0]] = [row[1]]
        cur.execute("SELECT m_code FROM offered_module WHERE coord_id = %s", (session['id'],))
        coord_module = cur.fetchone()
        if coord_module != None:
            if coord_module[0] not in class_list:
                class_list[coord_module[0]] = []
        return class_list
    except:
        pass
    return None

GET_CLASS_BY_CODE = """
SELECT overview
FROM   class
WHERE  m_code = %s
       AND c_name = %s
       AND EXISTS (SELECT s_id
                   FROM   takes
                   WHERE  s_id = %s
                          AND m_code = %s
                          AND c_name = %s
                   UNION
                   SELECT t_id
                   FROM   teaches
                   WHERE  t_id = %s
                          AND m_code = %s
                          AND c_name = %s
                   UNION
                   SELECT coord_id
                   FROM   offered_module
                   WHERE  coord_id = %s
                          AND m_code = %s
                  );
"""

@app.route('/interact/get/class')
def get_class():
    try:
        id = session['id']
        cur = mysql.connection.cursor()
        code = request.args['code']
        if 'name' in request.args:
            name = request.args['name']
            cur.execute(GET_CLASS_BY_CODE, (code, name, id, code, name, id, code, name, id, code))
            overview = cur.fetchone()[0]
            cur.execute('SELECT t_id, name FROM teaches NATURAL LEFT JOIN teacher WHERE m_code = %s AND c_name = %s', (code, name))
            teachers = list(zip(*cur.fetchall()))
            teacherIDs = []
            teacherNames = []
            if len(teachers) == 2:
                teacherIDs = teachers[0]
                teacherNames = teachers[1]
            return jsonify(overview=overview, teacherIDs=teacherIDs, teacherNames=teacherNames, teacher=(id in teacherIDs), coord=is_coord_of_module(code))
        else:
            cur.execute(GET_OFFERED_MODULE_BY_CODE, (id, code, id, id, id))
            mod = cur.fetchone()
            assert mod != None
            return jsonify(mod=mod, coord=is_coord_of_module(code))
    except:
        return jsonify(None)

@app.route('/interact/add/teacher', methods=['POST'])
def get_teacher():
    try:
        assert is_coord_of_module(request.form['mcode'])
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO teaches VALUES (%s, %s, %s)', (request.form['teacher'], request.form['mcode'], request.form['cname']))
        mysql.connection.commit()
        cur.execute('SELECT CONCAT(prefix, ". ", name) FROM teacher WHERE t_id = %s', (request.form['teacher'],))
        return jsonify(success=True, message=cur.fetchone()[0])
    except:
        return reject('There is an error in the system. Please try again later.')

@app.route('/interact/add/class', methods=['POST'])
def add_class():
    try:
        assert is_coord_of_module(request.form['mcode'])
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO class VALUES (%s, %s, "")', (request.form['mcode'], request.form['cname']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        pass
    return reject('')

@app.route('/interact/delete/class', methods=['POST'])
def delete_class():
    try:
        assert is_coord_of_module(request.form['mcode'])
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM class WHERE m_code = %s AND c_name = %s', (request.form['mcode'], request.form['cname']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        pass
    return reject('')

@app.route('/interact/edit/module/offered', methods=['POST'])
def edit_offered_module():
    try:
        assert is_coord_of_module(request.form['mcode'])
        try:
            cur = mysql.connection.cursor()
            cur.execute('UPDATE offered_module SET overview = %s WHERE m_code = %s', (request.form['overview'], request.form['mcode']))
            mysql.connection.commit()
            return jsonify(success=True)
        except Exception as e:
            return reject('MySQL Error [%d]: %s' % (e.args[0], e.args[1]))
    except:
        pass
    return reject('There is an error in the system. Please try again later.')

@app.route('/interact/edit/class', methods=['POST'])
def edit_class():
    try:
        try:
            cur = mysql.connection.cursor()
            if is_coord_of_module(request.form['mcode']):
                cur.execute('UPDATE class SET c_name = %s, overview = %s WHERE  m_code = %s AND c_name = %s;', (request.form['cname'], request.form['overview'], request.form['mcode'], request.form['org']))
            else:
                cur.execute('UPDATE class SET overview = %s WHERE m_code = %s AND c_name = %s', (request.form['overview'], request.form['mcode'], request.form['org']))
            mysql.connection.commit()
            return jsonify(success=True)
        except Exception as e:
            return reject('MySQL Error [%d]: %s' % (e.args[0], e.args[1]))
    except:
        pass
    return reject('There is an error in the system. Please try again later.')

@app.route('/interact/get/class/perms')
def get_class_perms():
    try:
        perms = class_perms(request.args['code'], request.args['name'])
        assert perms != None
        if perms:
            return jsonify(1)
        return jsonify(0)
    except:
        return jsonify(None)

@app.route('/interact/get/class/lessons')
def get_class_lessons():
    try:
        assert class_perms(request.args['code'], request.args['name']) != None
        cur = mysql.connection.cursor()
        cur.execute('SELECT l_day, l_time, hours FROM lesson WHERE m_code = %s AND c_name = %s ORDER BY l_time', (request.args['code'], request.args['name']))
        return jsonify(cur.fetchall())
    except:
        return jsonify(None)

@app.route('/interact/get/class/teachers')
def get_class_teachers():
    try:
        assert class_perms(request.args['code'], request.args['name']) != None
        cur = mysql.connection.cursor()
        cur.execute('SELECT t_id, CONCAT(prefix, ". ", name) FROM teaches NATURAL LEFT JOIN teacher WHERE m_code = %s AND c_name = %s ORDER BY t_id', (request.args['code'], request.args['name']))
        return jsonify(cur.fetchall())
    except:
        return jsonify(None)

@app.route('/interact/get/class/students')
def get_class_students():
    try:
        assert class_perms(request.args['code'], request.args['name']) != None
        cur = mysql.connection.cursor()
        cur.execute('SELECT s_id, name, mentor_group FROM takes NATURAL LEFT JOIN student NATURAL LEFT JOIN mentor WHERE m_code = %s AND c_name = %s ORDER BY s_id', (request.args['code'], request.args['name']))
        return jsonify(cur.fetchall())
    except:
        return jsonify(None)

@app.route('/interact/add/class/lesson', methods=['POST'])
def add_class_lesson():
    try:
        assert class_perms(request.form['code'], request.form['name']) == True
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO lesson VALUES (%s, %s, %s, %s, %s)', (request.form['code'], request.form['name'], request.form['day'], request.form['time'], request.form['hours']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        return reject('')

@app.route('/interact/add/class/teacher', methods=['POST'])
def add_class_teacher():
    try:
        assert class_perms(request.form['code'], request.form['name']) == True
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO teaches VALUES (%s, %s, %s)', (request.form['id'], request.form['code'], request.form['name']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        return reject('')

@app.route('/interact/add/class/student', methods=['POST'])
def add_class_student():
    try:
        assert class_perms(request.form['code'], request.form['name']) == True
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO takes VALUES (%s, %s, %s)', (request.form['id'], request.form['code'], request.form['name']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        return reject('')

@app.route('/interact/delete/class/lesson', methods=['POST'])
def delete_class_lesson():
    try:
        assert class_perms(request.form['code'], request.form['name']) == True
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM lesson WHERE m_code = %s AND c_name = %s AND l_day = %s', (request.form['code'], request.form['name'], request.form['day']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        return reject('')

@app.route('/interact/delete/class/teacher', methods=['POST'])
def delete_class_teacher():
    try:
        assert class_perms(request.form['code'], request.form['name']) == True
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM teaches WHERE t_id = %s AND m_code = %s AND c_name = %s', (request.form['id'], request.form['code'], request.form['name']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        return reject('')

@app.route('/interact/delete/class/student', methods=['POST'])
def delete_class_student():
    try:
        assert class_perms(request.form['code'], request.form['name']) == True
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM takes WHERE s_id = %s AND m_code = %s AND c_name = %s', (request.form['id'], request.form['code'], request.form['name']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        return reject('')

@app.route('/interact/get/consults')
def get_consults():
    try:
        cur = mysql.connection.cursor()
        if is_teacher():
            cur.execute('SELECT s_id, name, CONCAT(time, ""), approved FROM consults NATURAL LEFT JOIN student WHERE t_id = %s ORDER BY time', (session['id'],))
        else:
            cur.execute('SELECT t_id, CONCAT(prefix, ". ", name), CONCAT(time, ""), approved FROM consults NATURAL LEFT JOIN teacher WHERE s_id = %s ORDER BY time', (session['id'],))
        return jsonify(cur.fetchall())
    except:
        pass
    return jsonify(None)

@app.route('/interact/get/consult')
def get_consult():
    try:
        cur = mysql.connection.cursor()
        if is_teacher():
            cur.execute('SELECT s_id, name, CONCAT(time, ""), description, approved FROM consults NATURAL LEFT JOIN student WHERE s_id = %s AND t_id = %s', (request.args['id'], session['id']))
        else:
            cur.execute('SELECT t_id, CONCAT(prefix, ". ", name), CONCAT(time, ""), description, approved FROM consults NATURAL LEFT JOIN teacher WHERE s_id = %s AND t_id = %s', (session['id'], request.args['id']))
        row = list(cur.fetchone())
        row.append(not is_teacher())
        return jsonify(row)
    except:
        pass
    return jsonify(None)

@app.route('/interact/edit/consult', methods=['POST'])
def edit_consult():
    try:
        if is_teacher():
            try:
                cur = mysql.connection.cursor()
                cur.execute('UPDATE consults SET approved = %s WHERE s_id = %s AND t_id = %s', (request.form['approved'], request.form['id'], session['id']))
                mysql.connection.commit()
                return jsonify(success=True)
            except Exception as e:
                return reject('MySQL Error [%d]: %s' % (e.args[0], e.args[1]))
        else:
            if request.form['time'] == '':
                return reject('Please select a time')
            try:
                cur = mysql.connection.cursor()
                if request.form['org'] == '':
                    cur.execute('INSERT INTO consults VALUES (%s, %s, %s, %s, NULL)', (session['id'], request.form['id'], request.form['time'], request.form['description']))
                else:
                    cur.execute('UPDATE consults SET t_id = %s, time = %s, description = %s, approved = NULL WHERE s_id = %s AND t_id = %s', (request.form['id'], request.form['time'], request.form['description'], session['id'], request.form['org']))
                mysql.connection.commit()
                return jsonify(success=True)
            except Exception as e:
                return reject('MySQL Error [%d]: %s' % (e.args[0], e.args[1]))
    except:
        pass
    return reject('There is an error in the system. Please try again later.')

@app.route('/interact/delete/consult', methods=['POST'])
def delete_consult():
    try:
        assert not is_teacher()
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM consults WHERE s_id = %s AND t_id = %s', (session['id'], request.form['id']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        pass
    return reject('')

@app.route('/interact/get/student')
def get_student():
    try:
        assert not is_teacher()
        cur = mysql.connection.cursor()
        cur.execute('SELECT s_id, s.name, mentor_group, CONCAT(prefix, ". ", t.name), mentor_id, gender FROM student s NATURAL LEFT JOIN mentor LEFT JOIN teacher t ON mentor_id = t_id WHERE s_id = %s', (session['id'],))
        return jsonify(cur.fetchone())
    except:
        pass
    return jsonify(None)

@app.route('/interact/get/lessons')
def get_lessons():
    try:
        lesson_var = ' TEACHES WHERE t_id ' if is_teacher() else ' TAKES WHERE s_id '
        cur = mysql.connection.cursor()
        cur.execute('SELECT m_code, c_name, l_time, hours FROM lesson WHERE (m_code, c_name) IN (SELECT m_code, c_name FROM'+lesson_var+'= %s) AND l_day = %s ORDER BY l_time', (session['id'], request.args['day']))
        return jsonify(cur.fetchall())
    except:
        pass
    return jsonify(None)

@app.route('/interact/get/teachers')
def get_teachers():
    try:
        cur = mysql.connection.cursor()
        q = '%' + request.args['q'] + '%'
        departments = request.args['departments'].split(',')
        cur.execute(GET_QUERIED_TEACHERS, (departments, q, q))
        return jsonify(cur.fetchall())
    except:
        pass
    return jsonify(None)

@app.route('/interact/get/teachers/safe')
def get_teachers_safe():
    try:
        cur = mysql.connection.cursor()
        q = '%' + request.args['q'] + '%'
        departments = request.args['departments'].split(',')
        cur.execute(GET_QUERIED_TEACHERS_SAFE, (departments, q, q))
        return jsonify(cur.fetchall())
    except:
        pass
    return jsonify(None)

@app.route('/interact/get/modules')
def get_modules():
    try:
        cur = mysql.connection.cursor()
        q = '%' + request.args['q'] + '%'
        departments = request.args['departments'].split(',')
        types = request.args['types'].split(',')
        cur.execute(GET_QUERIED_MODULES_1 + ('LEFT' if request.args['notoffered'] == 'true' else '') + GET_QUERIED_MODULES_2, (q, q, departments, types))
        return jsonify(cur.fetchall())
    except:
        pass
    return jsonify(None)

@app.route('/interact/get/module')
def get_module():
    try:
        cur = mysql.connection.cursor()
        if 'id' in session:
            cur.execute(GET_MODULE_BY_CODE, (session['id'], request.args['code'], request.args['code']))
        else:
            cur.execute(GET_GUEST_MODULE_BY_CODE, (request.args['code'], request.args['code']))
        return jsonify(cur.fetchone())
    except:
        pass
    return jsonify(None)

@app.route('/interact/edit/module', methods=['POST'])
def edit_module():
    try:
        if request.form['title'] == '':
            return reject('Please enter a title')
        if request.form['code'] == '':
            return reject('Please enter a code')
        if request.form['type'] not in TYPE_LIST:
            return reject('Please select a valid type')
        if request.form['semesters'] == '':
            return reject('Please enter semesters')
        if request.form['mc'] == '':
            return reject('Please enter MC')
        if request.form['hours'] == '':
            return reject('Please enter hours')
        assert is_hod(request.form['department'])

        coord = request.form['coord']
        if coord == '':
            coord = None
        try:
            cur = mysql.connection.cursor()
            if request.form['org'] == '':
                cur.execute('INSERT INTO module VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (request.form['code'], request.form['department'], request.form['title'], request.form['description'], request.form['semesters'], request.form['mc'], request.form['type'], request.form['hours']))
            else:
                cur.execute('CALL edit_module(%s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['code'], request.form['title'], coord, request.form['type'], request.form['semesters'], request.form['mc'], request.form['hours'], request.form['description'], request.form['org']))
            mysql.connection.commit()
        except Exception as e:
            return reject('MySQL Error [%d]: %s' % (e.args[0], e.args[1]))
        return jsonify(success=True)
    except:
        pass
    return reject('There is an error in the system. Please try again later.')

@app.route('/interact/delete/module', methods=['POST'])
def delete_module():
    try:
        assert is_hod_of_module(request.form['code'])
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM module WHERE m_code = %s', (request.form['code'],))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        pass
    return reject('')

@app.route('/interact/offer/module', methods=['POST'])
def offer_module():
    try:
        assert is_hod_of_module(request.form['code'])
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO offered_module VALUES (%s, null, null)', (request.form['code'],))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        pass
    return reject('')

@app.route('/interact/stop/module', methods=['POST'])
def stop_module():
    try:
        assert is_hod_of_module(request.form['code'])
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM offered_module WHERE m_code = %s', (request.form['code'],))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        pass
    return reject('')

@app.route('/interact/get/department')
def get_department():
    try:
        cur = mysql.connection.cursor()
        if 'id' in session:
            cur.execute(GET_DEPARTMENT_BY_CODE, (session['id'], request.args['code']))
        else:
            cur.execute(GET_GUEST_DEPARTMENT_BY_CODE, (request.args['code'],))
        return jsonify(cur.fetchone())
    except:
        pass
    return jsonify(None)

@app.route('/interact/edit/department', methods=['POST'])
def edit_department():
    try:
        assert is_hod(request.form['code'])
        cur = mysql.connection.cursor()
        cur.execute("UPDATE department SET description = %s WHERE d_code = %s", (request.form['description'], request.form['code']))
        mysql.connection.commit()
        return jsonify(success=True)
    except:
        pass
    return reject('There is an error in the system. Please try again later.')

def is_teacher():
    return 'id' in session and REGEX.fullmatch(session['id']) == None

def item_perm(i_id):
    try:
        assert is_teacher()
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute(ITEM_CHECK, (i_id, id, i_id, id))
        return cur.fetchone() != None
    except:
        return False

COORD_CHECK_ITEM = """
SELECT *
FROM   item
       NATURAL LEFT JOIN module_item
       NATURAL LEFT JOIN offered_module
WHERE  i_id = %s
       AND coord_id = %s;
"""
COORD_CHECK_MODULE = """
SELECT *
FROM   offered_module
WHERE  m_code = %s
       AND coord_id = %s;
"""
HOD_CHECK = """
SELECT *
FROM   department
WHERE  d_code = %s
       AND hod_id = %s;
"""
HOD_CHECK_MODULE = """
SELECT *
FROM   module
       LEFT JOIN department ON module.d_code = department.d_code
WHERE  m_code = %s
       AND hod_id = %s;
"""

def is_coord_of_item(i_id):
    try:
        assert is_teacher()
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute(COORD_CHECK_ITEM, (i_id, id))
        return cur.fetchone() != None
    except:
        return False

def is_coord_of_module(m_code):
    try:
        assert is_teacher()
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute(COORD_CHECK_MODULE, (m_code, id))
        return cur.fetchone() != None
    except:
        return False

def is_hod(d_code):
    try:
        assert is_teacher()
        cur = mysql.connection.cursor()
        cur.execute(HOD_CHECK, (d_code, session['id']))
        return cur.fetchone() != None
    except:
        return False

def is_hod_of_module(m_code):
    try:
        assert is_teacher()
        cur = mysql.connection.cursor()
        cur.execute(HOD_CHECK_MODULE, (m_code, session['id']))
        return cur.fetchone() != None
    except:
        return False

def hod_of():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT d_code, name FROM department WHERE hod_id = %s', (session['id'],))
        return cur.fetchone()
    except:
        pass
    return None

def class_perms(code, name):
    try:
        id = session['id']
        if is_coord_of_module(code):
            return True
        cur = mysql.connection.cursor()
        cur.execute('SELECT s_id FROM takes WHERE s_id = %s AND m_code = %s AND c_name = %s UNION SELECT t_id FROM teaches WHERE t_id = %s AND m_code = %s AND c_name = %s', (id, code, name, id, code, name))
        assert cur.fetchone() != None
        return False
    except:
        pass
    return None

def logged_in():
    return 'id' in session

def reject(message):
    return jsonify(success=False, message=message)

if __name__ == '__main__':
    app.run(debug=True)


import hashlib
import os
import uuid
import shutil

import time as t
import MySQLdb.cursors
import shortuuid
from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

app = Flask(__name__)

app.secret_key = '195f89e59175eec4a3ae4630b800d31a'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'informationmanagement'

mysql = MySQL(app)

linkList = ["login", "register", "profile", "profile/edit"]
logout = "false"
@app.route('/login', methods=['GET', 'POST'])
def base():
    if 'loggedin' in session:
        return redirect(url_for('homepage'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST" and 'emlgn' in request.form and 'passlgn' in request.form:
        emlgn = request.form['emlgn']
        passlgn = request.form['passlgn']
        hashedpass = hashlib.md5(passlgn.encode())

        if emlgn == "" or passlgn == "":
            msgf = "Fields cannot be emtpy"
            return render_template('onlog.html', msgf=msgf, emlgnupdate=emlgn)


        else:
            cur.execute("SELECT * FROM users WHERE email=%s AND pass=%s", (emlgn, hashedpass.hexdigest()))
            dataFethcher = cur.fetchone()

            if dataFethcher:
                session['loggedin'] = True
                session['id'] = dataFethcher['id']
                session['schoolpos'] = dataFethcher['schoolpos']
                session['usernm'] = dataFethcher['fullname']
                session['user_id'] = dataFethcher['user_id']
                session['userpicalt'] = dataFethcher['fullname']
                session['userdefpic'] = dataFethcher['user_pp']
                session['schoolyr'] = dataFethcher['schoolyr']
                session['schoolid'] = dataFethcher['schoolid']
                session['bday'] = dataFethcher['bday']
                session['course'] = dataFethcher['course']
                session['userbday'] = dataFethcher['bday']
                session['userem'] = dataFethcher['email']
                return redirect(url_for('homepage'))
            else:

                msgf = "Incorrect Email or Password"

                return render_template('onlog.html', msgf=msgf, emlgnupdate=emlgn)
    else:
        return render_template('onlog.html')


@app.route('/')
def homepage():
    if 'loggedin' in session:
        return render_template('userDashpage.html', usernm=session['usernm'], schoolposition=session['schoolpos'],
                               userProfilepic=session['userpicalt'], userdefpic=session['userdefpic'],
                               userschoolyr=session['schoolyr'], userschoolid=session['schoolid'],
                               usercourse=session['course'], userbday=session['bday'], userem=session['userem'])
    else:
        return redirect(url_for('base'))


@app.route('/profile')
def profile():
    if 'loggedin' in session:
        return render_template('UserProfileDataFetcher.html', usernm=session['usernm'],
                               schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                               userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                               userschoolid=session['schoolid'], usercourse=session['course'], userbday=session['bday'],
                               userem=session['userem'])
    else:
        return redirect(url_for('base'))


@app.route('/profile/edit')
def profileEditor():
    if 'loggedin' in session:
        return render_template('UserProfileEditor.html', usernm=session['usernm'], schoolposition=session['schoolpos'],
                               userProfilepic=session['userpicalt'], userdefpic=session['userdefpic'])
    else:
        return redirect(url_for('base'))




@app.route('/logout', methods=['POST'])
def logout():
     if 'loggedin' in session:
           if request.method == "POST":
                logout = request.form['logoutin']

           if str(logout) == "True":
               session.pop('loggedin', None)
               session.pop('id', None)
               session.pop('schoolpos', None)
               session.pop('user_id', None)
               session.pop('usernm', None)
               session.pop('userdefpic', None)
               session.pop('userpicalt', None)
               session.pop('schoolyr', None)
               session.pop('schoolid', None)
               session.pop('course', None)
               session.pop('userbday', None)
               session.pop('userem', None)
               return redirect(url_for('base'))
           else:
               return redirect(url_for('homepage'))
     else:
           return redirect(url_for('base'))


@app.route('/register')
def register():
    if 'loggedin' in session:
        return redirect(url_for('homepage'))

    return render_template('fetchreg.html')


@app.route('/register', methods=['POST'])
def fetcher():
    if request.method == "POST":

        name = request.form['nmreg']
        emailreg = request.form['emreg']
        password = request.form['passreg']
        repassword = request.form['repassreg']

        p1 = hashlib.md5(password.encode())
        p2 = hashlib.md5(repassword.encode())
        p1uncrypt = str(password)
        p2uncrypt = str(repassword)
        em = str(emailreg)
        msgf = ''
        msgs = ''

        getName = str(name)
        getEmail = str(emailreg)
        getPass = str(password)
        getRepass = str(repassword)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", [em])
        emailCheck = cur.fetchone()

        if getName == "" and getEmail == "" and getPass == "" and getRepass == "" or getName == "" or getEmail == "" or getPass == "" or getRepass == "":
            msgf = "Fields cannot be empty"
            return render_template('fetchreg.html', msgf=msgf, nmregupdate=getName, emregupdate=getEmail,
                                   passregupdate=getPass, repassregupdate=getRepass)

        if emailCheck:
            msgf = "Email already existed"
            return render_template('fetchreg.html', msgf=msgf, nmregupdate=getName, passregupdate=getPass,
                                   repassregupdate=getRepass)

        if len(getPass) < 8:
            msgf = "Password must be minimum of 8 Characters"
            return render_template('fetchreg.html', msgf=msgf, nmregupdate=getName, emregupdate=getEmail)

        if p1uncrypt != p2uncrypt:
            msgf = "Password doesn't match"
            return render_template('fetchreg.html', msgf=msgf, nmregupdate=getName, emregupdate=getEmail)
        else:
            cur = mysql.connection.cursor()
            generateUUID = uuid.uuid4()

            userdirectory = str(generateUUID)
            userparent_dir = "./static/users/"
            userdirectorypath = os.path.join(userparent_dir, userdirectory)
            os.mkdir(userdirectorypath)

            userlocalstorage = "Images"
            userlocalstorage_dir = "./static/users/" + userdirectory + "/"
            userlocalstoragepath = os.path.join(userlocalstorage_dir, userlocalstorage)
            generateVisitorAccessID = shortuuid.ShortUUID().random(length=22)

            os.mkdir(userlocalstoragepath)
            def_pic = './images/default_profile_picture.png'
            cur.execute(
                "INSERT INTO `users` (`user_id`,`user_pp`,`fullname`, `email`, `pass`, `repass`) VALUES (%s, %s, %s, %s, %s, %s)",
                [generateUUID, def_pic, name, emailreg, str(p1.hexdigest()), str(p2.hexdigest())])
            cur.execute(
                "INSERT INTO `usersdictionary` (`userfn`,`userpp`,`visitorAccessID`) VALUES (%s, %s, %s)",
                [name, def_pic, generateVisitorAccessID])
            mysql.connection.commit()

            msgs = "Registered Successfully!"
            return render_template('fetchreg.html', msgs=msgs)


@app.route('/profile/edit', methods=['GET', 'POST'])
def editprofile():
    getUserID = session['user_id']
    getID = session['id']
    if request.method == "POST":
        userstatus = request.form.get('userstatusedit')
        usernm = request.form.get('usernmeditor')
        userem = request.form.get('useremeditor')
        userschoolyr = request.form.get('usersyedit')
        userschoolid = request.form.get('usersidneditor')
        userbday = request.form.get('userbdayeditor')
        usercourse = request.form.get('usercourseedit')
        userpass = request.form.get('userpasseditor')
        userrepass = request.form.get('userrepasseditor')

        getuserstatus = str(userstatus)
        getusernm = str(usernm)
        getuserem = str(userem)
        getuserschoolyr = str(userschoolyr)
        getuserschoolid = str(userschoolid)
        getuserbday = str(userbday)
        getusercourse = str(usercourse)
        getuserpass = str(userpass)
        getuserrepass = str(userrepass)

        if userpass and userrepass != '':

            p1 = hashlib.md5(userpass.encode())
            p2 = hashlib.md5(userrepass.encode())

            if userpass != userrepass:
                msgf = "Password doesn't match"
                return render_template('UserProfileDataFetcher.html', usernm=session['usernm'],
                                       schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                                       userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                                       userschoolid=session['schoolid'], usercourse=session['course'],
                                       userbday=session['bday'], userem=session['userem'], msgf=msgf)

            elif len(userpass) < 8:
                msgf = "Password must be minimum of 8 characters"
                return render_template('UserProfileDataFetcher.html', usernm=session['usernm'],
                                       schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                                       userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                                       userschoolid=session['schoolid'], usercourse=session['course'],
                                       userbday=session['bday'], userem=session['userem'], msgf=msgf)
            else:
                cur = mysql.connection.cursor()
                cur.execute("""
                UPDATE users
                SET pass=%s AND repass=%s
                WHERE user_id=%s
                """, (p1, p2, getUserID))
                mysql.connection.commit()

        if usernm != '':
            session.pop('usernm', None)
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE users
            SET fullname=%s
            WHERE user_id=%s
            """, (usernm, getUserID))

            cur.execute("""
            UPDATE usersdictionary
            SET userfn=%s
            WHERE id=%s
            """, (usernm, getID))
            mysql.connection.commit()

        if userstatus != " ":
            session.pop('schoolpos', None)

            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE users
            SET schoolpos=%s
            WHERE user_id=%s
            """, (userstatus, getUserID))

            cur.execute("""
            UPDATE usersdictionary
            SET schoolpos=%s
            WHERE id=%s
            """, (userstatus, getID))
            mysql.connection.commit()

        if userschoolyr != " ":
            session.pop('schoolyr', None)
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE users
            SET schoolyr=%s
            WHERE user_id=%s
            """, (userschoolyr, getUserID))
            mysql.connection.commit()

        if userschoolid != '':
            session.pop('schoolid', None)
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE users
            SET schoolid=%s
            WHERE user_id=%s
            """, (userschoolid, getUserID))
            mysql.connection.commit()

        if userbday != '':
            session.pop('userbday', None)
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE users
            SET bday=%s
            WHERE user_id=%s
            """, (userbday, getUserID))
            mysql.connection.commit()

        if usercourse != " ":
            session.pop('course', None)
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE users
            SET course=%s
            WHERE user_id=%s
            """, (usercourse, getUserID))
            mysql.connection.commit()

        if userem != '':
            session.pop('userem', None)
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE users
            SET email=%s
            WHERE user_id=%s
            """, (userem, getUserID))
            mysql.connection.commit()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE user_id=%s", [session['user_id']])
    dataFethcher = cur.fetchone()

    if dataFethcher:
        session['schoolpos'] = dataFethcher['schoolpos']
        session['usernm'] = dataFethcher['fullname']
        session['schoolyr'] = dataFethcher['schoolyr']
        session['schoolid'] = dataFethcher['schoolid']
        session['bday'] = dataFethcher['bday']
        session['course'] = dataFethcher['course']
        session['userem'] = dataFethcher['email']
        session['userpicalt'] = dataFethcher['fullname']
        msgs = 'Profile updated successfully!'
        return render_template('UserProfileDataFetcher.html', usernm=session['usernm'],
                               schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                               userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                               userschoolid=session['schoolid'], usercourse=session['course'],
                               userbday=session['bday'], userem=session['userem'], msgs=msgs)


@app.route('/profile', methods=['GET', 'POST'])
def changeprofile():
    img_ext = ['.jpg', '.jpeg', '.png', '.gif']
    Accepted = 0

    if request.method == "POST":

        f = request.files['newuserdp']
        filename = secure_filename(f.filename)

        lowerFN = filename.lower()

        for x in img_ext:
            result = lowerFN.find(x)

            if result != -1:
                Accepted = Accepted + 1

        if Accepted == 1:
            UPLOAD_FOLDER = 'static/users/' + session['user_id'] + '/Images'
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            newuserprofilepic = './users/' + session['user_id'] + '/Images/' + filename

            getUserID = session['user_id']
            getID = session['id']
            cur = mysql.connection.cursor()
            cur.execute("""
        
            UPDATE users
            SET user_pp=%s
            WHERE user_id=%s
            """, (newuserprofilepic, getUserID))

            cur.execute("""

            UPDATE usersdictionary
            SET userpp=%s
            WHERE id=%s
            """, (newuserprofilepic, getID))

            mysql.connection.commit()

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM users WHERE user_id=%s", [session['user_id']])
            dataFethcher = cur.fetchone()

            session.pop('userdefpic', None)
            session['userdefpic'] = dataFethcher['user_pp']
            t.sleep(3)
            msgs = 'Profile Picture updated successfully!'
            return render_template('UserProfileDataFetcher.html', usernm=session['usernm'],
                                   schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                                   userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                                   userschoolid=session['schoolid'], usercourse=session['course'],
                                   userbday=session['bday'], userem=session['userem'], msgs=msgs)

        else:
            t.sleep(3)
            msgf = 'File type not Supported!'
            return render_template('UserProfileDataFetcher.html', usernm=session['usernm'],
                                   schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                                   userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                                   userschoolid=session['schoolid'], usercourse=session['course'],
                                   userbday=session['userbday'], userem=session['userem'], msgf=msgf)


@app.route("/", methods=['GET', 'POST'])
def search():
    filtered = []
    userDict = []
    count = 0
    if request.method == "POST":
        getsearch = request.form['searcher']

        if not getsearch:
            Error = "Search input must not be empty"
            return render_template('userDashpage.html', usernm=session['usernm'],
                                   schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                                   userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                                   userschoolid=session['schoolid'], usercourse=session['course'],
                                   userbday=session['bday'], userem=session['userem'],
                                   error=Error)  # unfiltered[0]['userfn']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM usersdictionary")
        dataFetcher = cur.fetchall()

        for x in dataFetcher:
            userDict.append(x)

        for i in userDict:
            search = userDict[count]['userfn'].lower().find(getsearch.lower())
            if search != -1:
                filtered.append(userDict[count])
            count += 1

        if len(filtered) == 0:
            returnerror = True
            return render_template('searchPage.html', usernm=session['usernm'],
                                   schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                                   userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                                   userschoolid=session['schoolid'], usercourse=session['course'],
                                   userbday=session['bday'], userem=session['userem'],
                                   getreturn=returnerror, returnsearch=getsearch)  # unfiltered[0]['userfn']

        else:
            return render_template('searchPage.html', usernm=session['usernm'],
                                   schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                                   userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                                   userschoolid=session['schoolid'], usercourse=session['course'],
                                   userbday=session['bday'], userem=session['userem'],
                                   datas=filtered, returnsearch=getsearch)  # unfiltered[0]['userfn']



@app.route("/profile/<user>", methods=['GET', 'POST'])
def visitLinker(user):

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM usersdictionary WHERE visitorAccessID=%s", [user])
    visitorAccessIDFetch = cur.fetchone()

    getuserID = visitorAccessIDFetch['id']
    getVisitorID = visitorAccessIDFetch['visitorAccessID']


    if session['id'] == getuserID:
        return redirect(url_for('profile'))

    else:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE id=%s", [getuserID])
        visitordataFetch = cur.fetchone()



        return render_template('profileVisitor.html', usernm=session['usernm'],
                           schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                           userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                           userschoolid=session['schoolid'], usercourse=session['course'],
                           userbday=session['bday'], userem=session['userem'],
                           visitordefpic=visitordataFetch['user_pp'], visitorusernm=visitordataFetch['fullname'],
                           visitorschoolposition=visitordataFetch['schoolpos'],
                           visitorusernm2=visitordataFetch['fullname'],
                           visitorschoolposition2=visitordataFetch['schoolpos'],
                           visitoruserschoolyr=visitordataFetch['schoolyr'],
                           visitoruserschoolid=visitordataFetch['schoolid'],
                           visitoruserbday=visitordataFetch['bday'], visitorusercourse=visitordataFetch['course'],
                           user=visitorAccessIDFetch['visitorAccessID'])

@app.route("/profile/<user>", methods=['GET', 'POST'])
def visit(user):

    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM usersdictionary WHERE visitorAccessID=%s", [user])
        visitorAccessIDFetch = cur.fetchone()

        getuserID = visitorAccessIDFetch['id']

        if session['id'] == getuserID:
            return redirect(url_for('profile'))

        else:
            if request.method == "POST":
                visitor = request.form['visituserprofile']

                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("SELECT * FROM users WHERE id=%s", [str(visitor)])
                visitordataFetch = cur.fetchone()

                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("SELECT * FROM usersdictionary WHERE id=%s", [str(visitor)])
                visitorAccessIDFetch = cur.fetchone()

                return render_template('profileVisitor.html', usernm=session['usernm'],
                                   schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'],
                                   userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'],
                                   userschoolid=session['schoolid'], usercourse=session['course'],
                                   userbday=session['bday'], userem=session['userem'],
                                   visitordefpic=visitordataFetch['user_pp'], visitorusernm=visitordataFetch['fullname'], visitorschoolposition=visitordataFetch['schoolpos'], visitorusernm2=visitordataFetch['fullname'],
                                   visitorschoolposition2=visitordataFetch['schoolpos'], visitoruserschoolyr=visitordataFetch['schoolyr'], visitoruserschoolid=visitordataFetch['schoolid'],
                                   visitoruserbday=visitordataFetch['bday'], visitorusercourse=visitordataFetch['course'], user=visitorAccessIDFetch['visitorAccessID'])

    else:
        return redirect(url_for('homepage'))

@app.route("/<link>")
def goto(link):
    if 'loggedin' in session:
        if link in linkList:
            return redirect(url_for(link))
        else:
            return redirect(url_for('homepage'))
    else:
        if link in linkList:
            return redirect(url_for('base'))
        else:
            return redirect(url_for('base'))

if __name__ == "__main__":
    app.run(debug=True)

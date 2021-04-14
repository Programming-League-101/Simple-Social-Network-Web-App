import hashlib
import os
import uuid
import shutil

import MySQLdb.cursors
from flask import Flask, render_template, url_for, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key='195f89e59175eec4a3ae4630b800d31a'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'informationmanagement'

mysql = MySQL(app)


@app.route('/login', methods=['GET','POST'])
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
            cur.execute("SELECT * FROM users WHERE email=%s AND pass=%s",(emlgn, hashedpass.hexdigest()))
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
        return render_template('userDashpage.html', usernm=session['usernm'], schoolposition=session['schoolpos'] , userProfilepic=session['userpicalt'], userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'], userschoolid=session['schoolid'], usercourse=session['course'], userbday=session['userbday'], userem=session['userem'])
    else:
        return redirect(url_for('base'))
@app.route('/profile')
def profile():
    if 'loggedin' in session:
        return render_template('UserProfileDataFetcher.html',  usernm=session['usernm'], schoolposition=session['schoolpos'], userProfilepic=session['userpicalt'], userdefpic=session['userdefpic'], userschoolyr=session['schoolyr'], userschoolid=session['schoolid'], usercourse=session['course'], userbday=session['userbday'], userem=session['userem'])
    else:
        return redirect(url_for('base'))
    

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('schoolpos', None)
    session.pop('usernm', None)
    session.pop('userdefpic', None)
    session.pop('userpicalt', None)
    session.pop('schoolyr', None)
    session.pop('schoolid', None)
    session.pop('course', None)
    session.pop('userbday', None)
    session.pop('userem', None)

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
            return render_template('fetchreg.html', msgf=msgf, nmregupdate=getName, emregupdate=getEmail, passregupdate=getPass, repassregupdate=getRepass)

        if emailCheck:
            msgf = "Email already existed"
            return render_template('fetchreg.html', msgf=msgf, nmregupdate=getName, passregupdate=getPass, repassregupdate=getRepass)

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
            userlocalstorage_dir = "./static/users/"+userdirectory+"/"
            userlocalstoragepath = os.path.join(userlocalstorage_dir, userlocalstorage)
            os.mkdir(userlocalstoragepath)
            def_pic = './images/default_profile_picture.png'
            cur.execute("INSERT INTO `users` (`user_id`,`user_pp`,`fullname`, `email`, `pass`, `repass`) VALUES (%s, %s, %s, %s, %s, %s)",[generateUUID, def_pic, name, emailreg, str(p1.hexdigest()), str(p2.hexdigest())])
            mysql.connection.commit()



            msgs = "Registered Successfully!"
            return render_template('fetchreg.html', msgs=msgs)









if __name__ == "__main__":
    app.run(debug=True)

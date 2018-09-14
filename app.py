import datetime
import io

from flask import Flask, render_template, flash, request, url_for, redirect, session, Response, jsonify
from passlib.hash import sha256_crypt
from ConnectionDb import connection
import os
from pymysql import escape_string as thawrt
import gc
from PIL import Image
import base64

import PIL.Image

# UPLOAD_FOLDER = 'static/userpics'


app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.secret_key = "super secret key"
now = datetime.datetime.now()


@app.route('/')
def umain():
    return render_template("Home.html")


@app.route('/service/')
def service():
    return render_template("Services.html")


@app.route('/contact/')
def contact():
    return render_template("Contactus.html")


@app.route('/login/')
def login():
    return render_template("log.html")


@app.route('/register/')
def register():
    return render_template("reg.html")


@app.route('/aboutus/')
def aboutus():
    return render_template("AboutUs.html")


@app.route('/dashboard/')
def dash():
    c, cnx = connection()
    c.execute("SELECT COUNT(*) FROM message WHERE `REmail`=%s and `Status`='unread'", (thawrt(session['uemail']),))
    rows = c.fetchone()[0]
    session['messages'] = rows

    return render_template("dashboard.html")


@app.route('/regpet/')
def regpet():
    return render_template("Registerpet.html")


@app.route('/regdata/', methods=['GET', 'POST'])
def regdata():
    try:

        if request.method == "POST":
            fullname = request.form['name']

            lastname = request.form['lname']

            username = request.form['email']

            dateofbirth = request.form['dob']

            password = request.form['pword']

            confirmpassword = request.form['cpword']
            Truepassword = sha256_crypt.encrypt((str(password)))

            if password == confirmpassword:
                c, cnx = connection()
                c.execute("SELECT `Email` FROM `customers` WHERE `Email`=%s", (thawrt(username),))
                rows = c.fetchone()
                print(rows)

                if rows is 0 or rows is None:
                    # -------------------------------------------------------------- image upload

                    imgfile = request.files.getlist("file")
                    # print(imgfile)
                    capname = now.strftime("%Y-%m-%d %H-%M")
                    target = os.path.join(APP_ROOT, 'static/userpics')
                    # print(target)

                    if imgfile == []:
                        flash("please selct a image")
                    else:

                        if not os.path.isdir(target):
                            os.mkdir(target)

                        for file in request.files.getlist("file"):
                            # print(file)
                            filename = file.filename
                            # print(filename)
                            destination = "/".join([target, filename])
                            # print(destination)

                            file.save(destination)
                            newfile = 'static/userpics/' + capname + filename
                            newfilename = capname + filename
                            os.rename(destination, newfile)
                            # flash("Sucess")

                    c.execute(
                        "INSERT INTO `customers`(`FirstName`, `LastName`, `Email`, `dateofbirth`, `password`, `image`) VALUES (%s,%s,%s,%s,%s,%s)",
                        (
                            thawrt(fullname), thawrt(lastname), thawrt(username), thawrt(dateofbirth),
                            thawrt(Truepassword),
                            thawrt(newfilename)))
                    cnx.commit()
                    flash("Registration successful..!")

                    cnx.close
                    c.close()

                    gc.collect()
                    session['logged'] = True
                    session['uname'] = username
                    return redirect(url_for('umain'))

                else:
                    flash("The email already Registered,  please try another email..!")




            else:
                flash("Passowrd You Entered doesnt match..!")



        else:
            print("error")

    except Exception as e:
        print(e)
    return redirect(url_for("register"))


# ---------------------------------------------------------------------end of registration--------------------------
@app.route('/loginauth/', methods=['GET', 'POST'])
def loginauth():
    print("okk")
    try:
        print("2")

        if request.method == "POST":
            print("3")

            email = request.form['email']

            c, cnx = connection()

            c.execute(
                "SELECT  `FirstName`, `LastName`, `Email`, `dateofbirth`, `password`,`image` FROM `customers` WHERE `Email`=%s",
                (thawrt(email),))

            data = c.fetchall()
            print(data)
            for row in data:
                fname = row[0]
                lname = row[1]
                usermail = row[2]
                userdob = row[3]
                passw = row[4]
                userpic = row[5]
                print(fname)

            if sha256_crypt.verify(request.form['pass'], passw):
                print(request.form['pass'])
                session['logged'] = True
                session['firstname'] = fname
                session['lastname'] = lname
                session['uemail'] = usermail
                session['udob'] = userdob
                session['userpass'] = passw
                session['profic'] = userpic
                print(userpic)

                flash("you are now Logged in...!")
                return redirect(url_for('dash'))
            else:
                flash("Invalid credential, Plz try again..!")
                gc.collect()
                return redirect(url_for("login"))

        return redirect(url_for("login"))
    except Exception as e:
        print(e)
        flash("Login Error..! plz contact the Hash's Pet care Center...")

        return redirect(url_for("login"))


@app.route('/logout/')
def logout():
    gc.collect()
    session.clear()
    flash("You Have been Log out..")
    session.clear()

    return redirect(url_for('umain'))


# ---------------------------------------pet registration-------------------------------------------
@app.route('/petregister/', methods=['GET', 'POST'])
def petregister():
    try:
        if request.method == "POST":
            petname = request.form['petname']
            pettype = request.form['type']

            petbreed = request.form['Bread']

            petcolor = request.form['color']

            petgender = request.form['gender']

            petage = request.form['age']

            petbday = request.form['dob']
            image = request.files.getlist("pic")
            target = os.path.join(APP_ROOT, 'static/petpics')
            capname = now.strftime("%Y-%m-%d %H-%M")
            ownername = session['firstname']

            owneremail = session['uemail']

            if petgender == "Gender" or petgender == None:
                flash("Please Select Pet Gender...")

            if petage == "Age" or petage == None:
                flash("Please Select Pet Age...")

            if image == []:
                flash("please selct a image")

            else:
                if not os.path.isdir(target):
                    os.mkdir(target)

                for file in request.files.getlist("pic"):
                    # print(file)
                    filename = file.filename
                    # print(filename)
                    destination = "/".join([target, filename])
                    # print(destination)

                    file.save(destination)
                    newfile = 'static/petpics/' + capname + filename
                    newfilename = capname + filename
                    os.rename(destination, newfile)
                    # flash("Sucess")
                    c, cnx = connection()
                    c.execute(
                        "INSERT INTO `pets`(`ownerEmail`, `OwnerName`,`petsname`, `Breed`, `type`, `furColor`, `gender`, `Age`, `dob`, `image`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                            thawrt(owneremail), thawrt(ownername), thawrt(petname), thawrt(petbreed), thawrt(pettype),
                            thawrt(petcolor), thawrt(petgender), thawrt(petage), thawrt(petbday),
                            thawrt(newfilename)))
                    cnx.commit()
                    flash("Registration successful..!")

                    cnx.close
                    c.close()
                    return redirect(url_for("dash"))

            return redirect(url_for("regpet"))





    except Exception as e:
        print(e)
        flash(e)
    return redirect(url_for("regpet"))


# -----------------------------------------------view pet list-------------------------------------------------
@app.route('/view/')
def view():
    owneremail = session['uemail']
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `pets` WHERE `ownerEmail`=%s",
        (thawrt(owneremail),))

    data = c.fetchall()
    c.execute(
        "SELECT COUNT(*) FROM `pets` WHERE `ownerEmail`=%s",
        (thawrt(owneremail),))
    count=c.fetchone()[0]

    print(data)
    session['cat'] = data
    for row in data:
        session['tempownername'] = row[2]
        session['temppetname'] = row[3]
        session['breed'] = row[4]
        session['type'] = row[5]
        session['color'] = row[6]
        session['gender'] = row[7]
        session['age'] = row[8]
        session['dob'] = row[9]
        session['image'] = row[10]

        print(count)


    return render_template("View.html")


if __name__ == '__main__':
    app.run()

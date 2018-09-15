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
import json
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


# ------------------------------------------------------register customer------------------------------------------
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

    session['cat'] = data

    return render_template("View.html")


@app.route('/update/')
def update():
    owneremail = session['uemail']
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `pets` WHERE `ownerEmail`=%s",
        (thawrt(owneremail),))

    petsid = c.fetchall()

    session['tempid'] = petsid

    return render_template("updatefront.html")


@app.route('/updateauth/')
def updateauth():
    return render_template("updatepet.html")


@app.route('/delpet/')
def delpet():
    owneremail = session['uemail']
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `pets` WHERE `ownerEmail`=%s",
        (thawrt(owneremail),))

    data = c.fetchall()

    session['cat'] = data
    return render_template("deletepet.html")


@app.route('/delconf/', methods=['POST'])
def delconf():
    if request.method == 'POST':
        petidfordelete = request.form['petid']

        c, cnx = connection()
        c.execute(
            "DELETE FROM `pets` WHERE `petID`=%s",
            (thawrt(petidfordelete),))
        cnx.commit()
        flash("Record has been Successfully deleted..!")

    return redirect(url_for("delpet"))


@app.route('/startupdate/', methods=['POST'])
def startupdate():
    try:
        if request.method == "POST":
            updatepetid = request.form['petid']

            if updatepetid == 'Select Pet ID':
                flash("Please Select a Valid Pet ID")
                return redirect(url_for("update"))
            else:
                c, cnx = connection()
                c.execute(
                    "SELECT * FROM `pets` WHERE `petID`=%s",
                    (thawrt(updatepetid),))

                data = c.fetchall()

                session['uppet'] = data
                session['oids'] = updatepetid

                print(updatepetid)
                return redirect(url_for("updateauth"))
        else:
            flash("Please Select a Valid Pet ID")
            return redirect(url_for("update"))

    except Exception as e:
        print(e)
        return redirect(url_for("update"))


@app.route('/updateconfirm/', methods=['POST'])
def updateconfirm():
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

            updateid = session['oids']

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
                    print(updateid)
                    c.execute(
                        "UPDATE `pets` SET `petsname`=%s,`Breed`=%s,`type`=%s,`furColor`=%s,`gender`=%s,`Age`=%s,`dob`=%s,`image`=%s WHERE `petID`=%s",
                        (thawrt(petname), thawrt(petbreed), thawrt(pettype), thawrt(petcolor), thawrt(petgender),
                         thawrt(petage), thawrt(petbday), thawrt(newfilename), thawrt(updateid)))
                    cnx.commit()
                    flash("Registration successful..!")

                    cnx.close
                    c.close()
                    return redirect(url_for("view"))


    except Exception as e:
        print(e)
        flash("Update were not succesfull...")
        os.remove(newfile)
        return redirect(url_for("update"))


@app.route('/propic/')
def propic():
    print(session['profic'])

    return render_template("changeprofilet.html")


@app.route('/cp/', methods=['POST'])
def cp():
    try:
        if request.method == "POST":
            image = request.files.getlist("pic")
            target = os.path.join(APP_ROOT, 'static/petpics')
            capname = now.strftime("%Y-%m-%d %H-%M")
            email = session['uemail']

            if image == []:
                flash("please selct a image")

            else:
                if not os.path.isdir(target):
                    os.mkdir(target)

                for file in request.files.getlist("pic"):
                    print(file)
                    filename = file.filename
                    print(filename)
                    destination = "/".join([target, filename])
                    # print(destination)

                    file.save(destination)
                    newfile = 'static/userpics/' + capname + filename
                    newfilename = capname + filename
                    os.rename(destination, newfile)
                    # flash("Sucess")
                    c, cnx = connection()
                    # print(email)
                    c.execute("UPDATE `customers` SET `image`=%s WHERE `Email`=%s",
                              (thawrt(newfilename), thawrt(email)))
                    cnx.commit()
                    flash("Registration successful..!")
                    os.remove('static/userpics/' + session['profic'])

                    session['profic'] = newfilename

                    cnx.close
                    c.close()
                    return redirect(url_for("dash"))



    except Exception as e:
        print(e)
        flash("Upload Failed")
        return redirect(url_for("propic"))


@app.route('/changepw/')
def changepw():
    return render_template("changepw.html")


@app.route('/authpass/', methods=['POST'])
def authpass():
    try:
        if request.method == "POST":
            password = request.form['pword']

            newpassword = request.form['cpword']
            Truepassword = sha256_crypt.encrypt((str(newpassword)))

            if sha256_crypt.verify(password, session['userpass']):
                c, cnx = connection()
                # print(email)
                c.execute("UPDATE `customers` SET `password`=%s WHERE `Email`=%s",
                          (thawrt(Truepassword), thawrt(session['uemail'])))
                cnx.commit()
                flash("Password Has changed successfully..!")
                return redirect(url_for("dash"))
            else:
                flash("Current Passowrd is wrong..!")





    except Exception as e:
        print(e)
    return redirect(url_for("changepw"))
    flash("Save Failled..")


@app.route('/viewmsg/')
def viewmsg():
    owneremail = session['uemail']
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `message` WHERE `REmail`=%s ORDER BY `MessageId` DESC LIMIT 25",
        (thawrt(owneremail),))

    data = c.fetchall()

    session['mat'] = data
    return render_template("Viewmsg.html")


# ----------------------------------------------------Admin Section-------------------------------------------------

@app.route('/admin/')
def admin():
    return render_template("adminlogin.html")


@app.route('/adloginauth/', methods=['POST'])
def adloginauth():
    try:

        if request.method == "POST":
            usermail = request.form['email']

            firstname = request.form['fname']

            lastname = request.form['lname']

            usermobile = request.form['mobile']

            userrole = request.form['role']
            userpass1 = request.form['pass']
            userpass2 = request.form['pass2']
            print(usermail, firstname, lastname, usermobile, userrole, userpass1, userpass2)
            if userrole == 'User Role':
                flash("Please Select your Role here")

            Truepassword = sha256_crypt.encrypt((str(userpass1)))

            if userpass1 == userpass2:
                c, cnx = connection()
                c.execute("SELECT * FROM `admin` WHERE `email`=%s", (thawrt(usermail),))
                rows = c.fetchone()
                print(rows)

                if rows is 0 or rows is None:
                    # -------------------------------------------------------------- image upload

                    imgfile = request.files.getlist("pic")
                    print(imgfile)
                    capname = now.strftime("%Y-%m-%d %H-%M")
                    target = os.path.join(APP_ROOT, 'static/staff')
                    print(target)

                    if imgfile == []:
                        flash("please selct a image")
                    else:

                        if not os.path.isdir(target):
                            os.mkdir(target)

                        for file in request.files.getlist("pic"):
                            print(file)
                            filename = file.filename
                            print(filename)
                            destination = "/".join([target, filename])
                            print(destination)

                            file.save(destination)
                            newfile = 'static/staff/' + capname + filename
                            newfilename = capname + filename
                            os.rename(destination, newfile)
                            #flash("Sucess")

                    c.execute(
                        "INSERT INTO `admin`( `email`, `FirstName`, `LastName`, `Role`, `Mobile`, `pic`, `password`) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (
                            thawrt(usermail), thawrt(firstname), thawrt(lastname), thawrt(userrole),
                            thawrt(usermobile), thawrt(newfilename),
                            thawrt(Truepassword)))
                    cnx.commit()
                    flash("Registration successful..!")

                    cnx.close
                    c.close()

                    gc.collect()
                    session['logged'] = True
                    session['uname'] = usermail
                    return redirect(url_for('admindash'))

                else:
                    flash("The email already Registered,  please try another email..!")




            else:
                flash("Passowrd You Entered doesnt match..!")



        else:
            print("error")

    except Exception as e:
        print(e)
    return redirect(url_for("reguser"))


@app.route('/adminlogincheck/', methods=['POST'])
def adminlogincheck():
    try:

        if request.method == "POST":

            email = request.form['email']

            c, cnx = connection()

            c.execute(
                "SELECT * FROM `admin` WHERE `email`=%s",
                (thawrt(email),))

            data = c.fetchall()
            print(data)
            for row in data:
                myemail = row[1]
                fname = row[2]
                lname = row[3]
                Role = row[4]
                mobile = row[5]
                mypic = row[6]
                sts = row[7]
                passw = row[8]
                print(fname)

            if sha256_crypt.verify(request.form['pass'], passw):
                print(request.form['pass'])
                session['logged'] = True
                session['firstname'] = fname
                session['lastname'] = lname
                session['uemail'] = myemail
                session['myrole'] = Role
                session['mymobile'] = mobile
                session['mypic'] = mypic
                session['sts'] = sts
                session['passwordmy'] = passw


                flash("you are now Logged in...!")
                return redirect(url_for('admindash'))
            else:
                flash("Invalid credential, Plz try again..!")
                gc.collect()
                return redirect(url_for("admin"))

        return redirect(url_for("admin"))
    except Exception as e:
        print(e)
        flash("Login Error..! plz contact the Hash's Pet care Center...")

        return redirect(url_for("admin"))


@app.route('/admindash/')
def admindash():
    return render_template("Admindashboard.html")


@app.route('/reguser/')
def reguser():
    return render_template("newaccount.html")


if __name__ == '__main__':
    app.debug = True
    app.run()

import datetime
import io
import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


# -------------------------------------------------New Ap------------------------------------------------

@app.route('/cna/')
def cna():
    c, cnx = connection()
    c.execute(
        "SELECT `email` FROM `admin` WHERE `Role`='Doctor'")

    data = c.fetchall()
    print(data)

    session['docemail'] = data
    c, cnx = connection()
    c.execute(
        "SELECT `petID` FROM `pets` WHERE`ownerEmail`=%s", (thawrt(session['uemail']),))

    data1 = c.fetchall()
    session['petid'] = data1
    return render_template("ap.html")


# --------------------------------add Epoinment  Function------------------------------------

@app.route('/apauth/', methods=['POST'])
def apauth():
    if request.method == 'POST':
        reason = request.form['name']
        docmail = request.form['docid']
        petid = request.form['petid']
        petname = request.form['petname']
        today = request.form['date']
        message = request.form['message']
        frommail = session['uemail']
        sts = "on"

        c, cnx = connection()
        c.execute(
            "INSERT INTO `appointment`( `AppointmentReason`, `PetID`, `Petname`, `Doctor Mail`, `message`, `status`, `from`, `date`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                thawrt(reason), thawrt(petid), thawrt(petname), thawrt(docmail),
                thawrt(message), thawrt(sts), thawrt(frommail),
                thawrt(today)))
        cnx.commit()
        flash("New Appointment Created!")

        cnx.close
        c.close()

        gc.collect()

        return redirect(url_for("dash"))

    # ------------------------------------------------Manage Appoinments-------------------------------


@app.route('/ma/')
def ma():
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `appointment` WHERE `from`=%s and `status`='on'", (thawrt(session['uemail']),))

    data = c.fetchall()
    print(data)

    session['ap'] = data

    return render_template("Apoinmentmng.html")


# ------------------------------------Mange Apoinment functions--------------------------
@app.route('/apmng/', methods=['POST'])
def apmng():
    c, cnx = connection()
    c.execute(
        "SELECT `email` FROM `admin` WHERE `Role`='Doctor'")

    data = c.fetchall()
    print(data)

    session['docemail'] = data
    c, cnx = connection()
    c.execute(
        "SELECT `petID` FROM `pets` WHERE`ownerEmail`=%s", (thawrt(session['uemail']),))

    data1 = c.fetchall()
    session['petid'] = data1
    if request.method == 'POST':
        apid = request.form['evtid']
        session['apidss'] = apid
        c, cnx = connection()
        c.execute(
            "SELECT * FROM `appointment` WHERE  `AppointmentID`=%s", (thawrt(apid),))

        data = c.fetchall()
        print(data)

        session['ap'] = data
        for row in data:
            session['apr'] = row[1]
            session['appetid'] = row[2]
            session['appetname'] = row[3]
            session['apdoc'] = row[4]
            session['apmsg'] = row[5]
            session['apdate'] = row[8]

    return render_template("apm.html")


@app.route('/apmauth/', methods=['POST'])
def apmauth():
    if request.method == 'POST':
        reason = request.form['name']
        docmail = request.form['docid']
        petid = request.form['petid']
        petname = request.form['petname']
        today = request.form['date']
        message = request.form['message']
        if request.form['submit'] == 'btn1':
            c, cnx = connection()
            # print(email)
            c.execute(
                "UPDATE `appointment` SET `AppointmentReason`=%s,`PetID`=%s,`Petname`=%s,`Doctor Mail`=%s,`message`=%s,`date`=%s WHERE `from`=%s",
                (thawrt(reason), thawrt(petid), thawrt(petname), thawrt(docmail), thawrt(message), thawrt(today),
                 thawrt(session['uemail'])))
            cnx.commit()
            flash("Appointment Updated..!")
            return redirect(url_for("dash"))

        # -----------------------------------------------------------------Cancel Appoinment-----------------------

        if request.form['submit'] == 'btn2':
            c, cnx = connection()
            stss = "Canceled "
            # print(email)
            c.execute(
                "UPDATE `appointment` SET `status`=%s WHERE `AppointmentID`=%s",
                (thawrt(stss), thawrt(session['apidss']),))
            cnx.commit()
            flash("Appointment Canceled..!")
            return redirect(url_for("dash"))

    return redirect(url_for("apmng"))


# -----------------------------------------------Send Mail direct-----------------------------------------------------
@app.route('/sendm/')
def sendm():
    return render_template("sendusermail.html")


@app.route('/sendmfunc/', methods=['POST'])
def sendmfunc():
    if request.method == 'POST':
        frommail = session['uemail']
        subject = request.form['name']
        tomail = request.form['email']
        msg = request.form['message']
        dnt = now.strftime("%Y-%m-%d %H-%M -%p")
        stss = "unread"
        # print(subject,tomail,msg)
        c, cnx = connection()
        c.execute(
            "INSERT INTO `toadmin`( `frommail`, `tomail`, `message`, `status`, `dateandtime`,`subject`) VALUES  (%s,%s,%s,%s,%s,%s)",
            (
                thawrt(frommail), thawrt(tomail), thawrt(msg), thawrt(stss),
                thawrt(dnt), thawrt(subject)))
        cnx.commit()
        flash("Message Sent!")

        cnx.close
        c.close()

        gc.collect()

        return redirect(url_for("dash"))


# -------------------------------user out box-----------------------------------------------------------------------
@app.route('/uob/')
def uob():
    frommail = session['uemail']

    c, cnx = connection()
    c.execute(
        "SELECT * FROM `toadmin` WHERE `frommail`=%s ORDER BY `mid` DESC LIMIT 1000 ", (thawrt(frommail),))

    data = c.fetchall()

    session['uobs'] = data

    print(data)
    return render_template("userobox.html")


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
            sts = "normal"

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
                            # flash("Sucess")

                    c.execute(
                        "INSERT INTO `admin`( `email`, `FirstName`, `LastName`, `Role`, `Mobile`, `pic`,`status`, `password`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                            thawrt(usermail), thawrt(firstname), thawrt(lastname), thawrt(userrole),
                            thawrt(usermobile), thawrt(newfilename), thawrt(sts),
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
                print(sts)

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
    c, cnx = connection()
    c.execute("SELECT * FROM `appointment` WHERE `status`='on'")

    data = c.fetchall()
    print(data)
    for row in data:
        session['apoinID'] = row[0]

    session['appoin'] = data
    return render_template("Admindashboard.html")


@app.route('/reguser/')
def reguser():
    return render_template("newaccount.html")


@app.route('/changeadp/')
def changeadp():
    return render_template("changeadminpassword.html")


@app.route('/changemypass/', methods=['POST'])
def changemypass():
    try:
        if request.method == "POST":
            password = request.form['pword']

            newpassword = request.form['cpword']
            Truepassword = sha256_crypt.encrypt((str(newpassword)))

            if sha256_crypt.verify(password, session['passwordmy']):
                c, cnx = connection()
                # print(email)
                c.execute("UPDATE `admin` SET `password`=%s WHERE `email`=%s",
                          (thawrt(Truepassword), thawrt(session['uemail'])))
                cnx.commit()
                flash("Password Has changed successfully..!")
                return redirect(url_for("admindash"))
            else:
                flash("Current Passowrd is wrong..!")





    except Exception as e:
        print(e)
    return redirect(url_for("changeadp"))
    flash("Save Failled..")


@app.route('/deluserad/')
def deluserad():
    sts = "normal"
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `admin` WHERE `status`=%s",
        (thawrt(sts),))

    data = c.fetchall()
    print(data)

    session['users'] = data
    return render_template("deluserad.html")


@app.route('/deladconf/', methods=['POST'])
def deladconf():
    if request.method == 'POST':
        userid = request.form['uid']

        if userid == "Select User ID":
            flash("Please Select User ID")
        else:

            c, cnx = connection()
            c.execute(
                "DELETE FROM `admin` WHERE`id`=%s",
                (thawrt(userid),))
            cnx.commit()
            flash("Record has been Successfully deleted..!")

    return redirect(url_for("deluserad"))


@app.route('/searchpet/')
def searchpet():
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `pets` ")

    data = c.fetchall()

    session['allpet'] = data

    print(data)

    return render_template("searchpet.html")


@app.route('/searchnow/', methods=['POST'])
def searchnow():
    if request.method == 'POST':
        so = request.form['optradio']
        search = request.form['search']
        print(search)

        if so:
            # usermail

            c, cnx = connection()
            c.execute(
                "SELECT * FROM `pets` WHERE `ownerEmail`=%s",
                (thawrt(search),))

            data = c.fetchall()

            session['allpet'] = data

            return render_template("searchresult.html")
        else:
            # petid
            c, cnx = connection()
            c.execute(
                "SELECT * FROM `pets` WHERE `petID`=%s",
                (thawrt(search),))

            data = c.fetchall()

            session['allpet'] = data

            return render_template("searchresult.html")

    return redirect(url_for("searchpet"))


# ----------------------------------------------send message---------------------------------------

@app.route('/sendmessage/')
def sendmessage():
    return render_template("sendnewmessage.html")


@app.route('/authsendmsg/', methods=['POST'])
def authsendmsg():
    if request.method == 'POST':
        toname = request.form['name']
        toemail = request.form['email']
        petid = request.form['petid']
        petname = request.form['petname']
        today = request.form['date']
        message = request.form['message']
        frommail = session['uemail']
        sts = "unread"

        c, cnx = connection()
        c.execute(
            "INSERT INTO `message`( `FromMail`, `REmail`, `Message`, `Status`, `date`, `petid`, `petname`, `OwnerName`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                thawrt(frommail), thawrt(toemail), thawrt(message), thawrt(sts),
                thawrt(today), thawrt(petid), thawrt(petname),
                thawrt(toname)))
        cnx.commit()
        flash("Mesage Sent!")

        smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
        smtp_ssl_port = 465
        username = "hashspetcare1@gmail.com"
        password = "Hashpet@2018"
        sender = "hashspetcare1@gmail.com"
        targets = ["hashspetcare1@gmail.com", toemail]

        msg = MIMEText("Hi Mr. " + toname + "." + "about your pet " + petname + "." + message)
        msg['Subject'] = 'Pet Alert'
        msg['From'] = sender
        msg['To'] = ', '.join(targets)

        server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
        server.login(username, password)
        server.sendmail(sender, targets, msg.as_string())
        server.quit()

        cnx.close
        c.close()

        gc.collect()

        print(toname, toemail, today, petid, petname, message)

        return redirect(url_for("admindash"))


@app.route('/addevents/')
def addevents():
    return render_template("events.html")


@app.route('/addevt/', methods=['POST'])
def addevt():
    if request.method == 'POST':
        evtname = request.form['name']
        evtdate = request.form['edate']
        evttime = request.form['etime']
        evtdes = request.form['ta1']
        evtven = request.form['v']
        sts = "open"

        c, cnx = connection()
        c.execute(
            "INSERT INTO `events`( `eventname`, `eventdate`, `eventtime`, `eventdes`, `venue`, `status`) VALUES (%s,%s,%s,%s,%s,%s)",
            (
                thawrt(evtname), thawrt(evtdate),
                thawrt(evttime), thawrt(evtdes), thawrt(evtven),
                thawrt(sts)))
        cnx.commit()
        flash("New Event Added")

        cnx.close
        c.close()

        gc.collect()

        return redirect(url_for("admindash"))


# ----------------------------------------------------------------------------------------------------

@app.route('/mngevt/')
def mngevt():
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `events` WHERE `status`='open' ORDER BY `eventid` DESC LIMIT 100 ")

    data = c.fetchall()

    session['allevt'] = data

    print(data)
    return render_template("eventsmng.html")


# ---------------------------------------------------Manage Event Main page-----------------------------
@app.route('/selectmng/', methods=['POST'])
def selectmng():
    if request.method == 'POST':
        eventid = request.form['evtid']
        session['eids'] = eventid

        if eventid == 'Select Event ID':
            flash("Please Select a Event ID")
            return redirect(url_for("mngevt"))
        else:
            c, cnx = connection()
            c.execute(
                "SELECT * FROM `events` WHERE `eventid`=%s",
                (thawrt(eventid),))
            data = c.fetchall()
            for row in data:
                session['selevtname'] = row[1]
                session['seldate'] = row[2]
                session['seltime'] = row[3]
                session['seldes'] = row[4]
                session['selv'] = row[5]

            return render_template("Mangeeventsmain.html")


@app.route('/mngfunc/', methods=['POST'])
def mngfunc():
    if request.method == 'POST':

        if request.form['submit'] == 'btn1':
            print("1")

            evtname = request.form['name']
            evtdate = request.form['edate']
            evttime = request.form['etime']
            evtdes = request.form['ta1']
            evtven = request.form['v']
            c, cnx = connection()
            # print(email)
            c.execute(
                "UPDATE `events` SET `eventname`=%s,`eventdate`=%s,`eventtime`=%s,`eventdes`=%s,`venue`=%s WHERE `eventid`=%s",
                (thawrt(evtname), thawrt(evtdate), thawrt(evttime), thawrt(evtdes), thawrt(evtven),
                 thawrt(session['eids'])))
            cnx.commit()
            flash("Event Updated..!")
            return redirect(url_for("admindash"))
        # --------------------------------------Update event-------------------------------

        if request.form['submit'] == 'btn2':
            print("2")
            c, cnx = connection()
            c.execute(
                "DELETE FROM `events` WHERE `eventid`=%s",
                (thawrt(session['eids']),))
            cnx.commit()
            flash("Record has been Successfully deleted..!")
            return redirect(url_for("admindash"))

        # ---------------------------------Delete Event----------------------------------------

        if request.form['submit'] == 'btn3':
            print("3")
            de = "done"
            c, cnx = connection()
            # print(email)
            c.execute(
                "UPDATE `events` SET `status`=%s WHERE `eventid`=%s",
                (thawrt(de), thawrt(session['eids'])))
            cnx.commit()
            flash("Good Job..!")
            return redirect(url_for("admindash"))
        # ---------------------------------------------Event Done----------------------------------

        return redirect(url_for("admindash"))


# --------------------------------------------------view all events---------------------------
@app.route('/vae/')
def vae():
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `events` ORDER BY `eventid` DESC LIMIT 1000")

    data = c.fetchall()

    session['allevt'] = data

    print(data)
    return render_template("allevt.html")


# --------------------------------------------------View Current EVEnts---------------
@app.route('/vce/')
def vce():
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `events` WHERE `status`='open' ORDER BY `eventid` DESC LIMIT 1000")

    data = c.fetchall()

    session['allevt'] = data

    print(data)
    return render_template("vce.html")


# -----------------------------------View Done Events--------------------------------------
@app.route('/vde/')
def vde():
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `events` WHERE `status`='done' ORDER BY `eventid` DESC LIMIT 1000")

    data = c.fetchall()

    session['allevt'] = data

    print(data)
    return render_template("vde.html")


# -------------------------------------outboc-------------------------------------------

@app.route('/obox/')
def obox():
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `message` WHERE `FromMail`=%s ORDER BY `MessageId` DESC LIMIT 1000",
        (thawrt(session['uemail']),))

    data = c.fetchall()

    session['allevt'] = data

    print(data)
    return render_template("obox.html")


# --------------------------------------------------make done appoinment-------------------------
@app.route('/donejob/', methods=['POST'])
def donejob():
    if request.method == 'POST':
        eventid = request.form['evtid']
        print(eventid)
        c, cnx = connection()
        status = "done"
        # print(email)
        c.execute(
            "UPDATE `appointment` SET `status`=%s WHERE `AppointmentID`=%s",
            (thawrt(status), thawrt(eventid)))
        cnx.commit()
        flash("Done..!")
        return redirect(url_for("admindash"))

    return redirect(url_for("admindash"))


# ---------------------------------------------view all appoinment--------------------
@app.route('/vaa/')
def vaa():
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `appointment`  ORDER BY `AppointmentID` DESC LIMIT 1000")

    data = c.fetchall()

    session['allapi'] = data

    print(data)
    return render_template("Viewallappoinment.html")


# --------------------------------------view canceled-----------------------------------

@app.route('/vca/')
def vca():
    c, cnx = connection()
    c.execute(
        "SELECT * FROM `appointment` where `status`='Canceled' ORDER BY `AppointmentID` DESC LIMIT 1000")

    data = c.fetchall()

    session['canapp'] = data

    print(data)
    return render_template("viewcancelappoinment.html")


# -------------------------------recived Messages-------------------------------------------------------------

@app.route('/mymsg/')
def mymsg():
    c, cnx = connection()
    c.execute("SELECT * FROM `toadmin` WHERE `status`='unread'")

    data = c.fetchall()
    print(data)

    session['mymsgs'] = data

    return render_template("recivedmsg.html")


@app.route('/mymsgfunc/', methods=['POST'])
def mymsgfunc():
    if request.method == 'POST':
        msgid = request.form['msgid']
        print(msgid)
        c, cnx = connection()
        status = "Readed"
        # print(email)
        c.execute(
            "UPDATE `toadmin` SET `status`=%s WHERE `mid`=%s",
            (thawrt(status), thawrt(msgid)))
        cnx.commit()
        flash("Done..!")
        return redirect(url_for("admindash"))

    return redirect(url_for("admindash"))


@app.route('/allmymsg/')
def allmymsg():
    c, cnx = connection()
    c.execute("SELECT * FROM `toadmin` ORDER BY `mid` DESC LIMIT 1000 ")

    data = c.fetchall()
    print(data)

    session['allmymsgs'] = data

    return render_template("allrecivedmsg.html")


@app.route('/conta/', methods=['POST'])
def conta():
    email = request.form['email']
    name = request.form['name']
    mess = request.form['message']

    smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
    smtp_ssl_port = 465
    username = "hashspetcare1@gmail.com"
    password = "Hashpet@2018"
    sender = "hashspetcare1@gmail.com"
    targets = ["hashspetcare1@gmail.com", email]

    msg = MIMEText(
        "Hi Mr. " + name + "." + "thank you for mailing us. we will reply soon for your following message." + mess)
    msg['Subject'] = 'Pet Alert'
    msg['From'] = sender
    msg['To'] = ', '.join(targets)

    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(sender, targets, msg.as_string())
    server.quit()

    gc.collect()

    return redirect(url_for("umain"))


if __name__ == '__main__':
    app.debug = True
    app.run()

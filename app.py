from flask import Flask, session, flash, redirect, url_for, escape, request, render_template, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, RadioField
from wtforms.validators import DataRequired, ValidationError
from wtforms import validators
import MySQLdb
from MySQLdb import escape_string as thwart
import json
from passlib.hash import sha256_crypt
import gc
import datetime
import re




app = Flask(__name__)


# Initialize Form For Admin
class adminForm(FlaskForm): 
    adminUsername = StringField(validators=[DataRequired()],render_kw={"placeholder": "Admin Username"}, id="mc-password")
    adminPassword = PasswordField(validators=[DataRequired()],render_kw={"placeholder": "Admin Password"}, id="mc-password")

#Initialize Form For Deacons
class deaconsForm(FlaskForm):
    deaconUsername = StringField(validators=[DataRequired()],render_kw={"placeholder": "Deacon's Username"}, id="mc-password")
    deaconPassword = PasswordField(validators=[DataRequired()],render_kw={"placeholder": "Deacon ID"}, id="mc-password")
#Initialize Form for Visitors
class visitorsForm(FlaskForm):
   fullname = StringField(validators=[DataRequired()],render_kw={"placeholder": "Full Name"}, id="Full Name")
   phone = StringField(validators=[DataRequired()],render_kw={"placeholder": "Phone"}, id="phone-number")
   address = StringField(validators=[DataRequired()],render_kw={"placeholder": "Address"}, id="address")
   workPlace = StringField(validators=[DataRequired()],render_kw={"placeholder": "Place of Work"}, id="workplace")
   visitor = BooleanField()
   counselee = BooleanField()
   salvation = BooleanField() #id="salvation"
   rededication = BooleanField() #id="rededication"
   bhs = BooleanField() #id="bhs"
   joinFWC = RadioField('', choices=[('yes','Yes'),('no','No')]) #id="joinFWC-0 or joinFWC-1"
   prayerNeeds = TextAreaField(validators=[DataRequired()],render_kw={"placeholder": "What should we help you pray about?"}, id="prayerNeeds")

class enrollForm(FlaskForm):
    adminPassword = PasswordField(validators=[DataRequired()],render_kw={"placeholder": "Your Password"}, id="mc-password")
    adminUsername = StringField(validators=[DataRequired()],render_kw={"placeholder": "Your Username"}, id="mc-password")
    name = StringField(validators=[DataRequired()],render_kw={"placeholder": "Your Name"}, id="mc-password")
    deacon = StringField(validators=[DataRequired()],render_kw={"placeholder": "Coordinator Under"}, id="mc-password")

class cdForm(FlaskForm):
    cdUsername = StringField(validators=[DataRequired()],render_kw={"placeholder": "Coordinator Username"}, id="mc-password")
    cdPassword = PasswordField(validators=[DataRequired()],render_kw={"placeholder": "Password"}, id="mc-password")

class cgForm(FlaskForm):
    cgUsername = StringField(validators=[DataRequired()],render_kw={"placeholder": "CaregroupLead Username"}, id="mc-password")
    cgPassword = PasswordField(validators=[DataRequired()],render_kw={"placeholder": "Password"}, id="mc-password")

'''
#Initialize form for co-ordinators    
class cordForm(FlaskForm):
    cordID = StringField(validators=[DataRequired()], render_kw={"placeholder": "Coordinator ID"})

    
#Initialize Form For care group
class cgForm(FlaskForm):
    cgID = PasswordField(validators=[DataRequired()], render_kw={"placeholder": Caregroup ID"})'''
     

# Database Configurations
conn = MySQLdb.connect(host="localhost", 
                    user="root", 
                    passwd="jccofficial", 
                    db="fwclugbeDB")
cur = conn.cursor()

visitor = "Yes"
counselee = "Yes"
visited = "Visited"
notVisited = "NULL"

#retrieve count of total visitors
totalVisitors = cur.execute(
                    """SELECT COUNT(*) FROM visitors WHERE visitor = (%s)""", [visitor])
totalVisitors = cur.fetchone()[0]
#retrieve count of total counselee
totalCounselees = cur.execute(
                    """SELECT COUNT(*) FROM visitors WHERE counselee = (%s)""", [counselee])
totalCounselees = cur.fetchone()[0]
#retrieve total count of visited 
totalVisits = cur.execute(
                    """SELECT COUNT(*) FROM visitors WHERE visited = (%s)""", [visited])
totalVisits = cur.fetchone()[0]
#retrieve total count of not visited
totalNotVisited = cur.execute(
                    """SELECT COUNT(*) FROM visitors WHERE visited = (%s)""", [notVisited])
totalNotVisited = cur.fetchone()[0]

@app.route('/')
def home():
    return render_template('index.html', totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)

@app.route('/admin-login', methods=["GET", "POST"])
def adminLogin():
    form = adminForm()
    if 'adminPassword' in session:
        return redirect(url_for('adminPanel'))
    elif request.method == 'GET':
        return render_template('admin-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
    elif request.method == 'POST': 
        if form.validate_on_submit():
            username = request.form['adminUsername']
            print(username)
            passwordToVerify  = request.form['adminPassword']
            #use this sha256_crypt.verify(adminPassword, password)
            print(passwordToVerify)
            check = cur.execute(
                    """SELECT password FROM admins WHERE username = (%s)""", [username]) # CHECKS IF ADMIN ID EXISTS
            try:
                check = cur.fetchone()[0]
                print(check)
            except Exception as e:
                flash('User not found')
                return render_template('admin-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
            
                #password = str(check[3:-3])
            if sha256_crypt.verify(request.form['adminPassword'], check):
                session['adminPassword'] = request.form['adminUsername']
                data = cur.execute(
                """SELECT fullname, phone, address, sex, age, visitor,counselee, assigned_deacon, assigned_cd, assigned_cg, visited, remark FROM visitors""")
                data = cur.fetchall()
                return render_template('admin-panel.html', data=data, form=visitorsForm(), sex=['Choose','Male','Female'], maritalStatus=['Choose','Single','Married'], age=['Below 20','20-29','30-39','40-49','50-59','Above 60'], edQual=['OL','ND','NCE','Bsc','Msc','Phd','Other'], zDeac=['Choose','Deacon Akperawa Essien','Deacon Victor Kadiri', 'Deacon Abayomi Kuyebi','Deacon Rex Ogolo', 'Deacon Bidi Zachariah','Deacon Aderinkomi John'],totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
            flash('Invalid Login')
            return render_template('admin-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
        else:
            flash('All fields are required.')
            return render_template('admin-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)  

@app.route('/admin-panel', methods=["GET", "POST"])
def adminPanel():
    form = visitorsForm()
    if 'adminPassword' not in session:
        return redirect(url_for('adminLogin'))
    elif request.method == 'GET':
        data = cur.execute(
                    """SELECT fullname, phone, address, sex, age, visitor, counselee, assigned_deacon, assigned_cd, assigned_cg,visited, remark FROM visitors""")
        data = cur.fetchall()
        return render_template('admin-panel.html',form=form, data=data, sex=['Choose','Male','Female'], maritalStatus=['Choose','Single','Married'], age=['Below 20','20-29','30-39','40-49','50-59','Above 60'], edQual=['OL','ND','NCE','Bsc','Msc','Phd','Other'], zDeac=['Choose','Deacon Akperawa Essien','Deacon Victor Kadiri', 'Deacon Abayomi Kuyebi','Deacon Rex Ogolo','Deacon Bidi Zachariah','Deacon Aderinkomi John'],totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
    
@app.route('/submit-visitor', methods=['POST'])
def submitVisitor():
    form = visitorsForm()
    if form.validate_on_submit():
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        fullname  = str(request.form['fullname'].strip())
        print(fullname)
        phone  = str(request.form['phone'].strip())
        print(phone)
        sex = request.form.get('select_sex')
        print(sex)
        status = request.form.get('select_status')
        print(status)
        age = request.form.get('select_age')
        print(age)
        edQual = request.form.get('select_edQual')
        print(edQual)
        address  = str(request.form['address'].strip())
        print(address)
        workplace  = str(request.form['workPlace'].strip())
        print(workplace)
        visitor = str(form.visitor.data)
        if visitor == "True":
            visitor = "Yes"
        elif visitor == "False":
            visitor = "No"
        print(visitor)
        counselee = str(form.counselee.data)
        if counselee == "True":
            counselee = "Yes"
        elif counselee == "False":
            counselee = "No"
        print(counselee)
        salvation = str(form.salvation.data)
        if salvation == "True":
            salvation = "Yes"
        elif salvation == "False":
            salvation = "No"
        print(salvation)
        rededication = str(form.rededication.data)
        if rededication == "True":
            rededication = "Yes"
        elif rededication == "False":
            rededication = "No"
        print(rededication)
        bhs  = str(form.bhs.data)
        if bhs == "True":
            bhs = "Yes"
        elif bhs == "False":
            bhs = "No"
        print(bhs)
        joinFWC = form.joinFWC.data
        print(joinFWC)
        prayerNeeds = request.form['prayerNeeds']
        print(prayerNeeds)
        deacon = request.form.get('select_deacon')
        print(deacon)
        assigned_cd = "NULL"
        assigned_cg = "NULL"
        visited = "NULL"
        remark = "NULL"
        data = cur.execute(
                        """INSERT INTO visitors (date, fullname,sex, age, m_status, phone, address, edu_q, workplace, visitor, counselee, salvation, rededication, bhs, joinFWC, prayerneed, assigned_deacon, assigned_cd, assigned_cg, visited, remark)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""" ,(date, fullname, sex,age, status, phone, address, edQual, workplace, visitor, counselee, salvation, rededication, bhs, joinFWC, prayerNeeds, deacon, assigned_cd, assigned_cg, visited, remark ))# Update Visitors table.
        conn.commit()
        gc.collect()
        return jsonify(data={'':'Visitor added Successfully'})
    return jsonify(data={'':'Fields marked required must be filled out'})

@app.route('/enroll-deacon', methods=["GET", "POST"])
def enrollDeacon():
    form = enrollForm()
    if request.method == 'GET':
        return render_template('enroll-deacon.html', form = form, totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
    elif request.method == 'POST':
        name = request.form['name']
        username = request.form['adminUsername']
        cdUnder = request.form['deacon']
        password = request.form['adminPassword']
        print(password)
        password = sha256_crypt.hash(str(password))
        data = cur.execute(
                        """INSERT INTO cg_leaders (name, username, cd_under, password)
                        VALUES (%s,%s,%s,%s)""" ,(name, username, cdUnder, password))# Update Admins table.
        conn.commit()
        gc.collect()
        return("Record added Successfully") 

@app.route('/admin-logout')
def adminLogout():
    session.pop('adminPassword', None)
    return redirect(url_for('adminLogin'))

@app.route('/deacon-login', methods=["GET", "POST"])
def deaconLogin():
    form = deaconsForm()
    if 'deaconPassword' in session:
        return redirect(url_for('deaconPanel'))
    if request.method == 'GET':
        return render_template('deacon-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
    elif request.method == 'POST':
        if not form.validate_on_submit():
            flash('All fields are required.')
            return render_template('deacon-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
        username = request.form['deaconUsername']
        print(username)
        passwordToVerify  = request.form['deaconPassword']
        print(passwordToVerify)
        #use this sha256_crypt.verify(adminPassword, password)
        check = cur.execute(
                """SELECT password FROM deacons WHERE username = (%s)""", [username]) # CHECKS IF ADMIN ID EXISTS
        try:
            check = cur.fetchone()[0]
            print(check)
        except Exception as e:
            flash("User not found")
            return render_template('deacon-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
        #password = str(check[3:-3])
        if sha256_crypt.verify(request.form['deaconPassword'], check):
            session['deaconPassword'] = request.form['deaconUsername']
            name = cur.execute(
            """SELECT name FROM deacons WHERE username = (%s)""", [username])
            name = cur.fetchone()[0]
            print(name)
            data = cur.execute(
            """SELECT name FROM coordinators WHERE deacon_under = (%s)""", [name])
            data = cur.fetchall()
            newData = [item[0] for item in data]
            print(newData)
            checkValue = "NULL"
            newVisitors = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee FROM visitors WHERE assigned_deacon = (%s) AND assigned_cd = (%s)""", ([name], [checkValue]))
            newVisitors = cur.fetchall()
            oldVisitors = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee, assigned_cd FROM visitors WHERE assigned_deacon = (%s) AND NOT assigned_cd = (%s)""", ([name], [checkValue]))
            oldVisitors = cur.fetchall()
            return render_template('deacon-panel.html', newData=newData, newVisitors=newVisitors, oldVisitors=oldVisitors, name=name, totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
        flash("Invalid Credentials")
        return render_template('deacon-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)

@app.route('/deacon-panel', methods=["GET", "POST"])
def deaconPanel():
    if 'deaconPassword' not in session:
        return redirect(url_for('deaconLogin'))
    elif request.method == 'GET':
        username = session['deaconPassword']
        name = cur.execute(
                    """SELECT name FROM deacons WHERE username = (%s)""", [username])
        name = cur.fetchone()[0]
        print(name)
        data = cur.execute(
        """SELECT name FROM coordinators WHERE deacon_under = (%s)""", [name])
        data = cur.fetchall()
        newData = [item[0] for item in data]
        print(newData)
        checkValue = "NULL"
        newVisitors = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee FROM visitors WHERE assigned_deacon = (%s) AND assigned_cd = (%s)""", ([name], [checkValue]))
        newVisitors = cur.fetchall()
        oldVisitors = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee, assigned_cd FROM visitors WHERE assigned_deacon = (%s) AND NOT assigned_cd = (%s)""", ([name], [checkValue]))
        oldVisitors = cur.fetchall()

        return render_template('deacon-panel.html', newData=newData, newVisitors=newVisitors, oldVisitors=oldVisitors, name=name,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)

@app.route('/assign-cd', methods=["POST"])
def assignCd():
    data = request.json
    data = str(data)
    print(data)
    newData = ''.join( c for c in data if  c not in "'()20?:!/;" )
    print(newData)
    toReplace = ['%']
    for char in toReplace:
        newData = newData.replace("%"," ")
        print(newData)
    newData = newData.split('=', 1)
    print(newData)
    visitor,coordinator = newData
    visitor = visitor.strip()
    print(visitor) 
    coordinator = coordinator.strip()
    print(coordinator)

    update = cur.execute ("""
            UPDATE visitors
            SET assigned_cd=%s
            WHERE fullname=%s
            """, (coordinator,visitor))
    conn.commit()
    gc.collect()
    return jsonify(data={'':'Coordinator assigned successfully'})

@app.route('/assign-cg', methods=["POST"])
def assignCg():
    data = request.json
    data = str(data)
    print(data)
    newData = ''.join( c for c in data if  c not in "'()20?:!/;" )
    print(newData)
    toReplace = ['%']
    for char in toReplace:
        newData = newData.replace("%"," ")
        print(newData)
    newData = newData.split('=', 1)
    print(newData)
    visitor,careGroup = newData
    visitor = visitor.strip()
    print(visitor) 
    careGroup = careGroup.strip()
    print(careGroup)

    update = cur.execute ("""
            UPDATE visitors
            SET assigned_cg=%s
            WHERE fullname=%s
            """, (careGroup,visitor))
    conn.commit()
    gc.collect()
    return jsonify(data={'':'Caregroup Lead assigned successfully'})

@app.route('/confirm-visit', methods=["POST"])
def confirmVisit():
    data = request.json
    data = str(data)
    print(data)
    newData = ''.join( c for c in data if  c not in "'()20?:!/;" )
    print(newData)
    toReplace = ['%']
    for char in toReplace:
        newData = newData.replace("%"," ")
        print(newData)
    newData = newData.split('=', 1)
    print(newData)
    visitor,comment = newData
    visitor = visitor.strip()
    print(visitor) 
    comment = comment.strip()
    comment = str(comment + "\nDOV: "+ datetime.datetime.today().strftime('%Y-%m-%d'))
    print(comment)
    visited = "Visited"

    update = cur.execute ("""
            UPDATE visitors
            SET visited=%s, remark=%s
            WHERE fullname=%s
            """, (visited,comment,visitor))
    conn.commit()
    gc.collect()
    return jsonify(data={'':'Visit Status, Successfully Updated'})

@app.route('/deacon-logout')
def deaconLogout():
    session.pop('deaconPassword', None)
    return redirect(url_for('deaconLogin'))


@app.route('/coordinator', methods=["GET", "POST"])
def cdPanel():
    if 'cdUsername' not in session:
        return redirect(url_for('cdLogin'))
    elif request.method == 'GET':
        username = session['cdUsername']
        checkValue = "NULL"
        print(username)
        name = cur.execute(
                        """SELECT name FROM coordinators WHERE username = (%s)""", [username])
        name = cur.fetchone()[0]
        deaconUnder = cur.execute(
                        """SELECT deacon_under FROM coordinators WHERE name = (%s)""",[name])
        deaconUnder = cur.fetchone()[0]
        data = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee FROM visitors WHERE assigned_cd = (%s) AND assigned_cg = (%s)""",([name],[checkValue]))
        data = cur.fetchall()
        cgLeads = cur.execute(
                    """SELECT name FROM cg_leaders WHERE cd_under = (%s)""",[name])
        cgLeads = cur.fetchall()
        if cgLeads == ():
            cgLeads = ["No records"]
        oldVisitors = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee, assigned_cg FROM visitors WHERE assigned_cd = (%s) AND NOT assigned_cg = (%s)""", ([name], [checkValue]))
        oldVisitors = cur.fetchall()
        return render_template('coordinator.html', data=data, name=name, oldVisitors=oldVisitors, cgLeads=cgLeads,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)

@app.route('/cd-login', methods=['GET','POST'])
def cdLogin():
    form = cdForm()
    if 'cdUsername' in session:
        return redirect(url_for('cdPanel'))
    elif request.method == 'GET':
        return render_template('cd-login.html',form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
    elif request.method == 'POST': 
        if form.validate_on_submit():
            username = request.form['cdUsername']
            checkValue = "NULL"
            print(username)
            passwordToVerify  = request.form['cdPassword']
            #use this sha256_crypt.verify(adminPassword, password)
            print(passwordToVerify)
            check = cur.execute(
                    """SELECT password FROM coordinators WHERE username = (%s)""", [username]) # CHECKS IF ADMIN ID EXISTS
            try:
                check = cur.fetchone()[0]
                print(check)
            except Exception as e:
                flash('User not found')
                return render_template('cd-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
                #password = str(check[3:-3])
            if sha256_crypt.verify(request.form['cdPassword'], check):
                session['cdUsername'] = request.form['cdUsername']
                name = cur.execute(
                    """SELECT name FROM coordinators WHERE username = (%s)""", [username])
                name = cur.fetchone()[0]
                deaconUnder = cur.execute(
                    """SELECT deacon_under FROM coordinators WHERE name = (%s)""",[name])
                deaconUnder = cur.fetchone()[0]
                print(deaconUnder)
                data = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee FROM visitors WHERE assigned_cd = (%s) AND assigned_cg = (%s)""",([name], [checkValue]))
                data = cur.fetchall()
                cgLeads = cur.execute(
                    """SELECT name FROM cg_leaders WHERE cd_under = (%s)""",[name])
                cgLeads = cur.fetchall()
                if cgLeads == ():
                    cgLeads = ["No records"]
                oldVisitors = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee, assigned_cg FROM visitors WHERE assigned_cd = (%s) AND NOT assigned_cg = (%s)""", ([name], [checkValue]))
                oldVisitors = cur.fetchall()
                return render_template('coordinator.html',data=data, name=name, oldVisitors=oldVisitors, cgLeads=cgLeads,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
            flash('Invalid Credentials')
            return render_template('cd-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
        flash("All fields are required")
        return render_template('cd-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)

@app.route('/cd-logout')
def cdLogout():
    session.pop('cdUsername', None)
    return redirect(url_for('cdLogin'))

@app.route('/cg-login', methods=['GET','POST'])
def cgLogin():
    form = cgForm()
    if 'cgUsername' in session:
        return redirect(url_for('cgPanel'))
    elif request.method == 'GET':
        return render_template('cg-login.html',form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
    elif request.method == 'POST': 
        if form.validate_on_submit():
            username = request.form['cgUsername']
            checkValue = "NULL"
            print(username)
            passwordToVerify  = request.form['cgPassword']
            #use this sha256_crypt.verify(adminPassword, password)
            print(passwordToVerify)
            check = cur.execute(
                    """SELECT password FROM cg_leaders WHERE username = (%s)""", [username]) # CHECKS IF ADMIN ID EXISTS
            try:
                check = cur.fetchone()[0]
                print(check)
            except Exception as e:
                flash('User not found')
                return render_template('cg-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
            if sha256_crypt.verify(request.form['cgPassword'], check):
                session['cgUsername'] = request.form['cgUsername']
                name = cur.execute(
                    """SELECT name FROM cg_leaders WHERE username = (%s)""", [username])
                name = cur.fetchone()[0]
                coordinatorUnder = cur.execute(
                    """SELECT cd_under FROM cg_leaders WHERE name = (%s)""",[name])
                coordinatorUnder = cur.fetchone()[0]    
                data = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee FROM visitors WHERE assigned_cg = (%s) AND visited = (%s)""",([name],[checkValue]))
                data = cur.fetchall()
                oldVisitors = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee, prayerneed, visited FROM visitors WHERE assigned_cg = (%s) AND NOT visited = (%s)""",([name],[checkValue]))
                oldVisitors = cur.fetchall()
                return render_template('cg-panel.html',data=data, name=name, oldVisitors=oldVisitors,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
            flash('Invalid Credentials')
            return render_template('cg-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)
        flash("All Fields Are Required!")
        return render_template('cg-login.html', form=form,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)

@app.route('/cg-panel', methods=["GET", "POST"])
def cgPanel():
    if 'cgUsername' not in session:
        return redirect(url_for('cgLogin'))
    elif request.method == 'GET':
        username = session['cgUsername']
        checkValue = "NULL"
        print(username)
        name = cur.execute(
                        """SELECT name FROM cg_leaders WHERE username = (%s)""", [username])
        name = cur.fetchone()[0]
    
        data = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee FROM visitors WHERE assigned_cg = (%s) AND visited = (%s)""",([name],[checkValue]))
        data = cur.fetchall()
        oldVisitors = cur.execute(
                    """SELECT fullname, sex, age, phone, address, visitor, counselee, prayerneed, visited FROM visitors WHERE assigned_cg = (%s) AND NOT visited = (%s)""",([name],[checkValue]))
        oldVisitors = cur.fetchall()
        return render_template('cg-panel.html', data=data, name=name, oldVisitors=oldVisitors,totalVisitors=totalVisitors, totalCounselees=totalCounselees,totalVisits=totalVisits,totalNotVisited=totalNotVisited)

@app.route('/cg-logout')
def cgLogout():
    session.pop('cgUsername', None)
    return redirect(url_for('cgLogin'))

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run(debug=True)
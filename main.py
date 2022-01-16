from enum import unique
from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,LoginManager,login_manager
from flask_login import login_required,current_user
from flask_mail import Mail
import json
import os
local_server=True #my db cxn
 #initialising application
app=Flask(__name__)
app.secret_key='AjinSumesh'

with open(os.path.abspath('configuration.json'),'r') as c:
    params=json.load(c)["params"]

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)


app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/covid_bed_slot'

#for getting specific unique access
login_manager=LoginManager(app)
login_manager.login_view='login'

db=SQLAlchemy(app)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Hospital_user.query.get(int(user_id))

class User(db.Model,UserMixin ):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String,unique=True)
    email=db.Column(db.String,unique=True)
    password=db.Column(db.String)

class Hospital_user(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    h_code=db.Column(db.String)
    email=db.Column(db.String)
    password=db.Column(db.String)


class Hospital_data(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    h_code=db.Column(db.String,unique=True)
    h_name=db.Column(db.String)
    normal_beds=db.Column(db.Integer)
    hicu_beds=db.Column(db.Integer)
    icu_beds=db.Column(db.Integer)
    vent_beds=db.Column(db.Integer)
    
class Patient_booking(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String,unique=True)
    bed_type=db.Column(db.String)
    h_code=db.Column(db.String)
    spo2=db.Column(db.Integer)
    p_name=db.Column(db.String)
    p_phno=db.Column(db.String)
    p_address=db.Column(db.String)


class Trigr(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    h_code=db.Column(db.String)
    normal_beds=db.Column(db.Integer)
    hicu_beds=db.Column(db.Integer)
    icu_beds=db.Column(db.Integer)
    vent_beds=db.Column(db.Integer)
    Cred_opn =db.Column(db.String)
    Date=db.Column(db.String)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/usersignup',methods=['POST','GET'])
def user_signup():
    if request.method=='POST':
        srfid=request.form.get('srf')
        email=request.form.get('email')
        password=request.form.get('password')
        encpassword=generate_password_hash(password)
        user1=User.query.filter_by(srfid=srfid).first() #To check whether the SRFID and email Id already exists in the table
        user=User.query.filter_by(email=email).first()
        if user or user1:
            flash("Email or SRF ID is already taken","warning")
            return render_template("usersignup.html")
        new_user=db.engine.execute(f"INSERT INTO user(srfid,email,password) VALUES('{srfid}','{email}','{encpassword}')")
        
        flash("Signup Successful. Please Login","info")
        return render_template('userlogin.html')
    return render_template('usersignup.html')



@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        srfid=request.form.get('srf')
        password=request.form.get('password')
        user=User.query.filter_by(srfid=srfid).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")
    return render_template("userlogin.html")

@app.route('/logout')
@login_required
def user_logout():
    logout_user()
    flash("Logout successful","warning")
    return redirect(url_for('login'))

@app.route('/hospitallogin',methods=['POST','GET'])
def hospital_login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user=Hospital_user.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Successful","info")
            return render_template('index.html')
        else:
            flash("Invalid Credentials","danger")
            return render_template('hospitallogin.html')
    return render_template('hospitallogin.html')



@app.route('/admin',methods=['POST','GET'])
def admin_login():
    
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password') 
        if(username==params['username'] and password==params['password']):
            session['user']=username
            flash("login successful","info")
            return render_template('addhospitaluser.html')
        else:
            flash("Invalid Credentials","warning")
    return render_template('admin.html')

@app.route('/addhospitaluser',methods=['POST','GET'])
def add_Hospital_user():
    
    if('user' not in session and session['user']==params['user']):
            flash("Login and try Again","warning")
            return render_template("addhospitaluser.html")
    if request.method=='POST':
        email=request.form.get('email')
        h_code=request.form.get('h_code')
        password=request.form.get('password')
        encpassword=generate_password_hash(password)
        h_code=h_code.upper()
        user=Hospital_user.query.filter_by(email=email).first()
        h_code=h_code.upper()
        if user:
            flash("User with this email is already present","info")
                
        db.engine.execute(f"INSERT INTO hospital_user(h_code,email,password) values('{h_code}','{email}','{encpassword}')")
        # mail.send_message('LOGIN DETAILS FOR BED ALLOTMENT',sender=params['gmail-user'],recipients=[email],body=f"Welcome thanks for choosing Care India Health Services \n Your Login Credentials are \n\n Email Address: {email} \n Password: {password} \n Hospital Code: {h_code}\n\n\n Please don't share your password to to others \n Thank you.\nCare India")
        flash("Hospital data added successfully","info")
        return render_template('addhospitaluser.html')

        
@app.route('/logoutadmin')
def logout_admin():
    session.pop('user')
    flash("Admin Logout successful","warning")
    return render_template('admin.html')

@app.route('/addhospitalinfo',methods=['POST','GET'])
def add_hospital_info():
    #to check h_code exists in DB
    # h_user=db.engine.execute(f"SELECT * from hospital_user")
    email=current_user.email
    posts=Hospital_user.query.filter_by(email=email).first()
    code=posts.h_code
    postsdata=Hospital_data.query.filter_by(h_code=code).first()
    if request.method=='POST':
        h_code=request.form.get('h_code')
        h_name=request.form.get('h_name')
        normal_beds=request.form.get('normal_beds')
        h_icu=request.form.get('h_icu')
        icu_beds=request.form.get('icu_beds')
        vent_beds=request.form.get('vent_beds')
       
        h_code=h_code.upper()
        h_user=Hospital_user.query.filter_by(h_code=h_code).first()
        hduser=Hospital_data.query.filter_by(h_code=h_code).first()
        if hduser:
            flash("Data is already present. You can update it","primary")
            return render_template('hospitaldata.html')
        if h_user:
            db.engine.execute(f"INSERT INTO hospital_data(h_code,h_name,normal_beds,hicu_beds,icu_beds,vent_beds) VALUES('{h_code}','{h_name}','{normal_beds}','{h_icu}','{icu_beds}','{vent_beds}')")
            flash("Data Added  successfully","info")
        else:
            flash("Hospital Code doesn't exist","warning")
    return render_template('hospitaldata.html',postsdata=postsdata)


@app.route("/edit/<string:id>",methods=['POST','GET']) # passing string as id
@login_required
def edit_hosdata(id):
    if request.method=='POST':
        h_code=request.form.get('h_code')
        h_name=request.form.get('h_name')
        normal_beds=request.form.get('normal_beds')
        h_icu=request.form.get('h_icu')
        icu_beds=request.form.get('icu_beds')
        vent_beds=request.form.get('vent_beds')
        db.engine.execute(f"UPDATE hospital_data SET h_name='{h_name}',normal_beds='{normal_beds}',hicu_beds='{h_icu}',icu_beds='{icu_beds}',vent_beds='{vent_beds}' WHERE hospital_data.id={id}")
        flash("Data updated successfully","primary")
        h_code=h_code.upper()
        return redirect('/addhospitalinfo')
    posts=Hospital_data.query.filter_by(id=id).first()
    return render_template('edit.html',posts=posts)

@app.route("/delete/<string:id>",methods=['POST','GET']) # passing string as id
@login_required
def delete_hosdata(id):
    db.engine.execute(f"DELETE from hospital_data WHERE hospital_data.id={id}")
    flash("Data deleted successfully","info")
    return redirect('/addhospitalinfo')




@app.route('/slotbooking',methods=['POST','GET'])
@login_required
def slot_booking():
    query=db.engine.execute(f"SELECT * FROM hospital_data")
    if request.method=='POST':
        srfid=request.form.get('srfid')
        bed_type=request.form.get('bed_type')
        h_code=request.form.get('h_code')
        p_name=request.form.get('p_name')
        spo2=request.form.get('spo2')
        p_phno=request.form.get('p_phno')
        p_address=request.form.get('p_address')
        check_code=Hospital_data.query.filter_by(h_code=h_code).first()
        if not check_code:
            flash("The Hospital Code doesn't exist","warning")
        code=h_code
        query1=db.engine.execute(f"SELECT * from hospital_data WHERE hospital_data.h_code='{code}'")
        bedtype=bed_type
        if bed_type=='normal_beds':
            for i in query1:
                bed=i.normal_beds
                print(bed)
                get_code=Hospital_data.query.filter_by(h_code=code).first() #getting particular row of the hospital code
                get_code.normal_beds=bed-1
                db.session.commit()
        elif bed_type=='hicu_beds':
            for i in query1:
                bed=i.hicu_beds
                print(bed)
                get_code=Hospital_data.query.filter_by(h_code=code).first()
                get_code.hicu_beds=bed-1
                db.session.commit()
        elif bed_type=='icu_beds':
            for i in query1:
                bed=i.icu_beds
                print(bed)
                get_code=Hospital_data.query.filter_by(h_code=code).first()
                get_code.icu_beds=bed-1
                db.session.commit()

        elif bed_type=='vent_beds':
            for i in query1:
                bed=i.vent_beds
                print(bed)
                get_code=Hospital_data.query.filter_by(h_code=code).first()
                get_code.vent_beds=bed-1
                db.session.commit()
        else:
            pass
        check=Hospital_data.query.filter_by(h_code=code).first() #to check whether the given hospital code by the user is valid
        if(bed>0 and check):
            status=Patient_booking(srfid=srfid,bed_type=bed_type,h_code=h_code,spo2=spo2,p_name=p_name,p_phno=p_phno,p_address=p_address)
            db.session.add(status)
            db.session.commit()
            flash("Patient slot booking successful. Kindly visit the Hospital","success")
        else:
            flash("Technical Difficulties. Please try again","warning")
    
    return render_template('booking.html',query=query)

@app.route('/patientdetails',methods=['GET'])
@login_required
def display_patientdata():
    code=current_user.srfid
    data=db.engine.execute(f"SELECT * from patient_booking WHERE patient_booking.srfid='{code}'")
    return render_template('patientdata.html',data=data)


@app.route('/triggers')
def trigger():
     query=db.engine.execute(f"SELECT * FROM trigr")
     return render_template('triggers.html',query=query)
app.run(debug=True)

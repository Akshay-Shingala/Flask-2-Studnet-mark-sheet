from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select

########################################################################
# app dictation
app = Flask(__name__)

app.secret_key = "ABC"
# database connection
try:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///STUDENT.sqlite3"
    db = SQLAlchemy(app)

except:
    print("An exception occurred DB connection")


# table declaration
class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subjectName = db.Column(db.String, nullable=False)


class Teachers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    subject = db.Column(db.Integer, db.ForeignKey("subjects.id"))


class student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rollNo = db.Column(db.Integer, nullable=False)
    StuName = db.Column(db.String, nullable=False)
    subject = db.Column(db.Integer, db.ForeignKey("subjects.id"))
    Teacher = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    marks = db.Column(db.Integer)


# allStudents = student.query.all()
########################################################################
# routes for application


# home page routes add students
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        rollNo = request.form["StuRollNo"]
        name = request.form["stuName"]
        subjectId = request.form["stuSubject"]
        teacherId = request.form["stuTeacher"]
        marks = request.form["stuMarks"]
        if int(marks) <= 0 or int(marks) >= 100:
            flash("input valid marks ")
            return redirect(url_for("index"))
        checkUser = student.query.filter_by(rollNo=rollNo)
        print(type(checkUser.count()))
        if checkUser.count() != 0:
            if name != checkUser[0].StuName:
                flash("name must be " + checkUser[0].StuName)
                return redirect(url_for("index"))
        if int(subjectId) in [x.subject for x in checkUser]:
            flash("this subject is already used")
            return redirect(url_for("index"))
        stud = student(
            rollNo=rollNo,
            StuName=name,
            subject=subjectId,
            Teacher=teacherId,
            marks=marks,
        )
        db.session.add(stud)
        db.session.commit()
        return redirect(url_for("showStudent"))
    templatesSubjects = Subjects.query.all()
    templatesTeachers = Teachers.query.all()
    return render_template(
        "index.html", subjects=templatesSubjects, Teachers=templatesTeachers
    )


# show all students
@app.route("/ShowStudent")
def showStudent():
    students = student.query.all()  # .group_by(student.rollNo)
    for i in students:
        i.subject = Subjects.query.get(i.subject).subjectName
        i.Teacher = Teachers.query.get(i.Teacher).username
    return render_template("ShowStudent.html", students=students)


# delete student
@app.route("/deleteStudent", methods=["POST"])
def deleteStudent():
    deleteId = request.form["deleteID"]
    print(deleteId)
    user = student.query.get(deleteId)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("showStudent"))


# update student
@app.route("/updateStudent", methods=["POST"])
def updateStudent():
    try:
        id = request.form["userId"]
        rollNo = request.form["StuRollNo"]
        name = request.form["stuName"]
        checkUser = student.query.filter_by(rollNo=rollNo).first()
        if checkUser != None:
            if name != checkUser.StuName:
                flash("name must be" + checkUser.StuName)
                return redirect(url_for("index"))
        subjectId = request.form["stuSubject"]
        teacherId = request.form["stuTeacher"]
        marks = request.form["stuMarks"]
        if int(marks) <= 0 or int(marks) >= 100:
            flash("input valid marks ")
            return redirect(url_for("index"))
        stud = student.query.filter_by(id=id).update(
            dict(
                rollNo=rollNo,
                StuName=name,
                subject=subjectId,
                Teacher=teacherId,
                marks=marks,
            )
        )
        db.session.commit()
        return redirect(url_for("showStudent"))

    except Exception as e:
        print(e)
        editID = request.form["editID"]
        user = student.query.get(editID)
        templatesSubjects = Subjects.query.all()
        templatesTeachers = Teachers.query.all()
        return render_template(
            "studentEdit.html",
            user=user,
            Teachers=templatesTeachers,
            subjects=templatesSubjects,
        )


# view results of student
@app.route("/viewResult", methods=["GET", "POST"])
def viewResult():
    resultId = request.form["viewID"]
    print(resultId)
    user = student.query.get(resultId)
    users = student.query.filter_by(rollNo=user.rollNo)
    total = 0
    count = 0
    # replace the subject id and teacher id with the subject name and teacher name
    for i in users:
        i.subject = Subjects.query.get(i.subject).subjectName
        i.Teacher = Teachers.query.get(i.Teacher).username
        total += i.marks
        count += 1
    # convert into 2 decimal numbers
    per = "{:.2f}".format((total * 100) / (count * 100))
    return render_template("result.html", user=users, total=total, per=per)


with app.app_context():
    db.create_all()

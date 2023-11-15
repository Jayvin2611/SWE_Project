from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import (
    current_user,
    Security,
    SQLAlchemySessionUserDatastore,
    auth_required,
    hash_password,
    roles_required,
    login_required,
    verify_password,
    login_user,
)
from flask_security import UserMixin, RoleMixin
from flask_restful import Resource, Api, fields, marshal_with, reqparse
from sqlalchemy.exc import SQLAlchemyError


app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)
app.app_context().push()
app.config["SECRET_KEY"] = "secret key"
app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
app.config["SECURITY_PASSWORD_SALT"] = "mysecret"
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authentication-Token'
app.config["SECURITY_REGISTERABLE"] = False
app.config["SECURITY_CONFIRMABLE"] = False
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_UNAUTHORIZED_VIEW"] = None
app.config["WTF_CSRF_ENABLED"] = False


roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False)
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users"))
    student = db.relationship("Student", backref="user")
    school = db.relationship("SchoolDetails", backref="user")
    college = db.relationship("CollegeDetails", backref="user")
    jee = db.relationship("JeeDetails", backref="user")
    c_course = db.relationship("CompletedCourse", backref="user")


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)


class Courses(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    code = db.Column(db.String, unique=True)
    pre_requisite = db.Column(db.String)
    level = db.Column(db.String)


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    dob = db.Column(db.DateTime, nullable=False)
    roll_no = db.Column(db.String)
    gender = db.Column(db.String)
    category = db.Column(db.String)
    country = db.Column(db.String)
    pwd = db.Column(db.String)
    type_of_disability = db.Column(db.String)
    requirement = db.Column(db.String)
    bandwith = db.Column(db.String)
    reason_of_joining = db.Column(db.String)
    hours_dedicated = db.Column(db.String)
    source_kind = db.Column(db.String)
    target_for_iitm = db.Column(db.String)


class SchoolDetails(db.Model):
    __tablename__ = "schooldetails"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    school_name = db.Column(db.String)
    type_of_school = db.Column(db.String)
    marks = db.Column(db.String)
    pass_status = db.Column(db.String)
    year_of_passing = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    other_city = db.Column(db.String)
    other_state = db.Column(db.String)
    country_of_school = db.Column(db.String)


class CollegeDetails(db.Model):
    __tablename__ = "collegedetails"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    college_name = db.Column(db.String)
    university = db.Column(db.String)
    field_of_study = db.Column(db.String)
    roll_no = db.Column(db.String)
    college_status = db.Column(db.String)
    year_of_joining = db.Column(db.String)
    year_of_completion = db.Column(db.String)
    current_year = db.Column(db.String)
    reason_for_dropping = db.Column(db.String)
    college_state = db.Column(db.String)
    college_country = db.Column(db.String)
    qualifying_criteria = db.Column(db.String)


class JeeDetails(db.Model):
    __tablename__ = "jeedetails"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    jee_qualified = db.Column(db.String)
    reg_id = db.Column(db.String)
    qualified_month = db.Column(db.String)
    qualified_year = db.Column(db.String)


class CompletedCourse(db.Model):
    __tablename__ = "completedcourse"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    marks = db.Column(db.Integer)
    term_of_completion = db.Column(db.String)
    course = db.relationship("Courses", backref="c")


user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security(app, user_datastore)
app.app_context().push()
db.create_all()


class Login(Resource):
    def post(self):
        email = request.get_json().get("email")
        password = request.get_json().get("password")
        user = User.query.filter_by(email=email).first()
        if user is None:
            return {"error": "User Not Found"}, 404
        if verify_password(password, user.password):
            role = "user"
            if user.roles != []:
                role = user.roles[0].name
            return {"token": user.get_auth_token(), "role": role}, 200
        return {"error": "wrong password"}, 300


class Register(Resource):
    def post(self):
        email = request.get_json().get("email")
        password = request.get_json().get("password")
        full_name = request.get_json().get("full_name")
        role_name = request.get_json().get("role")
        try:
            user = user_datastore.create_user(
                email=email, password=hash_password(password), full_name=full_name
            )
            db.session.commit()
            if role_name != "admin":
                return {"message": "Registration Done"}, 200
            role = Role.query.filter_by(name=role_name).first()
            user.roles.append(role)
            db.session.commit()
            return {"message": "Registration Done"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "Unknown error"}, 500


class CourseApi(Resource):
    @auth_required("token")
    @roles_required("admin")
    def get(self):
        id = request.get_json().get("id")
        course = Courses.query.get(id)
        if course is None:
            return {"error": "course not found"}, 404
        return {
            "name": course.name,
            "code": course.code,
            "pre_requisite": course.pre_requisite,
            "level": course.level,
        }, 200

    @auth_required("token")
    @roles_required("admin")
    def post(self):
        name = request.get_json().get("name")
        code = request.get_json().get("code")
        course = Courses.query.filter_by(name=name, code=code).first()
        if course is not None:
            return {"error": "course already exits"}, 300
        pre_requisite = request.get_json().get("pre_requisite")
        level = request.get_json().get("level")
        course = Courses(name=name, code=code, pre_requisite=pre_requisite, level=level)
        db.session.add(course)
        db.session.commit()
        return {"message": "Course Added"}, 200

    @auth_required("token")
    @roles_required("admin")
    def put(self):
        id = request.get_json().get("id")
        course = Courses.query.get(id)
        if course is None:
            return {"error": "course doesnot exits"}, 404
        course.name = request.get_json().get("name")
        course.code = request.get_json().get("code")
        course.pre_requisite = request.get_json().get("pre_requisite")
        course.level = request.get_json().get("level")
        db.session.commit()
        return {"message": "Course Updated"}, 200

    @auth_required("token")
    @roles_required("admin")
    def delete(self):
        id = request.get_json().get("id")
        course = Courses.query.get(id)
        if course is None:
            return {"error": "course doesnot exits"}, 404
        db.session.delete(course)
        db.session.commit()
        return {"message": "Course deleted"}, 200


class StudentApi(Resource):
    @auth_required("token")
    def get(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student is None:
            return {"error": "no detail found"}, 404
        return {
            "dob": str(student.dob),
            "roll_no": student.roll_no,
            "gender": student.gender,
            "category": student.category,
            "country": student.country,
            "pwd": student.pwd,
            "type_of_disability": student.type_of_disability,
            "requirement": student.requirement,
            "bandwith": student.bandwith,
            "reason_of_joining": student.reason_of_joining,
            "hours_dedicated": student.hours_dedicated,
            "source_kind": student.source_kind,
            "target_for_iitm": student.target_for_iitm,
        }

    @auth_required("token")
    def post(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student is None:
            return {"error": "no detail found"}, 404
        dob = request.get_json().get("dob")
        roll_no = request.get_json().get("roll_no")
        gender = request.get_json().get("gender")
        category = request.get_json().get("category")
        country = request.get_json().get("country")
        pwd = request.get_json().get("pwd")
        type_of_disability = request.get_json().get("type_of_disability")
        requirement = request.get_json().get("requirement")
        bandwith = request.get_json().get("bandwith")
        reason_of_joining = request.get_json().get("reason_of_joining")
        hours_dedicated = request.get_json().get("hours_dedicated")
        source_kind = request.get_json().get("source_kind")
        target_for_iitm = request.get_json().get("target_for_iitm")
        student = Student(
            user_id=current_user.id,
            dob=dob,
            roll_no=roll_no,
            gender=gender,
            category=category,
            country=country,
            pwd=pwd,
            type_of_disability=type_of_disability,
            requirement=requirement,
            bandwith=bandwith,
            reason_of_joining=reason_of_joining,
            hours_dedicated=hours_dedicated,
            source_kind=source_kind,
            target_for_iitm=target_for_iitm,
        )
        db.session.add(student)
        db.session.commit()
        return {"message": "Student detailed added"}, 200

    @auth_required("token")
    def put(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student is None:
            return {"error": "no detail found"}, 404
        student.dob = request.get_json().get("dob")
        student.roll_no = request.get_json().get("roll_no")
        student.gender = request.get_json().get("gender")
        student.category = request.get_json().get("category")
        student.country = request.get_json().get("country")
        student.pwd = request.get_json().get("pwd")
        student.type_of_disability = request.get_json().get("type_of_disability")
        student.requirement = request.get_json().get("requirement")
        student.bandwith = request.get_json().get("bandwith")
        student.reason_of_joining = request.get_json().get("reason_of_joining")
        student.hours_dedicated = request.get_json().get("hours_dedicated")
        student.source_kind = request.get_json().get("source_kind")
        student.target_for_iitm = request.get_json().get("target_for_iitm")
        db.session.commit()
        return {"message": "Student detail updated"}, 200

    @auth_required("token")
    def delete(self):
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student is None:
            return {"error": "no detail found"}, 404
        db.session.delete(student)
        db.session.commit()
        return {"message": "Student detailed delete"}, 200


class SchoolApi(Resource):
    @auth_required("token")
    def get(self):
        school = current_user.school
        if school == []:
            return {"error": "no detail found"}, 404
        school = school[0]
        return {
            "school_name": school.school_name,
            "type_of_school": school.type_of_school,
            "marks": school.marks,
            "pass_status": school.pass_status,
            "year_of_passing": school.year_of_passing,
            "city": school.city,
            "state": school.state,
            "other_city": school.other_city,
            "other_state": school.other_state,
            "country_of_school": school.country_of_school,
        }

    @auth_required("token")
    def post(self):
        school = current_user.school
        if school != []:
            return {"error": "details already exits"}, 300
        school_name = request.get_json().get("school_name")
        type_of_school = request.get_json().get("type_of_school")
        marks = request.get_json().get("marks")
        pass_status = request.get_json().get("pass_status")
        year_of_passing = request.get_json().get("year_of_passing")
        city = request.get_json().get("city")
        state = request.get_json().get("state")
        other_city = request.get_json().get("other_city")
        other_state = request.get_json().get("other_state")
        country_of_school = request.get_json().get("country_of_school")
        school = SchoolDetails(
            user_id=current_user.id,
            school_name=school_name,
            type_of_school=type_of_school,
            marks=marks,
            pass_status=pass_status,
            year_of_passing=year_of_passing,
            city=city,
            state=state,
            other_city=other_city,
            other_state=other_state,
            country_of_school=country_of_school,
        )
        db.session.add(school)
        db.session.commit()
        return {"message": "school details added"}

    @auth_required("token")
    def put(self):
        school = current_user.school
        if school == []:
            return {"error": "details doesnot exits"}, 400
        school = school[0]
        school.school_name = request.get_json().get("school_name")
        school.type_of_school = request.get_json().get("type_of_school")
        school.marks = request.get_json().get("marks")
        school.pass_status = request.get_json().get("pass_status")
        school.year_of_passing = request.get_json().get("year_of_passing")
        school.city = request.get_json().get("city")
        school.state = request.get_json().get("state")
        school.other_city = request.get_json().get("other_city")
        school.other_state = request.get_json().get("other_state")
        school.country_of_school = request.get_json().get("country_of_school")
        db.session.commit()
        return {"message": "school details updated"}, 200

    @auth_required("token")
    def delete(self):
        school = current_user.school
        if school == []:
            return {"error": "details doesnot exits"}, 400
        school = school[0]
        db.session.delete(school)
        db.session.commit()
        return {"message": "school details delete"}, 200


class CollegeApi(Resource):
    @auth_required("token")
    def get(self):
        college = current_user.college
        if college == []:
            return {"error": "details doesnot exits"}, 400
        college = college[0]
        return {
            "college_name": college.college_name,
            "university": college.university,
            "field_of_study": college.field_of_study,
            "roll_no": college.roll_no,
            "college_status": college.college_status,
            "year_of_joining": college.year_of_joining,
            "year_of_completion": college.year_of_completion,
            "current_year": college.current_year,
            "reason_for_dropping": college.reason_for_dropping,
            "college_state": college.college_state,
            "college_country": college.college_country,
            "qualifying_criteria": college.qualifying_criteria,
        }

    @auth_required("token")
    def post(self):
        if current_user.college != []:
            return {"error": "details already exits"}
        college_name = request.get_json().get("college_name")
        university = request.get_json().get("university")
        field_of_study = request.get_json().get("field_of_study")
        roll_no = request.get_json().get("roll_no")
        college_status = request.get_json().get("college_status")
        year_of_joining = request.get_json().get("year_of_joining")
        year_of_completion = request.get_json().get("year_of_completion")
        current_year = request.get_json().get("current_year")
        reason_for_dropping = request.get_json().get("reason_for_dropping")
        college_state = request.get_json().get("college_state")
        college_country = request.get_json().get("college_country")
        qualifying_criteria = request.get_json().get("qualifying_criteria")
        college = CollegeDetails(
            user_id=current_user.id,
            college_name=college_name,
            university=university,
            field_of_study=field_of_study,
            roll_no=roll_no,
            college_status=college_status,
            year_of_joining=year_of_joining,
            year_of_completion=year_of_completion,
            current_year=current_year,
            reason_for_dropping=reason_for_dropping,
            college_state=college_state,
            college_country=college_country,
            qualifying_criteria=qualifying_criteria,
        )
        db.session.add(college)
        db.session.commit()
        return {"message": "Details added"}, 200

    @auth_required("token")
    def put(self):
        college = current_user.college
        if college == []:
            return {"error": "details doesnot exits"}, 404
        college = college[0]
        college.college_name = request.get_json().get("college_name")
        college.university = request.get_json().get("university")
        college.field_of_study = request.get_json().get("field_of_study")
        college.roll_no = request.get_json().get("roll_no")
        college.college_status = request.get_json().get("college_status")
        college.year_of_joining = request.get_json().get("year_of_joining")
        college.year_of_completion = request.get_json().get("year_of_completion")
        college.current_year = request.get_json().get("current_year")
        college.reason_for_dropping = request.get_json().get("reason_for_dropping")
        college.college_state = request.get_json().get("college_state")
        college.college_country = request.get_json().get("college_country")
        college.qualifying_criteria = request.get_json().get("qualifying_criteria")
        db.session.commit()
        return {"message": "Details updated"}, 200

    @auth_required("token")
    def delete(self):
        college = current_user.college
        if college == []:
            return {"error": "details doesnot exits"}, 404
        college = college[0]
        db.session.delete(college)
        db.session.commit()
        return {"message": "Details deleted"}, 200


class JeeApi(Resource):
    @auth_required("token")
    def get(self):
        jee = current_user.jee
        if jee == []:
            return {"error": "Details doesnot exits"}, 404
        jee = jee[0]
        return {
            "jee_qualified": jee.jee_qualified,
            "reg_id": jee.reg_id,
            "qualified_month": jee.qualified_month,
            "qualified_year": jee.qualified_year,
        }, 200

    @auth_required("token")
    def post(self):
        jee = current_user.jee
        if jee != []:
            return {"error": "Details already exits"}, 300
        jee_qualified = request.get_json().get("jee_qualified")
        reg_id = request.get_json().get("reg_id")
        qualified_month = request.get_json().get("qualified_month")
        qualified_year = request.get_json().get("qualified_year")
        jee = JeeDetails(
            user_id=current_user.id,
            jee_qualified=jee_qualified,
            reg_id=reg_id,
            qualified_month=qualified_month,
            qualified_year=qualified_year,
        )
        db.session.add(jee)
        db.session.commit()
        return {"message": "details added"}, 200

    @auth_required("token")
    def put(self):
        jee = current_user.jee
        if jee == []:
            return {"error": "Details doesnot exits"}, 404
        jee = jee[0]
        jee.jee_qualified = request.get_json().get("jee_qualified")
        jee.reg_id = request.get_json().get("reg_id")
        jee.qualified_month = request.get_json().get("qualified_month")
        jee.qualified_year = request.get_json().get("qualified_year")
        db.session.commit()
        return {"message": "details updated"}, 200

    @auth_required("token")
    def delete(self):
        jee = current_user.jee
        if jee == []:
            return {"error": "Details doesnot exits"}, 404
        jee = jee[0]
        db.session.delete(jee)
        db.session.commit()
        return {"message": "details deleted"}, 200


class CompletedCourseApi(Resource):
    @auth_required("token")
    def get(self):
        c_course = current_user.c_course
        if c_course == []:
            return {"error": "Details doesnot exits"}, 404
        c_list = []
        for c in c_course:
            course = c.course
            d = {
                "id": c.id,
                "course_id": c.course_id,
                "marks": c.marks,
                "term_of_completion": c.term_of_completion,
                "name": course.name,
            }
            c_list.append(d)
        return c_list

    @auth_required("token")
    def post(self):
        course_id = request.get_json().get("course_id")
        c_course = CompletedCourse.query.filter_by(
            user_id=current_user.id, course_id=course_id
        ).first()
        if c_course is not None:
            return {"error": "Course already exits"}, 404
        user_id = current_user.id
        marks = request.get_json().get("marks")
        term_of_completion = request.get_json().get("term_of_completion")
        c_course = CompletedCourse(
            user_id=user_id,
            course_id=course_id,
            marks=marks,
            term_of_completion=term_of_completion,
        )
        db.session.add(c_course)
        db.session.commit()
        return {"message": "Course added"}, 200

    @auth_required("token")
    def put(self):
        course_id = request.get_json().get("course_id")
        c_course = CompletedCourse.query.filter_by(
            user_id=current_user.id, course_id=course_id
        ).first()
        if c_course is None:
            return {"error": "Course doesnot exits"}, 404
        c_course.marks = request.get_json().get("marks")
        c_course.term_of_completion = request.get_json().get("term_of_completion")
        return {"message": "Course updated"}, 200

    @auth_required("token")
    def delete(self):
        course_id = request.get_json().get("course_id")
        c_course = CompletedCourse.query.filter_by(
            user_id=current_user.id, course_id=course_id
        ).first()
        if c_course is None:
            return {"error": "Course doesnot exits"}, 404
        db.session.delete(c_course)
        db.session.commit()
        return {"message": "Course deleted"}, 200


###########################################################################################################################


class AdminStudentApi(Resource):
    @auth_required("token")
    @roles_required("admin")
    def get(self):
        user_id = request.get_json().get("user_id")
        student = Student.query.filter_by(user_id=user_id).first()
        if student is None:
            return {"error": "no detail found"}, 404
        return {
            "dob": str(student.dob),
            "roll_no": student.roll_no,
            "gender": student.gender,
            "category": student.category,
            "country": student.country,
            "pwd": student.pwd,
            "type_of_disability": student.type_of_disability,
            "requirement": student.requirement,
            "bandwith": student.bandwith,
            "reason_of_joining": student.reason_of_joining,
            "hours_dedicated": student.hours_dedicated,
            "source_kind": student.source_kind,
            "target_for_iitm": student.target_for_iitm,
        }

    @auth_required("token")
    @roles_required("admin")
    def post(self):
        user_id = request.get_json().get("user_id")
        student = Student.query.filter_by(user_id=user_id).first()
        if student is None:
            return {"error": "no detail found"}, 404
        dob = request.get_json().get("dob")
        roll_no = request.get_json().get("roll_no")
        gender = request.get_json().get("gender")
        category = request.get_json().get("category")
        country = request.get_json().get("country")
        pwd = request.get_json().get("pwd")
        type_of_disability = request.get_json().get("type_of_disability")
        requirement = request.get_json().get("requirement")
        bandwith = request.get_json().get("bandwith")
        reason_of_joining = request.get_json().get("reason_of_joining")
        hours_dedicated = request.get_json().get("hours_dedicated")
        source_kind = request.get_json().get("source_kind")
        target_for_iitm = request.get_json().get("target_for_iitm")
        student = Student(
            user_id=user_id,
            dob=dob,
            roll_no=roll_no,
            gender=gender,
            category=category,
            country=country,
            pwd=pwd,
            type_of_disability=type_of_disability,
            requirement=requirement,
            bandwith=bandwith,
            reason_of_joining=reason_of_joining,
            hours_dedicated=hours_dedicated,
            source_kind=source_kind,
            target_for_iitm=target_for_iitm,
        )
        db.session.add(student)
        db.session.commit()
        return {"message": "Student detailed added"}, 200

    @auth_required("token")
    @roles_required("admin")
    def put(self):
        user_id = request.get_json().get("user_id")
        student = Student.query.filter_by(user_id=user_id).first()
        if student is None:
            return {"error": "no detail found"}, 404
        student.dob = request.get_json().get("dob")
        student.roll_no = request.get_json().get("roll_no")
        student.gender = request.get_json().get("gender")
        student.category = request.get_json().get("category")
        student.country = request.get_json().get("country")
        student.pwd = request.get_json().get("pwd")
        student.type_of_disability = request.get_json().get("type_of_disability")
        student.requirement = request.get_json().get("requirement")
        student.bandwith = request.get_json().get("bandwith")
        student.reason_of_joining = request.get_json().get("reason_of_joining")
        student.hours_dedicated = request.get_json().get("hours_dedicated")
        student.source_kind = request.get_json().get("source_kind")
        student.target_for_iitm = request.get_json().get("target_for_iitm")
        db.session.commit()
        return {"message": "Student detailed updated"}, 200

    @auth_required("token")
    @roles_required("admin")
    def delete(self):
        user_id = request.get_json().get("user_id")
        student = Student.query.filter_by(user_id=user_id).first()
        if student is None:
            return {"error": "no detail found"}, 404
        db.session.delete(student)
        db.session.commit()
        return {"message": "Student detailed delete"}, 200


class AdminSchoolApi(Resource):
    @auth_required("token")
    @roles_required("admin")
    def get(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        school = user.school
        if school == []:
            return {"error": "no detail found"}, 404
        school = school[0]
        return {
            "school_name": school.school_name,
            "type_of_school": school.type_of_school,
            "marks": school.marks,
            "pass_status": school.pass_status,
            "year_of_passing": school.year_of_passing,
            "city": school.city,
            "state": school.state,
            "other_city": school.other_city,
            "other_state": school.other_state,
            "country_of_school": school.country_of_school,
        }

    @auth_required("token")
    @roles_required("admin")
    def post(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        school = user.school
        if school != []:
            return {"error": "details already exits"}, 300
        school_name = request.get_json().get("school_name")
        type_of_school = request.get_json().get("type_of_school")
        marks = request.get_json().get("marks")
        pass_status = request.get_json().get("pass_status")
        year_of_passing = request.get_json().get("year_of_passing")
        city = request.get_json().get("city")
        state = request.get_json().get("state")
        other_city = request.get_json().get("other_city")
        other_state = request.get_json().get("other_state")
        country_of_school = request.get_json().get("country_of_school")
        school = SchoolDetails(
            user_id=user.id,
            school_name=school_name,
            type_of_school=type_of_school,
            marks=marks,
            pass_status=pass_status,
            year_of_passing=year_of_passing,
            city=city,
            state=state,
            other_city=other_city,
            other_state=other_state,
            country_of_school=country_of_school,
        )
        db.session.add(school)
        db.session.commit()
        return {"message": "school details added"}

    @auth_required("token")
    @roles_required("admin")
    def put(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        school = user.school
        if school == []:
            return {"error": "details doesnot exits"}, 400
        school = school[0]
        school.school_name = request.get_json().get("school_name")
        school.type_of_school = request.get_json().get("type_of_school")
        school.marks = request.get_json().get("marks")
        school.pass_status = request.get_json().get("pass_status")
        school.year_of_passing = request.get_json().get("year_of_passing")
        school.city = request.get_json().get("city")
        school.state = request.get_json().get("state")
        school.other_city = request.get_json().get("other_city")
        school.other_state = request.get_json().get("other_state")
        school.country_of_school = request.get_json().get("country_of_school")
        db.session.commit()
        return {"message": "school details updated"}, 200

    @auth_required("token")
    @roles_required("admin")
    def delete(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        school = user.school
        if school == []:
            return {"error": "details doesnot exits"}, 400
        school = school[0]
        db.session.delete(school)
        db.session.commit()
        return {"message": "school details delete"}, 200


class AdminCollegeApi(Resource):
    @auth_required("token")
    @roles_required("admin")
    def get(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        college = user.college
        if college == []:
            return {"error": "details doesnot exits"}, 400
        college = college[0]
        return {
            "college_name": college.college_name,
            "university": college.university,
            "field_of_study": college.field_of_study,
            "roll_no": college.roll_no,
            "college_status": college.college_status,
            "year_of_joining": college.year_of_joining,
            "year_of_completion": college.year_of_completion,
            "current_year": college.current_year,
            "reason_for_dropping": college.reason_for_dropping,
            "college_state": college.college_state,
            "college_country": college.college_country,
            "qualifying_criteria": college.qualifying_criteria,
        }

    @auth_required("token")
    @roles_required("admin")
    def post(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        if user.college != []:
            return {"error": "details already exits"}
        college_name = request.get_json().get("college_name")
        university = request.get_json().get("university")
        field_of_study = request.get_json().get("field_of_study")
        roll_no = request.get_json().get("roll_no")
        college_status = request.get_json().get("college_status")
        year_of_joining = request.get_json().get("year_of_joining")
        year_of_completion = request.get_json().get("year_of_completion")
        current_year = request.get_json().get("current_year")
        reason_for_dropping = request.get_json().get("reason_for_dropping")
        college_state = request.get_json().get("college_state")
        college_country = request.get_json().get("college_country")
        qualifying_criteria = request.get_json().get("qualifying_criteria")
        college = CollegeDetails(
            user_id=user.id,
            college_name=college_name,
            university=university,
            field_of_study=field_of_study,
            roll_no=roll_no,
            college_status=college_status,
            year_of_joining=year_of_joining,
            year_of_completion=year_of_completion,
            current_year=current_year,
            reason_for_dropping=reason_for_dropping,
            college_state=college_state,
            college_country=college_country,
            qualifying_criteria=qualifying_criteria,
        )
        db.session.add(college)
        db.session.commit()
        return {"message": "Details added"}, 200

    @auth_required("token")
    @roles_required("admin")
    def put(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        college = user.college
        if college == []:
            return {"error": "details doesnot exits"}, 404
        college = college[0]
        college.college_name = request.get_json().get("college_name")
        college.university = request.get_json().get("university")
        college.field_of_study = request.get_json().get("field_of_study")
        college.roll_no = request.get_json().get("roll_no")
        college.college_status = request.get_json().get("college_status")
        college.year_of_joining = request.get_json().get("year_of_joining")
        college.year_of_completion = request.get_json().get("year_of_completion")
        college.current_year = request.get_json().get("current_year")
        college.reason_for_dropping = request.get_json().get("reason_for_dropping")
        college.college_state = request.get_json().get("college_state")
        college.college_country = request.get_json().get("college_country")
        college.qualifying_criteria = request.get_json().get("qualifying_criteria")
        db.session.commit()
        return {"message": "Details updated"}, 200

    @auth_required("token")
    @roles_required("admin")
    def delete(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        college = user.college
        if college == []:
            return {"error": "details doesnot exits"}, 404
        college = college[0]
        db.session.delete(college)
        db.session.commit()
        return {"message": "Details deleted"}, 200


class AdminJeeApi(Resource):
    @auth_required("token")
    @roles_required("admin")
    def get(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        jee = user.jee
        if jee == []:
            return {"error": "Details doesnot exits"}, 404
        jee = jee[0]
        return {
            "jee_qualified": jee.jee_qualified,
            "reg_id": jee.reg_id,
            "qualified_month": jee.qualified_month,
            "qualified_year": jee.qualified_year,
        }, 200

    @auth_required("token")
    @roles_required("admin")
    def post(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        jee = user.jee
        if jee != []:
            return {"error": "Details already exits"}, 300
        jee_qualified = request.get_json().get("jee_qualified")
        reg_id = request.get_json().get("reg_id")
        qualified_month = request.get_json().get("qualified_month")
        qualified_year = request.get_json().get("qualified_year")
        jee = JeeDetails(
            user_id=user.id,
            jee_qualified=jee_qualified,
            reg_id=reg_id,
            qualified_month=qualified_month,
            qualified_year=qualified_year,
        )
        db.session.add(jee)
        db.session.commit()
        return {"message": "details added"}, 200

    @auth_required("token")
    @roles_required("admin")
    def put(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        jee = user.jee
        if jee == []:
            return {"error": "Details doesnot exits"}, 404
        jee = jee[0]
        jee.jee_qualified = request.get_json().get("jee_qualified")
        jee.reg_id = request.get_json().get("reg_id")
        jee.qualified_month = request.get_json().get("qualified_month")
        jee.qualified_year = request.get_json().get("qualified_year")
        db.session.commit()
        return {"message": "details updated"}, 200

    @auth_required("token")
    @roles_required("admin")
    def delete(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        jee = user.jee
        if jee == []:
            return {"error": "Details doesnot exits"}, 404
        jee = jee[0]
        db.session.delete(jee)
        db.session.commit()
        return {"message": "details deleted"}, 200


class AdminCompletedCourseApi(Resource):
    @auth_required("token")
    @roles_required("admin")
    def get(self):
        user_id = request.get_json().get("user_id")
        user = User.query.get(user_id)
        c_course = user.c_course
        if c_course == []:
            return {"error": "Details doesnot exits"}, 404
        c_list = []
        for c in c_course:
            course = c.course
            d = {
                "id": c.id,
                "course_id": c.course_id,
                "marks": c.marks,
                "term_of_completion": c.term_of_completion,
                "name": course.name,
            }
            c_list.append(d)
        return c_list

    @auth_required("token")
    @roles_required("admin")
    def post(self):
        course_id = request.get_json().get("course_id")
        user_id = request.get_json().get("user_id")
        c_course = CompletedCourse.query.filter_by(
            user_id=user_id, course_id=course_id
        ).first()
        if c_course is not None:
            return {"error": "Course already exits"}, 404
        marks = request.get_json().get("marks")
        term_of_completion = request.get_json().get("term_of_completion")
        c_course = CompletedCourse(
            user_id=user_id,
            course_id=course_id,
            marks=marks,
            term_of_completion=term_of_completion,
        )
        db.session.add(c_course)
        db.session.commit()
        return {"message": "Course added"}, 200

    @auth_required("token")
    @roles_required("admin")
    def put(self):
        course_id = request.get_json().get("course_id")
        user_id = request.get_json().get("user_id")
        c_course = CompletedCourse.query.filter_by(
            user_id=user_id, course_id=course_id
        ).first()
        if c_course is None:
            return {"error": "Course doesnot exits"}, 404
        c_course.marks = request.get_json().get("marks")
        c_course.term_of_completion = request.get_json().get("term_of_completion")
        return {"message": "Course updated"}, 200

    @auth_required("token")
    @roles_required("admin")
    def delete(self):
        course_id = request.get_json().get("course_id")
        user_id = request.get_json().get("user_id")
        c_course = CompletedCourse.query.filter_by(
            user_id=user_id, course_id=course_id
        ).first()
        if c_course is None:
            return {"error": "Course doesnot exits"}, 404
        db.session.delete(c_course)
        db.session.commit()
        return {"message": "Course deleted"}, 200


api.add_resource(Login, "/api/login")
api.add_resource(Register, "/api/register")
api.add_resource(StudentApi, "/api/student")
api.add_resource(SchoolApi, "/api/school")
api.add_resource(CollegeApi, "/api/college")
api.add_resource(JeeApi, "/api/jee")
api.add_resource(CompletedCourseApi, "/api/completedcourse")

api.add_resource(AdminStudentApi, "/api/admin/student")
api.add_resource(AdminSchoolApi, "/api/admin/school")
api.add_resource(AdminCollegeApi, "/api/admin/college")
api.add_resource(AdminJeeApi, "/api/admin/jee")
api.add_resource(AdminCompletedCourseApi, "/api/admin/completedcourse")

if __name__ == "__main__":
    app.run(debug=True)

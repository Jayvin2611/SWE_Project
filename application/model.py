from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

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
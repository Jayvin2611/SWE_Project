import pytest
from main import *
import json
import mpl_toolkits


@pytest.fixture(scope="module")
def client():
    app, api , user_datastore = create_app(__name__,"sqlite:///:memory:")
    
    app.app_context().push()
    api.add_resource(Login, "/api/login")
    api.add_resource(Register, "/api/register")
    api.add_resource(StudentApi, "/api/student")
    api.add_resource(SchoolApi, "/api/school")
    api.add_resource(CollegeApi, "/api/college")
    api.add_resource(JeeApi, "/api/jee")
    api.add_resource(CompletedCourseApi, "/api/completedcourse")
    api.add_resource(Recommendation, "/api/recommendation")

    api.add_resource(CourseApi, "/api/admin/course")
    api.add_resource(AdminStudentSearch, "/api/admin/studentsearch")
    api.add_resource(AdminStudentApi, "/api/admin/student")
    api.add_resource(AdminSchoolApi, "/api/admin/school")
    api.add_resource(AdminCollegeApi, "/api/admin/college")
    api.add_resource(AdminJeeApi, "/api/admin/jee")
    api.add_resource(AdminCompletedCourseApi, "/api/admin/completedcourse")
    app.app_context().push()

    with api.app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            admin_role = Role(name="admin", description="this is admin role")
            db.session.add(admin_role)
            db.session.commit()
            admin_user = user_datastore.create_user(
                email="admin@gmail.com",
                password=hash_password("password"),
                full_name="this is admin"
            )
            db.session.commit()
            admin_user.roles.append(admin_role)
            db.session.commit()
            user = user_datastore.create_user(
                email="user@gmail.com",
                password=hash_password("password"),
                full_name="this is user")
            db.session.commit()

        yield testing_client

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='module')
def access_token_admin(client):
    response = client.post('/api/login', json={
        'email': 'admin@gmail.com',
        'password': 'password'
    })
    return response.json['token']


@pytest.fixture(scope='module')
def access_token_user(client):
    response = client.post('/api/login', json={
        'email': 'user@gmail.com',
        'password': 'password'
    })
    return response.json['token']



def test_course_api_post(client,access_token_admin):
    data = {
        "name": "MAD1",
        "code": "C123",
        "pre_requisite": "Some prerequisite",
        "level": "Foundation"
    }
    response = client.post('/api/admin/course', json=data, headers={'Authentication-Token':f'{access_token_admin}'})
    print(Courses.query.all())
    assert response.status_code == 200


def test_course_api_put(client,access_token_admin):
    data = {
        "id": 1,
        "name": "Updated Course",
        "code": "C456",
        "pre_requisite": "Updated prerequisite",
        "level": "Foundation"
    }
    response = client.put('/api/admin/course', json=data, headers={'Authentication-Token':f'{access_token_admin}'})
    assert response.status_code == 200 

def test_get_course(client,access_token_admin):
    response = client.get('/api/course', json={'id': 1} , headers={'Authentication-Token':f'{access_token_admin}'})
    
    assert response.status_code == 404


def test_course_api_delete(client,access_token_admin):
    data = {"id": 1}
    response = client.delete('/api/admin/course', json=data, headers={'Authentication-Token':f'{access_token_admin}'})
    assert response.status_code == 200

def test_student_api_post(client,access_token_user):
    data = {
        "dob": "1990-01-01",
        "roll_no": "21f100000",
        "gender": "Male",
        "category": "General",
        "country": "India",
        "pwd": "No",
        "type_of_disability": "None",
        "requirement": "None",
        "bandwith": "High",
        "reason_of_joining": "Interest",
        "hours_dedicated": 10,
        "source_kind": "Online",
        "target_for_iitm": "Bsc"
    }
    response = client.post('/api/student', json=data, headers={'Authentication-Token':f'{access_token_user}'})
    assert response.status_code == 200

def test_student_api_put(client,access_token_user):
    data = {
        "dob": "1990-01-01",
        "roll_no": "21f100000",
        "gender": "Male",
        "category": "General",
        "country": "India",
        "pwd": "No",
        "type_of_disability": "None",
        "requirement": "None",
        "bandwith": "High",
        "reason_of_joining": "Interest",
        "hours_dedicated": 10,
        "source_kind": "Online",
        "target_for_iitm": "Bsc"
    }
    response = client.put('/api/student', json=data, headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_student_api_get(client,access_token_user):
    response = client.get('/api/student',headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_student_api_delete(client,access_token_user):
    response = client.delete('/api/student',headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200


def test_school_api_post(client,access_token_user):
    data = {
        "school_name": "High School",
        "type_of_school": "Public",
        "marks": 80,
        "pass_status": True,
        "year_of_passing": 2020,
        "city": "City",
        "state": "State",
        "other_city": "Other City",
        "other_state": "Other State",
        "country_of_school": "Country"
    }
    response = client.post('/api/school', json=data , headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_school_api_put(client,access_token_user):
    data = {
        "school_name": "Updated School",
        "type_of_school": "Private",
        "marks": 90,
        "pass_status": False,
        "year_of_passing": 2022,
        "city": "Updated City",
        "state": "Updated State",
        "other_city": "Updated Other City",
        "other_state": "Updated Other State",
        "country_of_school": "Updated Country"
    }
    response = client.put('/api/school', json=data , headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_school_api_get(client,access_token_user):
    response = client.get('/api/school',headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_school_api_delete(client,access_token_user):
    response = client.delete('/api/school',headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200



def test_college_api_post(client,access_token_user):
    # Test the POST endpoint of CollegeApi
    data = {
        "college_name": "ABC College",
        "university": "XYZ University",
        "field_of_study": "Computer Science",
        "roll_no": "123",
        "college_status": "Enrolled",
        "year_of_joining": 2018,
        "year_of_completion": 2022,
        "current_year": 4,
        "reason_for_dropping": "N/A",
        "college_state": "State",
        "college_country": "Country",
        "qualifying_criteria": "High"
    }
    response = client.post('/api/college', json=data, headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_college_api_put(client,access_token_user):
    data = {
        "college_name": "Updated College",
        "university": "Updated University",
        "field_of_study": "Updated Field",
        "roll_no": "456",
        "college_status": "Dropped",
        "year_of_joining": 2019,
        "year_of_completion": 2023,
        "current_year": 3,
        "reason_for_dropping": "Change of Interest",
        "college_state": "Updated State",
        "college_country": "Updated Country",
        "qualifying_criteria": "Medium"
    }
    response = client.put('/api/college', json=data, headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_college_api_get(client,access_token_user):
    response = client.get('/api/college',headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_college_api_delete(client,access_token_user):
    response = client.delete('/api/college',headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200 


def test_jee_api_post(client,access_token_user):
    data = {
        "jee_qualified": 'Yes',
        "reg_id": "JEE123",
        "qualified_month": "May",
        "qualified_year": 2022
    }
    response = client.post('/api/jee', json=data, headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_jee_api_put(client,access_token_user):
    data = {
        "jee_qualified": 'No',
        "reg_id": "JEE456",
        "qualified_month": "June",
        "qualified_year": 2021
    }
    response = client.put('/api/jee', json=data, headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_jee_api_get(client,access_token_user):
    response = client.get('/api/jee',headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_jee_api_delete(client,access_token_user):
    response = client.delete('/api/jee', headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200




def test_completed_course_api_post(client,access_token_user):
    course = Courses(name="Test Course", code="TEST123", pre_requisite="None", level="Diploma")
    db.session.add(course)
    db.session.commit()

    data = {
        "course_id": course.id,
        "marks": 85,
        "term_of_completion": "May 2023"
    }
    response = client.post('/api/completedcourse', json=data, headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_completed_course_api_put(client,access_token_user):
    course = Courses(name="Another Course", code="ANOTHER123", pre_requisite="None", level="Degree")
    db.session.add(course)
    db.session.commit()

    c_course = CompletedCourse(user_id=1, course_id=course.id, marks=90, term_of_completion="Jan 2023")
    db.session.add(c_course)
    db.session.commit()

    data = {
        "course_id": course.id,
        "marks": 95,
        "term_of_completion": "Sept 2023"
    }
    response = client.put('/api/completedcourse', json=data, headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200

def test_completed_course_api_get(client,access_token_user):
    response = client.get('/api/completedcourse', headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200


def test_completed_course_api_delete(client,access_token_user):
    course = Courses(name="Yet Another Course", code="YETANOTHER123", pre_requisite="None", level="Foundation")
    db.session.add(course)
    db.session.commit()

    c_course = CompletedCourse(user_id=1, course_id=course.id, marks=80, term_of_completion="Sept 2023")
    db.session.add(c_course)
    db.session.commit()

    data = {
        "course_id": course.id,
    }
    response = client.delete('/api/completedcourse', json=data, headers={'Authentication-Token':access_token_user})
    assert response.status_code == 200


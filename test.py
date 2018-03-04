#Authors: Daniel Bis and Abraham D’mitri Joseph

########################################################################################
########  "premature optimization is root cause of all evil" - Donald Knuth ###########
########################################################################################

from app import app, db
from app.mod_auth.models import User, Shop
from app.mod_provider.models import Schedule
from flask import abort, url_for
from urllib.parse import urlparse
import os
import unittest
import tempfile


class TestBase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["SIDOCHECK_TEST_DB"]
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        
        return app

    # executed after each test
    def tearDown(self):
        db.session.close()
        db.drop_all()


    ###############
    #### tests ####
    ###############
 
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
 

    ########################
    #### helper methods ####
    ########################
 
    def register(self, firstname, lastname, email, password):
        return self.app.post(
            'auth/signup',
            data=dict(firstname = firstname, lastname = lastname, email=email, password=password),
            follow_redirects=True
        )

    def login(self, email, password):
        user1 = User("testuser", "testuserlast", "testuser@gmail.com", "testuserpass")
        db.session.add(user1)
        db.session.commit()
        return self.app.post(
            'auth/login',
            data=dict(email=email, password=password),
            follow_redirects=True
    )

    def logout(self):
        return self.app.get(
            'auth/logout',
            follow_redirects=True
        )  

    def test_valid_user_registration(self):
        response = self.register('test', 'User1','testUser1@gmail.com','FlaskRocks')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>New user has been created!</h1>', response.data)

    """def test_login(self):
        expectedPath = "localhost:8080/dashboardcustomer"
        response = self.login("testuser@gmail.com", "testuserpass")
        self.assertEqual(response.status_code, 200)
        self.assertIn (b'<title>Dashboard Customer</title>', response.data)"""


 #(USER) def __init__(self, firstname, lastname, email, password, role, manager = 0, phonenumber = "")
    def test_user_model(self):
        user1 = User("testuser", "testuserlast")
        user2 = User("testuser2", "testuser2")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        self.assertEqual(User.query.count(), 2)

   







if __name__ == "__main__":
    unittest.main()

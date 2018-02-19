#Authors: Daniel Bis and Abraham D’mitri Joseph

from app import app, db
from app.mod_auth.models import User, Shop, Employee
from flask import abort, url_for

import os
import unittest
import tempfile


class TestBase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["SIDOCHECK_DB"]
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

        print("creating")
        user1 = User("testuser", "testuserlast", "testuser@gmail.com", "testuserpass")
        user2 = User("shop1", "shop1", "8506667676", "shop1@gmail.com", "shop1pass")

        #print("appended")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        return app

    # executed after each test
    def tearDown(self):
        pass

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
        response = self.register('test', 'User1','testUser1@gmail.com','FlaskSucks')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>New user has been created!</h1>', response.data)


    def test_user_model(self):
        self.assertEqual(User.query.count(), 2)

    """def test_shop_model(self):
        self.assertEqual(Shop.query.count(), 1)"""


if __name__ == "__main__":
    unittest.main()

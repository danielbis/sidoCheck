#Authors: Daniel Bis and Abraham D’mitri Joseph

########################################################################################
########  "premature optimization is root cause of all evil" - Donald Knuth ###########
########################################################################################

from app import app, db
from app.mod_auth.models import User, Shop, Employee
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
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/mydb'
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
        response = self.register('test', 'User1','testUser1@gmail.com','FlaskSucks')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>New user has been created!</h1>', response.data)

    def test_login(self):
        expectedPath = "localhost:8080/dashboardcustomer"
        response = self.login("testuser@gmail.com", "testuserpass")
        self.assertEqual(response.status_code, 200)
        self.assertIn (b'<title>Dashboard Customer</title>', response.data)



    def test_user_model(self):
        user1 = User("testuser", "testuserlast", "testuser@gmail.com", "testuserpass")
        user2 = User("shop1", "shop1", "8506667676", "shop1@gmail.com", "shop1pass")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        self.assertEqual(User.query.count(), 2)

    def test_shop_model(self):
        user1 = User("testuser", "testuserlast", "testuser@gmail.com", "testuserpass")
        user2 = User("shop1", "shop1", "8506667676", "shop1@gmail.com", "shop1pass")
        new_shop = Shop("shop1", 'location')
        user2.shops.append(new_shop)

        #print("appended")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        self.assertEqual(Shop.query.count(), 1)

    def test_employee_manager_model(self):
        user1 = User("shop1", "shop1", "8506667676", "shop1@gmail.com", "shop1pass")
        new_shop = Shop("shop1", 'location')
        user1.shops.append(new_shop)
        db.session.add(user1)
        db.session.commit()

        user2 = User("testuser", "testuserlast", "testuser@gmail.com", "testuserpass")
        new_employee = Employee("testuser", "testuserlast", 1) #manager

        employer = Shop.query.filter_by(shopname= "shop1").first()
        user2.employee.append(new_employee);
        #adding employee to the list of workers in the shop
        user2.shops.append(employer)

        db.session.add(user2)
        db.session.commit()
        empls = Employee.query.all()
        for e in empls:
            print(e.first_name, " ", e.last_name)
        self.assertEqual(Employee.query.count(), 1)

    def test_employee_model(self):
        user1 = User("shop1", "shop1", "8506667676", "shop1@gmail.com", "shop1pass")
        new_shop = Shop("shop1", 'location')
        user1.shops.append(new_shop)
        db.session.add(user1)
        db.session.commit()

        user2 = User("testuser", "testuserlast", "testuser@gmail.com", "testuserpass")
        new_employee = Employee("testuser", "testuserlast", 0) #not a manager 

        employer = Shop.query.filter_by(shopname= "shop1").first()
        if new_employee.manager:
            user2.shops.append(employer)
        
        user2.employee.append(new_employee);
        #adding employee to the list of workers in the shop

        db.session.add(user2)
        db.session.commit()
        empls = Employee.query.all()
        shops_employee_2 = User.query.filter_by(email="testuser@gmail.com").first().shops
        self.assertEqual(len(shops_employee_2), 0)






if __name__ == "__main__":
    unittest.main()

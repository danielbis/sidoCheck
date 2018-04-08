1. Introduction

There are two ways of accessing Sido:

	1. Version hosted online: http://sido-dev.herokuapp.com/auth/login
	2. Running website locally - cloning respiratory/downloading zip: https://github.com/danielbis/sidoCheck/archive/master.zip
	or: 
	https://drive.google.com/open?id=17OhliGQQuM0hCZ512VNfmbXt1J9mo4wU

The online version has populated database and is ready for testing and usage. All you need to do is follow the url. 

Running the website Locally requires installing dependencies and following the steps listed below.

The website requires multiple python packages. We included a link to our database hosted online so you do not have to actually install postgres. However, if you want maximum freedom of access, you can follow the postgres installation steps and change SQLALCHEMY_DATABASE_URI in config.py to your local db. It is easier to just follow the link. The description below is as specific as we can make it. We included outside tutorials and guides to make following these steps easy. On the bottom is a contact information under which further assistance can be provided. 



2. Dependencies:

- Python 3.6 (available here: https://www.python.org/downloads/release/python-364/)
- virtualenv for python (We recommend following the steps listed here: https://packaging.python.org/guides/installing-using-pip-and-virtualenv/)
- postgres database [OPTIONAL] - installation procedure is system dependent, various guides are available here: https://wiki.postgresql.org/wiki/Detailed_installation_guides

3. Environment Set-up and Running:

 I. Go to the directory where you unpacked the package. In parent directory 
     run command: source sido/bin/activate
 
 II. Run: pip install -r requirements.txt
 
 III.[OPTIONAL] After installing postgres run command: createdb cutcheck
      Your database url should now be 'postgresql://localhost/cutcheck’.
 
 
 V. [! ONLY IF YOU ARE USING LOCAL POSTGRESQL DB !] Now you can populate database by running: CLOUDINARY_URL=cloudinary://848925646618136:HelekvosM3FQEAPsY6gAlJhiedk@sidoproject  python populate_db.py
(yes, it is one long command)

 VI. Now you can run the website locally using: CLOUDINARY_URL=cloudinary://848925646618136:HelekvosM3FQEAPsY6gAlJhiedk@sidoproject python run.py
     Website should be available at:  http://127.0.0.1:8080/
     NOTE: CLOUDINARY_URL goes in front of python [some_file.py], it is necessary because we are hosting our images there.
 VII. You can run the tests using: python test.py

If you ran the populate_db.py script:
	- you can log in as a customer with following credentials:
		email: test_user1@email.com	password: password
	- you can log in as a shop with following credentials:
		email: test_shop1@email.com	password: password
These accounts have mocked up schedules, services etc.
However, you are more then encouraged to create your own accounts. 


4. Functionality:

Sido is a booking web-app. It allows service providers to register, add employees and their schedules,  create services and book appointments for clients that call or come to the store.
Individual users can create an account, browse shops (service providers) registered on the platform and book appointments for the time and employee matching their personal criteria. 

Sido makes the booking process fast and easy. The design is simple but efficient. 

5. Tutorial:

Shop side: (all of the buttons on the right side of the navigation bar)

 - Register an account
 - Add employee(s)
 - Add schedule(s) for the employee(s)
 - Add services and assign them to the employee.
 - Now you can book walk-ins or book appointments for the times whe employee(s) are available. 
 - List of the appointments for a given date is available in the Dashboard (main) view. You can access it by clicking „dashboard” on the navigation bar. 

Customer side:
 - Create account.
 - Choose a shop from your main view by clicking on the ‚visit’ button.
 - Choose an employee or try to book a next available spot using the button on the top. 
 - If you chosen an employee, choose a service, date, and time slot should appear if such is available on the chosen day. Click book it.
 - You should be taken to confirm page.
 - If the information is correct click confirm button and your appointment should be booked. 
 - You can go back to the main page and check your appointments in Your Appointments tab. 





As the package requires a few dependencies, and postgres sometimes causes issues while installing, you are welcome to contact me for help:

email: dmb16f@my.fsu.edu
cell: 850.566.18.17

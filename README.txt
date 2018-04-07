1. Introduction

There are two ways of accessing Sido:

	1. Version hosted online: http://sido-dev.herokuapp.com/auth/login
	2. Running website locally - cloning respiratory/downloading zip: https://github.com/danielbis/sidoCheck 

The online version has populated database and is ready for testing and usage. All you need to do is follow the url. 

Running the website Locally requires installing dependencies and following the steps listed below.
The website requires a database and multiple python packages. It is significantly easier to just follow the link. However, the description below is as specific as we can make it. We included outside tutorials and guides to make following these steps easy. On the bottom is a contact information under which further assistance can be provided. 


2. Dependencies:

- Python 3.6 (available here: https://www.python.org/downloads/release/python-364/)
- virtualenv for python (We recommend following the steps listed here: https://packaging.python.org/guides/installing-using-pip-and-virtualenv/)
- postgres database - installation procedure is system dependent, various guides are available here: https://wiki.postgresql.org/wiki/Detailed_installation_guides

3. Environment Set-up and Running:

 I. Go to the directory where you unpacked the package. In parent directory 
     run command: source sido/bin/activate
 
 II. Run: pip install -r requirements.txt
 
 III. After installing postgres run command: createdb cutcheck
 
 IV. You have to create environment variables to connect to the postgres database.
     If you followed step III your database url should be 'postgresql://localhost/cutcheck.
     Set environment variable SIDOCHECK_DB to that url and SECRET variable to a string of your choice.

	Guides for environment variables if needed: 
	MAC OS: https://medium.com/@himanshuagarwal1395/setting-up-environment-variables-in-macos-sierra-f5978369b255
	
	WINDOWS: https://www.computerhope.com/issues/ch000549.htm
	LINUX: https://askubuntu.com/questions/58814/how-do-i-add-environment-variables

(you could also manually change the variables in config.py file [SQLALCHEMY_DATABASE_URI, CSRF_SESSION_KEY, SECRET_KEY] to your postgres url, and setup your own secret keys).


 V. [OPTIONAL] Now you can populate database by running: CLOUDINARY_URL=cloudinary://848925646618136:HelekvosM3FQEAPsY6gAlJhiedk@sidoproject  python populate_db.py
(yes, it is one long command)
 VI. Now you can run the website locally using: CLOUDINARY_URL=cloudinary://848925646618136:HelekvosM3FQEAPsY6gAlJhiedk@sidoproject python run.py
 VII. You can run the tests using: python test.py


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





As the package requires many dependencies, and postgres sometimes causes issues while installing, you are welcome to contact me for help:

email: dmb16f@my.fsu.edu
cell: 850.566.18.17

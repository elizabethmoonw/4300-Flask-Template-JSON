<p style="text-align:center">
<img src="backend\static\images\lookalike_README.png" width="600px">  
</p>

# Lookalike.

## Contents

- [Summary](#summary)
- [Running Locally](#running-locally)
- [MySQL functionality](#mysql-functionality)

## Summary

[**Lookalike**](http://4300showcase.infosci.cornell.edu:5179/) is a makeup recommendation system offering personalized suggestions for high-quality, budget-friendly beauty products.

Created for **"CS/INFO 4300 class at Cornell University"**

## Running locally

### Step 1: Set up MySQL
You will need to install MySQL. Here are two tutorials that could help you with the process:
- For Windows users: https://blog.devart.com/how-to-install-mysql-on-windows-using-mysql-installer.html
  - Select CUSTOM installation and remove any Visual Studio dependencies
- For Mac users: Preferably use homebrew. Your default password will be empty (""). If not, follow this https://www.geeksforgeeks.org/how-to-install-mysql-on-macos/
- For Linux users: https://www.geeksforgeeks.org/how-to-install-mysql-on-linux/


You may choose to install MySQL in an alternative method such as brew, but you will need to figure it out on your own. Regardless, make sure you write down the root password you set during the installation process. You will need it later.

We advise against using another database system such as PostgreSQL. Note that our project server uses MySQL. The different flavors of SQL may cause your app to fail on our server while working perfectly fine on yours.

### Step 2: Set up a virtual environment
Create a virtual environment in Python. You may continue using the one you setup for assignment if necessary. To review how to set up a virtual environment and activate it, refer to A0 assignment writeup.

### Step 3: Install dependencies
You need to install dependencies by running `python -m pip install -r requirements.txt` in the backend folder.

### Step 4: Connection to MySQL

## NOTE: Post bugfix: 

Make sure your MySQL server is running, then in app.py, change the SQL credentials to match your local MySQL credentials.

```flask run --host=0.0.0.0 --port=5000```

## MySQL functionality

- Firstly, only use MySQL. No Postgres, no MongoDB and no SQLite
  - If you decide to use these, the server can still build them and deploy them with no problem, but you will be responsible for making it work
- A helper class called **MySQLDatabaseHandler.py** has been provided.
  - This class abstracts the process of creating and managing the database, the engine and the connections.
  - It also abstracts the process of querying the database.
  - The query_executor method will handle any non-select queries, like INSERT, UPDATE, DELETE etc. This is useful for modifying the DB as required
  - The query_selector method will return any SELECT queries made on the DB.
  - Preferably, you will not use any of the above two methods and will instead just implement your own in a more efficient way, but these functions have been provided just as an example, or as support for those who may not be comfortable with SQLAlchemy. If you are comfortable with SQLAlchemy, feel free to write the methods using the ORM framework and supported methods.
  - **NOTE: Do not modify the other methods besides the two mentioned. You can add new ones, and override the above two methods, but do not delete or modify the connection class**
- A few things to keep in mind:
  - If your database does not exist, it should automatically be created by the script (if it doesn't, post it up on ED)
  - Your authentication details for the DB are fixed along with the initial DB. 
   - Do not change these params unless you're aware of how the docker-compose file works.
- The **init.sql** file is special, in that as the name suggests, it's your de-facto DB. It will always be built before your service is ready to run, and is helpful in storing pre-existing data, like test users, some configs and anything else that you may want at run-time.
  - It has the ability to detect its environment, and will adapt based on whether you have deployed it on the server or not
  - When running locally, it will be loaded to your local database without any import commands required, and will be re-built each time
  - When deployed on the server however, it will only be run once at the start of deployment. Any changes made to the DB from here on will be permanent, unless destroyed.


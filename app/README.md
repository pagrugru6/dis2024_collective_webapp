### Prerequisites
    Setup psql: https://www.postgresql.org/download/

### Setup PostgreSQL
    1.Download and install a PostgreSQL server. For instructions, refer to the PostgreSQL documentation on www.postgresql.org.
        -Ensure that the installation includes the PostgreSQL Unicode ODBC driver.
        -During installation, set up a user account with superuser privileges.
    2.  -Add the PostgreSQL bin directory path to the PATH environmental variable.

### Running the program
    1. Open a terminal and write "psql -h localhost -U postgres".
    2. Login with your password if necessary.
    3. (First time only) Write "createdb collective".
    4. (First time only) Write createuser pacollective.
    5. (First time only)Set password to "mynameispa"
    6. (First time only) write "GRANT ALL PRIVILEGES ON DATABASE collective TO pacollective;".
    7. Enter the folder "collective_web-app\app" in a terminal.
    8. (First time only) Enter "pip install -r requirements.txt". 
    9. (First time only) Enter  "python .\init_db.py".  
    10. To run the website enter "python .\run.py".
    11. Enter the link from the terminal's response in a webbrowser and enjoy!
    12. 
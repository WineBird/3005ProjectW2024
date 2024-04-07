# COMP3005 Project

An application written in Python using psycopg3 which interacts with a PostgreSQL database.

### Demo Video

The demo video is [here](https://drive.google.com/file/d/1btXybV1BiewtQvXosKnS614X5fgdxpBW/view?usp=sharing).

### Files

1. 3005project: The Python file
2. Schema: A picture of the database schema. Included in case the version in the pdf is not clear.
3. ER model: A picture of the ER Model. Included in case the version in the pdf is not clear.
4. TestPasswords: A list of all the built-in Username-Password combinations as the inputs to the DML file are hashed.
5. SQL: A folder containing the DDL and DML files.

### Running the application

1. Create a database called "projectdb" in PostgreSQL. (optional, there is an included command in the DDL file if you wanted to create it in the postgres console - not recommended)
2. Run the DDL file to create the tables.
3. Run the DML file to populate the tables.
4. Run the python program either in IDLE or via terminal.

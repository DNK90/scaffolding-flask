Inspired from Leo-G's Flask-Scaffold

Flask-Scaffold let's you Prototype Database Driven Admin Dashboards with Python and a MySQL/Mariadb or PostgreSQL
Database. It will also scaffold a RESTFUL API which can be used with any REST Frontend Framework.

Features include

 - Python 3 Support
 - RESTFUL JSON API
 - Unit Testing with python Unit tests
 - Datatables support

###Installation

####Step 1:Clone the project to your application folder.

    git clone https://github.com/<your-git-username>/scaffolding-flask.git

#### Step 2 : Declare your Resource and it's fields in a JSON file as follows

     {
      "project_path": "path/to/project/dir",
      "app": "blog",
      "version": "v1",
      "python_command": ["python3", "pip3"],
      "db_username": "root",
      "db_password": "root",
      "db_name": "sample",
      "db_host_name": "localhost",
      "db": [
        {
          "table": "post",
          "columns": [
            {
              "name": "id",
              "type": "integer",
              "primary_key": true
            },
            {
              "name": "title",
              "type": "string"
            },
            {
              "name": "body",
              "type": "text"
            },
            {
              "name": "user_id",
              "type": "integer",
              "foreign_key": "user.id",
              "nullable": true
            }
          ],
          "relationships": ["user"]
        },
        {
          "table": "user",
          "columns": [
            {
              "name": "id",
              "type": "integer",
              "primary_key": true
            },
            {
              "name": "name",
              "type": "string"
            },
            {
              "name": "password",
              "type": "string"
            }
          ]
        }
      ]
    }

#### Step 3 : Create database which has the same name in configuration

#### Step 4 : Run the Scaffolding  and database migrations script

    python init.py path/to/file.json
    cd path/to/project
    python db.py db init
    python db.py db migrate
    python db.py db upgrade

####  Step 5 : Run the Server

    python run.py

###Examples
[Freddy a Blogging Engine](https://github.com/Leo-G/Freddy)

[Running Asynchronous commands on Linux with Flask and Celery](https://github.com/Leo-G/Flask-Celery-Linux)

###Tests

####For unit testing with python Unit tests

    For a Single module

    python app/<module_name>/test_<module_name>.py

    For all modules

    bash tests.bash

###For checking coding styles

    bash check_styles.bash

###API

API calls can be made to the following URL

Note: This example is for a Post module

| HTTP Method  | URL  | Results |
| :------------ |:---------------:| -----:|
| GET      | http://localhost:5000/api/v1/posts | Returns a list of all Posts |
| POST     | http://localhost:5000/api/v1/posts      |   Creates a New Post |
| GET | http://localhost:5000/api/v1/posts/1      | Returns details for the a single Post |
| PATCH | http://localhost:5000/api/v1/posts/1      | Update a Post |
| DELETE | http://localhost:8001/api/v1/posts/1      | Delete a Post |

The JSON format follows the spec at jsonapi.org and a sample is available in the sample.json   file

### Sample JSON
{
  "data":
 	{
      "type": "post",
      "attributes": {
      	"tittle": "test",
        "body":"this is the body of tested post"
      }   
    }
}

###Tutorials
http://techarena51.com/index.php/buidling-a-database-driven-restful-json-api-in-python-3-with-flask-flask-restful-and-sqlalchemy/

https://techarena51.com/index.php/category/flask-framework-tutorials-and-examples/

###Directory Structure
        Project-Folder
            |-- config.py
            |--run.py
            |--requirements.txt
            |-- db.py
            |__ /scaffold
            |-- scaffold.py
            |-- tests.bash    #Tests for all modules
            |-- check_styles.bash #Check coding styles based on PEP8
            |__ app/
                |-- __init__.py
                +-- module-1
                    |-- __init__.py
                    |-- models.py
                    |-- test_module-1.py  # Unit Tests for module 1
                    |-- views.py
                      Â Â 
                +-- module-2
                    |-- __init__.py
                    |-- models.py
                    |-- test_module-2.py  # Unit Tests for module 2
                    |-- views.py

The project was inspired from Flask-scaffold from Leo-G https://github.com/Leo-G/Flask-Scaffold
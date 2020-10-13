# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, update .env file with your system data then execute:

```bash
source .env
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## API Reference

### Error handeling

Supported error codes are 400, 404, 405, 422 and 500
returned as JSON response formatted as following

```
 {
    "success": False, 
    "error": 500,
    "message": "Internal server error"
}
```

### Endpoints
```
GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
{'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"}

GET '/questions'
- Fetches fixed number of questions regardless their categories given the page number
- Request Arguments:
    - page: the index of the page (results) to be returned
- Returns: A JSON represented by the keys {questions, total_questions, categories, current_category}. where questions is an array of the requested questions,  total_questions is the number of all questions in the database for pagination, categories are all categories and current categories is always None.

DELETE '/questions/<int:question_id>'
- Deletes a question given its id in the URL.
- Request Arguments: None
- Returns: JSON as following
{
    "success": True
}

POST '/questions'
- Adds new question to the database in specific category
- Request Payload:
    - question: the question text
    - answer: answe of the question
    - difficulty: a number to indicate the level of the question 
    - category: category id to link the question with its corresponding category.
- Returns: JSON as following
{
    "success": True
}

POST '/questions/searches'
- Searches for a question given any substring from the question text.
- Request Payload:
    - searchTerm: the text used in searching
- Returns: JSON as following
{
    "questions": array of questions objects,
    "total_questions": total number of questions meetings this search,
    "current_category": None
}

GET '/categories/<int:category_id>/questions'
- Fetches all qustions in category with category id = category_id
- Request Arguments: None
- Returns: JSON as following
{
    "questions": array of questions objects,
    "total_questions": total number of questions meetings this search,
    "current_category": None
}

POST '/quizzes'
- Returns a random question that has not being asked in this quiz till now
- Request Payload:
    - quiz_category: the category of the quiz which the endpoint should pick random question from.
    - previous_questions: array of integers to tell which questions shouldn't be picked next.
- Returns: JSON as following
{
    "questions": array of questions objects,
    "total_questions": total number of questions meetings this search,
    "current_category": id of the category from quiz_category object in the payload
}
```


## Testing
To run the tests, run
```
source .env
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
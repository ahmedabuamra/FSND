import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Question, Category
from random import *

def paginate_questions(request, questions_per_page=10):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * questions_per_page
  end = page * questions_per_page
  questions = Question.query.all()
  formatted_questions = [question.format() for question in questions]
  return formatted_questions[start:end], len(formatted_questions)

def search_for_questions(request):
  search_term = request.json['searchTerm']
  questions = Question.query.filter(Question.question.ilike(f'%{search_term}%'))
  formatted_questions = [question.format() for question in questions]
  return formatted_questions, len(formatted_questions)

def get_all_categories():
  categories = Category.query.all()
  formatted_categories = {}
  for category in categories:
    formatted_categories[category.id] = category.type.lower()
  return formatted_categories

def get_questions_in_category(category_id):
  '''
  if category_id is 0 then return all categories
  '''
  if category_id == 0:
    questions = Question.query.all()
  else:
    questions = Question.query.filter_by(category=category_id)
  formatted_questions = [question.format() for question in questions]
  return formatted_questions, len(formatted_questions)


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  CORS setup. Allow '*' for origins.
  '''
  cors = CORS(app, resources={'*': {'origins': '*'}})


  '''
  Setting Access-Control-Allow
  '''
  @app.after_request
  def after_request_recieved(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response


  '''
  An endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = get_all_categories()
    return jsonify({
      'categories': categories
    })


  '''
  An endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions, count = paginate_questions(request)
    categories = get_all_categories()
    if len(questions) == 0:
      abort(404)
    return jsonify({
      "questions": questions,
      "total_questions": count,
      "categories": categories,
      "current_category": None
    })


  '''
  An endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
      question.delete()
      return jsonify({
        "success": True
      })
    except:
      abort(422)


  '''
  An endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    try:
      data = request.json
      question = data.get('question')
      answer = data.get('answer')
      difficulty = data.get('difficulty')
      category = data.get('category')
      if question is None or answer is None or difficulty is None or category is None:
        abort(422)
      record = Question(question, answer, category, difficulty)
      record.insert()
      return jsonify({
        "success": True,
        "question_id": record.id
      })
    except:
      abort(422)


  '''
  A POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  # followed this link, which suggested implementing the searches as a resource
  # https://stackoverflow.com/questions/5020704/how-to-design-restful-search-filtering
  # I searched in this point because I believe one API should do excatly one thing  
  @app.route('/questions/searches', methods=['POST'])
  def search_questions():
    questions, count = search_for_questions(request)
    if len(questions) == 0:
      abort(404)
    return jsonify({
      "questions": questions,
      "total_questions": count,
      "current_category": None
    })


  '''
  A GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def category_questions(category_id):
    questions, count = get_questions_in_category(category_id)
    if len(questions) == 0:
      abort(404)
    return jsonify({
      "questions": questions,
      "total_questions": count,
      "current_category": None
    })


  '''
  A POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    data = request.json
    category_id = data['quiz_category']['id']
    previous_questions = data['previous_questions']
    questions, count = get_questions_in_category(category_id)
    if len(questions) == 0:
      abort(404)
    
    not_found = True
    question = None
    while not_found is True:
      index = randint(0, count-1)
      id = questions[index]['id']
      if id not in previous_questions:
        not_found = False
        question = questions[index]

    return jsonify({
      "question": question,
      "total_questions": count,
      "current_category": category_id
    })


  '''
  Error handlers for all expected errors 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "Bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Not found"
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "Method not allowed"
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable"
    }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Internal server error"
    }), 500

  return app

    
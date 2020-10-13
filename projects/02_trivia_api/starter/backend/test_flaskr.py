import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
import settings


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            settings.DB_USER,
            settings.DB_PASSWORD,
            settings.DB_DOMAIN,
            self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    

    def tearDown(self):
        """Executed after reach test"""
        pass


    def test_after_request_allowing_headers(self):
        res = self.client().get('/categories')
        self.assertEqual(res.headers['Access-Control-Allow-Headers'],
                         'Content-Type, Authorization')
        self.assertEqual(res.headers['Access-Control-Allow-Methods'],
                         'GET, POST, PATCH, DELETE, OPTIONS')


    def test_get_all_categories(self):
        res = self.client().get('/categories')
        res_categories = res.json['categories']
        categories = Category.query.all()
        self.assertEqual(res.status_code, 200)
        for category in categories:
            self.assertEqual(res_categories[str(category.id)], category.type.lower())


    def test_get_all_questions_in_not_found_page(self):
        res = self.client().get('/questions?page=1000000')
        self.assertEqual(res.status_code, 404)
        self.assertDictEqual({
            'error': 404,
            'message': 'Not found',
            'success': False
        }, res.json)


    def test_get_all_questions_page(self):
        res = self.client().get('/questions?page=1')
        size = len(Question.query.all())
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.json.get('categories'))
        self.assertIsNotNone(res.json.get('questions'))
        self.assertIsNotNone(res.json.get('total_questions'))
        self.assertEqual(str(type(res.json['questions'])), "<class 'list'>")
        self.assertEqual(res.json['total_questions'], size)


    def test_delete_question(self):
        new_question = Question("Test question", "Test answer", 1, 1)
        new_question.insert()
        question_added = Question.query.filter(Question.id == new_question.id).one_or_none()
        self.assertIsNotNone(question_added)
        res = self.client().delete('/questions/' + str(new_question.id))
        self.assertEqual(res.status_code, 200)
        question_after_delete = Question.query.filter(Question.id == new_question.id).one_or_none()
        self.assertIsNone(question_after_delete)


    def test_failed_delete_question(self):
        res = self.client().delete('/questions/99999999')
        self.assertEqual(res.status_code, 422)
        self.assertDictEqual({
            "success": False, 
            "error": 422,
            "message": "Unprocessable"
        }, res.json)


    def test_add_question(self):
        new_question = Question("Added question", "Added answer", 1, 1)
        res = self.client().post('/questions', json={
            'question': new_question.question,
            'answer': new_question.answer,
            'difficulty': new_question.difficulty,
            'category': new_question.category,
        })
        self.assertEqual(res.status_code, 200)
        question = Question.query.filter(Question.id == res.json['question_id']).one_or_none()
        self.assertEqual(question.question, new_question.question)
        self.assertEqual(question.answer, new_question.answer)
        self.assertEqual(question.category, new_question.category)
        self.assertEqual(question.difficulty, new_question.difficulty)
        question.delete()


    def test_add_question_missing_data(self):
        new_question = Question("Added question", "Added answer", 1, 1)
        res = self.client().post('/questions', json={
            'answer': new_question.answer,
            'difficulty': new_question.difficulty,
            'category': new_question.category,
        })
        self.assertEqual(res.status_code, 422)
        self.assertDictEqual({
            "success": False, 
            "error": 422,
            "message": "Unprocessable"
        }, res.json)


    def test_search(self):
        res = self.client().post('/questions/searches', json={
            'searchTerm': '19',
        })
        self.assertEqual(res.status_code, 200)
        questions = res.json['questions']
        for q in questions:
            self.assertIn("19", q['question'])


    def test_search_not_found(self):
        res = self.client().post('/questions/searches', json={
            'searchTerm': 'ds$df34435@44df',
        })
        self.assertEqual(res.status_code, 404)
        self.assertDictEqual({
            "success": False, 
            "error": 404,
            "message": "Not found"
        }, res.json)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
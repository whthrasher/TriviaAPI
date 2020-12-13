import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from sqlalchemy import func

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests _
  for all available categories.
  '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.type for category in categories]

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)
        categories = [category.type for category in Category.query.all()]
        if len(current_questions) == 0:
          abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(Question.query.all()),
            'categories': categories,
            'currentCategory': None
        })
    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def remove_question(question_id):
      question = Question.query.get(question_id)
      question.delete()

      return jsonify ({
        'success': True,
        'deleted': question_id
      })
    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        q = request.get_json()['question']
        a = request.get_json()['answer']
        c = request.get_json()['category']
        d = request.get_json()['difficulty']

        question = Question(question=q, answer=a, category=c, difficulty=d)
        Question.insert(question)

        return jsonify({
            'success': True
        })

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_str = request.get_json()['searchTerm']
        print(request.get_json())
        print(search_str)
        question_query = Question.query.filter(Question.question.ilike('%{}%'.format(search_str))).all()
        formatted_questions = [question.format() for question in question_query]


        return jsonify({
            'questions': formatted_questions,
            'totalQuestions': len(question_query),
            'currentCategory': None
        })


    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        selection = Question.query.filter_by(category=category_id)
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(Question.query.all()),
            'currentCategory': category_id
        })
    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def retrieve_quiz():
        quiz_category = request.get_json()['quiz_category']['id']
        print(quiz_category)
        previous_questions = request.get_json()['previous_questions']

        if quiz_category == 0:
            questions_query = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:
            questions_query = Question.query.filter(Question.category == quiz_category, Question.id.notin_(previous_questions)).all()

        length_of_available_question=len(questions_query)

        return jsonify({
            'success': True,
            'question': Question.format(
                            questions_query[random.randrange(
                                0,
                                length_of_available_question
                            )]
                        )
        })
    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app

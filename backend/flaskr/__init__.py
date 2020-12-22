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

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.type for category in categories]

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

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

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def remove_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(404)
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
                })
        except:
            abort(422)
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        if not request.get_json():
            abort(400)

        q = body['question']
        a = body['answer']
        c = body['category']
        d = body['difficulty']

        question = Question(question=q, answer=a, category=c, difficulty=d)
        Question.insert(question)

        return jsonify({
            'success': True
        })

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        if not body:
            abort(400)
        search_str = body['searchTerm']
        question_query = Question.query.filter(Question.question.ilike
                                               ('%{}%'.format(search_str))
                                               ).all()
        formatted_questions = [question.format() for question in
                               question_query]

        return jsonify({
            'questions': formatted_questions,
            'totalQuestions': len(question_query),
            'currentCategory': None
        })

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def retrieve_questions_by_category(id):
        category_id = id+1
        selection = Question.query.filter(Question.category == category_id)
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'totalQuestions': len(Question.query.all()),
            'currentCategory': category_id
        })

    @app.route('/quizzes', methods=['POST'])
    def retrieve_quiz():
        quiz_category = int(request.get_json()['quiz_category']['id'])
        previous_questions = request.get_json()['previous_questions']

        if quiz_category == 0:
            questions_query = Question.query.filter(
                Question.id.notin_(previous_questions)).all()
        else:
            questions_query = Question.query.filter(
                Question.category == int(quiz_category)+1,
                Question.id.notin_(previous_questions)).all()

        length_of_available_question = len(questions_query)
        print(length_of_available_question)

        if length_of_available_question == 0:
            question = None
        else:
            question = Question.format(
                            questions_query[random.randrange(
                                0,
                                length_of_available_question
                            )]
                        )

        return jsonify({
            'success': True,
            'question': question
        })

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
            "message": "Not Found"
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


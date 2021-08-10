import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def paginate_questions(request, selection):                      # paginating questions method
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions
#################

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={'/': {'origins': '*'}})               # set up CORS, allow * origins

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        return response
#########################################
    @app.route('/categories', methods=['GET'])
    def retrieve_all_categories():
       
        categories = Category.query.order_by(Category.type).all()                  # get all available categories and add them to categories_dict dictionary
        categories_dict = {}                               
        for category in categories:
            categories_dict[category.id] = category.type

        if (len(categories_dict) == 0):                         
            abort(404)
       
        return jsonify({                           
            'success': True,
            'categories': categories_dict,
            'total_categories': len(categories_query)
        })
#################################################
    @app.route('/questions', methods=['GET'])
    def retrieve_questions():                            #GET requests for getting all questions.
       
        selection = Question.query.order_by(Question.id).all()                     
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.type).all()                          
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        # abort 404 if no questions
        if (len(current_questions) == 0):
            abort(404)

        # return data to view
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dict
        })
####################################################
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_specified_question(id):
                                                              #deleting a question by id.
        try:
            question = Question.query.filter_by(id=id).one_or_none()      # get the question by id

            if question is None:      
                abort(404)

            question.delete()      # the question will be deleted
            
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            total_questions = len(selection)

            return jsonify({                                                  
                'success': True,
                'deleted': id,
                'total_questions': total_questions
            })
        except:
            abort(422)
#################################################
    @app.route('/questions', methods=['POST'])
    def add_new_question():
                                               #Handles POST requests for creating new questions and searching questions.
       
        body = request.get_json()                     # load the request body

        if (body.get('searchTerm')):
            
            search_term = body.get('searchTerm')
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            if (len(selection) == 0):                  # 404 if no results found
                abort(404)

            paginated = paginate_questions(request, selection)

            # return results
            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all())
            })
                                                    # if no search term, create new question
        else:
            # load data from body
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')

            # ensure all fields have data
            if ((new_question is None) or (new_answer is None)
                    or (new_difficulty is None) or (new_category is None)):
                abort(422)

            try:
                # create and insert new question
                question = Question(question=new_question, answer=new_answer,
                                    difficulty=new_difficulty, category=new_category)
                question.insert()

                # get all questions and paginate
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                # return data to view
                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
            except
                abort(422)
##########################################

    @app.route('/categories/<int:id>/questions')
    def retrieve_questions_by_category(id):
                                                                         #   GET requests for getting questions.
        category = Category.query.filter_by(id=id).one_or_none()
                                                     
        if (category is None):           #bad request if category isn't found
            abort(400)

        selection = Question.query.filter_by(category=category.id).all()
        paginated = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

    
    ########################################################
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
                                                              #Handles POST requests for playing quiz.
        body = request.get_json()
        previous = body.get('previous_questions')
        category = body.get('quiz_category')
                                                                 # category or previous questions not found
        if ((category is None) or (previous is None)):
            abort(400)

        if (category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all()
        total = len(questions)                               
        def get_random_question():                          # get random question
            return questions[random.randrange(0, len(questions), 1)]
                                                                                # to check if question is used
        def check_if_used(question):
            u = False
            for q in previous:
                if (q == question.id):
                    u = True
            return u

        question = get_random_question()
        while (check_if_used(question)):
            question = get_random_question()
            
            if (len(previous) == total):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
        })

# error handlers
############################################################################
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405
            

    return app

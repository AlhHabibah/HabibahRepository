import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

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
  CORS(app, resources={'/': {'origins': '*'}})
  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
      page = request.args.get('page', 1, type=int)
      categories_query = Category.query.order_by(Category.type).all()

      return jsonify({
            'success':True,
            'categories':{category.id: category.type for category in categories_query},
            'total_categories': len(categories_query)
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
  @app.route('/questions')
  def retrieve_questions():
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      categories = Category.query.order_by(Category.type).all()

      if len(current_questions) == 0:
          abort(404)

      return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': {category.id: category.type for category in categories},
            'current_category': None
        })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
      try:
          question = Question.query.get(question_id)
          if question is None:
              abort(404)

          question.delete()
          current_questions = paginate_questions(request, selection)
          flash('question was successfully deleted!')

          return jsonify({
                'success': True,
                'deleted': question_id,
                'question': current_question,
                'total_question': len(question)
            })

      except:
            abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/', methods=['POST'])
  def create_question():
      body = request.get_json()

      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_category = body.get('category', None)
      new_difficulty = body.get('difficulty', None)

      try:
          question = questions(question='new_question', answer='new_answer', category='new_category', difficulty ='new_difficulty')
          question.insert()

          selection = question.query.order_by(question.id).all()
          current_questions = paginate_questions(request, selection)
          flash('question was successfully created!')

          return jsonify({
                'success':True,
                'created':question_id,
                'question':current_question,
                'total_questions': len(selection)
            })

      except:
          abort(422)
            

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
      search = request.form.get('search_term')
      questions = questions.query.filter(questions.name.ilike('%' + request.form['search_term'] + '%')).all()
      result = []

      for search in questions:
          result.append({
                "id":search.id,
                "question":search.question,
                "answer":search.answer,
                "category":search.category,
                "new_difficulty":search.difficulty,
            })

          response={
                "count":len(questions),
                "data":result
            }
          return jsonify({
               'success':True,
               'question':current_question,
               'total_questions': len(questions)
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
      try:
          questions = Question.query.filter(
          Question.category == str(category_id)).all()

          return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
      except:
          abort(404)


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
  @app.route ('/quizzes/', methods=['POST'])
  def play_quiz():
      try:
          body = request.get_json()
          category_id = int(data["quiz_category"]["id"])
          category = Category.query.get(category_id)
          previous_questions = body.get('previous_questions')

          if not category == None:
              if "previous_questions" in data and len(previous_questions) > 0:
                  questions = Question.query.filter(
                  Question.id.notin_(previous_questions),
                  Question.category == category.id
                  ).all()
              else:
                    questions = Question.query.filter(Question.category == category.id).all()
          else:
              if "previous_questions" in data and len(previous_questions) > 0:
                  questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
              else:
                  questions = Question.query.all()
          max = len(questions) -1
          if max > 0:
              question = questions[random.randint(0, max)].format()
          else:
              question = False

          return jsonify({
                "success": True,
                "question": question
            })
      except:
          abort(500, "Error loading question")

  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
      "success": False,
      "error": 404,
      "message": "Resource Not found"
     }), 404


  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
     }), 422
      
  return app

    

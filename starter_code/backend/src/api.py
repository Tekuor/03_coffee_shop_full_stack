import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from flask import Flask
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import sys

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def retrieve_drinks():
    drinks = Drink.query.all()

    drinksFormatted = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinksFormatted
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
  drinks = Drink.query.all()

  drinksFormatted = [drink.long() for drink in drinks]

  return jsonify({
    'success': True,
    'drinks': drinksFormatted
  })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    try:
      drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
      drink.insert()

      return jsonify({
        'success': True,
        'drinks': drink.long()
      })

    except:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Incorrect claims. Please, check the audience and issuer.'
        }, 401)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload,id):
    try:
      body = request.get_json()
      drink = Drink.query.filter(Drink.id == id).one_or_none()

      if drink is None:
        abort(404)

      if 'title' in body:
        drink.title = body.get('title', None)
      if 'recipe' in body:
        drink.recipe =json.dumps(body.get('recipe', None))

      drink.update()
      drinksFormatted = [drink.long()]

      return jsonify({
        'success': True,
        'drinks': drinksFormatted
      })

    except:
      abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload,id):
    try:
      drink = Drink.query.filter(Drink.id == id).one_or_none()

      if drink is None:
        abort(404)

      drink.delete()

      return jsonify({
        'success': True,
        'delete': id
      })

    except:
      abort(422)



## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(500)
def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': "server error"
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': "bad request"
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
      'success': False,
      'error': 401,
      'message': "unauthorized"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
      'success': False,
      'error': 403,
      'message': "forbidden"
    }), 403

@app.errorhandler(405)
def invalid_method(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': "invalid method"
    }), 405

@app.errorhandler(409)
def duplicate_resource(error):
    return jsonify({
      'success': False,
      'error': 409,
      'message': "duplicate resource"
    }), 409

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def errorFailed(error):
    return jsonify({
                    "success": False, 
                    "error": error.status_code,
                    "message": error.error
                    }), error.status_code

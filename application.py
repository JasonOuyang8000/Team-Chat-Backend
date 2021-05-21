import os
from flask import Flask, request
from flask_cors import CORS
import sqlalchemy
from sqlalchemy.orm import joinedload
import bcrypt
import jwt
import requests
app = Flask(__name__)
import helper
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
import models
models.db.init_app(app)

WEATHER_API = os.environ.get('WEATHER_API')

@app.before_request
def hook():
    if request.headers.get('Authorization'):
     
        user_token = helper.tools.get_token(request.headers['Authorization'])
      
        decode = jwt.decode(user_token,os.environ.get('SECRET'),algorithms="HS256")

        user = models.User.query.filter_by(id = decode['id']).first()
        if user == None:
            return {
                'message': 'User not found'
            },400
        request.user = user
    else: 
        request.user = None
  

def root():
  return 'ok'
app.route('/', methods=["GET"])(root)





@app.route('/user/login', methods=["POST"])
def login():
  data = request.json  
  if data.get('username') == None or data.get('password') == None:
        return {
            'message': 'Username or password is not filled'
        },401

  user = models.User.query.filter_by(username=data["username"]).first()
  if user == None:
      return {
          'message':'User does not exist'
      },401

  if bcrypt.checkpw(data["password"].encode('utf8'), user.password.encode('utf8')):
    
    user_token = jwt.encode({"id": user.id}, os.environ.get('SECRET'))

    return { "usertoken": user_token,
    "user": user.to_json() }
  else:
    return { "message": "login failed" }, 401

@app.route('/user/verify', methods=["GET"])
def verify():
  user = request.user
  
  if user:
    return { "user": user.to_json() }
  else:
    return { "message": "user not found" }, 404

@app.route('/user/signup', methods=["POST"])
def signup():
  try:
    data = request.json
    if data.get('username') == None or data.get('password') == None:
        return {
            'message': 'Username and password cannot be empty.'
        },401
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(data['password'].encode('utf8'), salt).decode('utf8')
    user = models.User(
      username=data['username'],
      password=hashed,
    )
    models.db.session.add(user)
    models.db.session.commit()
    user_token = jwt.encode({"id": user.id}, os.environ.get('SECRET'))

    return { "usertoken": user_token,
    "user": user.to_json() }
  except sqlalchemy.exc.IntegrityError:
    return { "message": "username already taken" }, 400

@app.route('/workspace', methods=["GET","POST"])
def workspaces():
  try: 
    user = request.user
  
    if user == None:
       return { "message": "user not found" }, 404


    if request.method == 'GET':
      workspaces = models.Workspace.query.options(joinedload('owner')).all()
    
      return {
        'workspaces': [workspace.to_json() for workspace in workspaces]
      },200
    elif request.method == 'POST':
      if user.limit == 0:
        return {
          'message': 'You ran out of workspaces'
        }, 401
      data = request.json

      if data.get('name') == None or data.get('protected') == None:
        return {
          'message': 'Please Fill out the fields.'
        },401


      if data.get('protected') == True and data.get('password') == None:
        return {
          'message': 'Please add a Password.' 
        },401
   
    


      workspace = models.Workspace(
        name = data['name'],
        protected = data['protected'],
        password = bcrypt.hashpw(str(data['password']).encode('utf8'), bcrypt.gensalt()).decode('utf8') if data.get('protected') else None
      )
      user.limit -= 1
      user.owned_spaces.append(workspace)

      models.db.session.commit()

 

      return {
        'workspace': workspace.to_json()
      }
  except sqlalchemy.exc.IntegrityError:
    return {
      'message':'Workspace already exists...'
    }
  except Exception as ex:
    return {
        'message': str(ex)
    },400
  

if __name__ == '__main__':
  port = os.environ.get('PORT') or 5000
  app.run('0.0.0.0', port=port, debug=True)
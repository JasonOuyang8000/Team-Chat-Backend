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
from flask_socketio import SocketIO


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

app.config['SQLALCHEMY_ECHO'] = True
import models
models.db.init_app(app)

socket_io = SocketIO(app,cors_allowed_origins="*")

WEATHER_API = os.environ.get('WEATHER_API')

@app.before_request
def hook():
  try:
    if request.headers.get('Authorization') and request.headers.get('wstoken'):
      user_token = helper.tools.get_token(request.headers['Authorization'])

      decode = jwt.decode(user_token,os.environ.get('SECRET'),algorithms="HS256")
      wdecode = jwt.decode(request.headers.get('wstoken'),os.environ.get('W_SECRET'),algorithms="HS256")
      
      user = models.User.query.filter_by(id = decode['id']).first()
      workspace = models.Workspace.query.options(joinedload('channels')).filter_by(id = wdecode['id']).first()

      if user == None:
        return {
            'message': 'User not found.'
        },400
      elif workspace == None:
        return {
          'message': 'Workspace not found.'
        }
      
      if workspace.check_user(user):
        request.user = user
        request.workspace = workspace
      else:
        return {
          'message': 'Unauthorized'
        },401
    elif request.headers.get('Authorization'):
      user_token = helper.tools.get_token(request.headers['Authorization'])
    
      decode = jwt.decode(user_token,os.environ.get('SECRET'),algorithms="HS256")

      user = models.User.query.filter_by(id = decode['id']).first()
      if user == None:
          return {
              'message': 'User not found.'
          },400
      request.user = user
      request.workspace = None
    else: 
        request.user = None
        request.workspace = None
  except Exception as ex:
    return {
        'message': str(ex)
    },400

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
    return { "message": "Password is incorrect." }, 401

@app.route('/user/verify', methods=["GET"])
def verify():
  user = request.user
  
  if user:
    return { "user": user.to_json() }
  else:
    return { "message": "User not found.." }, 401

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
       return { "message": "User not found." }, 401


    if request.method == 'GET':
      workspaces = models.Workspace.query.options(joinedload('owner')).options(joinedload('users')).all()
    
      return {
        'workspaces': [workspace.to_json() for workspace in workspaces]
      },200
    elif request.method == 'POST':
      if user.limit == 0:
        return {
          'message': 'You ran out of workspaces/'
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
      workspace.users.append(user)
      
      channel = models.Channel(
        name="main",
      )

      workspace.channels.append(channel)

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

@app.route('/workspace/<id>/join', methods=["POST"])
def access_workspace(id):
  try: 
    user = request.user
    if user == None:
      return { 'message': 'User not found.' }, 401
    workspace = models.Workspace.query.options(joinedload('owner')).options(joinedload('users')).get(id)
    if workspace == None:
      return {
        'message': 'Workspace not found.'
      }, 401

    if workspace.check_user(user):
 
      workspace_token = jwt.encode({'id': workspace.id}, os.environ.get('W_SECRET'))

      return { 
        'worktoken': workspace_token
      }
    else:
      if workspace.protected == False:
        workspace.users.append(user)
        models.db.session.commit()
        workspace_token = jwt.encode({'id': workspace.id}, os.environ.get('W_SECRET'))

        return { 
          'worktoken': workspace_token
        }

      data = request.json
      if data.get('password') == None:
        return {
          'message': 'Password is empty'
        },401
      if bcrypt.checkpw(str(data['password']).encode('utf8'), workspace.password.encode('utf8')):
        workspace.users.append(user)
        models.db.session.commit()
        workspace_token = jwt.encode({'id': workspace.id}, os.environ.get('W_SECRET'))

        return { 
          'worktoken': workspace_token
        }
      else: 
        return {
          'message': 'Password is incorrect.'
        },401
  except Exception as ex:
    return {
        'message': str(ex)
    },400

@app.route('/workspace/channel', methods=["GET"])
def get_channels():
  try: 
    user = request.user
    workspace = request.workspace
    if user == None or workspace == None:
      return { 'message': 'unauthorized access' }, 401
    return {
      'workspace': workspace.to_json_channels()
    }

  except Exception as ex:
    return {
        'message': str(ex)
    },400
@app.route('/workspace/channel/message/<id>', methods=["GET","POST"])
def get_channel_messages(id):
  try:
    user = request.user
    workspace = request.workspace
    if user == None or workspace == None:
      return { 'message': 'unauthorized access' }, 401

   

    channel = models.Channel.query.options(joinedload(models.Channel.messages).joinedload(models.Channel_Message.user)).get(id)
    
    if channel == None:
      return {
        'message': 'Channel not found'
      }


    if request.method == 'GET':
  
      return channel.to_json_messages()

    elif request.method == 'POST':  
      data = request.json
      if data.get('text') == None:
        return {
          'message': 'Message is not posted'
        },401

      message = models.Channel_Message(
        text = data['text']
      )

      channel.messages.append(message)
      user.messages.append(message)

      models.db.session.commit()

    
      return {
        'message': message.to_json()
      }


    else:
      return {
        error: 'Where are you going?'
      },404
  except Exception as ex:
    return {
        'message': str(ex)
    },400
@app.route('/workspace/verify', methods=["GET"])
def verify_workspace():
  try:
    user = request.user
    workspace = request.workspace 
    if user:
      return { "user": user.to_json(),"workspace": workspace.to_json() }
    else:
      return { "message": "unauthenticated" }, 401
  except Exception as ex:
    return {
        'message': str(ex)
    },400




if __name__ == '__main__':
  port = os.environ.get('PORT') or 5000
  app.run('0.0.0.0', port=port, debug=True)
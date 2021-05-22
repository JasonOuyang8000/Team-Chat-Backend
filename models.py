from sqlalchemy.sql.expression import true
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String, nullable=False, unique=True)
  password = db.Column(db.String, nullable=False,)
  limit = db.Column(db.Integer,server_default='2')
  messages = db.relationship('Channel_Message', backref='user')
  created= db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
  owned_spaces = db.relationship('Workspace', backref='owner')
  work_spaces = db.relationship('Workspace',secondary='user_workspaces', backref='users')
  alerts = db.relationship('Channel_Alert', backref='user')
  def to_json(self):
    return {
      'id': self.id,
      'username': self.username,
      'limit': self.limit
    }

    
class Workspace(db.Model):
  __tablename__ = 'workspaces'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  password = db.Column(db.String, nullable=True)
  protected = db.Column(db.Boolean, default=False)
  channels = db.relationship('Channel', backref='workspace')
  ownerId = db.Column(db.Integer,db.ForeignKey('users.id'))
  created = db.Column(db.DateTime,server_default=db.func.now())
  updated = db.Column(db.DateTime,server_default=db.func.now(), server_onupdate=db.func.now())
  def to_json(self):
    return {
      'id': self.id,
      'name': self.name,
      'owner': self.owner.to_json(),
      'users': [user.to_json() for user in self.users],
      'created':self.created,
      'protected': self.protected
    }
  def to_json_channels(self):
    return {
      'id': self.id,
      'name': self.name,
      'owner': self.owner.to_json(),
      'users': [user.to_json() for user in self.users],
      'created':self.created,
      'protected': self.protected,
      'channels': [channel.to_json() for channel in self.channels]
    }

  def check_user(self,user):
    if self.owner.id == user.id:
      return True
    for u in self.users:
      if u.id == user.id:
        return True
    return False


class Channel_Alert(db.Model):
    __tablename__ = 'channel_alerts'
    id = db.Column(db.Integer, primary_key=True)
    read = db.Column(db.Boolean, nullable=False)
    userId = db.Column(db.Integer,db.ForeignKey('users.id'))
    channelId = db.Column(db.Integer,db.ForeignKey('channels.id'))
    created = db.Column(db.DateTime,server_default=db.func.now())
    updated = db.Column(db.DateTime,server_default=db.func.now(), server_onupdate=db.func.now())


class Channel(db.Model):
    __tablename__ = 'channels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    workspaceId = db.Column(db.Integer,db.ForeignKey('workspaces.id'))
    messages = db.relationship('Channel_Message', backref='channel')
    alerts = db.relationship('Channel_Alert', backref='channel')
    created = db.Column(db.DateTime,server_default=db.func.now())
    updated = db.Column(db.DateTime,server_default=db.func.now(), server_onupdate=db.func.now())
    def to_json(self):
      return {
        'id': self.id,
        'name':self.name,
        'created': self.created
      }

    def to_json_messages(self):
      return {
        'id': self.id,
        'name': self.name,
        'created': self.created,
        'messages': [message.to_json() for message in self.messages]
      }

class Channel_Message(db.Model):
    __tablename__ = 'channel_messages'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    userId = db.Column(db.Integer,db.ForeignKey('users.id'))
    channelId = db.Column(db.Integer,db.ForeignKey('channels.id'))
    created = db.Column(db.DateTime,server_default=db.func.now())
    updated = db.Column(db.DateTime,server_default=db.func.now(), server_onupdate=db.func.now())
    def to_json(self):
      print(self.user)
      return {
        'id':self.id,
        'created': self.created,
        'text': self.text,
        'user': {
          'id': self.user.id,
          'created': self.user.created,
          'username': self.user.username,
        }
      }
  
## Reference Table
class User_workspace(db.Model):
  __tablename__ = 'user_workspaces'
  id = db.Column(db.Integer, primary_key=True)
  userId = db.Column(db.Integer,db.ForeignKey('users.id'))
  workspaceId = db.Column(db.Integer,db.ForeignKey('workspaces.id'))
  created = db.Column(db.DateTime,server_default=db.func.now())
  updated = db.Column(db.DateTime,server_default=db.func.now(), server_onupdate=db.func.now())


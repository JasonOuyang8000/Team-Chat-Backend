from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String, nullable=False, unique=True)
  password = db.Column(db.String, nullable=False,)
  limit = db.Column(db.Integer,server_default='2')
  created= db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
  owned_spaces = db.relationship('Workspace', backref='owner')
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
  ownerId = db.Column(db.Integer,db.ForeignKey('users.id'))
  created = db.Column(db.DateTime,server_default=db.func.now())
  updated = db.Column(db.DateTime,server_default=db.func.now(), server_onupdate=db.func.now())
  def to_json(self):
    return {
      'id': self.id,
      'name': self.name,
      'owner': self.owner.to_json(),
      'created':self.created,
      'protected': self.protected
    }

  


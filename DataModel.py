from google.appengine.ext import ndb

class Question(ndb.Model):
    author = ndb.UserProperty()
    name = ndb.StringProperty(indexed=False)
    tags = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    create_time = ndb.DateTimeProperty(auto_now_add=True)
    modify_time = ndb.DateTimeProperty(auto_now=True)
    

class Answer(ndb.Model):
    author = ndb.UserProperty()
    name = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    create_time = ndb.DateTimeProperty(auto_now_add=True)
    modify_time = ndb.DateTimeProperty(auto_now=True) 
    vote =  ndb.IntegerProperty()
    difference = ndb.IntegerProperty()

class QVote(ndb.Model):
    author = ndb.UserProperty()
    vote = ndb.StringProperty(indexed=False)
    
class AVote(ndb.Model):
    author = ndb.UserProperty()
    vote = ndb.StringProperty(indexed=False)

class Tag(ndb.Model):
    name = ndb.StringProperty()
    
class QuestionImage(ndb.Model):
    img = ndb.BlobProperty()
    create_time = ndb.DateTimeProperty(auto_now_add=True)
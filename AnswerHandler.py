import os
import urllib
import string
import jinja2
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from DataModel import Answer, AVote

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# create or update question
class CreateAnswerPage(webapp2.RequestHandler):
    def get(self):
        qid = self.request.get('qid')
        aid = self.request.get('aid', '')
        aname = ''
        acontent = ''
        query_params = {'qid': qid}
        user = users.get_current_user()   
        create_btn_txt = 'Create Answer'
        if not user:
            self.redirect('/view_question?%s' % urllib.urlencode(query_params))
       
        # edit answer
        if aid != '':
            akey = ndb.Key(urlsafe=aid)
            answer = akey.get()
            # if answer creator is not current user 
            if answer.author.nickname() != user.nickname():
                    self.redirect('/view_question?%s' % urllib.urlencode(query_params))
            aname = answer.name 
            acontent = answer.content
            create_btn_txt = 'Update Answer'
            query_params = {'qid': qid, 'aid': aid}
        
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_values = {
            'user': users.get_current_user(),
            'query_params': urllib.urlencode(query_params),
            'aname': aname,
            'acontent': acontent,
            'url': url,
            'url_linktext': url_linktext,
            'create_btn_txt': create_btn_txt,
        }
        template = JINJA_ENVIRONMENT.get_template('/HTML/CreateAnswer.html')
        self.response.write(template.render(template_values))

# create or update question
class SaveAnswerPage(webapp2.RequestHandler):
    def post(self):
        qid = self.request.get('qid')
        qkey = ndb.Key(urlsafe=qid)     
        aid = self.request.get('aid', '')
        aname = self.request.get('aname')
        acontent = self.request.get('acontent')
        query_params = {'qid': qid}
        
        if not users.get_current_user():
            self.redirect('/view_question?%s' % urllib.urlencode(query_params))
        
        if aid == '':
            answer = Answer(parent=qkey)
        else:
            akey = ndb.Key(urlsafe=aid)
            answer = akey.get()
            
        answer.author = users.get_current_user()
        answer.name = aname
        answer.content = acontent
        answer.put()        
        self.redirect('/view_question?%s' % urllib.urlencode(query_params))
                
class VoteAnswerPage(webapp2.RequestHandler):
    def post(self):
        qid = self.request.get('qid')
        query_params = {'qid':qid}
        vote_str = self.request.get('vote')
        list = vote_str.split("====")
        aid = list[1]
        vote = list[0]
        user = users.get_current_user()
        akey = ndb.Key(urlsafe=aid)
        avotes = AVote.query(ancestor=akey)
        vote_count = avotes.filter(AVote.author == user).count()
        if vote_count == 1:
            # if user has already voted before then get the old vote 
            avoteList = []
            for v in avotes.filter(AVote.author == user):
                avoteList.append(v)
            avote = avoteList[0]
        else:
            avote =AVote(parent=akey)
        avote.vote = vote
        avote.author = user
        avote.put()
        self.redirect('/view_question?%s' % urllib.urlencode(query_params))
                           

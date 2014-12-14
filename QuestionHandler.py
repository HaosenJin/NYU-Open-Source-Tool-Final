import os
import urllib
import string
import jinja2
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb, db
from DataModel import Question, QVote, AVote, Answer, QuestionImage
from DataModel import Tag
from Utility import Formater


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# create or update question 
class CreateQuestionPage(webapp2.RequestHandler):
    def get(self):   
        if not users.get_current_user():
            self.redirect('/')
        qid = self.request.get('qid', '')
        qname = ''
        qcontent = ''
        qtag = ''
        
        if qid == '':
            create_btn_txt = 'Create Question'
            query_params = {'qid': ''}
            images = None
            img_num = 0
        else:
            create_btn_txt = 'Update Question'
            query_params = {'qid': qid}
            qkey = ndb.Key(urlsafe=qid)
            q = qkey.get()
            qname = q.name       
            qcontent = q.content
            qtag = q.tags
            # get question images 
            images = QuestionImage.query(ancestor=qkey).order(-QuestionImage.create_time) 
            img_num = QuestionImage.query(ancestor=qkey).order(-QuestionImage.create_time).count()
            
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_values = {
            'user': users.get_current_user(),
            'query_params': urllib.urlencode(query_params),
            'qname': qname,
            'qcontent': qcontent,
            'qtag': qtag,
            'images':images,
            'imgcount':img_num,
            'url': url,
            'url_linktext': url_linktext,
            'create_btn_txt': create_btn_txt,
        }
        template = JINJA_ENVIRONMENT.get_template('/HTML/CreateQuestion.html')
        self.response.write(template.render(template_values))
       
# save or update question to datastore
class SaveQuestionPage(webapp2.RequestHandler):
    def post(self):
        qid = self.request.get('qid')
        qname = self.request.get('qname')
        qtag = self.request.get('qtag')
        qcontent = self.request.get('qcontent')   
        img_names = self.request.get('img_names')
        img_names_list = img_names.split(";")        
        if not users.get_current_user():
            self.redirect('/')                
        if qid == '':
            # create new question
            q = Question()
        else:
            # update old question
            qkey = ndb.Key(urlsafe=qid)
            q = qkey.get()       
        q.author = users.get_current_user()
        q.content = qcontent
        q.tags = qtag
        q.name = qname
        q.put()
        
        # save images to datastore
        for img in img_names_list:
            img_content = self.request.get(img)
            if img_content != '':
                image = QuestionImage(parent=q.key)
                image.img = db.Blob(img_content)
                image.put()
                
        
        # update tags in the datastore
        tags = qtag.split(";");
        for tag in tags:
            tagstrip = string.strip(tag)
            if tagstrip != '':
                existingTag = Tag.query(Tag.name == tagstrip).count()            
                if  existingTag == 0:
                    t = Tag(name=tagstrip)
                    t.put()       
        query_params = {'qid': q.key.urlsafe()}
        self.redirect('/view_question?%s' % urllib.urlencode(query_params))
        
# view question            

class ViewQuestionPage(webapp2.RequestHandler):
    def get(self):
        qid = self.request.get('qid')
        if qid == '':
            self.redirect('/')        
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login' 
        qkey = ndb.Key(urlsafe=qid)
        question = qkey.get()
        question.content = jinja2.Markup(Formater.format_html_content(question.content))
        # calculate the question votes
        qvotes = QVote.query(ancestor=qkey)
        qvote_count = 0
        for v in qvotes:
            if v.vote == "up":
                qvote_count = qvote_count + 1
            if v.vote == "down":
                qvote_count = qvote_count - 1
         
        # calculate all the answer votes and re-order answers according to the difference between up and down votes
        answers = Answer.query(ancestor=qkey).order(-Answer.modify_time)
        answers_reorder = []
        for a in answers:
            avotes = AVote.query(ancestor=a.key)
            up = 0
            down = 0
            for avote in avotes:
                if avote.vote == 'up':
                    up = up + 1
                else: 
                    down = down + 1
            a.vote = up - down
            a.difference = abs(up - down)
            a.content = jinja2.Markup(Formater.format_html_content(a.content))
            answers_reorder.append(a)            
        answers_reorder.sort(key=lambda a:a.difference, reverse=True)
        
        # get question images 
        images = QuestionImage.query(ancestor=qkey).order(-QuestionImage.create_time)   
        img_num = QuestionImage.query(ancestor=qkey).order(-QuestionImage.create_time).count()              
        query_params = {'qid': qid}            
        template_values = {
            'user': users.get_current_user(),
            'query_params':urllib.urlencode(query_params),
            'question':question,
            'images':images,
            'imgcount':img_num,
            'answers':answers_reorder,
            'qvote': qvote_count,
            'url': url,
            'url_linktext': url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('/HTML/ViewQuestion.html')
        self.response.write(template.render(template_values))
                
class VoteQuestionPage(webapp2.RequestHandler):
    def post(self):
        qid = self.request.get('qid')
        vote = self.request.get('vote')
        query_params = {'qid': qid}
        user = users.get_current_user()
        if not user:
            self.redirect('/view_question?%s' % urllib.urlencode(query_params))     
        qkey = ndb.Key(urlsafe=qid)
        qvotes = QVote.query(ancestor=qkey)
        qvcount = qvotes.filter(QVote.author == user).count()
        
        if qvcount > 0:
            # if user has already voted before then get the old vote 
            qvoteList = []
            for v in qvotes.filter(QVote.author == user):
                qvoteList.append(v)
            qvote = qvoteList[0]
        else:
            # not voted before then create a new vote 
            qvote = QVote(parent=qkey)
        qvote.vote = vote
        qvote.author = user
        qvote.put()
        self.redirect('/view_question?%s' % urllib.urlencode(query_params))

        
    

import os
import urllib
import string

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
import QuestionHandler
import AnswerHandler
import ImageHandler

from DataModel import Question, Tag, QVote, AVote, Answer
from Utility import Formater

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

pagesize = 10

def generate(self, tags, page_num):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        allquestions = Question.query().order(-Question.modify_time)
        questions = []
        
        if tags == '':
            # get all the questions
            qlen = Question.query().count()
            for q in allquestions:
                questions.append(q)
        else:
            # get all the questions that have the tags specified in the query string
            qlen = 0
            for q in allquestions:
                for tag in tags.split(";"):
                    if tag != "" and q.tags.find(tag) != -1:
                        questions.append(q)
                        qlen = qlen + 1
                                
        # calculate page
        if qlen % pagesize == 0:
            total_page = qlen / pagesize
        else:
            total_page = qlen / pagesize + 1
        
        # if the length of the content of the question is greater than 500 then strip the first 500 characters
        for q in questions:
            if len(q.content) > 500:
                q.content = q.content[0:499] + '...'
          
        # format html tags for content       
        for q in questions:
            q.content = jinja2.Markup(Formater.format_html_content(q.content))

        if page_num > total_page:
            page_num = total_page
        if page_num < 1:
            page_num = 1
        prev_page_params = {'tags':tags, 'page_num':page_num - 1}
        next_page_params = {'tags':tags, 'page_num':page_num + 1}
        
        template_values = {
            'user': users.get_current_user(),
            'questions': questions[(page_num - 1) * pagesize:page_num * pagesize],
            'tags': Tag.query(),
            'total_page':total_page,
            'prev_page':page_num - 1,
            'next_page':page_num + 1,
            'prev_page_params':urllib.urlencode(prev_page_params),
            'next_page_params':urllib.urlencode(next_page_params),
            'url': url,
            'url_linktext': url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('/HTML/index.html')
        self.response.write(template.render(template_values))

class MainPage(webapp2.RequestHandler):        
    def post(self):
        tags = self.request.get('tags', '')
        page_str = self.request.get('page_num', '1')
        page_num = string.atoi(page_str)
        generate(self, tags, page_num)
        
    def get(self):
        tags = self.request.get('tags', '')
        page_str = self.request.get('page_num', '1')
        page_num = string.atoi(page_str)
        generate(self, tags, page_num)

        
class RSSXML(webapp2.RequestHandler):              
    def get(self):
        output = []
        output.append("<questions>") 
        allquestions = Question.query().order(-Question.modify_time)
        for question in allquestions:
            output.append("<question>")
            output.append("<author>"+question.author.nickname()+"</author>")    
            output.append("<name>"+question.name+"</name>")  
            output.append("<content>"+question.content+"</content>")  
            output.append("<createTime>"+str(question.create_time)+"</createTime>") 
            output.append("<modifyTime>"+str(question.modify_time)+"</modifyTime>")
            
            # generate tag information
            tags = question.tags.split(";")
            output.append("<tags>");
            for tag in tags:
                output.append("<tag>"+tag+"</tag>")
            output.append("</tags>");
            
            # generate question vote information    
            output.append("<questionVotes>");
            for vote in QVote.query(ancestor=question.key):
                output.append("<vote>")
                output.append("<author>"+vote.author.nickname()+"</author>")
                output.append("<content>"+vote.vote+"</content>")    
                output.append("</vote>")
            output.append("</questionVotes>");   
                     
            #generate answers
            output.append("<answers>");  
            for answer in Answer.query(ancestor=question.key):
                output.append("<answer>");
                output.append("<author>"+answer.author.nickname()+"</author>")
                output.append("<name>"+answer.name+"</name>")  
                output.append("<content>"+answer.content+"</content>")  
                output.append("<createTime>"+str(answer.create_time)+"</createTime>") 
                output.append("<modifyTime>"+str(answer.modify_time)+"</modifyTime>")
                
                # generate answer vote information   
                output.append("<answerVotes>");
                for vote in AVote.query(ancestor=answer.key):
                    output.append("<vote>")
                    output.append("<author>"+vote.author.nickname()+"</author>")
                    output.append("<content>"+vote.vote+"</content>")    
                    output.append("</vote>")
                output.append("</answerVotes>");            
                output.append("</answer>");    
            output.append("</answers>");     
            output.append("</question>")    
        output.append("</questions>")         
        xml = ''
        for s in output:
            xml = xml +s
        self.response.headers['Content-Type'] = 'Text/XML'        
        self.response.write(xml)
        
        
        
        

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/RSS', RSSXML),
    ('/create_question', QuestionHandler.CreateQuestionPage),
    ('/save_question', QuestionHandler.SaveQuestionPage),
    ('/view_question', QuestionHandler.ViewQuestionPage),
    ('/vote_question', QuestionHandler.VoteQuestionPage),
    ('/create_answer', AnswerHandler.CreateAnswerPage),
    ('/save_answer', AnswerHandler.SaveAnswerPage),
    ('/vote_answer', AnswerHandler.VoteAnswerPage),
    ('/img_question', ImageHandler.QuestionImage),
    ('/delete_image', ImageHandler.DeleteQuestionImage),
    ('/view_image', ImageHandler.ViewImage),
    ('/save_image', ImageHandler.SaveImage),
], debug=True)

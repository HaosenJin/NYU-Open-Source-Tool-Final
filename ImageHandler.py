import os
import urllib
import string
import jinja2
import webapp2

from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url
from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
pagesize = 5
class QuestionImage(webapp2.RequestHandler):
    def get(self):
        imgKey = ndb.Key(urlsafe=self.request.get('img_id'))
        image = imgKey.get()
        if image.img:
            self.response.headers['Content-Type'] = 'image/*'
            self.response.out.write(image.img)
        else:
            self.response.out.write('No image')

class DeleteQuestionImage(webapp2.RequestHandler):
    def get(self):
        qid = self.request.get('qid', '')
        img_id = self.request.get('img_id', '')
        if qid == '':
            self.redirect('/')
        query_params = {'qid':qid}
        if img_id == '':
            self.redirect('/create_question?%s' % urllib.urlencode(query_params)) 
        imgKey = ndb.Key(urlsafe=img_id)
        img = imgKey.get()
        img.key.delete()
        self.redirect('/create_question?%s' % urllib.urlencode(query_params)) 

class ViewImage(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect('/')
        page_str = self.request.get('page', '1')
        page_num = string.atoi(page_str)
        # get all images
        image_urls = []
        images = []
        image_count = 0
        for b in BlobInfo.all():
            images.append(b)            
        images.sort(key=lambda i:i.creation, reverse=True)        
        for img in images:
            image_urls.append(get_serving_url(img.key()))
            image_count = image_count + 1    
                
        # calculate page
        if image_count % pagesize == 0:
            total_page = image_count / pagesize
        else:
            total_page = image_count / pagesize + 1
        if page_num > total_page:
            page_num = total_page
        if page_num < 1:
            page_num = 1
        prev_page_params = {'page':page_num - 1}
        next_page_params = {'page':page_num + 1}
           
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        upload_url = blobstore.create_upload_url('/save_image')
        template_values = {
            'user': users.get_current_user(),
            'url': url,
            'url_linktext': url_linktext,
            'images':image_urls[(page_num - 1) * pagesize:page_num * pagesize],
            'imgcount':image_count,
            'total_page':total_page,
            'prev_page':page_num - 1,
            'next_page':page_num + 1,
            'prev_page_params':urllib.urlencode(prev_page_params),
            'next_page_params':urllib.urlencode(next_page_params),
            'upload_url':upload_url
        }
        template = JINJA_ENVIRONMENT.get_template('/HTML/ViewImage.html')
        self.response.write(template.render(template_values))
            
class SaveImage(blobstore_handlers.BlobstoreUploadHandler): 
    def post(self):
        self.redirect('/view_image')
        
                    
       
    
    
    
    

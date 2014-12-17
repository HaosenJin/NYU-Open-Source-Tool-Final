# something you need to know
URL: http://micro-dynamo-795.appspot.com/
Github: https://github.com/HaosenJin/NYU-Open-Source-Tool-Final.git

1. The system will handle multiple users. You need to use google account to login.

2. You need to login to create question, answer and vote.

3. You don't need to create tags separately. When new questions created, tags in the questions will be stored in the system automatically.
Tags must be separated by semi-colon in questions. 

4. Images can be uploaded in a separate page, image URLs are listed below the images.

5. jQuery is used for searching questions by tag and dynamically creating file upload controls.

6. jQuery validation plugin is used for non-empty inputs check. Name and content must be  non-empty. Upload file type must be image type.

 # something extra features
1. Pager is created not only for older questions but also newer ones.
 
2. Images could be added to a question when create or edit a question
 
3. Add email notification. When a new answer created, question author will receive email notification.

4. add some css 

# code guide
1. All the data model used in the system are listed in DataModel.py
 
2. QuestionHandler.py is responsible for question creation, edit, vote and view. Related pages include CreateQuestion.html and ViewQuestion.html.
 
3. AnswerHandler.py is responsible for answer creation, edit and vote. Related pages include CreateAnswer.html and ViewQuestion.html.

4. ImageHandler.py is responsible for image upload, view and delete. Related pages include CreateQuestion.html, ViewQuestion.html and ViewImage.html.
 
5. main.py lists all the quesitons and provides search by tags function. Related pages include index.html.

6. Utility.py is responsible for adding html tag in the content for http or https links.
 


 



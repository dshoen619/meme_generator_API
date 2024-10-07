# meme_generator_API
A RESTful API for a Meme Generator service using Django and PostgreSQL. This service allows users to create, retrieve, and rate memes.

<h3>Running The Project</h3>
Ensure you have docker, postgres, and the required packages installed. In the docker-compose.yaml, change the Database URL to your postgres user, password, and database you wish to use.

To start the server, initialize the database,populate the meme templates with two default templates, apply migrations, and create a super user run 
<br>
<br>
__docker-compose up__

<h3>API Endpoints</h3>

   - POST /signup/ - Signup a user
   - POST /login/ - login a user
   - POST /signout/ -Signout a user
   - GET /api/templates/ - List all meme templates 
   - GET /api/memes/ - List all memes (with pagination) 
   - POST /api/memes/ - Create a new meme 
   - GET /api/memes/<id>/ - Retrieve a specific meme 
   - POST /api/memes/<id>/rate/ - Rate a meme  
   - GET /api/memes/random/ - Get a random meme 
   - GET /api/memes/top/ - Get top 10 rated memes
   - POST /api/meme_template/create/ - Create a new Template 

  Some endpoints require certain keys to be present in the request body and/or request header. 

  **Examples**

  1) POST /signup/
  <br>
  header = None
  
  body = {
  
          username = davidshoen,
          password = davidshoen,
          email = david@shoen.com
          }

  response = {
  
    "id": 6,
    "username": "davidshoen"
   }

2) POST /login/
   <br>
   header = None
   
   body = {
   
           username = davidshoen,
           password = davidshoen
           }

  response = {
  
    "message": "Welcome davidshoen",
    "id": 6,
    "token": "819f2583435daf55d4a15e4fa6afe46fe913396d"
}

  Note: Authentication is performed by matching the id and the token in the requests header. If any request that requires authentication either does not have the appropriate headers or they are incorrect, it will not be executed.

3) GET /api/templates/
   <br>
     header = {

              Token = <Token>
              Id = <Id>
     }
   <br>
   body = None

   response =

   ```[
    {
        "name": "Template 1",
        "image_url": "https://example.com/template1.png",
        "default_top_text": "Default Top Text 1",
        "default_bottom_text": "Default Bottom Text 1"
    },
    {
        "name": "Template 2",
        "image_url": "https://example.com/template2.png",
        "default_top_text": "Default Top Text 2",
        "default_bottom_text": "Default Bottom Text 2"
    }]```

Note: These are the templates that are autopopulated when the server is first ran. You can also create new templates with POST /api/meme_template/create/

3) POST /api/memes/
   <br>
     header = {

              Token = <Token>
              Id = <Id>
     }

  body =

   {

    "template":"2",
    "image_url":"http://www.google.com"

}

  response = {
  
    "id": 5,
    "message": "Meme created successfully!"
}

3) GET /api/memes/
   <br>
     header ={

              Token = <Token>
              Id = <Id>
     }
     
     body = None

     response =

    ```{
    "count": 4,
    "next": "http://localhost:8000/api/memes/?page=2",
    "previous": null,
    "results": [
        {
            "template": 2,
            "top_text": "Default Top Text 2",
            "bottom_text": "Default Bottom Text 2"
        },
        {
            "template": 1,
            "top_text": "Default Top Text 1",
            "bottom_text": "Default Bottom Text 1"
        }
    ]}```


<h3>Unit Tests</h3>
The Unit tests test all of the API Endpoints mentioned above. They can be found at meme_generator/tests.py. To run the tests, in your terminal run
<strong>python manage.py test</strong>



     
     
  

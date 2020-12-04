# WEB APP

### Flask
`pip install flask` Flask simplifies the overhead required to program a web app from scratch. There are already made 
libraries which are engulfed or could be downloaded along side with the framework. Consist:
- **URL Directing:** all the routing of pages via URL's 
- **Jinja2:** A template Engine which is designer friendly as it works with .html files and simple to hook up backend
    data into the using objects. 
    
      {{ <Variable> }}
      {% <Code Block> %}
    
    **_PACKAGES INSTALLED_**
- **WTForms:** `pip install flask-wtf` Already made form which translates into HTML using Jinja2 and also renders CSS 
    tag's as for the design.
- **SQLAlchemy:** `pip install flask-sqlalchemy` It is an object relational mapper, accessing database in an object
    oriented manner.
- **Bcrypt:** `pip install flask-bcrypt` It is an hashing algorithm, for password protection. We only stores the hash of
    of the passwords written into the database.
- **email-validator:** `pip install email-validator` its a package which validates emails.
- **Login Manager:** `pip install flask-login` This creates the unique session for the user in the dashboard. Also,
    prevents program from loading multiple session in the app from the same service. Registers logging in and out.
- **Pillow:** `pip install pillow` Python Imaging Library that adds support for opening, manipulating, and saving many 
    different image file formats. We use it for the changes in the account picture size and cropping.
- **Mail:** `pip install flask-mail` This is a email handler which handles the flask reset password email.
    
### SQLite
It is an easy to use simple SQL database preinstalled with python. We are using a object relational mapper (SQLAlchemy)
to make accessing data easier using objects. 

> NOTE: To Deploy the Application install all the required packages mentioned above and call `python _init_.py` from the 
> command line.

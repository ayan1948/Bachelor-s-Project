from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from WebApp import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader  # Session creator using the login manager
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    tests = db.relationship('Test', backref='author', lazy=True)  # Setting up the relation with the DataPoints

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):  # A way of representing when the class is called as a variable
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    ch1 = db.Column(db.Boolean, default=False)
    ch2 = db.Column(db.Boolean, default=False)
    ch3 = db.Column(db.Boolean, default=False)
    ch4 = db.Column(db.Boolean, default=False)
    iteration = db.Column(db.Integer, nullable=False)
    moment = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # user_id

    def __repr__(self):
        return f"Test('{self.title}')"

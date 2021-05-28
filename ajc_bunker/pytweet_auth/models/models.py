from pytweet_auth.database import db
from flask_login import UserMixin

# EXERCISE: FlaskLoginのUserMixinを継承したUserモデルを追加しましょう ======================
# EXERCISE: Let's implement User Model which inherited FlaskLogin's UserMixin =============
'''
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    screen_name = db.Column(db.String(21), unique=True)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(80))
    auth_status = db.Column(db.Boolean, default=False)
    avatar_url = db.Column(db.String(500))
    bio = db.Column(db.String(240))
    def __init__(self, screen_name, email, password):
        self.screen_name = screen_name
        self.email = email
        self.password = password
        self.auth_status = auth_status
        self.avatar_url = avatar_url
        self.bio = bio

    def __repr__(self):
        return '<User %r>' % (self.screen_name)
#=====================================================================================
'''
class Login(db.Model):    
    __tablename__ = 'login'    
    id = db.Column(db.Integer, primary_key=True)    
    login_name = db.Column(db.String(50), nullable=False)    
    password = db.Column(db.String(50), nullable=False)    
    users = db.relationship("User", uselist=False, backref="login")    
    follow = db.relationship("Followers", uselist=False, backref="login")


class User(db.Model):    
    __tablename__ = 'users'    

    id = db.Column(db.Integer,primary_key=True)    
    name = db.Column(db.String(255), nullable=False)    
    address = db.Column(db.String(255), nullable=False)    
    number = db.Column(db.String(20), nullable=False)    
    login_id = db.Column(db.Integer, db.ForeignKey('login.id'), nullable=False)      
    profile = db.relationship('Profile',uselist=False, backref="users")    
    tweets = db.relationship('Tweet',backref= "users")    
    follow = db.relationship('Followers', backref ="users")

class Tweet(db.Model):    
    __tablename__ = 'tweets'    
    id = db.Column(db.Integer, primary_key=True)    
    word = db.Column(db.String(300), nullable=True)    
    photo = db.Column(db.String(900), nullable=True)     
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)        
    user = db.relationship('User', backref=db.backref("users", lazy =True)) #add    reply = db.relationship('Reply',backref="tweet")    # replyを１つだけ表示のため        #add    good_count = db.Column(db.Integer, default=0)    good = False    Good = db.relationship("Good",backref="tweets")

class Reply(db.Model):    
    __tablename__ = 'replys'    
    id = db.Column(db.Integer, primary_key=True)    
    comment = db.Column(db.String(300), nullable=False)    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweets.id'),nullable=False)    
    user = db.relationship('User',uselist=False, backref="replys")

class Profile(db.Model):    
    __tablename__ = 'profiles'    
    id = db.Column(db.Integer,primary_key=True)    
    avatar = db.Column(db.String(900), nullable=True)    
    bio = db.Column(db.String(500), nullable=True)    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    
    user = db.relationship('User', backref="profiles")

class Likes(db.Model):    
    __tablename__ = 'likes'    
    id=db.Column(db.Integer,primary_key=True)    
    color =db.Column(db.String(50),nullable=True)    
    tweet_id = db.Column(db.Integer,db.ForeignKey('tweets.id'), nullable=False)    
    tweet = db.relationship("Tweet",backref="good")    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Followers(db.Model):    
    __tablename__ = 'followers'    
    id= db.Column(db.Integer,primary_key=True)    
    source_user_id = db.Column(db.Integer,db.ForeignKey('login.id'),nullable=False)    
    target_user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)            
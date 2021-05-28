from flask import request, redirect, render_template, flash, url_for, session, Flask, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from pytweet_auth import app, db
from pytweet_auth.models import *
from urllib.request import Request, urlopen
import json, os
import base64

app.config["IMAGE_UPLOADS"] = 'pytweet_auth/static/images'

bootstrap = Bootstrap(app)


# EXERCISE: Initialize processing of LoginManager ===============
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# ================================================
def img_upload_to_imgur(img_data):
    # Define the header to send a request
    header = {'Authorization': 'Client-ID {}'.format(app.config['IMGUR_CLI_ID']),
              'Content-Type': 'application/json'}
    data = {'image': img_data}                          # Define the data to send
    encoded_data = json.dumps(data).encode('utf-8')     # Encode the data to send with urllib

    # Actually send the request
    req = Request(app.config["IMG_UPLOAD_URL"], encoded_data, headers=header)
    # Pick up the link of images by opening a response
    with urlopen(req) as res:
        body = json.loads(res.read().decode('utf8'))
    return body['data']['link']


def convert_file_to_data(file_obj):
    _raw_binary = file_obj.read()
    _encoded_bin = base64.b64encode(_raw_binary).decode('utf-8')
    return _encoded_bin


class LoginForm(FlaskForm):
    screen_name = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    screen_name = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


# EXERCISE:@login_manager.user_loaderで認証ユーザーの呼び出し方を定義しましょう =============
# EXERCISE:Let's define how to call authed user with @login_manager.user_loader =======
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# ================-


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
@login_required
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = Login.query.filter_by(login_name=request.form['login_name'],password=request.form['password']).first()

        if login:
            session['id']=login.id
            return redirect('dashboard')

        else:
            return 'Eroor in login in. Please try again'
    else:
        return render_template('login.html')         


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        check = Login.query.filter_by(login_name=request.form['login_name']).first()
        print("check",check)
        if check == None: 
            login = Login(login_name=request.form['login_name'],password=request.form['password'])

            try:
                db.session.add(login)
                db.session.commit()

                db.session.refresh(login)
                print(login.id)

                user = User(login_id=login.id, name=request.form['name'], address=request.form['address'],number=request.form['number'])
                db.session.add(user)
                db.session.commit()

                return redirect('/login')
            except:
                return 'Error'
        else:
            return 'Sorry, login name is already in use.<br> Please change your login name.<br> <a href=/signup "class="btn btn-outline-primary">Back</a>' 
    else:
        return render_template('signup.html')        
                    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/home')


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

@app.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.id

@app.route('/users/me')
@login_required
def show_me():
    return render_template('user/show.html', user=current_user)

@app.route('/users/me/edit', methods=['GET', 'POST'])
@login_required
def edit_me():
    if request.method == 'POST':
     current_user.screen_name = request.form['screen_name']
     current_user.email = request.form['email']
     current_user.bio = request.form['bio']
     if 'avatar' in request.files:
         avatar = request.files['avatar']
     db.sessions.commit()
     return redirect(url_for('show_me'))
    return render_template('user/edit.html', user=current_user) 

@app.route('/user/me/delete/', methods=['DELETE'])    
@login_required
def delete_user():
    db.session.delete(current_user)
    db.session.commit()
    flash('Your date was successfully deleted')
    return redirect('login')

@app.route('/dashboard', methods=['POST','GET'])
def dashboard():
    id = session['id']

    login = Login.query.filter_by(id=id).first()
    user = User.query.filter_by(login_id=id).first()

    my_tweet = Tweet.query.filter_by(user_id=id).order_by(Tweet.id.desc()).all() #dispay my tweet
    tweet = Tweet.query.order_by(Tweet.id.desc()).all() #dispaly all user's tweet
    # print("tweet : ",tweet)
    # print("my tweet :", my_tweet)
    # print(len(my_tweet))
    reply = Reply.query.order_by(Reply.id).all()
    profile = Profile.query.filter_by(user_id=id).first() #login user's profile

    gooded_id_list = Likes.query.filter_by(user_id = id).all() #ログインユーザーのgood.id list
    gooded_list= []
    for gooded in gooded_id_list:
        gooded_list.append(gooded.tweet_id)
    # print('gooded_list',gooded_list)
    # print('gooded_id_list :',gooded_id_list)

    #for follow
    followed_id_list = Followers.query.filter_by(source_user_id = id).all() #lodin user's follow list
    followed_list = [id] #my id + target_user_id
    for followed in followed_id_list:
        followed_list.append(followed.target_user_id)
    print("followed_list :" ,followed_list)
    
    # tweet =====================================
    if request.method == 'POST':
        
        if 'photo' not in request.files:
            tweet = Tweet(word=request.form['word'], user_id=id, photo=None)
            
            db.session.add(tweet)
            db.session.commit()
            return redirect('/dashboard')
        else:
            images = request.files['photo']
            pic_name = images.filename
            print(pic_name)
            
            images.save(os.path.join(app.config["IMAGE_UPLOADS"],images.filename))
            tweet = Tweet(word=request.form['word'], user_id=id, photo=pic_name)

            db.session.add(tweet)
            db.session.commit()

            return redirect('/dashboard')
    else:
        return render_template('dashboard.html',login=login, user=user, tweets=tweet,replys=reply,profile=profile, 
        gooded_id_list=gooded_id_list,gooded_list=gooded_list,
        followed_list=followed_list, my_tweet=my_tweet)


@app.route('/edit_tweet/<int:tweet_id>', methods=['POST','GET'])
def edit_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)

    id = session['id']
    login = Login.query.filter_by(id=id).first()
    user = User.query.filter_by(login_id=id).first()
    profile = Profile.query.filter_by(user_id=id).first()

    if request.method == 'POST':
        
        if not 'photo' in request.files:
            tweet.word = request.form['word']
        else:
            images = request.files['photo']
            pic_name=images.filename
            images.save(os.path.join(app.config["IMAGE_UPLOADS"],images.filename))

            tweet.word=request.form['word']
            tweet.photo=pic_name
        
        try:
            db.session.commit()
            return redirect('dashboard')

        except:
            return 'edit error'
    else:
        return render_template('edit_tweet.html',tweet=tweet,login=login,user=user,profile=profile)

@app.route('/tweets/<int:id>/reply',methods=['POST'])
def new_reply(id):
    user_id = session['id']
    user = User.query.filter_by(login_id=user_id).first()
    tweet = Tweet.query.filter_by(id=id)

    reply = Reply(comment=request.form['comment'],
    user_id=user_id, 
    tweet_id=id)

    try:
        db.session.add(reply)
        db.session.commit()
        return redirect('/dashboard')
    except Exception as e:
        print(e)
        return 'Reply Error'

@app.route('/tweets/<int:id>/reply_by_profile', methods=['POST'])
def reply_by_profile(id):
    login_id = session['id']
    tweet = Tweet.query.filter_by(id=id).first()
    print("tweet : ", tweet)
    target = tweet.user_id

    reply = Reply(comment=request.form['comment'],
    user_id=login_id,
    tweet_id=id)

    try:
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('user_profile',id=target))
    except Exception as e:
        print(e)
        return 'Reply Error'    

@app.route('/update',methods=['POST','GET'])
def update_user():    
    id = session['id']    
    user = User.query.filter_by(login_id=id).first()    
    login = Login.query.filter_by(id=id).first()   

    if request.method == 'POST':              
        user.name = request.form['name']       
        user.address = request.form['address']        
        user.number = request.form['number']        
        try:            
            db.session.commit()              
            return redirect('update')        
        except:            
            return 'Error in updating'    
    else:        
        return render_template('update.html', user=user,login=login)        


#my profile
@app.route('/profile',methods=['POST','GET']) #login.id 
def profile(): #login.id =user.id
    id = session['id']
    user = User.query.get_or_404(id)

    profile = Profile.query.filter_by(user_id=id).first()

    if request.method == 'POST':
        
        if not profile :
            if 'avatar' not in request.files:
                profile = Profile(bio = request.form['bio'],avatar=None,user_id=id)
            else:
                images = request.files['avatar']
                pic_name = images.filename
                print(pic_name)

                images.save(os.path.join(app.config["IMAGE_UPLOADS"], images.filename))

                profile = Profile(bio=request.form['bio'], avatar=pic_name, user_id=id)

        else:
            if 'avatar' not in request.files:
                profile.bio = request.form['bio']
            else:
                images = request.files['avatar']
                pic_name = images.filename
                print(pic_name)

                images.save(os.path.join(app.config["IMAGE_UPLOADS"], images.filename))
                profile.bio = request.form['bio']
                profile.avatar = pic_name
        try:
            db.session.add(profile)
            db.session.commit()
            
            return redirect('/profile')
        except:
            return 'Error in profile update'
    else:
        return render_template('profile.html', profile=profile, user=user)

@app.route('/delete_tweet/<int:id>')
def delete_tweet(id):     #tweet.id   
   
    tweet_to_delete = Tweet.query.get_or_404(id)
    print('tweet_to_delete: ',tweet_to_delete)

    reply= Reply.query.filter_by(tweet_id=id).all() #delete reply at the same time
    print('reply :', reply)

    good = Likes.query.filter_by(tweet_id=id).all()

    if len(reply) > 0:   
        for r in reply:
            print('r : ',r)
            db.session.delete(r)
            db.session.commit()
            print('sussess to delete reply of this tweet')
    if len(good) > 0:
        for g in good:
            print('g : ', g)
            db.session.delete(g)
            db.session.commit()
            print('success to delete good of this tweet')
    try:
        db.session.delete(tweet_to_delete)
        db.session.commit()
        print('success to delete of this tweet')
        
        return redirect('/dashboard')

    except Exception as e:
        print(e)
        return 'delete Error '


@app.route('/tweet/<int:tweet_id>/good', methods=['GET','POST'])
def tweet_good(tweet_id):
    login_id = session['id']

    # print('tweet_id from GET  : ', tweet_id)

    # tweet = Tweet.query.filter_by(id=tweet_id).first() #カウント作りたい
    # print("tweet_id :", tweet)

    already_good = Likes.query.filter_by(tweet_id=tweet_id,user_id =login_id).first()
    # print('already_good :',already_good)

    if already_good == None:
      
        good = Likes(tweet_id=tweet_id, user_id=login_id ,color='active')

        db.session.add(good)
        db.session.commit()
        print('success to good')

        return redirect('/dashboard')
    else:

        db.session.delete(already_good)   
        db.session.commit()
        print('delete to good')
        
        return redirect('/dashboard')

#other user's pfofile 
@app.route('/user_profile/<int:id>') #user_id
def user_profile(id):
    login_id = session['id']
    user_profile = Profile.query.filter_by(user_id=id).first()
    user = User.query.filter_by(id=id).first()

    followed_id_list = Followers.query.filter_by(source_user_id=login_id).all() #lodin user's follow list
    followed_list = [] #ログインユーザーのフォロー済みのユーザーID
    for followed in followed_id_list:
        followed_list.append(followed.target_user_id)

    # print("フォロー済みuser_id :" ,followed_list)
    
    #display tweet
    gooded_id_list = Likes.query.filter_by(user_id=login_id).all() #ログインユーザーのgood.id list
    gooded_list= []
    for gooded in gooded_id_list:
        gooded_list.append(gooded.tweet_id)
    # print('gooded_list',gooded_list)
    # print('gooded_id_list :',gooded_id_list)

    tweets = Tweet.query.filter_by(user_id=id).order_by(Tweet.id.desc()).all()
    # print("tweets",tweets)
    replys = Reply.query.order_by(Reply.id).all()

    return render_template('user_profile.html', user_profile=user_profile,user=user,followed_list=followed_list,tweets=tweets,replys=replys,gooded_list=gooded_list)


@app.route('/user_profile/<int:target_id>/follow',methods=['GET','POST'])
def follow(target_id):
    login_id= session['id']
  
    already_followed = Followers.query.filter_by(source_user_id=login_id,target_user_id=target_id).first()
    print('already_followed :', already_followed)

    if already_followed == None:
        follow = Follow(source_user_id=login_id, target_user_id=target_id)
        db.session.add(follow)
        db.session.commit()
        print("success to follow")

        return redirect(url_for('user_profile',id=target_id))
    else:
        db.session.delete(already_followed)
        db.session.commit()
        print("success to stop following")

        return redirect(url_for('user_profile',id=target_id))
        
    return render_template('user_profile.html', followed_id_list=followed_id_list,followed_list=followed_list,follow=follow)

@app.route('/search', methods=['GET','POST'])
def search():
    keyword = request.form['keyword']
    login_id=session['id']

    users = User.query.order_by(User.id).all()
    # print("users",users)

    if request.method== 'POST':
        
        results = []
        for user in users:
            if keyword in user.name:
                # print("user.name : ",user.name)
                results.append(user)
        # print("results : ",results)

        return render_template('search.html',results=results,users=users)
    
    return render_template('search.html', users=users)



@app.route('/delete_reply/<int:id>')
def delete_reply(id):     #reply.id   
   
    tweet_to_reply = Reply.query.get_or_404(id)
    # print('tweet_to_reply: ',tweet_to_reply)

    try:
        db.session.delete(tweet_to_reply)
        db.session.commit()
        print('success to delete of this reply')
        
        return redirect('/dashboard')

    except Exception as e:
        print(e)
        return 'delete Error '


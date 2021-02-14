from flask import Flask, render_template, request, session, redirect, url_for
import requests
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
from functools import wraps



import templates

app = Flask(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = dict(session).get('profile', None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if user:
            return f(*args, **kwargs)
        return 'You aint logged in, no page for u!'
    return decorated_function


GOOGLE_CLIENT_ID = "726953725717-2u6oit75qfmvpphaachdst1ltl36ffh0.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "1YFNVLLMFql7IN_CWDjEeiwj"
app.secret_key= "yourmomwhateverthisway"
app.config['SESSION_COOKIE_NAME'] = GOOGLE_CLIENT_SECRET
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)


##setup OAuth
oauth=OAuth(app)
google = oauth.register(
    name = 'google',
    client_id = GOOGLE_CLIENT_ID,
    client_secret = GOOGLE_CLIENT_SECRET,
    access_token_url= 'https://accounts.google.com/o/oauth2/token',
    access_token_params =None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url ='https://accounts.google.com/o/oauth2/auth',
    userinfo_endpoint= 'https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)




@app.route('/')
@login_required
def get_index():
    return render_template('index.html')


@app.route('/pricing', methods=['GET'])
def pricing():
    return render_template('pricing.html')


@app.route("/download")
def download():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/authorized")
def authorized():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    #user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    #session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


if __name__ == '__main__':
    app.run()

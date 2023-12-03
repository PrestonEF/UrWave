"""
Routes and views for the flask application.
"""

import random
import string
import re
import smtplib
import secrets
from datetime import datetime
from flask import render_template, request, Flask, redirect, url_for, session
from UrWave_Project import app
from email.mime.text import MIMEText

app.secret_key = secrets.token_hex(16)

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='UrWave',
        year=datetime.now().year,
    )

@app.route('/login')
def login():
    """Renders the login page."""
    return render_template(
        'login.html',
        year=datetime.now().year,
        username='[username]'
    )

def get_playlist_for_user_input(mood, activity, weather, color, music_preference):
    # Define mapping rules for each combination of responses
    playlist_mapping = {
        ('happy', 'workout', 'sunny', 'yellow', 'pop'): [
            "Happy by Pharrell Williams",
            "Don\'t Stop Believin\' by Journey",
            "Can\'t Stop the Feeling! by Justin Timberlake",
            "Uptown Funk by Mark Ronson ft. Bruno Mars",
            "Walking on Sunshine by Katrina and the Waves",
            "I Gotta Feeling by The Black Eyed Peas",
            "Happy Together by The Turtles",
            "Dancing Queen by ABBA",
            "Good Vibrations by The Beach Boys",
            "Here Comes The Sun by The Beatles"
        ],
        ('sad', 'study', 'rainy', 'blue', 'acoustic'): [
            "Someone Like You by Adele",
            "Skinny Love by Bon Iver",
            "Hurt by Johnny Cash",
            "Back to Black by Amy Winehouse",
            "The Night We Met by Lord Huron",
            "All I Want by Kodaline",
            "Nothing Compares 2 U by Sinead O'Connor",
            "Someone You Loved by Lewis Capaldi",
            "Creep by Radiohead",
            "Tears in Heaven by Eric Clapton"
        ],
        ('relaxed', 'relaxing', 'cloudy', 'purple', 'relaxing'): [
            "Weightless by Marconi Union",
            "Clair de Lune by Claude Debussy",
            "Spa Music by Various Artists",
            "Ambient 1: Music for Airports by Brian Eno",
            "Nocturn in E-flat Major by Frederic Chopin",
            "Deep Forest by Deep Forest",
            "Misty by Erroll Garner",
            "Rainforest Sounds by Nature Sounds",
            "Gymnopedie No.1 by Erik Satie",
            "Adagio for Strings by Samuel Barber"
        ],
        # Add more playlists and songs as needed
    }

    # Convert user input to lowercase for consistency
    user_input = (mood.lower(), activity.lower(), weather.lower(), color.lower(), music_preference.lower())

    # Check if the combination of user responses is in the mapping
    if user_input in playlist_mapping:
        return playlist_mapping[user_input]
    else:
        # If no specific mapping is found, return an empty list
        return []

@app.route('/music', methods=['GET', 'POST'])
def music():
    if request.method == 'GET':
        return render_template(
            'music.html',
            title='Music',
            year=datetime.now().year,
        )
    elif request.method == 'POST':
        mood = request.form['mood'].lower()
        activity = request.form['activity'].lower()
        weather = request.form['weather'].lower()
        color = request.form['color'].lower()
        music_preference = request.form['music_preference'].lower()

        recommended_playlist = get_playlist_for_user_input(mood, activity, weather, color, music_preference)
        
        return render_template('results.html', mood=mood, activity=activity, weather=weather, color=color, music_preference=music_preference, recommended_playlist=recommended_playlist)
    

# Database to store user information
user_credentials = {
    'deexfloyd': '123456',
    'Prezto2K': 'qwerty',
}

# Email verification codes
verification_codes = {}

def generate_verification_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def register(username, password, email):
    if username not in user_credentials:
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            verification_code = generate_verification_code()
            verification_codes[username] = verification_code

            print(f"Verification email sent to {email}. Check your email for the code.")
            send_verification_email(email, verification_code)

            # Redirect to the '/verification' route
            return redirect(url_for('verification'))
        else:
            print("Invalid email format. Please enter a valid email.")
            return False
    else:
        print("Username already exists. Please choose another username.")
        return False
    
def send_verification_email(email, verification_code):
    sender_email = 'urwaveemail@gmail.com'  
    password = 'aejs ylqf mrpy ppcn'  
    #MusicM4kesM4N!
    subject = 'UrWave Verification Code'
    body = f'Your verification code is: {verification_code}'

    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, email, message.as_string())
        print("Verification email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"SMTP Exception: {str(e)}")
    except Exception as ex:
        print(f"Error sending email: {str(ex)}")

def user_login(username, password):  # Changed function name from 'login' to 'user_login'
    if username in user_credentials and user_credentials[username] == password:
        return True
    else:
        return False

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')

    # Ensure the required fields are present in the form data
    if 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Call the register function from the provided logic
        register_successful = register(username, password, email)

        if register_successful:
            return redirect(url_for('verification'))  # Redirect to the login page after successful registration
        else:
            # Handle registration failure
            return render_template('register.html', error="Registration failed. Please try again.")
    else:
        # Handle missing form fields
        return render_template('register.html', error="Please fill in all the required fields.")
    
@app.route('/login', methods=['GET', 'POST'])
def login_handler():
    if request.method == 'POST':
        # Perform user authentication here (check username and password)
        username = request.form['username']
        password = request.form['password']

        if username in user_credentials and user_credentials[username] == True:
            session['current_user'] = username  # Set the current user in the session
            return redirect(url_for('profile', username=username))
        else:
            error = "Invalid credentials. Please try again."
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('current_user', None)  # Remove the current user from the session
    return redirect(url_for('home'))

@app.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == 'GET':
        return render_template('verification.html')
    elif request.method == 'POST':
        entered_code = request.form.get('verification_code')
        username = request.form.get('username')

        print(f"Entered Code: {entered_code}")
        print(f"Username: {username}")
        print(f"Verification Codes: {verification_codes}")

        if username in verification_codes:
            stored_verification_code = verification_codes[username]

            print(f"Stored Verification Code: {stored_verification_code}")

            if entered_code == stored_verification_code:
                user_credentials[username] = True  # Update user credentials after verification
                verification_codes.pop(username)
                return redirect(url_for('login_handler'))  # Redirect to login after successful verification

        error = "Invalid verification code or username. Please try again."
        return render_template('verification.html', error=error)

        
@app.route('/profile/<username>')
def profile(username):

    user_info = {
        'username': username,
    }

    return render_template('profile.html', user=user_info)

if __name__ == '__main__':
    app.run(debug=True)

"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')

@app.route('/users')
def show_users():
    """Display list of users."""

    users = User.query.all()

    return render_template('user_list.html',
                            users=users)

@app.route('/login')
def login():

    return render_template('login_form.html')


@app.route('/process-login', methods=['POST'])
def process_login():
    """Logs in existing users; adds new users to database along with password."""

    # pull data from form
    email = request.form.get("email")
    password = request.form.get("password")

    # select the user from the database who has the given email (if any)
    user = User.query.filter(User.email == email).first()

    if user == None:
        # instantiate a user object with the information provided
        user = User(email=email, password=password)
        
        # add user to session and commit to database
        db.session.add(user)
        db.session.commit()

        # set a cookie identifying the user; return to homepage
        session['user_id'] = user.user_id
        flash('You are now logged in.')
        return redirect('/')
    else:
        # check to see if password is correct
        if password == user.password:
            # set a cookie identifying the user; return to homepage
            session['user_id'] = user.user_id
            flash('You are now logged in.')
            return redirect('/')
        else:  # if password does not match database
            # flash message, stay on page
            flash('Your password was incorrect. Please enter your information again.')
            return redirect('/login')

    # TODO: handle logging out
        # have a logout button on the base template?

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()

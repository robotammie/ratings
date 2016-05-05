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


@app.route('/movies')
def show_movies():
    """Display list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    # movie.released_at.strftime(%Y)

    return render_template('movie_list.html',
                            movies=movies)


@app.route('/users/<cheesecake>')
def display_user(cheesecake):
    """Display user information for any given user."""

    user = User.query.get(cheesecake)
    movies = user.ratings

    # create a list of tuples: (movie id, title, score) for all movies rated by user
    rating_info = [(m.movie_id, m.movie.title, m.score) for m in movies]

    return render_template('/user_page.html',
                           user=user,
                           rating_info=rating_info)


@app.route('/movies/<cheesecake>')
def display_movie(cheesecake):
    """Display movie information for any given movie."""

    movie = Movie.query.get(cheesecake)

    num_ratings = len(movie.ratings)

    total_score = 0.0

    for rating in movie.ratings:
        total_score += rating.score

    average = total_score / num_ratings

    user_rating = Rating.query.filter(Rating.user_id == session['user_id'],
                                      Rating.movie_id == cheesecake).first()

    # average rating on top, your rating below

    # TODO: if user is logged in, let them rate the movie (either rate new
    # or update previously given rating)
    # radio buttons?

    return render_template('/movie_page.html',
                           movie=movie,
                           average=average,
                           user_rating=user_rating)


@app.route('/rateit', methods=['POST'])
def rate_movie():
    """Logs user's rating in the database."""

    # get data from form
    score = request.form.get("score")
    movie = request.form.get("movie_id")

    # check to see if the user has already rated the movie, get request object
    user_rating = Rating.query.filter(Rating.user_id == session['user_id'],
                                      Rating.movie_id == movie).first()

    if user_rating == None: # user has not rated movie before
        # create new record for database
        rating = Rating(movie_id=movie, user_id=session['user_id'], score=score)
        
        db.session.add(rating)
        db.session.commit()

    else: # user has rated movie before
        user_rating.score = score  # update score in database

        db.session.commit()

    return redirect('/movies/{}'.format(movie))


@app.route('/login', methods=['POST', 'GET'])
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


@app.route('/logout', methods=['POST'])
def process_logout():
    """Log user out of ratings website."""

    # remove user id from session
    del session ['user_id']
    flash('You are now logged out.')

    return redirect('/')




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()

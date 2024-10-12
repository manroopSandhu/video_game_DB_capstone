from flask import Flask, request, render_template, redirect, session, flash, jsonify
from models import db, connect_db, User, Favorite
from forms import SignUpForm, LoginForm
from secret import API_SECRET_KEY
import requests
import os
# DATE MANIPULATION MODULES TO USE FOR API REQUEST PARAMS
from datetime import date
from dateutil.relativedelta import relativedelta
# pip install python-dateutil

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    'DATABASE_URL', "postgresql:///video_games_DB")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'hellosecret1')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)


@app.route('/')
def homepage():
    """Redirect to games page"""

    return redirect('/games')


# /* **************************MAIN ROUTES FOR DISPLAYING GAMES BY DIFFERENT CATEGORIES(Goes until line 312)************************* */
@app.route('/games')
def games_page():
    """Homepage for presenting a list of games"""
    # iterates over all the keys in the session, and for each key that is not 'username' removes that key from the session. this effectiviely clears the session while presererving the 'username'
    # useful for clearing out old or unnesessary session data while keeping the user's logged-in status
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    # using the dateutil package installed with pip take today's date along with 3 months prior to show all the most recent games
    # "(relativedelta(months=-3))" means subtract 9 months from the current date
    current_date = date.today()
    five_months = current_date + relativedelta(months=-5)
    # prepares the API to make a request to "RAWG" to retrieve all the games added in the last 9 months
    # NOTE: the date is subject to change (i changed it 5 times already and it's only 2 days )
    BASE_URL = f"https://rawg.io/api/games?dates={five_months},{current_date}&ordering=-added&page_size=40"
    
    # send a GET request to the RAWG API to get the data about the games which is then stored in the variable "response"
    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

    # Holds parsed JSON data, allowing us to easily access specific parts of the reponse
    data = resp.json()
    # in many API's the 'results' key will hold the main data. Now data_results will hold that information
    # NOTE: chatGPT told me i could just name the variable "results" instead of data_results: which i should have done in the beggining
    # the rest of my comments will have "data_results" as the variable name
    results = data["results"]
    # contains a URL or identifier for the next page of results. Otherwise it will be "none" if you are on the last page
    next_page = data["next"]
    # usually contains a URL or identifier for the previous page
    previous_page = data["previous"]
    # these lines of code is designed to handle paginated API responses, making it easy to navigate through multiple pages of results

    session['next_page'] = next_page
    session['previous_page'] = previous_page
  
    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page)


@app.route('/games/upcoming')
# most comments are re-written to make sure i have an understanding/grasp at my work.
def games_upcoming_page():
    """Homepage for presenting a list of most anticipated games"""
    # iterates over all the keys in the session, and for each key that is not 'username' removes that key from the session. this effectiviely clears the session while presererving the 'username'
    # useful for clearing out old or unnesessary session data while keeping the user's logged-in status
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    # call and store today's date using the datetime package installed by pip
    current_date = date.today()
    # using the dateutil package installed with pip take today's date along with 9 months ahead to show all the most upcoming games
    # "(relativedelta(months=+3))" means add 3 from the current date     
    # NOTE: i went back and changed the previous "five_months_prior" to "nine_months_prior" after finishing these next few lines of code. Some of my comments will be outdated.
    six_months = current_date + relativedelta(months=+6)
    # prepares the API to make a request to "RAWG" to retrieve all the games added in the last 3 months
    BASE_URL = f"https://rawg.io/api/games?dates={current_date},{six_months}&ordering=-added&page_size=40"
    
    # send a GET request to the RAWG API to get the data about the games which is then stored in the variable "response" 
    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

    # Holds parsed JSON data, allowing us to easily access specific parts of the reponse
    data = resp.json()
    # in many API's the 'results' key will hold the main data. Now data_results will hold that information
    results = data["results"]
    # contains a URL or identifier for the next page of results. Otherwise it will be "none" if you are on the last page
    next_page = data["next"]
    # usually contains a URL or identifier for the previous page
    previous_page = data["previous"]
    # these lines of code is designed to handle paginated API responses, making it easy to navigate through multiple pages of results\

    # By storing it in the session the application can remember this value across multiple requests making it easier to fetch
    session['next_page'] = next_page
    session['previous_page'] = previous_page
    session['six_months'] = six_months
  
    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page, six_months=six_months)


@app.route('/games/new')
def games_new_page():
    """Homepage for presenting a list of newly released games"""
    # iterates over all the keys in the session, and for each key that is not 'username' removes that key from the session. this effectiviely clears the session while presererving the 'username'
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    # call and store today's date using the datetime package installed by pip
    current_date = date.today()
    # prepares the API to make a request to "RAWG" to retrieve the newest games added from the past 3 weeks
    # NOTE: i believe this way my newest page will not be too similar to the regular home page if i were to do 1-3 months of the newest games (alot of new indie games every week it will be information overload)
    # decided to go with games one month old because some of my friends said theyd rather wait a month let the dust settle and see what people say about the game then
    one_month = current_date + relativedelta(months=-1)
    BASE_URL = f"https://rawg.io/api/games?dates={one_month},{current_date}&ordering=-added&page_size=40"
    
    # send a GET request to the RAWG API to get the data about the games which is then stored in the variable "response"
    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

    # Holds parsed JSON data, allowing us to easily access specific parts of the reponse
    data = resp.json()
    # in many API's the 'results' key will hold the main data. Now data_results will hold that information
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page
    session['one_month'] = one_month
  
    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page, one_month=one_month)    


@app.route('/games/next_page')
def next_page():
    """Next page pagination for standard games"""
    # retrieves URL for next page of game data from the session
    next_page = session.get('next_page')
    one_month = session.get('one_month')
    six_months = session.get('six_months')
    # sends a request to the API that fetches the next page
    resp = requests.get(next_page, params = {"key": API_SECRET_KEY})
    # removes the next_page entry from the session
    session.pop('next_page')
    
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page, one_month=one_month, six_months=six_months)


@app.route('/games/previous_page')
def previous_page():
    """Previous page pagination for standard games"""
    previous_page = session.get('previous_page')
    one_month = session.get('one_month')
    six_months = session.get('six_months')
    resp = requests.get(previous_page, params = {"key": API_SECRET_KEY})
    session.pop('previous_page')
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('games.html', results=results, next_page=next_page, previous_page=previous_page, one_month=one_month, six_months=six_months)


@app.route('/games/<int:id>')
def game_info(id):
    """Game info page"""
    # request data about the game that was selected
    resp = requests.get(f"https://api.rawg.io/api/games/{id}", params = {"key": API_SECRET_KEY})
    # Saves relative data from api
    data = resp.json()

    return render_template('gameinfo.html', data=data)


@app.route('/category/next_page')
def next_category_page():
    """Next page pagination for categorized games"""
# Route for allowing all category pages to click to the next relative page. Gets api value(url) for next page from session and passes it in as a request url for pagination 
    next_page = session.get('next_page')
    slug = session.get('slug')
    resp = requests.get(next_page, params = {"key": API_SECRET_KEY})
    session.pop('next_page')
    # saves relatice data from api
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('category.html', results=results, next_page=next_page, previous_page=previous_page, slug=slug.upper())


@app.route('/category/previous_page')
def previous_category_page():
    """Previous page pagination for categorized games"""
    # Route for allowing all category pages to click to the previous relative page. Gets api value(url) for previous page from session and passes it in as a request url for pagination 
    previous_page = session.get('previous_page')
    slug = session.get('slug')
    resp = requests.get(previous_page, params = {"key": API_SECRET_KEY})
    session.pop('previous_page')
    # saves relatice data from api
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('category.html', results=results, next_page=next_page, previous_page=previous_page, slug=slug.upper())    


@app.route('/genres')
def genres_page():
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    """Page for presenting a list of genres"""
    resp = requests.get("https://rawg.io/api/genres?page_size=40", params = {"key": API_SECRET_KEY})
    data = resp.json()
    results = data["results"]


    return render_template('genres.html', results=results)


@app.route('/genres/<slug>')
def genre_games_page(slug):
    """Page for presenting a list of games by a specific genre"""
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    session['slug'] = slug
    BASE_URL = f"https://rawg.io/api/games?genres={slug}&ordering=-added&page_size=40"
    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})
    
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page
  
    return render_template('category.html', results=results, next_page=next_page, previous_page=previous_page, slug=slug.upper())


@app.route('/platforms')
def platforms_page():
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    """Page for presenting a list of platforms"""
    resp = requests.get("https://rawg.io/api/platforms?page_size=40", params = {"key": API_SECRET_KEY})
    data = resp.json()
    results = data["results"]
    
    return render_template('platforms.html', results=results)


@app.route('/platforms/<slug>')
def platform_games_page(slug):
    """Page for presenting a list of games by a specific platform"""
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    plat_dict = eval(slug)
    id = plat_dict['id']
    session['id'] = id
    slug = plat_dict['name']
    session['slug'] = slug
    BASE_URL = f"https://rawg.io/api/games?platforms={id}&page_size=40"

    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page
  
    return render_template('category.html', results=results, next_page=next_page, previous_page=previous_page, slug=slug.upper())


@app.route('/search')
def search():
    """Handles search bar input for api search request"""
    [session.pop(key) for key in list(session.keys()) if key != "username"]
    search = request.args.get('search')
    BASE_URL = f"https://rawg.io/api/games?search={search}&page_size=40"

    resp = requests.get(BASE_URL, params = {"key": API_SECRET_KEY})

    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('search.html', results=results, next_page=next_page, previous_page=previous_page)


@app.route('/search/next_page')
def search_next_page():
    """Next page pagination for standard games"""
    next_page = session.get('next_page')
    resp = requests.get(next_page, params = {"key": API_SECRET_KEY})
    session.pop('next_page')
    
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('search.html', results=results, next_page=next_page, previous_page=previous_page)


@app.route('/search/previous_page')
def search_previous_page():
    """Previous page pagination for standard games"""
    previous_page = session.get('previous_page')
    resp = requests.get(previous_page, params = {"key": API_SECRET_KEY})
    session.pop('previous_page')
    data = resp.json()
    results = data["results"]
    next_page = data["next"]
    previous_page = data["previous"]

    session['next_page'] = next_page
    session['previous_page'] = previous_page

    return render_template('search.html', results=results, next_page=next_page, previous_page=previous_page)



# /* **************************USER ROUTES************************* */

@app.route('/register', methods=['GET','POST'])
def register():
    """Route for registering user"""

    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        image_url = form.image_url.data or None

        user = User.register(username, password, image_url)

        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect('/')
        
    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login_route():

    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect('/')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('username')

    return redirect('/')


@app.route('/users/<username>')
def user_page(username):
    if "username" in session and username == session['username']:
        user = User.query.get(username)
        favorite = user.favorites

        return render_template('user.html', user=user, favorite=favorite)


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Handle form submission for deleting an existing user"""

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect("/")


@app.route('/games/<int:id>/<username>/favorite', methods=["POST"])
def add_fav(id, username):
    """Favorites a game"""
    user = User.query.get_or_404(username)
    game_id = request.form.get('game_id')
    name = request.form.get('name')
    background_image = request.form.get('background_image')

    favorite = Favorite(username=session['username'], game_id=game_id, name=name, background_image=background_image)
    db.session.add(favorite)
    db.session.commit()

    return redirect(f'/users/{user.username}')


@app.route('/games/<int:id>/<username>/delete', methods=["POST"])
def delete_fav(id, username):
    """Deletes a favorite"""
    favorite = Favorite.query.get(id)
    user = User.query.get_or_404(username)
    
    db.session.delete(favorite)
    db.session.commit()

    return redirect(f'/users/{user.username}')

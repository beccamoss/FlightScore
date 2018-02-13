"""FlightScore"""

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from model import Flight, Carrier, connect_to_db, db
from functions import get_flight_results, update_results_for_display

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/search')
def search_flights():
   
    # Get input from form
    try:
        # get the origin and destination airports, split them into airport code and description
        origin, origin_description = request.args.get("origin").split(', ')
        destination, destination_description = request.args.get("destination").split(', ')
    except:
        flash("Please enter a valid airport")
        return render_template("home.html")  

    # make sure a valid date was entered
    date = request.args.get("date")
    if date == '':
        flash("Please enter a valid date")
        return render_template("home.html")

    # use the user's input to search the Google Flight API for results
    # in addition, also query the database to get the correcsponding FlightScore
    results = get_flight_results(origin, destination, date)

    # extract just the time of the flight arrival and departure
    results = update_results_for_display(results)


    return render_template("results.html",
                        results=results,
                        origin=origin_description,
                        destination=destination_description)
   

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
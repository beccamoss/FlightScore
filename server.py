"""FlightScore"""

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)

from model import Flight, Carrier, connect_to_db, db
from functions import get_flight_results, get_info_from_flight, update_results_for_display

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
    """ This route makes sure the input from the search form is valid, and if so,
    uses the Google Flights API to get flight results back for the search and renders
    them in results.html """

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
    results = get_flight_results(origin, destination, date)

    return render_template("results.html",
                           results=results,
                           origin=origin_description,
                           destination=destination_description)

@app.route('/getstats')
def get_stats():
    """ This route completes an AJAX request to get the stats associated with the FlightScore 
    information on the flight is stored as data on the button, so this data is
    passed in and used for our database lookup in get_info_from_flight() """

    # Get flight information from parameters
    flight_id = request.args.get("flightId")
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    depart = request.args.get("depart")

    # Get the FlightScore stats from our database
    flight_info = get_info_from_flight(flight_id[:2], origin, destination, depart)

    # Build our dictionary of values to pass back to the client.  Then jsonify it!
    flight = {"flightId": flight_id, "pctDelay": flight_info["percent_delay"], "avgDelay": flight_info["avg_delay"], "pctCancel": flight_info["percent_cancel_divert"]}

    return jsonify(flight)


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
"""FlightScore"""

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)

from model import Flight, Carrier, Score, connect_to_db, db
from functions import (get_flight_results, get_info_from_flight, date_valid, build_stats)
from datavis import (get_data_for_vis, get_pct_delay, VOL, AVG_DELAY, NUM_DELAY, SCORE, PCT_DELAY)
from datavis import cur_airports
import sys

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

    
# Set a variable to determine whether to call the QPX Express API or not
# because the service will be discontinued 4/20.  This can be overridden as an 
# argument 'qpx' to server.py 
call_qpx = False

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
    uses the QPX Express API to get flight results back for the search and renders
    them in results.html.  Or if we aren't using the API, we get the results from
    the database for the origin, destination and date"""
    
    # Get input from form
    try:
        # get the origin and destination airports, split them into airport code and description
        origin, origin_description = request.args.get("origin").split(', ')
        destination, destination_description = request.args.get("destination").split(', ')
    except:
        # Todo - should also check if user entered same airport for origin/dest
        flash("Please enter a valid airport")
        return render_template("home.html")  

    # make sure a valid date was entered
    date = request.args.get("date")
    if not date_valid(date):
        flash("Please enter a valid date")
        return render_template("home.html")

    # use the user's input to call the QPX Express API for results or get back results
    # from the database if we aren't calling the API
    try:
        results = get_flight_results(origin, destination, date, call_qpx)
    except:
        flash("No results returned from API")
        return render_template("home.html")

    # Render the right template based on whether or not we called the API
    if call_qpx:
        return render_template("results.html", 
                               date=date,
                               results=results,
                               origin=origin_description,
                               destination=destination_description)
    else:
        return render_template("resultsdb.html", 
                               date=date,
                               results=results,
                               origin=origin_description,
                               destination=destination_description)

@app.route('/getstats')
def get_stats():
    """ This route completes an AJAX request to get the stats associated with the FlightScore 
    Information on the flight is stored as data on the button, so this data is
    passed in and used for our database lookup in get_info_from_flight() """

    # Get flight information from parameters
    flight_id = request.args.get("flightId")
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    depart = request.args.get("depart")
    date = request.args.get("date")

    # Get the FlightScore stats from our database
    airline = flight_id[:2]
    flight_info = get_info_from_flight(airline, origin, destination, depart, date)

    # Build our dictionary of values to pass back to the client.  Then jsonify it!
    flight = {"flightId": flight_id, "pctDelay": flight_info["percent_delay"], "avgDelay": flight_info["avg_delay"], "pctCancel": flight_info["percent_cancel_divert"]}

    return jsonify(flight)

@app.route('/datavis')
def data_vis():
    """ This route gets the volume of all flights between selected cities from the
    database and puts them into a matrix format which will be the input for our D3
    data visualization of airport traffic """

    matrix = get_data_for_vis(VOL, cur_airports)
    all_scores = build_stats(VOL)

    return render_template("datavis.html", names=cur_airports, vol_flights=matrix, all_scores=all_scores)

@app.route('/datavispctdelay')
def data_vis_pct_delay():
    """ This route gets both the volume of all flights, and the number of flights 
    delayed between selected airports.  From these results, we then created a 3rd
    matrix containing the percentage of flights delayed between each selected airport.
    This new matrix is then passed to datavispctdelay.html as input for the D3 chord
    chart visualization.  We also pass in vol_flights so we can display overall stats
    for each airport """

    matrix = get_data_for_vis(VOL, cur_airports)
    matrix2 = get_data_for_vis(NUM_DELAY, cur_airports)
    matrix3 = get_pct_delay(matrix, matrix2, cur_airports)
    all_scores = build_stats(PCT_DELAY)

    return render_template("datavispctdelay.html", names=cur_airports, vol_flights=matrix, num_delay=matrix2, pct_delay=matrix3, all_scores=all_scores)

@app.route('/datavisavgdelay')
def data_vis_avg_delay():
    """ This route gets both the number of delayed flights between each airport, but
    also calculates a weighted average of delayed flights between each city.  these
    two matrices are then passed along to datavisavgdelay.html for display in a D3
    chord chart """

    matrix = get_data_for_vis(AVG_DELAY, cur_airports)
    matrix2 = get_data_for_vis(NUM_DELAY, cur_airports)
    all_scores = build_stats(AVG_DELAY)

    return render_template("datavisavgdelay.html", names=cur_airports, min_delay=matrix, num_delay=matrix2, all_scores=all_scores)

@app.route('/datavisscore')
def data_vis_score():
    """ This route gets both the number of delayed flights between each airport, but
    also calculates a weighted average of delayed flights between each city.  these
    two matrices are then passed along to datavisavgdelay.html for display in a D3
    chord chart """

    # Get matrix of scores for 10 busiest airports for D3 vis
    matrix = get_data_for_vis(SCORE, cur_airports)

    # Create a list of lists containing airport code, city name and score to pass to client
    # for ALL 50 airports for table display
    all_scores = build_stats(SCORE)
    
    return render_template("datavisscore.html", names=cur_airports, score=matrix, all_scores=all_scores)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    if len(sys.argv) > 1 and sys.argv[1] == "qpx":
        call_qpx = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
    
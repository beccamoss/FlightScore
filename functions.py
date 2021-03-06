import urllib2
import json
import os
from model import Flight, Carrier, Score, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datavis import VOL, AVG_DELAY, SCORE, PCT_DELAY

MORNING = 1
AFTERNOON = 2
EVENING = 3
REDEYE = 4

def query_QPX(parameter):
    """Send query with parameter and url to QPX"""  

    # Insert key into QPX API url
    url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=%s" %(os.environ["API_KEY"])

    # Turns parameters into JSON string
    json_param = json.dumps(parameter, encoding = 'utf-8')

    # Sends JSON string request to QPX and returns JSON
    flight_request = urllib2.Request(url, json_param, {'Content-Type': 'application/json'})

    return flight_request


def QPX_results(flight_request):
    """Read results from query to QPX into python and add to list"""

    # Opens JSON results
    results = urllib2.urlopen(flight_request)

    # Read results and turn it into Python
    python_result = json.load(results)
    # Closes JSON results
    results.close()

    return python_result

def get_flight_results(origin, destination, date, call_qpx):
    """ create the input for the QPX query based on user's input """

    parameter = {
    "request": {
        "passengers": {"adultCount": 1},
        "slice": [{
            "origin": origin,
            "destination": destination,
            "date": date,
            "maxStops": 0
            }],
        }
    }

    if call_qpx:
        # Query the QPX Express Api
        # python_result = flight_results(parameter)
    
        # write out results to file for reuse. Limited to 50 API calls/day
        # write_flight_results_to_files(python_result)

        # read in test data instead of calling API.  Limited to 50 API calls/day
        python_result = flight_results_from_file('seed_data/demoflightsearchfinal.txt')

        # Take the result and parse to just get the information we need
        flights = parse_flight_results(python_result)
    else:
        # Don't call the API, instead query the database to show FlightScores
        # for possible future flights based on 2017 data
        flights = get_flights_from_db(origin, destination, date)

    return flights

def flight_results(parameter):
    """ Call QPX Express API """
    # import pdb; pdb.set_trace()
    flight_request = query_QPX(parameter)
    return QPX_results(flight_request)

def flight_results_from_file(filename):
    """ read in test data instead of calling API.  Limited to 50 API calls/day """

    with open(filename, 'r') as f:
        python_result = json.load(f)
    return python_result

def write_flight_results_to_files(python_result):
    """ Write QPX Express search results to file to prevent overuse of API """

    with open('seed_data/demoflightsearch.txt', 'w') as outfile:
        json.dump(python_result, outfile)

def parse_flight_results(python_result):
    """ take the API search result and parse it.  Put the relevant info into a flight_info
    dictionary and append it to a list of flights."""

    flights = []

    for j in range(len(python_result["trips"]["tripOption"])):
        for flight_slice in python_result["trips"]["tripOption"][j]["slice"]:
            for flight_segment in flight_slice["segment"]:
                flight_info = {}

                # Extract the info we need from the API result and add key-value pairs to dictionary
                flight_info["price"] = python_result["trips"]["tripOption"][j]["saleTotal"]
                flight_info["airline_code"] = flight_segment["flight"]["carrier"]
                flight_info["flight_num"] = flight_segment["flight"]["number"]
                flight_info["origin_code"] = flight_segment["leg"][0]["origin"]
                flight_info["destination_code"] = flight_segment["leg"][0]["destination"]
                flight_info["departure_datetime"] = flight_segment["leg"][0]["departureTime"]
                flight_info["arrival_datetime"] = flight_segment["leg"][0]["arrivalTime"]
                flight_info["duration"] = flight_segment["leg"][0]["duration"]

                # Query the Carrier table to get the full name of the airline
                flight_info["carrier"] = db.session.query(Carrier.name).filter(Carrier.carrier_id == flight_info["airline_code"]).first()

                # Get score for flight
                flight_info["score"] = get_score_for_flight(flight_info["airline_code"],
                                                            flight_info["origin_code"],
                                                            flight_info["destination_code"],
                                                            flight_info["departure_datetime"])
                
                # Append this dictionary to the flights list
                flights.append(flight_info)

    return flights

def get_flights_from_db(origin, destination, date):
    """ This function us called when we are not calling the QPX Exress API.  Instead,
    we are querying the database for all flights between origin and destination for
    the quarter in which the date falls.  It then builds a list of flights for each
    airline and time of day with corresponding flight scores for display in 
    resultsdb.html """

    flights = []

    # Set the quarter of the year by the month
    quarter = get_quarter_from_month(int(date[5:7]))

    # Query the database to get all stats from that that quarter of the year betwee
    # the two specified cities for all times of day
    flights_from_db = db.session.query(Flight).filter(Flight.origin == origin,
                                              Flight.destination == destination,
                                              Flight.quarter == quarter).all()
    
    # Loop through each record returned from the database query, and build the dictionary
    # of info to add to the flights list
    for flight in flights_from_db:
        flight_info = {}
        flight_info["airline_code"] = flight.carrier
        flight_info["origin_code"] = flight.origin
        flight_info["destination_code"] = flight.destination
        flight_info["score"] = str(flight.score)
        flight_info["time"] = get_time(flight.time)
        # Query the Carrier table to get the full name of the airline
        flight_info["carrier"] = db.session.query(Carrier.name).filter(Carrier.carrier_id == flight_info["airline_code"]).first()

        # Append this to the flights list
        flights.append(flight_info)

    return flights


def get_time(time):
    """ Get string reflecting the time slice to display in HTML"""

    if time == 1:
        return 'Morning'
    elif time == 2:
        return 'Afternoon'
    elif time == 3:
        return 'Evening'
    else:
        return 'Red-Eye'

def get_quarter_from_month(month):
    """ Get the quarter of the year based on the month """

    if month < 4:
        quarter = 1
    elif month < 7:
        quarter = 2
    elif month < 10:
        quarter = 3
    else:
        quarter = 4
    return quarter

def get_score_for_flight(airline_code, origin_code, destination_code, departure_datetime):
    """ Look up the score for the flight with similar characteristics. Return the score """

    # Get the past history flight data and score for matching flight from db
    flight = get_matching_flight_from_db(airline_code,
                                         origin_code,
                                         destination_code,
                                         departure_datetime)

    # If flight history in database is insufficient for prediction, set
    # score to N/A
    if flight == None:
        return "N/A"
    return flight.score


def get_info_from_flight(airline_code, origin_code, destination_code, departure_datetime, date=None):
    """ This function is called from an AJAX request to get stats for the 
    selected FlightScore """

    flight_info = {}

    # If QPX Express API not called, mock a departure time to reflect the time of day
    if departure_datetime in ["Morning", "Afternoon", 'Evening', "Red-Eye"]:
        departure_datetime = mock_departure_from_time(departure_datetime, date)

    # Get the past history flight data and score for matching flight from db
    flight = get_matching_flight_from_db(airline_code,
                                         origin_code,
                                         destination_code,
                                         departure_datetime)

    if flight == None:
        flight_info["avg_delay"] = ''
        flight_info["percent_delay"] = ''
        flight_info["num_flights"] = ''
        flight_info["percent_cancel_divert"] = ''
    else:
        # Set more key-value pairs in the dictionary from this database query
        flight_info["avg_delay"] = flight.avg_delay
        flight_info["percent_delay"] = '%0.1f' % (flight.num_delayed / float(flight.num_flights) * 100)
        flight_info["num_flights"] = flight.num_flights
        flight_info["percent_cancel_divert"] = '%0.1f' % (flight.num_cancel_divert / float(flight.num_flights) * 100)

    return flight_info


def get_matching_flight_from_db(carrier, origin, destination, flight_datetime):
    """ given a flight search result, query the database to get the
    corresponding FlightScore for a flight that shares the same characteristics
    including: departure time, time of year, carrier name, origin and destination,
    then return the Flight data for that matching flight """
   
    month = int(flight_datetime[5:7])
    hour = int(flight_datetime[11:13])
   
    # Set the quarter of the year by the month
    quarter = get_quarter_from_month(month)

    # Set the slice of day by the hour:
    if (hour >= 5) and (hour < 11):
        time = MORNING
    elif (hour >= 11) and (hour < 17):
        time = AFTERNOON
    elif (hour >= 17) and (hour < 23):
        time = EVENING
    else:
        time = REDEYE

    flight_info = db.session.query(Flight).filter(Flight.carrier == carrier,
                                                  Flight.origin == origin,
                                                  Flight.destination == destination,
                                                  Flight.quarter == quarter,
                                                  Flight.time == time).first()

    # If no results returned, try querying again with a code share airline
    if not flight_info:
        carriers = get_code_share(carrier)
        for carrier in carriers:
            flight_info = db.session.query(Flight).filter(Flight.carrier == carrier,
                                                      Flight.origin == origin,
                                                      Flight.destination == destination,
                                                      Flight.quarter == quarter,
                                                      Flight.time == time).first()
            if flight_info:
                break

    return flight_info


def get_code_share(carrier):
    """ This function maps carriers to one another that have code share flights.  
    These code shares are used to requery the database if no FlightScore is returned
    for a particular QPX search 
    """

    if carrier == "UA": # United == Skywest
        return ["OO"]
    elif carrier == "OO":
        return ["UA"]
    elif carrier == "AS": # Alaska == Virgin
        return ["QX", "VX", "OO"]
    elif carrier == "VX":
        return ["AS", "QX", "OO"]
    else:
        return carrier


def date_valid(date):
    """ Check if date entered is valid.  If it's in the past or not in the current
    year, or empty, return false """

    today = datetime.now()

    try:
        month = int(date[5:7])
        day = int(date[8:])
        year = int(date[:4])
        
        if year > today.year:
            return False
        elif (month < today.month) or ((month == today.month) and (day < today.day)):
            return False
        else:
            return True
    except: 
        return False

def mock_departure_from_time(departure, date):
    """ This function takes in a departure date and a string containing the
    time of day and 'mocks' a fake departure date and time for database query since
    we aren't calling the QPX Express API and getting specific flight dates 
    and times """

    if departure == "Morning":
        return date + "-06"
    elif departure == "Afternoon":
        return date + "-12"
    elif departure == "Evening":
        return date + "-18"
    else:
        return date + "-01"

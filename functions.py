import urllib2
import json
import os
from model import Flight, Carrier, Airport, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy

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

def get_flight_results(origin, destination, date):
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
        # "solutions": 10
        }
    }

    # Query the Google Flights Api
    # flight_request = query_QPX(parameter)
    # python_result = QPX_results(flight_request)

    # import pdb; pdb.set_trace()
    # write out results to file for reuse. Limited to 50 API calls/day
    # with open('test/flights.txt', 'w') as outfile:
    #     json.dump(python_result, outfile)
    
    # read in test data instead of calling API.  Limited to 50 API calls/day
    with open('test/flights.txt', 'r') as f:
        python_result = json.load(f)

    # Take the result and parse to just get the information we need
    flights = parse_flight_results(python_result)

    return flights

def parse_flight_results(python_result):
    """ take the API search result and parse it.  Put the relevant info into a flight_info
    dictinary and append it to a list of flights."""

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

                # Get the past history flight data and score for matching flight from db
                flight = get_matching_flight_from_db(flight_info["airline_code"],
                                                     flight_info["origin_code"],
                                                     flight_info["destination_code"],
                                                     flight_info["departure_datetime"])

                # Set more key-value pairs in the dictionary from this database query
                # import pdb; pdb.set_trace()
                flight_info["score"] = flight.score
                flight_info["avg_delay"] = flight.avg_delay
                flight_info["percent_delay"] = flight.num_delayed / float(flight.num_flights) * 100
                flight_info["num_flights"] = flight.num_flights
                flight_info["percent_cancel_divert"] = flight.num_cancel_divert / float(flight.num_flights) * 100

                # Query the Carrier table to get the full name of the airline
                flight_info["carrier"] = db.session.query(Carrier.name).filter(Carrier.carrier_id == flight.carrier).first()

                # Append this dictionary to the flights list
                flights.append(flight_info)

    return flights

def get_matching_flight_from_db(carrier, origin, destination, flight_datetime):
    """ given a flight search result, query the database to get the
    corresponding FlightScore, return that score """
   
    month = int(flight_datetime[5:7])
    hour = int(flight_datetime[11:13])
   
    # Set the quarter of the year by the month
    if month < 4:
        quarter = 1
    elif month < 7:
        quarter = 2
    elif month < 10:
        quarter = 3
    else:
        quarter = 4

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

    # If matching flight record NOT found, ease query restrictions and try again
    # using just origin, destination and time of day
    if flight_info is None:
        flight_info = db.session.query(Flight).filter(Flight.origin == origin,
                                                      Flight.destination == destination,
                                                      Flight.time == time).first()
    
    return flight_info

def update_results_for_display(results):
    """ Update departure and arrival time, origin and destination fields and airline
    info for display purpose on results.html 
    """

    for flight in results:
        flight["arrival_datetime"] = flight["arrival_datetime"][11:16]
        flight["departure_datetime"] = flight["departure_datetime"][11:16]

    return results
            
def print_flight_results(python_result):
    """ display function for debugging purposes """

    flights = parse_flight_results(python_result)

    for flight in flights:
        print "Airline: ", flight["airline_code"]
        print "Flight Number: ", flight["flight_num"]
        print "Origin: ", flight["origin_code"]
        print "Destination: ", flight["destination_code"]
        print "Departure: ", flight["departure_datetime"]
        print "Arrival: ", flight ["arrival_datetime"]
        print "Duration: ", flight["duration"]
        print "Price: ", flight["price"]
        print

    return
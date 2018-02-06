import urllib2
import json
import os
from model import Flight, Carrier, Airport, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy


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
            "maxStops": 1
            }],
        "solutions": 10
        }
    }

    # Query the Google Flights Api
    flight_request = query_QPX(parameter)
    python_result = QPX_results(flight_request)

    # Output results for debugging
    print_flight_results(python_result)

    # Take the result and parse to just get the information we need
    # flights = parse_flight_results(python_result)

    return 

def parse_flight_results(python_result):
    """ take the API search result and parse it.  Put the relevant info into a flight_info
    dictinary and append it to a list of flights."""

    flights = []
    for j in range(len(python_result["trips"]["tripOption"])):
        for flight_slice in python_result["trips"]["tripOption"][j]["slice"]:
            for flight_segment in flight_slice["segment"]:
                flight_info = {}
                flight_info["price"] = python_result["trips"]["tripOption"][j]["saleTotal"]
                flight_info["airline_code"] = flight_segment["flight"]["carrier"]
                flight_info["flight_num"] = flight_segment["flight"]["number"]
                flight_info["origin_code"] = flight_segment["leg"][0]["origin"]
                flight_info["destination_code"] = flight_segment["leg"][0]["destination"]
                flight_info["departure_datetime"] = flight_segment["leg"][0]["departureTime"]
                flight_info["arrival_datetime"] = flight_segment["leg"][0]["arrivalTime"]
                flight_info["duration"] = flight_segment["leg"][0]["duration"]
                flight_info["score"] = get_score_for_flight(flight_info["airline_code"],
                                                            flight_info["origin_code"],
                                                            flight_info["destination_code"],
                                                            flight_info["departure_datetime"])
                flights.append(flight_info)
    return flights

def get_score_for_flight(carrier, origin, destination, flight_datetime):
    """ given a flight search result, query the database to get the
    corresponding FlightScore, return that score """
    
    month = int(flight_datetime[5:7])
    hour = int(flight_datetime[11:13])
    
    # import pdb; pdb.set_trace()

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
    # 1 = 5:00-11:00
    # 2 = 11:00-17:00
    # 3 = 17:00-23:00
    # 4 = 23:00-5:00
    if (hour >= 5) and (hour < 11):
        time = 1
    elif (hour >= 11) and (hour < 17):
        time = 2
    elif (hour >= 17) and (hour < 23):
        time = 3
    else:
        time = 4    

    score = db.session.query(Flight).filter(Flight.carrier==carrier,
                                            Flight.origin==origin,
                                            Flight.destination==destination,
                                            Flight.quarter==quarter,
                                            Flight.time==time).first()
    return score
    


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

    return flights
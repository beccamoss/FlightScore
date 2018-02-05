import urllib2
import json
import os
from pprint import pprint

def query_QPX(parameter):
    """Send query with parameter and url to QPX"""

    # Get key from environment
    API_KEY = 'AIzaSyBPf9JjKfSUoS_aB_UBxKr4j9qqrXvhvP4'

    # Insert key into QPX API url
    url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=%s" %(API_KEY)

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

    # def parameter_by_params(query):
    # """Get parameter dictionary from params"""

    # Get inputs from params into parameters
parameter = {
"request": {
    "passengers": {"adultCount": 1},
    "slice": [{
        "origin": "JFK",
        "destination": "SFO",
        "date": "2018-04-21",
        "maxStops": 1
        }],
    "solutions": 10
    }
}

flight_request = query_QPX(parameter)
python_result = QPX_results(flight_request)
print "Results"
pprint(python_result)

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
            flights.append(flight_info)

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

import urllib2
import json
import os
from model import Flight, Carrier, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy

# 10 Busiest airports
airports = ["ATL", "LAX", "ORD", "DFW", "JFK", "DEN", "SFO", "LAS", "CLT", "SEA"]

def get_data_for_vis():

    total_flights_1 = 0
    total_flights_2 = 0
    matrix = [[] for _ in xrange(len(airports))]    

    for i in range(len(airports)-1):
        matrix[i].append(0) 
        for j in range(i+1, len(airports)):

            # Query the database for flight stats in both directions
            flights_1 = db.session.query(Flight).filter(Flight.origin == airports[i],
                                                        Flight.destination == airports[j]).all() 

            flights_2 = db.session.query(Flight).filter(Flight.origin == airports[j],
                                                        Flight.destination == airports[i]).all()

            for k in range(len(flights_1)):
                total_flights_1 = total_flights_1 + flights_1[k].num_flights

            for k in range(len(flights_2)):
                total_flights_2 = total_flights_2 + flights_2[k].num_flights

            matrix[i].append(total_flights_1)
            matrix[j].append(total_flights_2)

            total_flights_2 = 0
            total_flights_1 = 0

    matrix[len(airports)-1].append(0)
    return matrix
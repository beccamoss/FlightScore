import urllib2
import json
import os
from model import Flight, Carrier, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy

# Hard coded list of the 10 busiest airports in the US
cur_airports = ["ATL", "LAX", "ORD", "DFW", "JFK", "DEN", "SFO", "LAS", "CLT", "SEA"]

# Constants used to distinguish what kinds of data is required for Data Vis
VOL = 1
NUM_DELAY = 2
AVG_DELAY = 3
SCORE = 4
PCT_DELAY = 5

def get_data_for_vis(data_type, query_airports):
    """ 
    This function take data_type as a parameter to distinguish what type of information
    is required from the database to visualize.  This can be:
        VOL = Volume of total flights between each airports
        NUM_DELAY = Total number of flights delayed over 30 minutes between each airports
        AVG_DELAY = A weighted average of the minutes delayed between each airport
        SCORE = Calculates a weighted average of FlighScores between airports

    Query the database between each airport twice - once for each directions
    Calculate the totals for each flight in that flight segment
    Calculate the weighted average if necessary
    Append to matrix which will eventually be passed to D3 for display in chord chart 
    """

    total_flights_1 = total_flights_2 = avg_flights_1 = avg_flights_2 = 0
    matrix = [[] for _ in xrange(len(query_airports))]    

    for i in range(len(query_airports)-1):
        matrix[i].append(0)
        for j in range(i+1, len(query_airports)):

            # Query the database for flight stats in both directions
            flights_1 = db.session.query(Flight).filter(Flight.origin == query_airports[i],
                                                        Flight.destination == query_airports[j]).all() 

            flights_2 = db.session.query(Flight).filter(Flight.origin == query_airports[j],
                                                        Flight.destination == query_airports[i]).all()

            # Total up stats for all flight segments going both directions
            for k in range(len(flights_1)):
                if data_type == VOL:
                    total_flights_1 = total_flights_1 + flights_1[k].num_flights
                elif data_type == NUM_DELAY:
                    total_flights_1 = total_flights_1 + flights_1[k].num_delayed
                elif data_type == AVG_DELAY:
                    avg_flights_1 = avg_flights_1 + (flights_1[k].avg_delay * flights_1[k].num_delayed)
                    total_flights_1 = total_flights_1 + flights_1[k].num_delayed
                elif data_type == SCORE:
                    avg_flights_1 = avg_flights_1 + (flights_1[k].score * flights_1[k].num_flights)
                    total_flights_1 = total_flights_1 + flights_1[k].num_flights

            # Total stats for the other direction
            for k in range(len(flights_2)):
                if data_type == VOL:
                    total_flights_2 = total_flights_2 + flights_2[k].num_flights
                elif data_type == NUM_DELAY:
                    total_flights_2 = total_flights_2 + flights_2[k].num_delayed
                elif data_type == AVG_DELAY:
                    avg_flights_2 = avg_flights_2 + (flights_2[k].avg_delay * flights_2[k].num_delayed)
                    total_flights_2 = total_flights_2 + flights_2[k].num_delayed
                elif data_type == SCORE:
                    avg_flights_2 = avg_flights_2 + (flights_2[k].score * flights_2[k].num_flights)
                    total_flights_2 = total_flights_2 + flights_2[k].num_flights

            # Get weighted average of delays or FlightScores
            if (data_type == AVG_DELAY) or (data_type == SCORE):
                if total_flights_1 != 0:
                    total_flights_1 = avg_flights_1 / total_flights_1
                if total_flights_2 != 0:
                    total_flights_2 = avg_flights_2 / total_flights_2

            # Add stats to matrix
            matrix[i].append(total_flights_1)
            matrix[j].append(total_flights_2)

            # Zero out variables before query again
            total_flights_2 = total_flights_1 = avg_flights_2 = avg_flights_1 = 0

    matrix[len(query_airports)-1].append(0)
    return matrix

def get_pct_delay(vol_flights, num_delay, airports):
    """ This function takes two matrices as input, one for number of flights delayed
    and another with the volume of flights, and returns a new matrix which
    contains the percentage of delayed flights for each corresponding matrix location 
    in the inputs.  This resulting matrix will be used for D3 chord chart display
    in /datavispctdelay """

    matrix = [[] for _ in xrange(len(airports))]

    for i in range (len(airports)):
        for j in range (len(airports)):
            if (vol_flights[i][j] == 0):
                matrix[i].append(0)
            else:
                matrix[i].append(100 * num_delay[i][j] / float(vol_flights[i][j]))

    return matrix
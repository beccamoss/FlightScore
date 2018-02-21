import urllib2
import json
import os
from model import Flight, Carrier, connect_to_db, db
from flask_sqlalchemy import SQLAlchemy


cur_airports = ["ATL", "LAX", "ORD", "DFW", "JFK", "DEN", "SFO", "LAS", "SJC", "SEA"]
all_airports = ["ATL", "LAX", "ORD", "DFW", "JFK", "DEN", "SFO", "LAS", "SJC", "SEA", "PDX"]
VOL = 1
NUM_DELAY = 2
AVG_DELAY = 3
SCORE = 4

def get_data_for_vis(data_type, query_airports):
    """ 
    This function take data_type as a parameter to distinguish what type of information
    is required from the database to visualize.  This can be:
        VOL = Volume of total flights between each airports
        NUM_DELAY = Total number of flights delayed over 30 minutes between each airports
        AVG_DELAY = A weighted average of the minutes delayed between each airport

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
    """ This function takes two matrices as input and returns a new matrix which
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

def get_top_ten(scores, all_airports):
    all_scores = {}
    top_ten = {}
    min_score = 100
    sumScores = numLegs = 0

    # Calculate average FlightScores for each airport in all_airports
    for i in range (len(all_airports)):
        for j in range (len(all_airports)):
            sumScores += (scores[i][j] + scores[j][i])
            if scores[i][j] != 0:
                numLegs = numLegs + 2
        all_scores[all_airports[i]] = sumScores / numLegs
        sumScores = numLegs = 0

    # Loop through all scores unpacking the airport with corresponding score to build
    # a top_ten dictionary of airport and scores
    for airport, score in all_scores.items():
        if len(top_ten) < 10:
            top_ten[airport] = score
            if score < min_score:
                min_score = score
        elif score > min_score:
            # Look for airport with current min_score
            for cur_airport in top_ten:
                if top_ten[cur_airport] == min_score:
                    airport_to_remove = cur_airport
                    break
       
            # Delete airport to remove. Then add new airport and score
            del top_ten[airport_to_remove]
            top_ten[airport] = score

            # Find new minimum score
            lst_scores = top_ten.values()
            lst_scores.sort()
            min_score = lst_scores[0]

    lst_of_tuples = top_ten.items()
    lst_of_tuples.sort(key=lambda tup: tup[1], reverse=True)

    return list_from_tuples(lst_of_tuples)


def list_from_tuples(lst):
    new_lst = []
    for tup in lst:
        sub_lst = []
        sub_lst.append(tup[0])
        sub_lst.append(tup[1])
        new_lst.append(sub_lst)
    return new_lst


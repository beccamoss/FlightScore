"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import Flight
from model import Carrier
from model import Score
from model import connect_to_db, db
from server import app
from datavis import get_data_for_vis, SCORE
all_airports = {}


def load_flights():
    """ Load flights from flights.csv """

    for row in open("seed_data/flights.csv"):
        row = row.strip()
        origin, destination, carrier, quarter, time, avg_delay, \
            duration, num_flights, num_delay, num_can_div, score = row.split(",")

        flight = Flight(origin=origin, destination=destination, carrier=carrier,
                        quarter=int(quarter), time=int(time), num_flights=int(num_flights),
                        num_delayed=int(num_delay), num_cancel_divert=int(num_can_div), duration=int(duration), 
                        avg_delay=int(avg_delay), score=float(score))

        # Add each flight to the session
        db.session.add(flight)

    # Once we're done, commit all the flights to the database
    db.session.commit()
    return

def load_carriers():
    for row in open("seed_data/carriers.txt"):
        row = row.strip()
        code, name = row.split("|")

        # check if carrier was in operation in 2017, skip if the year format
        # doesn't end in .... (year - )
        if name[-3:-2] != "-": 
            continue
        else:
            name = name[:-10] # strip the year from the name of the carrier
        # import pdb; pdb.set_trace()

        carrier = Carrier(carrier_id=code, name=name, img="")

        # Add each airport to the session
        db.session.add(carrier)

    # Once we're done, commit all the carriers to the database
    db.session.commit()
    return

def load_airports_from_file():

    with open('seed_data/allairports.txt', 'r') as f:
        for line in f:
            code, city = line.split(',')
            all_airports[code] = city.rstrip()
    return

def calculate_scores():
    all_scores = {}
    # top_ten = {}
    # min_score = 100
    sumScores = numLegs = 0
    i = j = 0

    # Query the database to get all scores between all airports
    scores = get_data_for_vis(SCORE, all_airports.keys())

    # Calculate average FlightScore for each airport between all airports in all_airports
    for origin_code in all_airports.keys():
        for j in range(len(all_airports)):
            sumScores += (scores[i][j] + scores[j][i])
            if scores[i][j] != 0:
                numLegs = numLegs + 2

        # import pdb; pdb.set_trace()
        all_scores[origin_code] = sumScores / numLegs
        sumScores = numLegs = 0
        i += 1

    return all_scores


def load_scores():
    load_airports_from_file()
    airports_and_scores = calculate_scores()
    for airport in airports_and_scores.keys():
        score = Score(airport_code=airport, city=all_airports[airport], score=airports_and_scores[airport])

        # Add each airport to the session
        db.session.add(score)

    # Once we're done, commit all the scores to the database
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    # load_airports()
    load_carriers()
    load_flights()
    load_scores()
   
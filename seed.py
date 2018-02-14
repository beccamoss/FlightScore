"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import Flight
from model import Carrier
from model import connect_to_db, db
from server import app

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

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    # load_airports()
    load_carriers()
    load_flights()
   
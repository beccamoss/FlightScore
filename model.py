from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database
db = SQLAlchemy()

##############################################################################
# Model definitions

class Flight(db.Model):
    """ Data on an individual flight segment """

    __tablename__ = "flights"

    flight_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    origin = db.Column(db.String(3))
    destination = db.Column(db.String(3))
    carrier = db.Column(db.String(3), db.ForeignKey('carriers.carrier_id'))
    quarter = db.Column(db.Integer)
    time = db.Column(db.Integer)
    num_flights = db.Column(db.Integer)
    num_delayed = db.Column(db.Integer)
    num_cancel_divert = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    avg_delay = db.Column(db.Integer)
    score = db.Column(db.Integer)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<#_flights={} #_delay={} duration={} avg_delay={}>". \
                format(self.num_flights, self.num_delayed,
                       self.duration, self.avg_delay)

class Carrier(db.Model):
    """ Data on airline carriers """

    __tablename__ = "carriers"

    carrier_id = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(90))
    img = db.Column(db.String(32))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<carrier_id={} name={} img={}>".format(self.carrier_id,
                                                        self.name,
                                                        self.img))

class Score(db.Model):
    """ Table of Airport Scores """

    __tablename__ = "scores"

    airport_code = db.Column(db.String(3), primary_key=True)
    city = db.Column(db.String(100))
    score = db.Column(db.Integer)
    volume = db.Column(db.Integer)
    pct_delay = db.Column(db.Float)
    avg_delay = db.Column(db.Integer)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<airport_code={} city={} score={} volume={} pct_delay={} avg_delay={}>"
                .format(self.airport_code, self.city, self.score, self.volume, self.pct_delay, self.avg_delay))


##############################################################################
# Helper functions

def connect_to_db(app, database='postgresql:///flights'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

def example_data():
    """ Create some sample data for database tests """

    c1 = Carrier(carrier_id="NK", name="Spirit Airlines")
    c2 = Carrier(carrier_id="UA", name="United Airlines")
    db.session.add_all([c1, c2])
    db.session.commit()
  
    f1 = Flight(origin="SEA", destination="SFO", carrier="NK", quarter=1, time=2, num_flights=10, num_delayed=1, num_cancel_divert=1, duration=120, avg_delay=40, score=65)
    f2 = Flight(origin="ORD", destination="DFW", carrier="UA", quarter=1, time=2, num_flights=20, num_delayed=3, num_cancel_divert=0, duration=110, avg_delay=35, score=70)
    f3 = Flight(origin="LAX", destination="SFO", carrier="NK", quarter=1, time=2, num_flights=10, num_delayed=1, num_cancel_divert=1, duration=120, avg_delay=40, score=65)
    f4 = Flight(origin="DFW", destination="DFW", carrier="UA", quarter=1, time=2, num_flights=20, num_delayed=3, num_cancel_divert=0, duration=110, avg_delay=35, score=70)
    f5 = Flight(origin="CLT", destination="SFO", carrier="NK", quarter=1, time=2, num_flights=10, num_delayed=1, num_cancel_divert=1, duration=120, avg_delay=40, score=65)
    f6 = Flight(origin="LAS", destination="DFW", carrier="UA", quarter=1, time=2, num_flights=20, num_delayed=3, num_cancel_divert=0, duration=110, avg_delay=35, score=70)
    f7 = Flight(origin="JFK", destination="SFO", carrier="NK", quarter=1, time=2, num_flights=10, num_delayed=1, num_cancel_divert=1, duration=120, avg_delay=40, score=65)
    f8 = Flight(origin="DEN", destination="DFW", carrier="UA", quarter=1, time=2, num_flights=20, num_delayed=3, num_cancel_divert=0, duration=110, avg_delay=35, score=70)
    f9 = Flight(origin="ATL", destination="LAX", carrier="NK", quarter=1, time=2, num_flights=10, num_delayed=1, num_cancel_divert=1, duration=120, avg_delay=40, score=65)
    f10 = Flight(origin="SFO", destination="DFW", carrier="UA", quarter=1, time=2, num_flights=20, num_delayed=3, num_cancel_divert=0, duration=110, avg_delay=35, score=70)


    db.session.add_all([f1, f2, f3, f4, f5, f6, f7, f8, f9, f10])
    db.session.commit()

    s1 = Score(airport_code="SEA", city="Seattle WA", score=55)
    s2 = Score(airport_code="SFO", city="San Francisco CA", score=35)
    s3 = Score(airport_code="DFW", city="Dallas TX", score=45)
    s4 = Score(airport_code="ORD", city="Chicago IL", score=40)

    db.session.add_all([s1, s2, s3, s4])
    db.session.commit()

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
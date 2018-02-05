from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database
db = SQLAlchemy()

##############################################################################
# Model definitions

class Flight(db.Model):
    """ Data on an individual flight segment """

    __tablename__ = "flights"

    flight_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    origin = db.Column(db.String(3), db.ForeignKey('airports.airport_id'))
    destination = db.Column(db.String(3), db.ForeignKey('airports.airport_id'))
    carrier = db.Column(db.String(3), db.ForeignKey('carriers.carrier_id'))
    quarter = db.Column(db.Integer)
    time = db.Column(db.Integer)
    num_flights = db.Column(db.Integer)
    num_delayed = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    avg_delay = db.Column(db.Integer)
    score = db.Column(db.Float)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<flight_id={} origin={} dest={} carrier={} time={} quarter={} num_flights={} num_delayed={} duration={} min_delay={} score={}>". \
                format(self.flight_id, self.origin, self.destination, self.carrier,
                       self.time, self.quarter, self.num_flights, self.num_delayed,
                       self.duration, self.avg_delay, self.score)

class Airport(db.Model):
    """ Data on airports """

    __tablename__ = 'airports'

    airport_id = db.Column(db.String(3), primary_key=True)
    description = db.Column(db.String(128))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<airport_id={} description={}>".format(self.airport_id,
                                                                  self.description))


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

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flights'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
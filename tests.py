from unittest import TestCase
from server import app
from model import connect_to_db, db, example_data
from flask import session
import functions

class FlaskTests(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_home(self):
        """Test homepage page."""

        result = self.client.get("/")
        self.assertIn("homepage", result.data)

    def test_about(self):
        """Test about page"""

        result = self.client.get("/about")
        self.assertIn("6M", result.data)

class FlaskSearch(TestCase):
    """ Flask tests that test the input fields on the home page """

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Make mock of Google Flights API call
        def _mock_flight_results(parameter):
            return functions.flight_results_from_file('seed_data/testflights.txt')

        functions.flight_results = _mock_flight_results

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_bad_airport(self):
        """ Test behavior when user enters a non-existent airport """
        result = self.client.get("/search?origin=foo&destination=DFW%2C+Dallas+TX&date=2018-05-21")
        self.assertNotIn('<meter', result.data)
        self.assertIn('enter a valid airport', result.data)

    def test_bad_date_1(self):
        """ Test behavior when user enters a bad date """
        result = self.client.get("/search?origin=ORD%2C+Chicago+IL&destination=DFW%2C+Dallas+TX&date=2017-01-01")
        self.assertNotIn('<meter value="70"', result.data)
        self.assertIn('enter a valid date', result.data)

    def test_bad_date_2(self):
        """ Test behavior when user enters a bad date """
        result = self.client.get("/search?origin=ORD%2C+Chicago+IL&destination=DFW%2C+Dallas+TX&date=2020-01-01")
        self.assertNotIn('<meter value="70"', result.data)
        self.assertIn('enter a valid date', result.data)

    def test_bad_date_3(self):
        """ Test behavior when user enters a bad date """
        result = self.client.get("/search?origin=ORD%2C+Chicago+IL&destination=DFW%2C+Dallas+TX&date=")
        self.assertNotIn('<meter value="70"', result.data)
        self.assertIn('enter a valid date', result.data)


class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Make mock of Google Flights API call
        def _mock_flight_results(parameter):
            return functions.flight_results_from_file('seed_data/testflights.txt')

        functions.flight_results = _mock_flight_results

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def testCarrierTable(self):
        """ Test Carrier name DB lookup"""

        result = self.client.get("/search?origin=ORD%2C+Chicago+IL&destination=DFW%2C+Dallas+TX&date=2018-05-21")
        self.assertIn("United", result.data)

    def testScoreTable(self):
        """ Test FlightScore DB lookup"""

        result = self.client.get("/search?origin=ORD%2C+Chicago+IL&destination=DFW%2C+Dallas+TX&date=2018-05-21")
        self.assertIn('<meter value="70"', result.data)


if __name__ == '__main__':
    import unittest

    unittest.main()
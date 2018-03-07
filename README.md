# FlightScore

## Summary

**FlightScore** is a web app which helps users make better travel choices when purchasing airline tickets. By analyzing the on-time performance data of nearly 6M domestic flights in 2017, it algorithmically generates FlightScores for categories of flights, giving users more insight into how future flights may perform. This algorithm analyzes statistics between any two airports including the percentage of delayed flights, the average length of delay, and the percentage of flights cancelled or diverted, while considering the airline, time of year and departure time of each flight. D3 chord charts are integrated for data visualization of these performance statistics between the ten busiest US airports.

## About the Developer

FlightScore was created by Becca Moss, a software engineer in Menlo Park, CA. Read more about her on [LinkedIn](https://www.linkedin.com/in/becca-moss).

## Technologies

**Tech Stack:**

- Python
- Flask
- SQLAlchemy
- Jinja2
- HTML
- CSS
- Javascript
- JQuery
- AJAX
- JSON
- Bootstrap
- Python unittest module
- D3
- QPX Express API (Service ends April 10, 2018)

FlightScore is an app built on a Flask server with a PostgreSQL database, with SQLAlchemy as the ORM. The front end templating uses Jinja2, the HTML was built using Bootstrap, and the Javascript uses JQuery and AJAX to interact with the backend. The graphs are rendered using D3. Server routes and functions are tested using the Python unittest module.

## Features

![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/landing_screenshot.png "FlightScore Home Page")

![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/results_qpx_screenshot.png "Results Page Using Flights Returned From QPX Express API")

![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/results_qpx_expand.png "Past Performance Statistics Shown Inline For Each Flight")

![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/results_expand.png "Results Page Without QPX Express API Use")

![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/pct_delay_screenshot.png "Chart Showing Percentage of Flights Delayed Between 10 Busiest Airports - Using D3")

![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/pct_delay_screenshot.png "Chart Interactivity with Chord Highlighting Upon Hover")


## For Version 2.0

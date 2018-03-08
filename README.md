# FlightScore

## Summary

Deployed at: http://flightscore.us

**FlightScore** is a web app which helps users make better travel choices when purchasing airline tickets. By analyzing the on-time performance data of nearly 6M domestic flights in 2017, it algorithmically generates FlightScores for categories of flights, giving users more insight into how future flights may perform. This algorithm analyzes statistics between any two airports including the percentage of delayed flights, the average length of delay, and the percentage of flights cancelled or diverted, while considering the airline, time of year and departure time of each flight. Users can then make travel decisions based on both price and past performance. D3 chord charts are integrated for data visualization of these performance statistics between the ten busiest US airports.

**Important:** The QPX Express API will no longer be available for use after April 10, 2018.  When this occurs, FlightScores for categories of flights will be shown instead of flights returned from the API. See screenshot further down.


## About the Developer

FlightScore was created by Becca Moss, a software engineer in the Bay Area. Read more about her on [LinkedIn](https://www.linkedin.com/in/becca-moss).

## Technologies

**Tech Stack:**

Python, Flask, SQLAlchemy, Jinja2, HTML, CSS, JavaScript, JQuery, AJAX, JSON, Bootstrap, Python unittest module, D3, QPX Express API (Service ends April 10, 2018)

FlightScore is an app built on a Flask server with a PostgreSQL database, with SQLAlchemy as the ORM. The front end templating uses Jinja2, the HTML was built using Bootstrap, and the Javascript uses JQuery and AJAX to interact with the backend. The graphs are rendered using D3. Server routes and functions are tested using the Python unittest module.

## Features
**The home page lets the user enter the origin and destination airports, as well as the date of travel.**
![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/landing_screenshot.PNG "FlightScore Home Page")
<br /><br />

**The screenshot below shows flight results returned from the QPX Express API with real-time pricing. In the far left column is a FlightScore associated with each flight.  Under the hood, analysis is done on the past performance history of nearly 6M domestic flights to algorithmically generate FlightScores for categories of flights. Statistics like the percentage of delayed flights, the length of delays and the percentage of cancelled flights are weighted and combined to create an overall FlightScore for each category of flight which is then stored in a PostgreSQL database for quick retrieval on the results page.**
![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/results_qpx_screenshot.PNG "Results Page Using Flights Returned From QPX Express API")
<br /><br />

**If the user wants to see the underlying statistics on which the FlightScore is based, they can click on the FlightScore button which then makes an AJAX call to the database to retrieve those stats for inline display**
![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/results_qpx_expand.PNG "Past Performance Statistics Shown Inline For Each Flight")
<br /><br />

**The screenshot below shows the flight search results page without calling the QPX Express API. The user can still use this tool to view FlightScores for flights they are considering buying on another site.  This is the version deployed on AWS.**
![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/results_expand.png "Results Page Without QPX Express API Use")
<br /><br />

**Data visualization has been incorporated into the app as well.  Using D3, interactive chord charts can be explored to get a deeper understanding of the relationship between airports for statistics including: FlightScores, Percentage of Delayed Flights, Average Length of Delay and the Volume of Flights. Data is also displayed in sortable tables for interactivity and to give a deeper understanding of flight performance by airport.**
![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/pct_delay_screenshot.PNG "Chart Showing Percentage of Flights Delayed Between 10 Busiest Airports - Using D3")
<br /><br />

**Note that the charts are interactive.  Hovering over an airport, or chord in the chart highlights those chords while displaying tooltip text describing the statistics it represents.**
![alt text](https://github.com/beccamoss/FlightScore/blob/master/static/img/pct_delay_chord_screenshot.PNG "Chart Interactivity with Chord Highlighting Upon Hover")
<br /><br />

## For Version 2.0
1. Get access to another Flight API to reintegrate this feature once the QPX Express API access is turned off.

2. Integrate data prior to 2017 into my algorithm

3. Use 2016 data to see if it is predictive of 2017 performance




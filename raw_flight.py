import os
import collections

#files = ['raw/tenflights.csv']
#files = ['test/test1.csv', 'test/test2.csv']
files = ['raw/january2017.csv', 'raw/february2017.csv', 'raw/march2017.csv',
         'raw/april2017.csv', 'raw/may2017.csv', 'raw/june2017.csv',
         'raw/july2017.csv', 'raw/august2017.csv', 'raw/september2017.csv',
         'raw/october2017.csv', 'raw/november2017.csv', 'raw/december2016.csv']
CANCELLED_OR_DIVERTED = -1
DELAY_THRESHOLD = 30
WEIGHT_PCT_FLIGHTS_DELAYED = 1
WEIGHT_AVG_MIN_DELAYED = .8
WEIGHT_CANCEL_DIVERT = .1

def makehash():
    return collections.defaultdict(makehash)

class FlightInfo(object):

    def __init__(self, min_delay, duration):
        """ Create and initialize a new flight object and add to the nested 
        dictionary raw_flight_data if this is a new flight record"""

        self.duration = duration
        self.num_flights = 1
        if min_delay >= DELAY_THRESHOLD:
            self.num_delay = 1
            self.min_delay = min_delay
            self.num_cancelled_diverted = 0
        elif min_delay < 0:
            self.num_delay = 0
            self.min_delay = 0
            self.num_cancelled_diverted = 1
        else:
            self.num_delay = 0
            self.min_delay = 0
            self.num_cancelled_diverted = 0

        self.score = 0

    def update_flight_info(self, min_delay, duration):
        """ If the flight info for has already been added to the raw_flight_data
        object, then update that record with the new flight info"""

        if min_delay >= DELAY_THRESHOLD:
            self.min_delay += min_delay
            self.num_delay += 1
        elif min_delay < 0: # flight cancelled
            self.num_cancelled_diverted += 1
        self.duration += duration
        self.num_flights += 1

    def add_or_update_flight_score(self, score):
        """ Add calculated flight score to raw_flight_data object """

        self.score = score
        return


def load_flight_data():
    """  Loop through input files and load all the flight info into the nested
    dictionary object raw_flight_data """
   
    for monthly_file in files:
        f = open(monthly_file, "r")

        # for each line in file read in origin, destination, carrier, slice_day,
        # min_delay and duration
        for line in f:
            quarter, carrier, origin, destination, depart_time, min_delay, duration, slice_day = line.split(',')

            # check if this field is empty.  This indicates a cancelled or diverted flight
            # which we will use in our FlightScore calculation later
            if min_delay:
                min_delay = int(min_delay)
            else:
                min_delay = CANCELLED_OR_DIVERTED

            duration = int(duration)

            # Update raw_flight_data dictionary with current flight info
            origin_airport = raw_flight_data.get(origin)
            if origin_airport:
                destination_airport = origin_airport.get(destination)
                if destination_airport:
                    carrier_info = destination_airport.get(carrier)
                    if carrier_info:
                        quarter_id = carrier_info.get(quarter)
                        if quarter_id:
                            time_of_day = quarter_id.get(slice_day)
                            if time_of_day:
                                # Record found - update FlightInfo object with current flight
                                time_of_day.update_flight_info(min_delay, duration)
                            else:
                                quarter_id[slice_day] = FlightInfo(min_delay, duration)
                        else:
                            # Add a new FlightInfo object as value to new slice_day key
                            carrier_info[quarter][slice_day] = FlightInfo(min_delay, duration)
                    else:
                        # Add new FlightInfo object as value to new carrier key
                        destination_airport[carrier][quarter][slice_day] = FlightInfo(min_delay, duration)
                else:
                    # Add new FlightInfo object as value to new destination key
                    origin_airport[destination][carrier][quarter][slice_day] = FlightInfo(min_delay, duration)
            else:
                # add new FlightInfo object as value to new origin key
                raw_flight_data[origin][destination][carrier][quarter][slice_day] = FlightInfo(min_delay, duration)
        f.close()
    return

def write_flight_data_to_file():
    """ Writes flights stats to a file """

    f = open("seed_data/flights.csv", "w")

    #f.write("origin,destination,carrier,quarter,time,avg_delay,avg_duration,num_flights,num_delayed,num_canceldivert,score\n")
    for k in raw_flight_data:
        for j in raw_flight_data[k]:
            for m in raw_flight_data[k][j]:
                for n in raw_flight_data[k][j][m]:
                    for o in raw_flight_data[k][j][m][n]:
                        d = raw_flight_data[k][j][m][n][o]
                        if d.num_delay == 0:
                            avg_delay = 0
                        else:
                            avg_delay = d.min_delay // d.num_delay
                        duration = d.duration // d.num_flights
                        f.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(k, j, m, n, o.strip(),
                                                                            avg_delay,
                                                                            duration,
                                                                            d.num_flights,
                                                                            d.num_delay,
                                                                            d.num_cancelled_diverted,
                                                                            d.score))
    f.close()
    return

def get_scaled_delay(avg_min_delay):
        """ Scaled the avgerage minute delay to a range between 0 and 1 """

        if avg_min_delay < DELAY_THRESHOLD:
            avg_delay = 0
        elif avg_min_delay < 45:
            avg_delay = .2
        elif avg_min_delay < 60:
            avg_delay = .4
        elif avg_min_delay < 90:
            avg_delay = .6
        elif avg_min_delay < 120:
            avg_delay = .8
        else:
            avg_delay = 1
        return avg_delay    

def calculate_flight_score():
    """ Evaluate each flight record and calculate a Flight Score which will be used
    in the FlightScore application.  This calculation is based on a weighted 
    combination of 1) the percentage of flights delayed and 2) the average minutes
    delayed.  This calculation is then scaled linearly between 0-1 and stored in the
    raw_flight_data data structure."""

    min_flight_score = 1000
    max_flight_score = 0

    # first loop through data to calculate the avg min delay and the pct flights
    # delayed, combine these to a flight score and keep track of the MAX(flightscore)
    # and MIN(flightscore) so we can normalize data between 0-1
    for k in raw_flight_data:
        for j in raw_flight_data[k]:
            for m in raw_flight_data[k][j]:
                for n in raw_flight_data[k][j][m]:
                    for o in raw_flight_data[k][j][m][n]:
                        flight_data = raw_flight_data[k][j][m][n][o]

                        # Calculate FlightScore as a weighted combination of:
                        # 1. The percentage of flights delayed
                        # 2. The average minutes delayed for all delayed flights
                        # 3. The percentage of flights cancelled or diverted
                        if flight_data.num_delay == 0:
                            # no flight delays, so don't add that in the calculation
                            flight_score = (WEIGHT_PCT_FLIGHTS_DELAYED * flight_data.num_delay / float(flight_data.num_flights)) + \
                                           (WEIGHT_CANCEL_DIVERT * flight_data.num_cancelled_diverted / float(flight_data.num_flights))
                        else:
                            avg_delay = get_scaled_delay(flight_data.min_delay / float(flight_data.num_delay))
                            flight_score = (WEIGHT_AVG_MIN_DELAYED * avg_delay) + \
                                           (WEIGHT_PCT_FLIGHTS_DELAYED * flight_data.num_delay / float(flight_data.num_flights)) + \
                                           (WEIGHT_CANCEL_DIVERT * flight_data.num_cancelled_diverted / float(flight_data.num_flights))

                        raw_flight_data[k][j][m][n][o].score = flight_score
                        # Track and update new min/max flight scores for normalization below
                        if flight_score > max_flight_score:
                            max_flight_score = flight_score
                        elif flight_score < min_flight_score:
                            min_flight_score = flight_score
    
    print "min: ", min_flight_score
    print "max: ", max_flight_score

    # Normalize Flight Score between 0-1
    for k in raw_flight_data:
        for j in raw_flight_data[k]:
            for m in raw_flight_data[k][j]:
                for n in raw_flight_data[k][j][m]:
                    for o in raw_flight_data[k][j][m][n]:
                        flight_data = raw_flight_data[k][j][m][n][o]
                        new_score = (flight_data.score - min_flight_score) / (max_flight_score - min_flight_score)
                        raw_flight_data[k][j][m][n][o].score = new_score
                        
    return

    

raw_flight_data = makehash()
load_flight_data()
calculate_flight_score()
write_flight_data_to_file() 
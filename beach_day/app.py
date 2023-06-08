# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, text, select
import datetime as dt


from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///beach_day\Resources\hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()


# reflect the tables
Base.prepare(autoload_with=engine)
## print(Base.classes.keys())

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station


## print(Measurements)
## print(Stations)

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start_date><br/>"
        f"/api/v1.0/start_date/end_date/<start_date>/<end_date><br/>"
    )

### Precipitation page:
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precip():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query the session for rainfall from "climate_starter.ipynb" >= 2016-08-23
    results = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= '2016-08-23').all()
    session.close()
    precip_dict = dict(results)
    return jsonify(precip_dict)


### Stations page:
# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def station():
    # Create session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Stations.name).all()
    session.close()

    station_names = list(np.ravel(results))
    print(station_names)

    return jsonify(station_names)


### tobs page:
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurements.date, Measurements.tobs).\
    filter(Measurements.station == 'USC00519281').\
    filter(Measurements.date >= '2016-08-18').all()
    tobs_data = list(np.ravel(results))
    return jsonify(tobs_data)


@app.route("/api/v1.0/start_date/<start_date>")
def date_range(start_date):
    """Returns temperature data for all stations depending on input start date.
    Throws error if input is outside of date range.
    Input date must be in string format of YYYY-%m-%d (example: 2017-03-25)"""

    #first create a dictionary of Measurements table rows and append to a list:
        # source [6]
    session = Session(engine)
    results = session.query(Measurements.id, Measurements.station, Measurements.date, Measurements.prcp, Measurements.tobs).all()

    measurement_data = []
    for id, station, date, prcp, tobs in results:
        measurement_dict = {}
        measurement_dict["id"] = id
        measurement_dict["station"] = station
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        measurement_dict["tobs"] = tobs
        measurement_data.append(measurement_dict)
    # print(measurement_data)

    # now filter the measurement data list based on start date value
        # source [7]

    user_entry = str(start_date)
    start_date_list = [d for d in measurement_data if d['date'] >= user_entry]

# Check if start date is present in list:
    if not any(v['date'] == user_entry for v in measurement_data):
        return 'Error: No data for that date value could be found. Did you format your date as example: "2017-03-25"?<br>\
            The oldest date is 2010-01-01 and the most recent date available is 2017-08-23'
    
    else:
        temps = [t['tobs'] for t in start_date_list]
        min_temp = str(min(temps))
        max_temp = str(max(temps))
        avg_temp = str(round(sum(temps)/len(temps)))
        temps_list = [min_temp, avg_temp, max_temp]
        return jsonify(temps_list)
        ### unused text version:
        # f'The minimum temperature on {user_entry} was: {min_temp} fahrenheit.<br>\
        # The average temperature on that day was: {avg_temp} fahrenheit.<br>\
        # The maximum temperature was: {max_temp} fahrenheit.<br><br>\
        # {temps_list}'


@app.route("/api/v1.0/start_date/end_date/<start_date>/<end_date>")
def date_bracket(start_date, end_date):
    """Returns temperature data for all stations depending on input start and dates.
    Throws error if input start or end date is outside of date range.
    Input dates must be in string format of YYYY-%m-%d (example: 2017-03-25)"""

    #first create a dictionary of Measurements table rows and append to a list:
        # source [6]
    session = Session(engine)
    results = session.query(Measurements.id, Measurements.station, Measurements.date, Measurements.prcp, Measurements.tobs).all()

    measurement_data = []
    for id, station, date, prcp, tobs in results:
        measurement_dict = {}
        measurement_dict["id"] = id
        measurement_dict["station"] = station
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        measurement_dict["tobs"] = tobs
        measurement_data.append(measurement_dict)
    # print(measurement_data)

    # now filter the measurement data list based on start date value
        # source [7]

    user_start = str(start_date)
    user_end = str(end_date)
    date_list = [d for d in measurement_data if d['date'] >= user_start and d['date'] <= user_end]
    
# Check if both start and end dates are within valid range:
    if user_start < min(v['date'] for v in measurement_data) or user_end > max(e['date'] for e in measurement_data):
        return f'Error: No data for those date values could be found.\
                Did you format your start and end dates as example: "2017-03-25"?\
                The oldest date is {min(v["date"] for v in measurement_data)} and the most recent date available is {max(e["date"] for e in measurement_data)}'
    
    else:
        temps = [t['tobs'] for t in date_list]
        min_temp = str(min(temps))
        max_temp = str(max(temps))
        avg_temp = str(round(sum(temps)/len(temps)))
        temps_list = [min_temp, avg_temp, max_temp]
        return jsonify(temps_list)

# make sure session is closed:
session.close()

# Run the app on local machine:
if __name__ == "__main__":
    app.run(debug=True)
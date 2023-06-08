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
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
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
    precip_dict = dict(results)
    return jsonify(precip_dict)

    session.close()

    # Convert list of tuples into normal list
    precip_dates = list(np.ravel(results))

    return jsonify(all_names)




session.close()
if __name__ == "__main__":
    app.run(debug=True)

# I need to figure out how to do the SQL statement within the .query method...
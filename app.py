import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# link to the database, echo = True to see queries on command line, line of communication
engine = create_engine("sqlite:///hawaii03.sqlite" , echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables - loads table metadata
Base.prepare(engine, reflect=True)

# print to see what's in sqlite datebase
# print(Base.classes.keys())

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>stations</a></br>"
        f"<a href='/api/v1.0/tobs'>temperature</a>")
        # f"<a href='/api/v1.0/<start>temperature</a>"

@app.route("/api/v1.0/precipitation")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    print(Measurement.__table__.columns.keys())

    # Query all passengers
    results = session.query(Measurement.date, func.sum(Measurement.prcp)).filter(Measurement.date >= '2016-08-23').group_by(Measurement.date).all()

    session.close()
   
    # Create a dictionary from the row data and append to a list of data
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to the DB
    session = Session(engine)

    # Query all stations from the dataset
    results = session.query(Station.station).all()

    session.close()
    
    print(results)

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to the DB
    session = Session(engine)

    # Query all temp data for most active station from last year of data
    results = session.query(Measurement.station,Measurement.date,Measurement.prcp).filter(Measurement.date >= '2016-08-23').filter(Measurement.station == "USC00519281").all()

    session.close()

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
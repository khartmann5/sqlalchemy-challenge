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
        f"<a href='/api/v1.0/precipitation'>Precipitation data from last year of data</a><br/>"
        f"<a href='/api/v1.0/stations'>List of Stations</a></br>"
        f"<a href='/api/v1.0/stationinfo'>Station information</a></br>"
        f"<a href='/api/v1.0/tobs'>Temperature for most active station from last year of data</a></br>"
        f"<a href='/api/v1.0/date/2015-05-01'>Temperature data starting at May 1 2015</a></br>"
        f"<a href='/api/v1.0/date/2012-01-01/2015-12-31'>Temperature data from start to end dates</a>"
        )   

@app.route("/api/v1.0/precipitation")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    print(Measurement.__table__.columns.keys())

    # Query all passengers
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(date[0],'%Y-%m-%d')
    query_date = recent_date - dt.timedelta(days=366)
    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= query_date).all()

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
    sel = [Station.name]
    results = session.query(*sel).all()

    session.close()

    # Convert list of tuples into normal list
    station_results = list(np.ravel(results))

    return jsonify(station_results)

@app.route("/api/v1.0/stationinfo")
def stationinfo():
    # Create session from Python to the DB
    session = Session(engine)

    # Query all stations from the dataset
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    results = session.query(*sel).all()

    session.close()
    
    print(results)

    # Create a dictionary from the row of data and append to a list
    stations = []
    for station,name,latitude,longitude,elevation in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_dict["Elevation"] = elevation
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to the DB
    session = Session(engine)

    # Query all temp data for most active station from last year of data
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(date[0],'%Y-%m-%d')
    query_date = recent_date - dt.timedelta(days=366)
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    sel = [Measurement.station,Measurement.date,Measurement.tobs]
    results = session.query(*sel).filter(Measurement.date >= query_date).\
        filter(Measurement.station == most_active_station[0]).all()

    session.close()

    # Create a dictionary from the row of data and append to a list
    active_station_temp = []
    for station,date,tobs in results:
        active_station_dict = {}
        active_station_dict["Station"] = station
        active_station_dict["Date"] = date
        active_station_dict["Temp"] = tobs
        active_station_temp.append(active_station_dict)

    return jsonify(active_station_temp)

@app.route("/api/v1.0/date/<value>")
def startdate(value):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= value).all()

    session.close()
   
    # Create a dictionary from the row data and append to a list of data
    start_temp = []
    for min,max,avg in results:
        start_temp_dict = {}
        start_temp_dict["min"] = min
        start_temp_dict["max"] = max
        start_temp_dict["avg"] = avg
        start_temp.append(start_temp_dict)

    return jsonify(start_temp)

@app.route("/api/v1.0/date/<start>/<stop>")
def daterange(start,stop):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()

    session.close()
   
    # Create a dictionary from the row data and append to a list of data
    start_stop_temp = []
    for min,max,avg in results:
        start_stop_temp_dict = {}
        start_stop_temp_dict["min"] = min
        start_stop_temp_dict["max"] = max
        start_stop_temp_dict["avg"] = avg
        start_stop_temp.append(start_stop_temp_dict)

    return jsonify(start_stop_temp)

if __name__ == '__main__':
    app.run(debug=True)
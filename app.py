######################################################################
#  A Flask API based on the queries developed in climate_starter.ipynb
######################################################################

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
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
def home():
    """List all routes that are available"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-07-30<br/>"
        f"/api/v1.0/2017-07-29/2017-08-06"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary 
    using date as the key and prcp as the value and
    return the JSON representation of your dictionary.
    """
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    # A query to retrieve the last 12 months of precipitation data
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
   
    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = most_recent_date - dt.timedelta(days=365)
   
    # Perform a query to retrieve the date and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Empty dictionary 
    precipitation_dict = {}
    
    # Loop to add date as keys and prcp as values
    for row in results:
        precipitation_dict[row.date] = row.prcp
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve the stations
    results =  session.query(Station.station).group_by(Station.station).all()

    session.close()
    
    # Unpack the 'station' from results and save into a list
    stations_list = [result[0] for result in results]
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the 
    most active station for the last year of data and Return 
    a JSON list of temperature observations (TOBS) for the previous year."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # A query to retrieve the last 12 months of tobs data
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
   
    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = most_recent_date - dt.timedelta(days=365)
   
    # Perform a query to retrieve the most active station
    station_count = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station = station_count[0][0]

    # Perform a query to retrieve the tobs
    # results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()
    results = session.query(Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Unpack the 'tobs' from results and save into a list
    temp_list = [result[0] for result in results]
    
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def temp_data_start(start):
    """Calculate TMIN, TAVG, and TMAX for all dates 
    greater than and equal to the start date and return a 
    JSON list of the minimum temperature, the average temperature,
    and the max temperature for a given start date."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve the tobs greater than and equal to the start date
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    session.close()

    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def temp_data_start_end(start, end):
    """Calculate the TMIN, TAVG, and TMAX for dates 
    between the start and end date inclusive and return
    a JSON list of the minimum temperature, the average
    temperature,and the max temperature for a given start-end date range."""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve the tobs for dates between the start and end date inclusively
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    session.close()
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)

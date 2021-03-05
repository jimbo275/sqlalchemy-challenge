# Import everything you used in the starter_climate_analysis.ipynb file, along with Flask modules
from flask import Flask, jsonify
import sqlalchemy
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime 
import datetime as dt

#################################################
# Database Setup
#################################################
# Create an engine
engine = create_engine("sqlite:///data/hawaii.sqlite")
# reflect an existing database into a new model with automap_base() and Base.prepare()
Base = automap_base()

# reflect the tables with Base.prepare(), passing in the engine and reflect=True
Base.prepare(engine, reflect=True)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Instantiate a Session and bind it to the engine
session = Session(bind=engine)

# Find the last date in the database
last_date = (session
                .query(measurement.date)                      
                .order_by(measurement.date.desc())
                .first())

# Calculate the date 1 year ago from the last data point in the database
my_date = datetime.strptime(last_date[0], "%Y-%m-%d")
session.close()
#################################################
# Flask Setup
#################################################
# Instantiate a Flask object at __name__, and save it to a variable called app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Set the app.route() decorator for the base '/'
@app.route('/')
# define a welcome() function that returns a multiline string message to anyone who visits the route
def welcome():
    """List all available api routes."""
    return (
            f"Welcome to James' climate analysis page!<br/>"
            f"Available routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/temp"
    )
# Set the app.route() decorator for the "/api/v1.0/precipitation" route
@app.route("/api/v1.0/precipitation")


# define a precipitation() function that returns jsonified precipitation data from the database
def precipitation():
# In the function (logic should be the same from the starter_climate_analysis.ipynb notebook):
    """Return precipitation from 1 year ago"""
    session = Session(bind=engine)
    # Calculate the date 1 year ago from last date in database
    year_ago = dt.date(my_date.year, my_date.month, my_date.day) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year

    prep_results = (session
                    .query(measurement.date, measurement.prcp, measurement.station)                      
                    .filter(measurement.date >= year_ago)
                    .all())

    # Create a dictionary to store the date: prcp pairs. 
    prcp_pairs = []
    # Hint: check out a dictionary comprehension, which is similar to a list comprehension but allows you to create dictionaries
    for date, prcp, station in prep_results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_dict["station"] = station
        prcp_pairs.append(prcp_dict)
    
    session.close()
    # Return the jsonify() representation of the dictionary
    return jsonify(prcp_pairs)
               
# Set the app.route() decorator for the "/api/v1.0/stations" route
@app.route("/api/v1.0/stations")
# define a stations() function that returns jsonified station data from the database
def stations():
    """Return a list of stations"""
    session = Session(bind=engine)
    year_ago = dt.date(my_date.year, my_date.month, my_date.day) - dt.timedelta(days=365)
# In the function (logic should be the same from the starter_climate_analysis.ipynb notebook):
    # Query for the list of stations
    stat_results = (session
                     .query(measurement.date, measurement.prcp, measurement.station)                      
                     .filter(measurement.date >= year_ago)
                     .all())
    # Unravel results into a 1D array and convert to a list
    # Hint: checkout the np.ravel() function to make it easier to convert to a list
    stat_names = list(np.ravel(stat_results))
    session.close()
    # Return the jsonify() representation of the list
    return jsonify(stat_names)

# Set the app.route() decorator for the "/api/v1.0/tobs" route
@app.route("/api/v1.0/tobs")
# define a temp_monthly() function that returns jsonified temperature observations (tobs) data from the database
def temp_monthly():
    """Returns temperature obs from the database"""
    session = Session(bind=engine)
    year_ago = dt.date(my_date.year, my_date.month, my_date.day) - dt.timedelta(days=365)
# In the function (logic should be the same from the starter_climate_analysis.ipynb notebook):
    # Calculate the date 1 year ago from last date in database
    year_ago = dt.date(my_date.year, my_date.month, my_date.day) - dt.timedelta(days=365)
    # Query the primary station for all tobs from the last year
    temp_results = (session
                     .query(measurement.date, measurement.station, measurement.tobs)                      
                     .filter(measurement.date >= year_ago)
                     .all()) 
    # Unravel results into a 1D array and convert to a list
    # Hint: checkout the np.ravel() function to make it easier to convert to a list
    temp = list(np.ravel(temp_results))    
    # Return the jsonify() representation of the list
    session.close()
    return jsonify(temp)

# Set the app.route() decorator for the "/api/v1.0/temp/<start>" route and "/api/v1.0/temp/<start>/<end>" route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Returns temp begin and end"""
    session = Session(bind=engine)
    # If the end argument is None:
 
    if end is None:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        temp_date_results = (session.query(func.min(measurement.tobs), 
                                    func.avg(measurement.tobs), 
                                    func.max(measurement.tobs))
                                    .filter(measurement.date >= start)
                                    .all())
 
        # Unravel results into a 1D array and convert to a list
        # Hint: checkout the np.ravel() function to make it easier to convert to a list
        temp_date = list(np.ravel(temp_date_results))  
        # Return the jsonify() representation of the list
        return jsonify(temp_date)
    else:
        # calculate TMIN, TAVG, TMAX with both start and stop
        temp_date_results = (session.query(func.min(measurement.tobs), 
                                    func.avg(measurement.tobs), 
                                    func.max(measurement.tobs))
                                    .filter(measurement.date >= start)
                                    .filter(measurement.date <= end)
                                    .all())
        # Unravel results into a 1D array and convert to a list
        # Hint: checkout the np.ravel() function to make it easier to convert to a list
        temp_date = list(np.ravel(temp_date_results))  
        # Return the jsonify() representation of the list
        session.close()
        return jsonify(temp_date)

if __name__ == '__main__':
    app.run()

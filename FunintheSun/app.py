# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

#set api var
api = "/api/v1.0/"

# Flask Routes
# / , api/v1.0/precipitation , /api/v1.0/stations , /api/v1.0/tobs , /api/v1.0/<start> and /api/v1.0/<start>/<end>
#/ route
@app.route("/")
def welcome():
    """List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"{api}precipitation<br/>"
        f"{api}stations<br/>"
        f"{api}tobs<br/>"
        f"</br>"
        f"You can also use the API to return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range using the below format:</br>"
        f"</br>"
        f"{api}<start date> (YYYY-MM-DD Format)<br/>"
        f"{api}<start date>/<end date> (YYYY-MM-DD Format)<br/>"
    )

#/precip route
@app.route(f"{api}precipitation")
def precipitation():

    # Find the most recent date in the data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()

    # Calculate the date one year ago from the last date in the dataset
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Perform the query to retrieve the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date >= one_year_ago) \
        .filter(Measurement.date <= most_recent_date) \
        .all()

    # Create a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    # Close the session
    session.close()

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

# /stations route
@app.route(f"{api}stations")
def stations():


    # Query all stations from the dataset
    station_data = session.query(Station.station).all()

    # Convert the query results to a list
    station_list = [station[0] for station in station_data]

    # Close the session
    session.close()

    # Return the JSON representation of the list
    return jsonify(station_list)

#tobs route
@app.route(f"{api}tobs")
def tobs():

    # Query the dates and temperature observations for the most active station for the previous year
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()

    # Calculate the date one year ago from the last date in the dataset
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    prev_year_data = session.query(Measurement.date, Measurement.tobs) \
        .filter(Measurement.station == 'USC00519281') \
        .filter(Measurement.date >= one_year_ago) \
        .filter(Measurement.date <= most_recent_date) \
        .all()

    # Create a dictionary with date as the key and tobs as the value
    tobs_dict = {date: tobs for date, tobs in prev_year_data}

    # Close the session
    session.close()

    # Return the JSON representation of the dictionary
    return jsonify(tobs_dict)

#<start> route
@app.route(f"{api}<start>")
def calc_temps_start(start):
    
    # Query the TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .all()

    # Create a list of dictionaries with the calculated values
    temps_list = []
    for result in results:
        temps = {
            'TMIN': result[0],
            'TAVG': result[1],
            'TMAX': result[2]
        }
        temps_list.append(temps)

    # Close the session
    session.close()

    # Return the JSON representation of the list
    return jsonify(temps_list)

#<combo> route
@app.route(f"{api}<start>/<end>")
def calc_temps_start_end(start, end):

    # Query the TMIN, TAVG, and TMAX for dates from the start date to the end date, inclusive
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end)\
        .all()

    #end session
    session.close()

    # Create a list of dictionaries with the calculated values
    temps_list = []
    for result in results:
        temps = {
            'TMIN': result[0],
            'TAVG': result[1],
            'TMAX': result[2]
        }
        temps_list.append(temps)

    # Return the JSON representation of the list
    return jsonify(temps_list)

if __name__ == '__main__':
    app.run()
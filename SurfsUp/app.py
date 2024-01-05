# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///./Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Create our session (link) from Python to the DB
app = Flask(__name__)



#################################################
# Flask Setup
#################################################
@app.route("/")
def home():
    print("In & Out of Home section.")
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<br/>"
        f"/api/v1.0/start/end"
    )



#################################################
# Flask Routes
#################################################

@app.route('/api/v1.0/precipitation/')
def precipitation():
    #link session from python to db
    session = Session(engine)

    """Return a list of all precipitation and date"""
    # Query all precipitation and date
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    #Convert list of tuples into dict
    all_prcp=[]
    for date,prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route('/api/v1.0/stations/')
def stations():
    session = Session(engine)
    query = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    queryresult = session.query(*query).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

# Return a JSON-list of Temperature Observations from the dataset.
@app.route('/api/v1.0/tobs/')
def tobs():
    #link session from python to db 
    session = Session(engine)

    #find date 1 year ago from last data point in the database
    most_recent = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = most_recent[0]
    most_recent_date = dt.datetime.strptime(str(most_recent), '%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    one_year = most_recent_date - dt.timedelta(days=365)
    #query to retrieve the data and precipitation scores
    results=session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.desc()).\
            filter(Measurement.date>=one_year).all()
    session.close()
    alltemps=[]
    for tobs,date in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        alltemps.append(tobs_dict)
    return jsonify(alltemps)

@app.route('/api/v1.0/<start>')
def calc_temps_sd(start):
    #link session from python to db
    session = Session(engine)
    #TMIN, TAVG, and TMAX for a list of dates.
    
    #Args:
        #start_date (string): A date string in the format %Y-%m-%d
        
    #Returns:
    #      TMIN, TAVE, and TMAX
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    tempobs={}
    tempobs["Min_Temp"]=results[0][0]
    tempobs["avg_Temp"]=results[0][1]
    tempobs["max_Temp"]=results[0][2]
    return jsonify(tempobs)

@app.route('/api/v1.0/<start>/<end>')
def calc_temps(start, end):
    #link session from python to db
    session = Session(engine)
    #TMIN, TAVG, and TMAX for a list of dates.
    
    #Args:
    #    start_date (string): A date string in the format %Y-%m-%d
    #    end_date (string): A date string in the format %Y-%m-%d
        
    #Returns:
    #    TMIN, TAVE, and TMAX

    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    tempobs={}
    tempobs["Min_Temp"]=results[0][0]
    tempobs["avg_Temp"]=results[0][1]
    tempobs["max_Temp"]=results[0][2]
    return jsonify(tempobs)

if __name__ == "__main__":
    app.run(debug=True)
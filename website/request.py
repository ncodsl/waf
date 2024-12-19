import datetime  # to set the time
import sqlite3 
import pandas as pd
import json
import os  # to open any path
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class Request(object):  
    def __init__(self, id=None, timestamp=None, origin=None, host=None, request=None, body=None, method=None, headers=None, threats=None, geo_location={}, threat_state={}):
        self.id = id
        self.timestamp = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Default to current timestamp if None
        self.origin = origin
        self.host = host
        self.request = request
        self.body = body
        self.method = method
        self.headers = headers
        self.threats = threats
        self.geo_location = geo_location
        self.threat_state = threat_state

    def to_json(self):
        output = {}

        if self.request:
            output['request'] = self.request

        if self.body:
            output['body'] = self.body

        if self.headers:
            for header, value in self.headers.items():
                output[header] = value

        return json.dumps(output)


class DBController(object):
    """
    Used to save the parsed Request into the database.
    """
    def __init__(self):
        self.connect_to_mongodb = MongoClient(os.getenv("MONGODB_URI"))  # Connect to database
        self.db = self.connect_to_mongodb["Web_Application_Firewall"]
        self.collection_logs = self.db["logs"]
        self.collection_threats = self.db["threats"]
        self.collection_header = self.db["full_header"]
        self.collection_location = self.db["geo_location"]
        self.collection_stat = self.db["stat"]
        self.collection_threat_location = self.db['threat_location']

    def save(self, req: Request):
        try:
            # Get the highest _id value in the collection and increment it
            highest_id = self.collection_logs.find_one(sort=[('_id', -1)])['_id']
        except (TypeError, KeyError):
            highest_id = 0  # If no records exist, start with id 1

        req.id = highest_id + 1

        # Save basic request information to logs collection
        document = {
            '_id': req.id,
            "timestamp": req.timestamp,
            "origin": req.origin,
            "host": req.host,
            "method": req.method
        }
        self.collection_logs.insert_one(document)

        # Save threat data to threats collection
        for threat, location in req.threats.items():
            document_two = {
                '_id': req.id,
                "threat_type": threat,
                "location": location
            }
            self.collection_threats.insert_one(document_two)

        # Save headers data to full_header collection
        headers = {'_id': req.id}
        for key, value in req.headers.items():
            headers[key] = value
        self.collection_header.insert_one(headers)

        # Save geo-location and threat state to geo_location collection
        geo_location = {'_id': req.id, 'threat_state': req.threat_state}
        for key, value in req.geo_location.items():
            geo_location[key] = value
        self.collection_location.insert_one(geo_location)

        # Analyze threats and statistics from the threat data
        df = pd.DataFrame(list(self.collection_threats.find()))
        threat_counts = df['threat_type'].value_counts()
        total = threat_counts.sum() if len(df) > 0 else 1

        # Calculate threat percentages
        valid_count_pres = threat_counts.get('valid', 0) / total * 100
        xss_count_pres = threat_counts.get('xss', 0) / total * 100
        sql_count_pres = threat_counts.get('sqli', 0) / total * 100
        cmdi_count_pres = threat_counts.get('cmdi', 0) / total * 100
        pathTrav_count_pres = threat_counts.get('path-traversal', 0) / total * 100
        sum_att = (xss_count_pres + sql_count_pres + cmdi_count_pres + pathTrav_count_pres)

        # Calculate location statistics
        location_counts = df["location"].value_counts()
        location_total = location_counts.sum() if len(df) > 0 else 1

        Request_count = location_counts.get("Request", 0) / location_total * 100
        Body_count = location_counts.get("Body", 0) / location_total * 100
        Cookie_count = location_counts.get("Cookie", 0) / location_total * 100
        User_Agent_count = location_counts.get("User_Agent", 0) / location_total * 100
        Accept_Encoding_count = location_counts.get("Accept_Encoding", 0) / location_total * 100
        Accept_Language_count = location_counts.get("Accept_Language", 0) / location_total * 100

        # Save statistics to stat collection
        stat = {
            '_id': req.id,
            'valid': valid_count_pres,
            'xss': xss_count_pres,
            'sql': sql_count_pres,
            'cmdi': cmdi_count_pres,
            'path-traversal': pathTrav_count_pres,
            'sum_Attacks': sum_att
        }
        self.collection_stat.insert_one(stat)

        # Save threat location statistics to threat_location collection
        document_three = {
            '_id': req.id,
            "Request": Request_count,
            "Body": Body_count,
            "Cookie": Cookie_count,
            "User_Agent": User_Agent_count,
            "Accept_Encoding": Accept_Encoding_count,
            "Accept_Language": Accept_Language_count
        }
        self.collection_threat_location.insert_one(document_three)


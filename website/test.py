import requests
import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi
from typing import Dict, List, Any

load_dotenv()

class WAFDatabase:
    def __init__(self):
        try:
            # MongoDB Atlas connection
            self.client = MongoClient(
                os.getenv("MONGODB_URI"),
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=50,
                retryWrites=True,
                tls=True,
                tlsCAFile=certifi.where()
            )
            
            # Initialize database and collections
            self.db = self.client["Web_Application_Firewall"]
            self.collection_logs = self.db["logs"]
            self.collection_threats = self.db["threats"]
            self.collection_header = self.db["full_header"]
            self.collection_location = self.db["geo_location"]
            
            # Test connection
            self.client.admin.command('ping')
            print("MongoDB connection successful!")
            
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            raise

    def get_threat_statistics(self) -> Dict[str, float]:
        try:
            # Get threats data
            df = pd.DataFrame(list(self.collection_threats.find()))
            
            if df.empty:
                return {}
            
            # Calculate percentages
            counts = df['threat_type'].value_counts()
            total = counts.sum()
            
            stats = {
                'valid': (counts.get('valid', 0) / total) * 100,
                'xss': (counts.get('xss', 0) / total) * 100,
                'sql': (counts.get('sqli', 0) / total) * 100,
                'cmdi': (counts.get('cmdi', 0) / total) * 100,
                'path-traversal': (counts.get('path-traversal', 0) / total) * 100
            }
            
            return stats
            
        except Exception as e:
            print(f"Error calculating threat statistics: {e}")
            return {}

    def get_raw_counts(self) -> pd.Series:
        """Get raw threat type counts"""
        try:
            df = pd.DataFrame(list(self.collection_threats.find()))
            return df['threat_type'].value_counts()
        except Exception as e:
            print(f"Error getting threat counts: {e}")
            return pd.Series()

# Usage example
if __name__ == "__main__":
    waf_db = WAFDatabase()
    
    # Get statistics
    stats = waf_db.get_threat_statistics()
    print("\nThreat Statistics (%):")
    for threat_type, percentage in stats.items():
        print(f"{threat_type}: {percentage:.2f}%")
    
    # Get raw counts
    print("\nRaw Counts:")
    print(waf_db.get_raw_counts())
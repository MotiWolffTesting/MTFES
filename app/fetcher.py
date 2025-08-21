import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

class DataFetcher:
    """Handling data fetch from MongoDB connection"""
    def __init__(self):
        load_dotenv()
        self.connection_string = os.getenv('MONGODB_URI')                               
        self.db_name = os.getenv('DB_NAME', 'IranMalDB')
        self.client = None
        self.db = None
        
    def connect(self):
        "Connect to MongoDB Atlas"
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.admin.command('ping')
            print("Successfully conneced to MongoDB Atlas!")
            return True
        except Exception as e:
            print(f"Failed to connect to Atlas: {e}")
            return False
        
    def fetch_data(self):
        "Fetch all records from the database"
        if not self.connect():
            return pd.DataFrame()
        
        try:
            # Get all collections and fetch data
            collections = self.db.list_collection_names() # type: ignore
            all_data = []
            
            for collection_name in collections:
                collection = self.db[collection_name] # type: ignore
                documents = list(collection.find({}))
                all_data.extend(documents)
                
            # Convert to DataFrame
            df = pd.DataFrame(all_data)
            
            if not df.empty:
                # Ensure we have the required id/text fields
                if '_id' in df.columns:
                    df['id'] = df['_id'].astype(str)
                elif 'TweetID' in df.columns:
                    df['id'] = df['TweetID'].astype(str)

                # Try to determine which column contains the text
                possible_text_cols = [
                    'original_text', 'Text', 'text', 'tweet', 'tweet_text',
                    'full_text', 'content', 'message', 'body', 'description'
                ]
                source_col = next((c for c in possible_text_cols if c in df.columns), None)
                if source_col:
                    df['original_text'] = df[source_col]

                # Keep only rows with some text present
                if 'original_text' in df.columns:
                    df = df.dropna(subset=['original_text'])
                    df = df[df['original_text'].astype(str).str.strip().ne('')]
                else:
                    print("Warning: Could not find a text field in documents. Add a mapping in fetcher.")

                print(f"Successfully fetched {len(df)} records.")
            
            return df
        
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame
        finally:
            if self.client:
                self.client.close()
                
    def __del__(self):
        if self.client:
            self.client.close()
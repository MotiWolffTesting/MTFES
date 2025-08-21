from .fetcher import DataFetcher
from .processor import TextProcessor
import pandas as pd
from typing import List, Dict

class DataManager:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.processor = TextProcessor()
        self.processed_data: pd.DataFrame = pd.DataFrame()
        
    def fetch_and_process(self):
        "Fetch data from MongoDB and process it"
        print("Starting data fetch and processing...")
        
        # Fetch data
        raw_data = self.fetcher.fetch_data()
        if raw_data.empty:
            print("No data fetched from database")
            return False
        
        # Process data
        self.processed_data = self.processor.process_dataframe(raw_data)
        
        if self.processed_data.empty:
            print("Data processing failed")
            return False
        
        print("Data fetch and processing completed successfully")
        return True
    
    def get_processed_data(self) -> pd.DataFrame:
        """Return the processed data"""
        return self.processed_data
    
    def get_json_response(self) -> List[Dict[str, str]]:
        "Return data in JSON format"
        if self.processed_data.empty:
            return []
        
        # Convert to the expected format
        response_data = []
        
        for _, row in self.processed_data.iterrows():
            record = {
                "id": str(row.get('id', '')),
                "original_text": str(row.get('original_text', '')),
                "rarest_word": str(row.get('rarest_word', '')),
                "sentiment": str(row.get('sentiment', '')),
                "weapons_detected": str(row.get('weapons_detected', ''))
            }
            response_data.append(record)
        
        return response_data
    
    def refresh_data(self):
        "Refresh data by fetching and processing again"
        print("Refreshing data...")
        return self.fetch_and_process()

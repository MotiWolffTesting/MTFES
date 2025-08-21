from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from .manager import DataManager
import uvicorn
from contextlib import asynccontextmanager

# Initialize the data manager
data_manager = DataManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to initialize data on startup"""
    print("Starting up Malicious Text Feature Engineering System...")
    success = data_manager.fetch_and_process()
    if not success:
        print("Warning: Initial data fetch failed")
    yield

app = FastAPI(
    title="Malicious Text Feature Engineering System",
    description="System for processing and analyzing malicious text data from MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

app.get("/data")
async def get_data():
    "Get processed data"
    try:
        data = data_manager.get_json_response()
        if not data:
            # Try to fetch and process data
            if data_manager.fetch_and_process():
                data = data_manager.get_json_response()
                
        if not data:
            raise HTTPException(status_code=404, detail="No data available")
        
        return JSONResponse(content=data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
app.get("/refresh")
async def refresh_data():
    "Refresh data from database"
    try:
        success = data_manager.refresh_data()
        if success:
            return {"message": "Data refreshed successfully", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh data")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing data: {str(e)}")
    
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "malicious-text-system"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
import pickle
import fastapi
import pandas as pd
import uvicorn
from typing import List, Dict
from fastapi import HTTPException
from pydantic import BaseModel, validator, constr

from mangum import Mangum

# Create the FastAPI app
app = fastapi.FastAPI()

# Wrap the FastAPI app with Mangum
# This allows the app to run on AWS Lambda
handler = Mangum(app)

# Load the model at startup.
# Done outside any function so that the model is loaded when the script starts and is kept in memory.
with open('model/model.pkl', 'rb') as f:
    _model = pickle.load(f)

# Define the top 10 features used to train the model (using feature importance as suggested by DS)
# Ensure the order of columns matches the trained model.
# This is important because the model expects the features in a specific order.
top_10_features = [
    "OPERA_Latin American Wings",
    "MES_7",
    "OPERA_Grupo LATAM",
    "OPERA_Sky Airline",
    "MES_10",
    "MES_8",
    "MES_12",
    "TIPOVUELO_I",
    "OPERA_JetSmart SPA",
    "MES_4"
]

# List of valid airlines taken from the raw data.
valid_airlines = [
    'Grupo LATAM', 
    'Sky Airline', 
    'Aerolineas Argentinas', 
    'Copa Air', 
    'Latin American Wings', 
    'Avianca', 
    'JetSmart SPA', 
    'Gol Trans', 
    'American Airlines', 
    'Air Canada', 
    'Iberia', 
    'Delta Air', 
    'Air France', 
    'Aeromexico', 
    'United Airlines', 
    'Oceanair Linhas Aereas', 
    'Alitalia', 
    'K.L.M.', 
    'British Airways', 
    'Qantas Airways', 
    'Lacsa', 
    'Austral', 
    'Plus Ultra Lineas Aereas'
]

# Define request and response models
# These models are used to validate the request body and response body.

class Flight(BaseModel):
    # constr(strip_whitespace=True) for the OPERA field to apply a constraint 
    # to a string type where any leading or trailing whitespace will be automatically stripped
    OPERA: constr(strip_whitespace=True)
    TIPOVUELO: str
    MES: int

    # If the OPERA field contains an airline not in the valid_airlines list, 
    # it will raise an HTTP 400 error with message "invalid airline".
    @validator("OPERA")
    def check_airline(cls, v):
        if v not in valid_airlines:
            raise HTTPException(status_code=400, detail="Invalid airline!")
        return v

    # If the TIPOVUELO field contains a value other than "N" or "I", 
    # it will raise an HTTP 400 error with message "invalid type of flight".
    @validator("TIPOVUELO")
    def check_flight_type(cls, v):
        if v not in ["N", "I"]:
            raise HTTPException(status_code=400, detail="Invalid type of flight!")
        return v

    #If the MES field contains a value outside of 1-12, 
    # it will raise an HTTP 400 error with message "invalid month".
    @validator("MES")
    def check_month(cls, v):
        if v < 1 or v > 12:
            raise HTTPException(status_code=400, detail="Invalid month!")
        return v

class PredictionResponse(BaseModel):
    predict: List[int]

# Health check endpoint
@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

# Prediction endpoint
@app.post("/predict", status_code=200, response_model=PredictionResponse)
async def post_predict(data: Dict[str, List[Flight]]) -> dict:
    flights = data.get("flights", [])
    if not flights:
        raise HTTPException(status_code=400, detail="No flights data provided!")

    # Preprocess data
    df = pd.DataFrame([flight.dict() for flight in flights])
    # Convert OPERA and TIPOVUELO to expected format
    df = pd.get_dummies(df, columns=["OPERA", "TIPOVUELO"]).astype(int)
    # Make sure MES is one-hot encoded as well
    for i in range(1, 13):  # Months 1-12
        column_name = f"MES_{i}"
        df[column_name] = (df["MES"] == i).astype(int)
    df.drop("MES", axis=1, inplace=True)

    for feature in top_10_features:
        if feature not in df.columns:
            df[feature] = 0

    # Ensure the order of columns matches the trained model
    df = df[top_10_features]

    # Predict using model
    delay_predictions = _model.predict(df)
    return {"predict": delay_predictions.tolist()}

# For debugging purposes:
# uncomment the following lines and run `python api.py` from the command line
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
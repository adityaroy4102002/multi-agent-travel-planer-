import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv("AVIATIONSTACK_API_KEY")


def search_flights(query):
    url="https://api.aviationstack.com/v1/flights"

    params={
        "access_key":API_KEY,
        "LIMIT": 5
    }

    response=requests.get(url,params=params)

    data=response.json()

    flights=[]

    if "data" in data:

        for flight in data["data"][:5]:

            airline=flight.get("airline",{}).get("name","unknown")
            departure=flight.get("departure",{}).get("airport","unknown")
            arrival=flight.get("arrival",{}).get("airport","unknown")
            status=flight.get("flight_status","unknown")

            flights.append(f"""Airline:{airline} 
            Departure:{departure}
            arrival:{arrival}
            status:{status}""")
        return "\n".join(flights)
    
            

import os
from typing import TypedDict,Annotated
import operator
import asyncio
import psycopg
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import AnyMessage,HumanMessage,AIMessage,SystemMessage

from langchain_groq import ChatGroq

#from tools.tavily_tool import tavily_search

from mcp_client import (tavily_mcp_search,aviation_mcp_call,get_airports,get_airlines)
#from tools.flight_tool import search_flights

from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")

DATABASE_URL=os.getenv("DATABASE_URL")

class TravelState(TypedDict):
    messages:Annotated[list[AnyMessage],operator.add]
    user_query:str
    flight_results:str
    hotel_results:str
    itinerary:str
    llm_calls:int

def flight_agent(state:TravelState):
    query=state["user_query"]
    flight_data=search_flights(query)
    return {
        "flight_results":flight_data,
        "messages":[AIMessage(content=f"Flight results fetched")],
        #"llm_calls":state.get("llm_calls",0)+1
    }

def hotel_agent(state:TravelState):
    query=f"best hotels for {state["user_query"]}"
    #hotel_results=tavily_search(query)
    hotel_results=asyncio.run(
        tavily_mcp_search(query)
    )


    return {
        "hotel_results":hotel_results,
        "messages":[AIMessage(content="hotel information fetched")],
        #"llm_calls":state.get("llm_calls",0)+1

    }

def itinerary_agent(state:TravelState):
    prompt=f"""
    create a travel itinerary.
    User Query:
    {state["user_query"]}

    flight Results:
    {state["flight_results"]}

    hotel results:
    {state["hotel_results"]}"""


    response=llm.invoke([SystemMessage(content="you are an expert travel planner"),HumanMessage(content=prompt)])

    return {
        "itinerary":response.content,
        "messages":[response],
        "llm_calls":state.get("llm_calls",0)+1
    }

def final_agent(state:TravelState):
    final_prompt=f"""
    generate final travel response.

    flights:{state["flight_results"]}

    hotels:{state["hotel_results"]}

    itinerary:{state["itinerary"]}
    """
    response=llm.invoke([
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages":[response],
        "llm_calls":state.get("llm_calls",0)+1
    }

graph=StateGraph(TravelState)

graph.add_node("flight_agent",flight_agent)
graph.add_node("hotel_agent",hotel_agent)
graph.add_node("itinerary-agent",itinerary_agent)
graph.add_node("final_agent",final_agent)

graph.add_edge(START,"flight_agent")
graph.add_edge("flight_agent","hotel_agent")
graph.add_edge("hotel_agent","itinerary-agent")
graph.add_edge("itinerary-agent","final_agent")
graph.add_edge("final_agent",END)

_conn=psycopg.connect(DATABASE_URL)
_conn.autocommit = True
checkpointer=PostgresSaver(_conn)
checkpointer.setup()

app=graph.compile(checkpointer=checkpointer)

if __name__ =="__main__":
    config={
        "configurable":{
            "thread_id":"user_adi"
        }
    }

    user_input=input("enter the query")

    result=app.invoke(
        {
            "messages":[
                HumanMessage(content=user_input)
            ],
            "user_query":user_input,
            "flight_results":"",
            "hotel_results":"",
            "itinerary":"",
            "llm_calls":0

        },
        config=config
    )

    print("final")
    for message in result["messages"]:
        print(message.content)

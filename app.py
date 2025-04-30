# from flask import Flask, request, jsonify
# from supabase import create_client, Client
# from google import genai
# import os
# from dotenv import load_dotenv
# load_dotenv()

# # Initialize Supabase client
# url = os.getenv('SUPABASE_URL')
# key = os.getenv('SUPABASE_KEY')
# supabase: Client = create_client(url, key)

# # Initialize Gemini client
# client=genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# app = Flask(__name__)

# # Endpoint to handle user queries
# @app.route('/query', methods=['POST'])
# def handle_query():
#     user_query = request.json.get("query")

#     # Fetch machine data from Supabase
#     machine_data = fetch_machine_data()
#     technician_data = fetch_technicians_data()
#     # Construct the prompt for Gemini model
#     prompt = construct_prompt(user_query, machine_data,technician_data)

#     # Generate response using Gemini model
#     response = client.models.generate_content(
#         model="gemini-2.0-flash",
#         contents=prompt
#         )

#     return jsonify({"response": response.text})

# def fetch_machine_data():
#     # Fetch data from Supabase (example query)
#     machines = supabase.table('machines').select('*').execute()
  
#     return machines.data


# def fetch_technicians_data():
#     # Fetch data from Supabase (example query)
#     technicians = supabase.table('technichians').select('*').execute()
  
#     return technicians.data

# def construct_prompt(user_query, machine_data,technician_data):
#     # Construct a prompt for Gemini based on query and data
#     machine_list = "\n".join([f"{m['Machine_Name']} ({m['Status']}): {m['Last_Check']}" for m in machine_data])
#     technician_list= "\n".join([f"{m['Technician']} ({m['Status']}): {m['Type']}" for m in technician_data])
#     prompt = f"""
#     You are a maintenance assistant. Here is the machine data:

#     {machine_list}
#     Here is the technician data:
#     {technician_list}
#     User's query: "{user_query}"

#     Respond in a human-readable format based on the machine data. and in a very friendly tone.

#     Do not start with a reasoning or explanation. Just give the answer directly.
#     """
#     return prompt

# if __name__ == '__main__':
#     app.run(debug=True)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(url, key)

# Initialize Gemini client
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class QueryModel(BaseModel):
    query: str

# Endpoint to handle user queries
@app.post("/query")
async def handle_query(request: QueryModel):
    user_query = request.query

    machine_data = fetch_machine_data()
    technician_data = fetch_technicians_data()
    sensor_data = fetch_sensor_data()
    maintenance_logs = fetch_maintenance_logs()

    prompt = construct_prompt(user_query, machine_data, technician_data,sensor_data, maintenance_logs)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens = 100,
        )
    )

    return {"response": response.text}

def fetch_machine_data():
    machines = supabase.table('machines').select('*').execute()
    return machines.data

def fetch_technicians_data():
    technicians = supabase.table('technichians').select('*').execute()
    return technicians.data

#Sensor_data
def fetch_sensor_data():
    sensors = supabase.table('Sensor_data').select('*').execute()
    return sensors.data
#maintenance_logs
def fetch_maintenance_logs():
    logs = supabase.table('maintenance_log').select('*').execute()
    return logs.data

def construct_prompt(user_query, machine_data, technician_data,sensor_data, maintenance_logs):
    machine_list = "\n".join([f"{m['Machine_Name']} ({m['Status']}): {m['Last_Check']}" for m in machine_data])
    technician_list = "\n".join([f"{m['Technician']} ({m['Status']}): {m['Type']}" for m in technician_data])
    # sensor_list = "\n".join([f"{s['Machine_ID']} ({s['Temperature_C']}): {s['Last_Reading']}" for s in sensor_data])
    # maintenance_list = "\n".join([f"{l['Log_ID']} ({l['Status']}): {l['Date']}" for l in maintenance_logs])
    prompt = f"""
    You are a maintenance assistant. Here is the machine data:

    {machine_list}
    Here is the technician data:
    {technician_list}

    Here is the sensor data:
    {sensor_data}

    Here is the maintenance logs data:
    {maintenance_logs}
    User's query: "{user_query}"

    Respond in a human-readable format based on the machine data be professional.

    Do not start with a reasoning or explanation. Just give the answer directly.
    """
    return prompt
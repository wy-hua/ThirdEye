from openai import OpenAI

client = OpenAI(api_key=os.getenv("VITE_OPENAI_API_KEY"))
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import mysql.connector
from typing import Optional, List
import json

# Load OpenAI API key from .env file
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

class QueryKeyword(BaseModel):
    location: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    people_names: Optional[List[str]] = []

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="myuser",
        password="mypassword",
        database="mydatabase"
    )

def extract_entities(query: str) -> QueryKeyword:
    """ Use OpenAI's API to extract key entities from user input. """

    prompt = f"""
    Extract key information from the following query and format it in JSON:
    
    Query: "{query}"

    JSON Schema:
    {{
        "location": "City or place name if mentioned, otherwise null",
        "from_date": "Start date if present, otherwise null (ISO 8601 format YYYY-MM-DD)",
        "to_date": "End date if present, otherwise null (ISO 8601 format YYYY-MM-DD)",
        "people_names": ["List of people's names mentioned"]
    }}

    JSON Output:
    """

    response = client.chat.completions.create(model="gpt-4",
    messages=[{"role": "system", "content": "You are an assistant that extracts structured information."},
              {"role": "user", "content": prompt}],
    temperature=0)

    extracted_data = json.loads(response.choices[0].message.content)
    return QueryKeyword(**extracted_data)


def search_images(location: Optional[str], from_date: Optional[datetime], to_date: Optional[datetime], people_names: Optional[List[str]]):
    """ Search images in MySQL database based on extracted keywords. """

    conditions = []
    params = []

    query = "SELECT id, shot_at_when, shot_at_where, people_involved, image_description FROM images WHERE 1=1"

    if location:
        conditions.append("shot_at_where LIKE %s")
        params.append(f"%{location}%")

    if from_date:
        conditions.append("shot_at_when >= %s")
        params.append(from_date)

    if to_date:
        conditions.append("shot_at_when <= %s")
        params.append(to_date)

    if people_names:
        people_conditions = []
        for name in people_names:
            people_conditions.append("JSON_CONTAINS(people_involved, JSON_ARRAY(%s))")
            params.append(name)
        if people_conditions:
            conditions.append(f"({' OR '.join(people_conditions)})")

    if conditions:
        query += " AND " + " AND ".join(conditions)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "shot_at_when": row[1].isoformat(),
                "shot_at_where": row[2],
                "people_involved": eval(row[3]) if row[3] else [],
                "image_description": row[4]
            })
        return results
    finally:
        cursor.close()
        conn.close()


def generate_story(images):
    """ Generate a storytelling description using OpenAI's API """

    image_text = "\n".join([f"- {img['image_description']} (Taken on {img['shot_at_when']})" for img in images])

    prompt = f"""
    Here are some images with metadata:
    
    {image_text}
    
    Write a storytelling description that connects these images in an engaging way.
    """

    response = client.chat.completions.create(model="gpt-4",
    messages=[{"role": "system", "content": "You are a creative storyteller."},
              {"role": "user", "content": prompt}],
    temperature=0.7)

    return response.choices[0].message.content


@app.post("/album_query")
async def album_query(request: QueryRequest):
    """ Handles user queries and returns structured results and storytelling descriptions. """

    # Step 1: Extract structured query keywords
    extracted_keywords = extract_entities(request.query)

    # Step 2: Query the database
    images = search_images(
        extracted_keywords.location,
        extracted_keywords.from_date,
        extracted_keywords.to_date,
        extracted_keywords.people_names
    )

    # Step 3: Generate storytelling description
    story_description = generate_story(images)

    return {
        "query_keywords": extracted_keywords.dict(),
        "image_metadata": images,
        "story_description": story_description
    }



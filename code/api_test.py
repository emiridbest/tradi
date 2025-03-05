from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

def test_api_connection():
    """Test OpenAI API connection and available models."""
    try:
        client = OpenAI()
        models = client.models.list()
        print("Available models:", [model.id for model in models])
        return True
    except Exception as e:
        print(f"API connection error: {str(e)}")
        return False

# Add this to your main() function to test:
if test_api_connection():
    st.success("API connection successful!")
else:
    st.error("API connection failed. Please check your API key and permissions.")
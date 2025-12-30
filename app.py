# app.py - Flask Backend for Claude Resume Chatbot

# === IMPORTS ===
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
import os
import json
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === FLASK APP SETUP ===
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

print("Flask app created successfully")

# === LOAD RESUME DATA ===

def load_resume_data():
    """
    Load all CSV files and convert to JSON for Claude.
    
    This function runs ONCE when the server starts.
    The data stays in memory so it's fast to access.
    """
    
    print("Loading resume data...")
    
    try:
        def read_csv_to_dict(filepath):
            """Helper function to read CSV and convert to list of dicts"""
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        
        # Read each CSV file
        work_exp = read_csv_to_dict('data/work_experience.csv')
        achievements = read_csv_to_dict('data/achievements.csv')
        skills = read_csv_to_dict('data/skills_matrix.csv')
        projects = read_csv_to_dict('data/projects.csv')
        community = read_csv_to_dict('data/community_involvement.csv')
        education = read_csv_to_dict('data/education.csv')
        
        # Read the JSON metadata file
        with open('data/context_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        # Combine into resume context
        resume_context = {
            "candidate_info": metadata,
            "work_experience": work_exp,
            "achievements": achievements,
            "skills": skills,
            "projects": projects,
            "community_involvement": community,
            "education": education
        }
        
        print(f"✓ Loaded {len(work_exp)} work experiences")
        print(f"✓ Loaded {len(achievements)} achievements")
        print(f"✓ Loaded {len(skills)} skills")
        print(f"✓ Loaded {len(projects)} projects")
        print(f"✓ Loaded {len(community)} community activities")
        print(f"✓ Loaded {len(education)} education records")
        
        return resume_context
        
    except FileNotFoundError as e:
        print(f"ERROR: Could not find data files: {e}")
        print("Make sure CSV files are in the 'data/' folder")
        return None
    except Exception as e:
        print(f"ERROR loading resume data: {e}")
        return None

# Load the data when server starts
RESUME_DATA = load_resume_data()

# Check if loading was successful
if RESUME_DATA is None:
    print("WARNING: Resume data not loaded. Chatbot will not work.")
else:
    print("✅ Resume data loaded successfully!")

# === CLAUDE API SETUP ===

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

def build_system_prompt():
    """
    Build the system prompt that tells Claude how to behave.
    """
    
    # Convert resume data to nicely formatted JSON string
    resume_json = json.dumps(RESUME_DATA, indent=2)
    
    prompt = f"""You are an intelligent resume assistant for Madeline Cook. Your job is to answer recruiter questions about her qualifications, experience, and fit for roles.

RESUME DATA:
{resume_json}

INSTRUCTIONS:
1. Answer questions accurately based ONLY on the data provided above
2. When asked about likelihood/fit for skills, provide:
   - Confidence level (High/Medium/Low)
   - Supporting evidence from resume
   - Relevant projects/achievements with specific metrics
3. Be concise but thorough (3-5 sentences unless more detail is requested)
4. If data doesn't support a claim, say so honestly and explain what IS available
5. Highlight transferable skills when relevant
6. Always reference specific metrics and achievements when applicable
7. Format responses clearly with line breaks between points

TONE: Professional, confident, data-driven, helpful

EXAMPLE:
Q: "Does she have Snowflake experience?"
A: Yes, Madeline has Advanced Snowflake proficiency with 3 years of experience (2022-present). 

Key achievements include building a cost monitoring dashboard that eliminated $22K in monthly waste ($264K annualized) and reducing dashboard load times by 50% through warehouse tuning. 

She also engineered data lineage pipelines monitoring 2,000+ daily jobs across Snowflake and Tableau."""
    
    return prompt

# === API ROUTES ===

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    This is a simple route to test if the server is running.
    Visit http://localhost:5000/api/health to see if it works.
    """
    return jsonify({
        'status': 'healthy',
        'data_loaded': RESUME_DATA is not None,
        'api_key_set': os.environ.get("ANTHROPIC_API_KEY") is not None
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint.
    
    This is where the magic happens:
    1. Receives question from frontend
    2. Sends to Claude API
    3. Returns answer to frontend
    """
    
    try:
        # Get the JSON data from the request
        data = request.json
        
        # Extract the question
        question = data.get('question', '').strip()
        
        # Validate question exists
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Check if resume data is loaded
        if not RESUME_DATA:
            return jsonify({'error': 'Resume data not loaded'}), 500
        
        print(f"\n=== New Question ===")
        print(f"Q: {question}")
        
        # Call Claude API
        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # Latest Claude model
            max_tokens=1000,                   # Max length of response
            system=build_system_prompt(),      # Instructions for Claude
            messages=[
                {"role": "user", "content": question}
            ]
        )
        
        # Extract the text response
        response_text = message.content[0].text
        
        print(f"A: {response_text[:100]}...")  # Print first 100 chars
        print(f"Tokens used: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
        
        # Return response to frontend as JSON
        return jsonify({
            'answer': response_text,
            'question': question,
            'usage': {
                'input_tokens': message.usage.input_tokens,
                'output_tokens': message.usage.output_tokens
            }
        })
    
    except anthropic.APIError as e:
        # Claude API error (bad key, rate limit, etc.)
        print(f"Claude API error: {e}")
        return jsonify({'error': f'Claude API error: {str(e)}'}), 500
    
    except Exception as e:
        # Any other error
        print(f"Server error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/')
def serve_chatbot():
    """
    Serve the chatbot HTML file.
    
    When someone visits http://localhost:5000/
    they get the chatbot interface.
    """
    return send_from_directory('static', 'chatbot.html')

# === START SERVER ===

if __name__ == '__main__':
    # Check if API key is set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found!")
        print("Please add it to your .env file")
        print("\nExample .env file:")
        print("ANTHROPIC_API_KEY=sk-ant-your-key-here")
        exit(1)
    
    # Check if resume data loaded
    if not RESUME_DATA:
        print("\n❌ ERROR: Resume data not loaded!")
        print("Please check your data/ folder has all CSV files")
        exit(1)
    
    print("\n" + "="*50)
    print("✅ All checks passed!")
    print("="*50)
    print("\n🚀 Starting Flask server...")
    print("Visit: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    print("API endpoint: http://localhost:5000/api/chat")
    print("\nPress CTRL+C to stop the server\n")
    
    # Start the Flask development server
    app.run(
        debug=True,        # Show detailed errors (only for development)
        host='0.0.0.0',    # Listen on all network interfaces
        port=5000          # Use port 5000
    )

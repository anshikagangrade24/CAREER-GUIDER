from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import csv
from langchain_google_genai import ChatGoogleGenerativeAI
import re
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set up the Google API key securely (preferably from environment variables)
os.environ["GOOGLE_API_KEY"] = "AIzaSyDnAQJ-AoS3jpz1n5I575vtXRUII5Yrz-k"

# Initialize the Gemini model with specified parameters for faster response
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.5,
    max_tokens=256,
    timeout=20,  # Increase the timeout to allow the model more time
    max_retries=1,
)

def formatProfile(text, choice):
    
    if choice == 'fresher':

        # Regex pattern to match each career path's details
        pattern = re.compile(
            r"(?P<index>\d+)\.\s+\*\*Career Path:\*\*\s*(?P<career_path>.+?)\s*\n"
            r"\s*-\s+\*\*Why It's a Good Fit:\*\*\s*(?P<why_fit>.+?)\s*\n"
            r"\s*-\s+\*\*Related Seminars/Courses:\*\*\s*(?P<seminars_courses>.+?)\s*\n"
            r"\s*-\s+\*\*Internship:\*\*\s*(?P<internship>.+?)\s*\n"
            r"\s*-\s+\*\*Networking:\*\*\s*(?P<networking>.+?)\s*(?:\n|$)"
        )
        # Finding all matches
        matches = pattern.findall(text)

        # Creating an array with each career path's details and a dictionary called careerOptions
        careerOptions = {}

        for match in matches:
                
            career_data = {
                "title": match[1],
                "why_fit": match[2],
                "courses": match[3],
                "internship": match[4],
                "networking": match[5]
            }
            careerOptions[match[1]] = career_data
            
        return careerOptions

    else:

        # Regex pattern to match each career path's details
        pattern = re.compile(
            r"(?P<index>\d+)\.\s+\*\*Career Path:\*\*\s*(?P<career_path>.+?)\s*\n"
            r"\s*-\s+\*\*Why It's a Good Fit:\*\*\s*(?P<why_fit>.+?)\s*\n"
            r"\s*-\s+\*\*Related Seminars/Courses:\*\*\s*(?P<seminars_courses>.+?)\s*\n"
            r"\s*-\s+\*\*Advanced Skills Development:\*\*\s*(?P<skills>.+?)\s*\n"
            r"\s*-\s+\*\*Networking:\*\*\s*(?P<networking>.+?)\s*(?:\n|$)"
        )
        # Finding all matches
        matches = pattern.findall(text)

        # Creating an array with each career path's details and a dictionary called careerOptions
        careerOptions = {}

        for match in matches:
                
            career_data = {
                "title": match[1],
                "why_fit": match[2],
                "courses": match[3],
                "skills": match[4],
                "networking": match[5]
            }
            careerOptions[match[1]] = career_data
            
        return careerOptions
    
# Endpoint to get roadmap
@app.route('/get-roadmap', methods=['POST'])
def getRoadMapData():
    data = request.json
    profile = data.get('profile')

    # Check if profile clarity is 'fresher'
    if profileClarity == 'fresher':
        prompt_text = (
            f"Create a comprehensive career roadmap for aspiring {profile}."
             "Include 2-3 lines for each section."
             "No additional text to be added except the given format."
             "Do not add any bullet point to any of the sections."
             "Each section should highlight key actions and considerations. Format strictly as follows without adding any additional text to it:"
             "Self Assessment: <Data>"
             "Hard Skills: <Data>"
             "Soft Skills: <Data>"
             "Job Search Strategy: <Data>"
             "Networking & Connections: <Data>"
             "Resume & Personal Building: <Data>"
             "Workshops & Seminars: <Data>"
             "Interview Preparations: <Data>"
        )

        messages = [
            ("system", "You are a professional career advisor."),
            ("human", prompt_text),
        ]

        aiData = llm.invoke(messages) 

        # Compile the regex pattern to capture the sections and their contents
        pattern = re.compile(
            r"(?P<section>\w[\w\s&]+):\s*(?P<content>.+?)(?=\n\w[\w\s&]+:|$)",
            re.DOTALL
        )

        roadmapFresher = {
            'title': profile
        }

        # Finding all matches
        matches = pattern.findall(aiData.content.strip())

        for match in matches:
            section_title = match[0].strip()
            section_content = match[1].strip()
            
            roadmapFresher[section_title] = section_content
        
        # Return the roadmap data
        return jsonify(roadmapFresher)

    elif profileClarity == 'experienced':

        # Needs to be changed as per experienced
        prompt_text = (
            f"Create a comprehensive career roadmap for experienced {profile}."
            "Include 2-3 lines for each section."
            "No additional text to be added except the given format."
            "Do not add any bullet points to any of the sections."
            "Each section should highlight advanced actions and considerations. Format strictly as follows without adding any additional text to it:"
            "Industry & Market Trends: <Data>"
            "Advanced Skills Development: <Data>"
            "Negotiation Skills: <Data>"
            "Job Search Strategy: <Data>"
            "Network Building: <Data>"
            "Career Advancements: <Data>"
            "Branding & Personal Marketing: <Data>"
            "Work Life Balance: <Data>"
        )


        messages = [
            ("system", "You are a professional career advisor."),
            ("human", prompt_text),
        ]

        aiData = llm.invoke(messages) 

        # Compile the regex pattern to capture the sections and their contents
        pattern = re.compile(
            r"(?P<section>\w[\w\s&]+):\s*(?P<content>.+?)(?=\n\w[\w\s&]+:|$)",
            re.DOTALL
        )

        roadmapExp = {
            'title': profile
        }

        # Finding all matches
        matches = pattern.findall(aiData.content.strip())

        for match in matches:
            section_title = match[0].strip()
            section_content = match[1].strip()
            
            roadmapExp[section_title] = section_content
        
        # Return the roadmap data
        return jsonify(roadmapExp)

    else:
        return jsonify({'error': 'Profile clarity must be either "fresher" or "experienced".'}), 400  # Return a 400 Bad Request status


# Endpoint to get career recommendations
@app.route('/get-career-recommendation', methods=['POST'])
def get_career_recommendation():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid input, JSON expected.'}), 400

    user_input = data.get('answers', {})  # Use 'answers' as expected by the frontend

    # Extract user inputs
    profile_clarity = user_input.get('profileClarity')
    profile_clarity = profile_clarity.lower()
    global profileClarity 
    profileClarity = profile_clarity
    
    # All question-answers are not being utilized properly. Need to take care of it during testing phase
    # Construct the prompt based on user input
    if profile_clarity == 'fresher':
        prompt_text = (
            "You are a career counselor guiding a fresher who is unsure about their career path. "
            "Based on the user's background, suggest 4 concise and relevant career options. For each career, provide the following information in a structured format:\n\n"
            "- Career Path: The career name (1-2 words).\n"
            "- Why It's a Good Fit: 1-2 sentences explaining why this career aligns with the user's background.\n"
            "- Related Seminars/Courses (Duration): Suggest one or two relevant courses/seminars with an estimated duration "
            "(e.g., 'Data Analysis with Python (2-3 months)').\n"
            "- Internship (Duration): Recommend the type of internships to pursue with a recommended duration (e.g., '3-6 months').\n"
            "- Networking: Suggest networking opportunities like professional meetups or LinkedIn groups to build connections in the field.\n\n"
            "User's Background:\n"
            f"1. Education: {user_input.get('educationalQualifications')}\n"
            f"2. Field of Study: {user_input.get('fieldOfStudy')}\n"
            f"3. Interests and Hobbies: {user_input.get('personalInterests')}\n"
            f"4. Skills: {user_input.get('skills')}\n"
            f"5. Work Experience: {user_input.get('workExperience')}\n"
            f"6. Current Industry Interest: {user_input.get('currentIndustry')}\n\n"
            "Please ensure the suggestions are brief, practical, and easy to follow, with realistic timelines for skill development. "
            "Use the following format without any additional text:\n\n"
            "1. Career Path:\n"
            "- Why It's a Good Fit: <Data>\n"
            "- Related Seminars/Courses: <Data>\n"
            "- Internship: <Data>\n"
            "- Networking: <Data>\n"
        )

    else:
        prompt_text = (
        "You are a career counselor advising experienced professionals who want a clear roadmap to advance or pivot in their careers. "
        "The user is an experienced professional with defined career goals. Based on the information below, suggest 4 advanced career options. "
        "For each career, keep your suggestions concise but relevant. Provide the following information for each:\n"
        "\n*Career Path*: The career name (1-2 words)."
        "\n*Why It's a Good Fit*: 1-2 sentences explaining why this career matches the user's background."
        "\n*Related Seminars/Courses (Duration)*: Provide one or two relevant seminars or courses for the career path, with an estimated duration (e.g., 'Advanced Data Science (3-6 months)')."
        "\n*Advanced Skills Development*: Suggest advanced skills to develop for this career path (e.g., 'Leadership training, advanced data analysis techniques')."
        "\n*Networking*: Suggest networking opportunities (e.g., professional meetups, LinkedIn groups) to build connections in this field.\n\n"
        f"User's Background:\n"
        f"1. Career focus: {user_input.get('careerFocus')}\n"
        f"2. Work environment: {user_input.get('workEnvironment')}\n"
        f"3. Organization type: {user_input.get('organizationType')}\n"
        f"4. Work location: {user_input.get('workLocation')}\n"
        f"5. Work experience: {user_input.get('experienceLevel')}\n"
        f"6. Desired role: {user_input.get('careerField')}\n"
        f"7. Industry interests: {user_input.get('industryInterest')}\n"
        f"8. Skills: {user_input.get('technicalSkills')}\n"
        f"9. Interests and hobbies: {user_input.get('personalInterests')}\n"
        f"10. Willingness to explore: {user_input.get('careerFieldInterest')}\n\n"
        "Make sure each suggestion is brief, practical, and relevant, including realistic timelines for skill development."
        "Use the following format without any additional text:\n\n"
        "1. Career Path:\n"
        "- Why It's a Good Fit: <Data>\n"
        "- Related Seminars/Courses: <Data>\n"
        "- Advanced Skills Development: <Data>\n"
        "- Networking: <Data>\n"
    )


    # Messages to send to the Google AI model
    messages = [
        ("system", "You are a career advisor."),
        ("human", prompt_text),
    ]

    try:
        # Invoke the model with the constructed prompt
        ai_msg = llm.invoke(messages)
        roadmap = formatProfile(ai_msg.content.strip(), profile_clarity)
       
        # Handle empty JSON later on        
        return json.dumps(roadmap, indent=4)
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Log any error to the console
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500 
    

# Endpoint to store feedback in a CSV file
@app.route('/store-feedback', methods=['POST'])
def store_feedback():
    data = request.json
    feedback_message = data.get('message')

    if not feedback_message:
        return jsonify({'error': 'Feedback message is empty.'}), 400

    try:
        with open('feedback.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([feedback_message])

        return jsonify({'success': True})

    except Exception as e:
        print(f"Error writing to CSV: {str(e)}")
        return jsonify({'error': 'Failed to store feedback.'}), 500



if __name__ == '__main__':
    app.run(debug=True)
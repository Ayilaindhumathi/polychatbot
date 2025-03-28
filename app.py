from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from system environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate database URL
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found. Check your system environment variables.")

# Connect to Supabase PostgreSQL
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()
    print("✅ Connected to Supabase PostgreSQL")
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    exit()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# List of common greetings
greetings = {
    "hi": "Hello! How can I assist you today?",
    "hello": "Hi there! What information do you need?",
    "hlo": "Hey! Ask me about polytechnic colleges, courses, or facilities.",
    "hey": "Hey! How can I help you today?",
    "good morning": "Good morning! What can I do for you?",
    "good afternoon": "Good afternoon! How can I assist you?",
    "good evening": "Good evening! Let me know what you need.",
    "how are you": "I'm just a chatbot, but I'm always ready to help!"
}

# Predefined responses including POLYCET
predefined_responses = {
    "sbtet": """📘 State Board of Technical Education and Training (SBTET), Andhra Pradesh\n
SBTET is responsible for the development of technical education in Andhra Pradesh. It oversees diploma courses, polytechnic colleges, curriculum development, and AP POLYCET admissions.\n
🔹 Official Website: [https://sbtetap.gov.in](https://sbtetap.gov.in)\n
🔹 Roles & Responsibilities:
   - Conducts AP POLYCET entrance exams for diploma admissions.
   - Frames syllabus and academic regulations for polytechnic courses.
   - Oversees diploma exams, results, and certifications.
   - Provides accreditation and affiliations to polytechnic colleges.\n
🔹 Contact Details:
   - 📍 Location: Vijayawada, Andhra Pradesh
   - 📞 Phone: +91-866-2489933
   - 📧 Email: support@sbtetap.gov.in
""",
    "polycet": """📝 **Andhra Pradesh POLYCET (AP POLYCET)**\n
AP POLYCET (Polytechnic Common Entrance Test) is a state-level entrance exam conducted by SBTET Andhra Pradesh for admission into diploma/polytechnic courses in engineering and non-engineering fields.\n
✅ **Eligibility Criteria:**\n
   - Candidates must have passed SSC/10th from a recognized board.\n
   - No age limit for appearing in the exam.\n
✅ **Exam Pattern:**\n
   - Total Questions: 120 (Maths: 60, Physics: 30, Chemistry: 30)\n
   - Duration: 2 hours\n
   - Mode: Offline (OMR-based)\n
✅ **Important Dates:**\n
   - Exam Date: April-May (Tentative)\n
   - Result Declaration: Within 10 days after the exam\n
✅ **Application Process:**\n
   - Registration on [https://polycetap.nic.in](https://polycetap.nic.in)\n
   - Application Fee: ₹400 (General), ₹250 (SC/ST)\n
✅ **Admission Process:**\n
   - After results, rank-wise counseling takes place for seat allocation in polytechnic colleges.\n
📞 **Helpline:**\n
   - SBTET Andhra Pradesh Contact: +91-866-2489933\n
   - Email: support@polycetap.nic.in
"""
}

# Chatbot API Route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_query = data.get("message", "").lower().strip()

    if not user_query:
        return jsonify({"response": "Please enter a valid query."})

    # Remove unnecessary words like "Tell me about"
    user_query = re.sub(r"(tell me about|information on|details of)", "", user_query).strip()

    # Check if the input is a greeting
    if user_query in greetings:
        return jsonify({"response": greetings[user_query]})

    # Check for predefined responses (SBTET, POLYCET, Polytechnic advantages, etc.)
    for keyword in predefined_responses:
        if keyword in user_query:
            return jsonify({"response": predefined_responses[keyword]})

    # Search colleges by name, district, or course
    try:
        cursor.execute("""
            SELECT c.Name, c.Code, c.Address, c.District, c.Email, c.Phone, 
                   ARRAY_AGG(DISTINCT co.CourseName || ' (' || co.Seats || ' seats)') AS Courses,
                   ARRAY_AGG(DISTINCT f.FacilityName) AS Facilities
            FROM Colleges c
            LEFT JOIN Courses co ON c.CollegeID = co.CollegeID
            LEFT JOIN Facilities f ON c.CollegeID = f.CollegeID
            WHERE LOWER(c.Name) LIKE %s OR LOWER(c.District) LIKE %s OR LOWER(co.CourseName) LIKE %s
            GROUP BY c.CollegeID
        """, (f"%{user_query}%", f"%{user_query}%", f"%{user_query}%"))
        
        results = cursor.fetchall()
        print(f"🔎 SQL Query Results: {results}")  # Debugging

        if not results:
            return jsonify({"response": "No matching colleges found. Try searching by district, course, or college name."})

        # Format Response for Readability
        structured_responses = []
        for row in results:
            college_name, code, address, district, email, phone, courses, facilities = row
            structured_text = (
                f"🏫 College Name: {college_name}\n"
                f"📜 Courses Offered:\n"
                + "\n".join([f"   - {course}" for course in courses]) + "\n"
                f"🏷 College Code: {code}\n"
                f"📍 Location: {address}, {district}\n"
                f"📧 Email: {email if email else 'N/A'}\n"
                f"📞 Phone: {phone if phone else 'N/A'}\n"
                f"🏢 Facilities Available:\n"
                + "\n".join([f"   - {facility}" for facility in facilities]) + "\n"
            )
            structured_responses.append(structured_text)

        return jsonify({"response": "\n\n------------------------------------------------------\n\n".join(structured_responses)})

    except Exception as e:
        print(f"❌ SQL Error: {e}")
        return jsonify({"response": "Database error. Please try again later."})

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)

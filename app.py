from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate database URL
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found. Check your .env file.")

# Connect to Supabase PostgreSQL
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()
    print("✅ Connected to Supabase PostgreSQL")
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    exit()

# Initialize Flask app
app = Flask(__name__)  # ✅ Fixed here
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

# Predefined responses
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
    "advantages of polytechnic": """🎓 Advantages of Polytechnic Compared to Other Courses\n
Polytechnic courses provide practical, industry-oriented education and offer several benefits over other traditional degree programs:\n
✅ Shorter Duration: Most diploma courses last 3 years, compared to 4-5 years for engineering degrees.\n
✅ Affordable Fees: Lower tuition costs compared to B.Tech or other professional degrees.\n
✅ Early Job Opportunities: Polytechnic graduates can enter the workforce earlier and start earning.\n
✅ Practical Learning: Focus on hands-on training and real-world applications rather than just theoretical concepts.\n
✅ Industry Demand: Skilled diploma holders in engineering, computer science, and electronics are highly sought after.\n
✅ Lateral Entry to B.Tech: Polytechnic students can directly enter the second year of B.Tech, saving time and costs.\n
✅ Government & Private Jobs: Eligible for government sector jobs (like JE, ITI, PSU) and private company placements.\n
✅ Entrepreneurial Opportunities: With practical skills, students can start their own businesses or work as freelancers.\n
Polytechnic courses are a great choice for students looking for early employment and skill-based education. 🚀
"""
}

# Chatbot API Route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_query = data.get("message", "").lower().strip()

    if not user_query:
        return jsonify({"response": "Please enter a valid query."})

    # Check if the input is a greeting
    if user_query in greetings:
        return jsonify({"response": greetings[user_query]})

    # Check for predefined responses (SBTET, Polytechnic advantages, etc.)
    for keyword in predefined_responses:
        if keyword in user_query:
            return jsonify({"response": predefined_responses[keyword]})

    # Search colleges by name, district, or course
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

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)


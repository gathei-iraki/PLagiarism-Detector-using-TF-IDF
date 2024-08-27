from flask import Flask, request, render_template_string, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Dummy data for the example. In a real application, you would use a database.
SIGN_FILE = os.path.join(os.path.dirname(__file__), 'docs', 'sign.txt')
MATOKEO_FILE_PATH = os.path.join(os.path.dirname(__file__), 'docs', 'matokeo.txt')

def save_user(username, password):
    with open(SIGN_FILE, "a") as file:
        hashed_password = generate_password_hash(password)
        file.write(f"{username}:{hashed_password}\n")

def check_user(username, password):
    # Construct the path to 'sign.txt' located in 'docs' inside the current directory
    SIGN_FILE = os.path.join(os.path.dirname(__file__), 'docs', 'sign.txt')

    try:
        with open(SIGN_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(":", 1)  # Split on the first occurrence of ':'
                if len(parts) == 2:
                    file_username, file_password_hash = parts
                    if file_username == username and check_password_hash(file_password_hash, password):
                        return True
    except FileNotFoundError:
        print(f"Error: The file '{SIGN_FILE}' does not exist.")
        return False

    return False

# Record of plagiarism checks for the admin to view. This would also typically be stored in a database.
plagiarism_records = []

# Ensure this function is defined before the Flask route that uses it
def vectorize(Text):
    return TfidfVectorizer().fit_transform(Text).toarray()

# Load the content of juma
juma_filename = "juma"
juma_file_path = os.path.join(os.path.dirname(__file__), 'docs', f"{juma_filename}.txt")

if os.path.exists(juma_file_path):
    with open(juma_file_path, "r", encoding="utf-8") as juma_file:
        juma_text = juma_file.read()
else:
    juma_text = ""

# Vectorize juma.txt
juma_text_vector = vectorize([juma_text])


# Define the welcome route as the default route(index.html)
@app.route('/')
def welcome():
    return render_template('index.html')


    
# Student Sign Up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_user(username, password):
            return 'Username already exists', 400

        save_user(username, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():

    if 'username' not in session:
        return redirect(url_for('login'))

    if session['username'] == 'admin':
        plagiarism_records = []
        try:
                with open(MATOKEO_FILE_PATH, "r") as matokeo_file:
                 for line in matokeo_file:
                    parts = line.strip().split(':', 1)  # Split on the first colon only
                    if len(parts) == 2:
                        student_username, plagiarism_percentage = parts
                        plagiarism_records.append((student_username, plagiarism_percentage))
        except FileNotFoundError:
            plagiarism_records = [("No records found", "")]
        # Render the admin view with plagiarism records
        return render_template('admindash.html', plagiarism_records=plagiarism_records)



    else:
        # Student view for uploading files
        return render_template('upload.html')
       

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_user(username, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials', 401

    return render_template('login.html')
    

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))




   


@app.route('/check_plagiarism', methods=['POST'])
def check_plagiarism():
    if 'files' not in request.files:
        return 'No files were uploaded'

    files = request.files.getlist('files')
    student_notes = [file.stream.read().decode('utf-8') for file in files]

    # If juma is not among the submitted files, include it
    if juma_text and juma_filename not in [file.filename for file in files]:
        student_notes.append(juma_text)

    # Process the notes and check for plagiarism
    vectors = vectorize(student_notes)
    s_vectors = list(zip(range(len(student_notes)), vectors))  # Use indices as file names
    plagiarism_scores = []

    for student_a, text_vector_a in s_vectors:
        new_vectors = s_vectors.copy()
        current_index = new_vectors.index((student_a, text_vector_a))
        del new_vectors[current_index]
        for student_b, text_vector_b in new_vectors:
            sim_score = cosine_similarity([text_vector_a], [text_vector_b])[0][0]
            plagiarism_scores.append(sim_score)

    # Find the maximum plagiarism score and convert it to a percentage
    if plagiarism_scores:
        max_score = max(plagiarism_scores)
        results_percentage = max_score * 100

        # Record the student username and plagiarism result in 'matokeo' text file
        with open(MATOKEO_FILE_PATH, "a") as matokeo_file:
            student_username = session.get('username', 'Unknown Student')
            matokeo_file.write(f"{student_username}: {results_percentage:.2f}%\n")

        return f"""
        <div style="text-align: center; padding: 20px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px;">
            <h2 style="color: #721c24;">Plagiarism Detected!</h2>
            <p style="font-size: 18px; color: #721c24;">
                Plagiarism has been detected in your document. The percentage of plagiarism detected is: <strong>{results_percentage:.2f}%</strong>.
            </p>
        </div>
        """
    else:
        return "No plagiarism detected."




if __name__ == '__main__':
    app.run(debug=True)
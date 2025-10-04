from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
# Change this secret key to something random and secret
app.secret_key = 'your_super_secret_key_123'

# --- Database Connection Configuration ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Use your XAMPP/MySQL password (default is often empty)
    'database': 'quizapp' # The database with users, topics, etc.
}

def get_db_connection():
    """Establishes a connection to the database."""
    conn = mysql.connector.connect(**db_config)
    return conn

# --- User Management Routes ---

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username or email already exists.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# --- Main Application Routes ---

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all available quiz topics
    cursor.execute("SELECT * FROM topics")
    topics = cursor.fetchall()

    # Calculate user's overall progress
    cursor.execute("""
                   SELECT score, total_questions
                   FROM quiz_attempts
                   WHERE user_id = %s
                   """, (user_id,))
    attempts = cursor.fetchall()

    cursor.close()
    conn.close()

    total_score = 0
    total_possible = 0
    for attempt in attempts:
        total_score += attempt['score']
        total_possible += attempt['total_questions']

    # Calculate percentage, handle division by zero if no attempts yet
    progress_percentage = 0
    if total_possible > 0:
        progress_percentage = int((total_score / total_possible) * 100)

    return render_template('dashboard.html', topics=topics, progress=progress_percentage)


@app.route('/quiz/<int:topic_id>')
def quiz(topic_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT topic_name FROM topics WHERE topic_id = %s", (topic_id,))
    topic = cursor.fetchone()

    cursor.execute("SELECT * FROM questions WHERE topic_id = %s", (topic_id,))
    questions = cursor.fetchall()

    cursor.close()
    conn.close()

    if not topic:
        return "Topic not found!", 404

    # The fix is here: Pass the python list directly.
    # The `| tojson` filter in quiz.html will handle the conversion.
    return render_template('quiz.html',
                           topic=topic,
                           questions=questions,
                           num_questions=len(questions))


@app.route('/submit/<int:topic_id>', methods=['POST'])
def submit(topic_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    responses = request.get_json()
    user_answers = responses.get('answers')
    question_ids = list(user_answers.keys())

    if not question_ids:
        return jsonify({'score': 0, 'total': 0})

    placeholders = ','.join(['%s'] * len(question_ids))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"SELECT question_id, correct_answer FROM questions WHERE question_id IN ({placeholders})"
    cursor.execute(query, tuple(question_ids))
    correct_answers_rows = cursor.fetchall()
    correct_answers = {str(row['question_id']): row['correct_answer'] for row in correct_answers_rows}

    score = 0
    for q_id, user_ans in user_answers.items():
        if q_id in correct_answers and user_ans == correct_answers[q_id]:
            score += 1

    total_questions = len(question_ids)

    # Save the quiz attempt to the database
    user_id = session['user_id']
    cursor.execute(
        "INSERT INTO quiz_attempts (user_id, topic_id, score, total_questions) VALUES (%s, %s, %s, %s)",
        (user_id, topic_id, score, total_questions)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'score': score, 'total': total_questions})


@app.route('/results')
def results():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # This SQL query joins the attempts with the topics table to get the topic name
    query = """
            SELECT t.topic_name, qa.score, qa.total_questions, qa.attempted_on
            FROM quiz_attempts qa
                     JOIN topics t ON qa.topic_id = t.topic_id
            WHERE qa.user_id = %s
            ORDER BY qa.attempted_on DESC
            """
    cursor.execute(query, (user_id,))
    attempts = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('results.html', attempts=attempts)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "quiz_secret_key"

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Varsha@28",
    database="quiz_system"
)

cursor = db.cursor()

# -------------------------------
# LOGIN PAGE
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['name']
        return render_template('subjects.html')

    return render_template('login.html')


# -------------------------------
# SUBJECT QUIZ
# -------------------------------
@app.route('/quiz/<subject>')
def quiz(subject):
    cursor.execute(
        "SELECT * FROM questions WHERE subject=%s ORDER BY RAND() LIMIT 5",
        (subject,)
    )
    quiz_questions = cursor.fetchall()

    if not quiz_questions:
        return f"<h2>No questions found for {subject}</h2>"

    # ✅ Store in session
    session['quiz_questions'] = quiz_questions
    session['subject'] = subject

    return render_template('quiz.html', questions=quiz_questions, subject=subject)


# -------------------------------
# SUBMIT QUIZ
# -------------------------------
@app.route('/submit', methods=['POST'])
def submit():
    username = session.get('username')
    quiz_questions = session.get('quiz_questions')
    subject = session.get('subject')

    score = 0

    for i, q in enumerate(quiz_questions):
        user_answer = request.form.get(f"q{i+1}")
        correct_answer = q[4]

        if user_answer == correct_answer:
            score += 1

    total = len(quiz_questions)
    percentage = (score / total) * 100
    status = "Pass ✅" if percentage >= 50 else "Fail ❌"

    # Save result
    cursor.execute(
        "INSERT INTO results (name, score, subject) VALUES (%s, %s, %s)",
        (username, score, subject)
    )
    db.commit()

    return render_template(
        "result.html",
        username=username,
        score=score,
        percentage=percentage,
        status=status,
        subject=subject
    )


# -------------------------------
# SUBJECT-WISE LEADERBOARD
# -------------------------------
@app.route('/leaderboard/<subject>')
def leaderboard(subject):
    cursor.execute(
        "SELECT * FROM results WHERE subject=%s ORDER BY score DESC",
        (subject,)
    )
    data = cursor.fetchall()

    return render_template(
        'leaderboard.html',
        data=data,
        subject=subject
    )


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
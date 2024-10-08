from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from flask_socketio import SocketIO, emit
import traceback
import io
import sys
import shelve
import random
import multiprocessing
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["500 per minute"]
)

socketio = SocketIO(app)
leaderboard_db = 'leaderboard.db'

forbidden_patterns = ["eval(", "exec(", "import os", "import sys"]

def check_even_odd(n):
    return "Even\n" if n % 2 == 0 else "Odd\n"

def print_numbers(n):
    return ''.join([f"{i}\n" for i in range(1, n + 1)])

def sum_of_first_n_numbers(n):
    return f"{sum(range(1, n + 1))}\n"

def multiplication_table(n):
    return ''.join([f"{n} x {i} = {n * i}\n" for i in range(1, 11)])

def reverse_number(n):
    return f"{int(str(n)[::-1])}\n"

def sum_of_digits(n):
    return f"{sum(int(digit) for digit in str(n))}\n"

def is_prime(n):
    if n <= 1:
        return "Not Prime\n"
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return "Not Prime\n"
    return "Prime\n"

def print_odd_numbers(n):
    return ''.join([f"{i}\n" for i in range(1, n + 1) if i % 2 != 0])

def execute_user_code(user_code, test_case):
    local_vars = {'input_value': test_case}
    user_stdout = io.StringIO()
    sys.stdout = user_stdout

    user_input = io.StringIO(str(test_case) + "\n")
    sys.stdin = user_input

    exec(user_code, {}, local_vars)

    sys.stdout = sys.__stdout__
    sys.stdin = sys.__stdin__

    return user_stdout.getvalue()

@app.route('/')
def index():
    user_id = request.cookies.get('user_id')
    username = request.cookies.get('username')
    if not user_id or not username:
        return redirect(url_for('login'))
    return render_template('index.html', username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('user_id', user_id)
        resp.set_cookie('username', username)
        return resp
    return render_template('login.html')

@app.route('/check_answer', methods=['POST'])
@limiter.limit("500 per minute")
def check_answer():
    data = request.json
    user_id = data['user_id']
    username = data['username']
    question_type = data['question_type']
    user_code = data['user_code']

    for pattern in forbidden_patterns:
        if pattern in user_code:
            return jsonify({
                'score': 0,
                'feedback': f'Your code contains a forbidden pattern: {pattern}'
            })

    test_cases = {
        'even_odd': random.sample([4, 7, 10, 15, 100, 0, -3, 23, 56, 78, 91, 12, 35, 68, 90, 102, 7, 14, 19, 21], 10),
        'print_numbers': random.sample([5, 3, 7, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90], 10),
        'sum_first_n': random.sample([5, 10, 3, 100, 50, 25, 75, 150, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300], 10),
        'multiplication_table': random.sample([3, 5, 12, 15, 7, 9, 11, 14, 17, 19, 2, 4, 6, 8, 10, 13, 16, 18, 20, 21], 10),
        'reverse_number': random.sample([123, 4567, 890, 1001, 765, 234, 987, 4321, 8765, 56789, 654321, 123456, 987654, 111111, 222222, 333333, 444444, 555555, 666666, 777777], 10),
        'sum_of_digits': random.sample([123, 4567, 890, 1001, 765, 234, 987, 4321, 8765, 56789, 654321, 123456, 987654, 111111, 222222, 333333, 444444, 555555, 666666, 777777], 10),
        'is_prime': random.sample([7, 10, 29, 1, 0, 11, 13, 17, 19, 23, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71], 10),
        'print_odd_numbers': random.sample([10, 7, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100], 10)
    }

    correct_answers = {
        'even_odd': [check_even_odd(tc) for tc in test_cases['even_odd']],
        'print_numbers': [print_numbers(tc) for tc in test_cases['print_numbers']],
        'sum_first_n': [sum_of_first_n_numbers(tc) for tc in test_cases['sum_first_n']],
        'multiplication_table': [multiplication_table(tc) for tc in test_cases['multiplication_table']],
        'reverse_number': [reverse_number(tc) for tc in test_cases['reverse_number']],
        'sum_of_digits': [sum_of_digits(tc) for tc in test_cases['sum_of_digits']],
        'is_prime': [is_prime(tc) for tc in test_cases['is_prime']],
        'print_odd_numbers': [print_odd_numbers(tc) for tc in test_cases['print_odd_numbers']]
    }

    user_answers = []
    error_message = ""

    try:
        for tc in test_cases[question_type][:5]:
            process = multiprocessing.Process(target=execute_user_code, args=(user_code, tc))
            process.start()
            process.join(5)

            if process.is_alive():
                process.terminate()
                process.join()
                return jsonify({
                    'score': 0,
                    'feedback': 'Code execution time exceeded. Please optimize your code.'
                })

            user_answers.append(execute_user_code(user_code, tc))
    except Exception as e:
        error_message = traceback.format_exc()

        return jsonify({
            'score': 0,
            'feedback': f'Error in code execution: {error_message}'
        })

    score = 0
    feedback = ""

    def normalize_output(output):
        return output.strip().lower()

    if not error_message:
        for i, (ua, ca) in enumerate(zip(user_answers, correct_answers[question_type][:5])):
            normalized_user_answer = normalize_output(ua)
            normalized_correct_answer = normalize_output(ca)
            
            if normalized_user_answer == normalized_correct_answer:
                score += 10 / len(correct_answers[question_type][:5])
            else:
                feedback += f"Incorrect for input {test_cases[question_type][i]}.\n"
                feedback += f"Expected: {ca.strip()}\n"
                feedback += f"Got: {ua.strip()}\n"
                
                if ua.strip() == ca.strip().lower():
                    feedback += "Note: Your output is correct but capitalization is wrong.\n"
                elif ua.strip().replace(" ", "") == ca.strip().replace(" ", ""):
                    feedback += "Note: Your output is correct but there are extra/missing spaces.\n"
                elif ua.strip() == ca.strip()[::-1]:
                    feedback += "Note: Your output is reversed.\n"
                else:
                    feedback += "Your output differs significantly from the expected result.\n"

        hidden_test_cases = correct_answers[question_type][5:]
        hidden_user_answers = []

        try:
            for tc in test_cases[question_type][5:]:
                hidden_user_answers.append(execute_user_code(user_code, tc))
        except Exception as e:
            error_message = traceback.format_exc()

        if not error_message:
            for i, (ua, ca) in enumerate(zip(hidden_user_answers, hidden_test_cases)):
                if normalize_output(ua) == normalize_output(ca):
                    score += 10 / len(hidden_test_cases)

    with shelve.open(leaderboard_db) as db:
        leaderboard = db.get(f'leaderboard_{question_type}', [])

        leaderboard_entry = next((entry for entry in leaderboard if entry['user_id'] == user_id), None)
        if leaderboard_entry:
            leaderboard_entry['score'] = max(leaderboard_entry['score'], score)
            leaderboard_entry['attempts'] += 1
        else:
            leaderboard.append({
                'user_id': user_id,
                'username': username,
                'score': score,
                'attempts': 1,
                'rating': 0
            })

        leaderboard.sort(key=lambda x: (-x['score'], x['attempts']))
        db[f'leaderboard_{question_type}'] = leaderboard

    socketio.emit('update_leaderboard', leaderboard[:10], namespace='/')

    return jsonify({
        'score': score,
        'feedback': feedback
    })

@app.route('/get_leaderboard/<question_type>', methods=['GET'])
def get_leaderboard(question_type):
    with shelve.open(leaderboard_db) as db:
        leaderboard = db.get(f'leaderboard_{question_type}', [])
    return jsonify(leaderboard[:10])

@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Connected'})

if __name__ == '__main__':
    socketio.run(app, debug=True)

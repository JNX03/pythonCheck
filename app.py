from flask import Flask, render_template, request, jsonify
import traceback
import io
import sys

app = Flask(__name__)

def check_even_odd(n):
    return "Even\n" if n % 2 == 0 else "Odd\n"

def print_numbers(n):
    return ''.join([f"{i}\n" for i in range(1, n + 1)])

def sum_of_first_n_numbers(n):
    return f"{sum(range(1, n + 1))}\n"

def multiplication_table(n):
    return ''.join([f"{n} x {i} = {n * i}\n" for i in range(1, 11)])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    question_type = data['question_type']
    user_code = data['user_code']

    test_cases = {
        'even_odd': [4, 7, 10, 15],
        'print_numbers': [5, 3, 7],
        'sum_first_n': [5, 10, 3],
        'multiplication_table': [3, 5]
    }

    correct_answers = {
        'even_odd': [check_even_odd(tc) for tc in test_cases['even_odd']],
        'print_numbers': [print_numbers(tc) for tc in test_cases['print_numbers']],
        'sum_first_n': [sum_of_first_n_numbers(tc) for tc in test_cases['sum_first_n']],
        'multiplication_table': [multiplication_table(tc) for tc in test_cases['multiplication_table']]
    }

    user_answers = []
    error_message = ""

    try:
        for tc in test_cases[question_type]:
            local_vars = {'input_value': tc}
            user_stdout = io.StringIO()
            sys.stdout = user_stdout
            exec(user_code, {}, local_vars)
            sys.stdout = sys.__stdout__
            user_answers.append(user_stdout.getvalue())
    except Exception as e:
        error_message = traceback.format_exc()

    score = 0
    feedback = ""

    if not error_message:
        for i, (ua, ca) in enumerate(zip(user_answers, correct_answers[question_type])):
            if ua == ca:
                score += 10 / len(correct_answers[question_type])
            else:
                feedback += f"Incorrect for input {test_cases[question_type][i]}. Expected {ca.strip()}, but got {ua.strip()}.\n"
    else:
        feedback = f"Error in code execution: {error_message}"

    return jsonify({'score': score, 'feedback': feedback})

if __name__ == '__main__':
    app.run(debug=True)

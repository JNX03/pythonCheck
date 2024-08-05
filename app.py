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

def reverse_number(n):
    reverse_num = 0
    while n > 0:
        digit = n % 10
        reverse_num = reverse_num * 10 + digit
        n = n // 10
    return f"{reverse_num}\n"

def sum_of_digits(n):
    total = 0
    while n > 0:
        digit = n % 10
        total += digit
        n = n // 10
    return f"{total}\n"

def is_prime(n):
    if n <= 1:
        return "Not Prime\n"
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return "Not Prime\n"
    return "Prime\n"

def print_odd_numbers(n):
    return ''.join([f"{i}\n" for i in range(1, n + 1) if i % 2 != 0])

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
        'multiplication_table': [3, 5],
        'reverse_number': [123, 4567],
        'sum_of_digits': [123, 4567],
        'is_prime': [7, 10],
        'print_odd_numbers': [10, 7]
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
        for tc in test_cases[question_type]:
            local_vars = {'input_value': tc}
            user_stdout = io.StringIO()
            sys.stdout = user_stdout
            
            # Simulate input() with StringIO
            user_input = io.StringIO(str(tc) + "\n")
            sys.stdin = user_input
            
            exec(user_code, {}, local_vars)
            
            # Reset stdin and stdout
            sys.stdout = sys.__stdout__
            sys.stdin = sys.__stdin__
            
            user_answers.append(user_stdout.getvalue())
    except Exception as e:
        error_message = traceback.format_exc()
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__

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

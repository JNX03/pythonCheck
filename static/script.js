document.addEventListener("DOMContentLoaded", function () {
    const socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function () {
        console.log('Connected to server');
    });

    socket.on('update_leaderboard', function (data) {
        updateLeaderboard(data);
    });

    updateQuestionDetails();
    fetchLeaderboard();
});

function updateQuestionDetails() {
    const questionType = document.getElementById('question_type').value;
    const questions = {
        'even_odd': {
            'text': 'Given an integer, determine if it is Even or Odd.',
            'example_input': '4',
            'example_output': 'Even'
        },
        'print_numbers': {
            'text': 'Print all numbers from 1 to N.',
            'example_input': '5',
            'example_output': '1\n2\n3\n4\n5'
        },
        'sum_first_n': {
            'text': 'Calculate the sum of the first N numbers.',
            'example_input': '5',
            'example_output': '15'
        },
    };

    const question = questions[questionType];
    document.getElementById('question_text').innerText = question.text;
    document.getElementById('example_input').innerHTML = `<strong>Input:</strong> ${question.example_input}`;
    document.getElementById('example_output').innerHTML = `<strong>Output:</strong> ${question.example_output}`;
    
    fetchLeaderboard(questionType);
}

function submitCode() {
    const user_id = getCookie('user_id');
    const username = getCookie('username');
    const question_type = document.getElementById('question_type').value;
    const user_code = document.getElementById('user_code').value;

    fetch('/check_answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: user_id,
            username: username,
            question_type: question_type,
            user_code: user_code,
        }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('score').innerText = data.score;
        document.getElementById('feedback').innerText = data.feedback;
    })
    .catch(error => console.error('Error:', error));
}

function fetchLeaderboard(questionType = document.getElementById('question_type').value) {
    fetch(`/get_leaderboard/${questionType}`)
        .then(response => response.json())
        .then(data => {
            updateLeaderboard(data);
        })
        .catch(error => console.error('Error:', error));
}

function updateLeaderboard(leaderboard) {
    const leaderboard_data = document.getElementById('leaderboard_data');
    leaderboard_data.innerHTML = '';
    leaderboard.forEach((entry, index) => {
        const row = `<tr>
            <td>${index + 1}</td>
            <td>${entry.username}</td>
            <td>${entry.score}</td>
            <td>${entry.attempts}</td>
        </tr>`;
        leaderboard_data.insertAdjacentHTML('beforeend', row);
    });
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

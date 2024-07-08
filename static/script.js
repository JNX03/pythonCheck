document.getElementById('exercise-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const questionType = document.getElementById('question_type').value;
    const userCode = document.getElementById('user_code').value;

    fetch('/check_answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question_type: questionType,
            user_code: userCode
        }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('score').textContent = data.score;
        document.getElementById('feedback').textContent = data.feedback;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

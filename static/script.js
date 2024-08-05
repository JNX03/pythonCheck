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
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('score').textContent = data.score !== undefined ? data.score : 'N/A';
        document.getElementById('feedback').textContent = data.feedback || 'No feedback available';
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('score').textContent = 'Error';
        document.getElementById('feedback').textContent = `An error occurred: ${error.message}`;
    });
});

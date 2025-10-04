document.addEventListener('DOMContentLoaded', () => {
    // Get all the necessary HTML elements
    const quizContainer = document.querySelector('.quiz-container');
    const questionTextEl = document.getElementById('question-text');
    const optionsAreaEl = document.getElementById('options-area');
    const nextBtn = document.getElementById('next-btn');
    const progressTextEl = document.getElementById('progress-text');

    // This checks if the 'questions' variable (created by |tojson in the HTML) exists and has items.
    if (typeof questions !== 'undefined' && questions.length > 0) {

        let currentQuestionIndex = 0;
        const userAnswers = {}; // To store user answers { questionId: selectedOption }

        function loadQuestion() {
            // Update the progress text, e.g., "Question 1 of 10"
            progressTextEl.innerText = `Question ${currentQuestionIndex + 1} of ${questions.length}`;

            // Clear out the options from the previous question
            optionsAreaEl.innerHTML = '';

            const currentQuestion = questions[currentQuestionIndex];
            questionTextEl.innerText = currentQuestion.question_text;

            const options = {
                'A': currentQuestion.option_a,
                'B': currentQuestion.option_b,
                'C': currentQuestion.option_c,
                'D': currentQuestion.option_d
            };

            // Create and display a radio button for each option
            for (const [key, value] of Object.entries(options)) {
                const label = document.createElement('label');
                label.className = 'option';
                const radio = document.createElement('input');
                radio.type = 'radio';
                radio.name = 'option';
                radio.value = key;

                label.appendChild(radio);
                label.appendChild(document.createTextNode(` ${value}`));
                optionsAreaEl.appendChild(label);
            }

            // If it's the last question, change the button text
            if (currentQuestionIndex === questions.length - 1) {
                nextBtn.innerText = 'Submit Quiz';
            }
        }

        async function submitQuiz() {
            const topicId = window.location.pathname.split('/').pop();

            const response = await fetch(`/submit/${topicId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answers: userAnswers })
            });

            const result = await response.json();

            quizContainer.innerHTML = `
                <div class="quiz-header">
                    <h1>Quiz Complete!</h1>
                    <h2>You scored ${result.score} out of ${result.total}</h2>
                    <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
                </div>
            `;
        }

        nextBtn.addEventListener('click', () => {
            const selectedOption = document.querySelector('input[name="option"]:checked');

            if (!selectedOption) {
                alert('Please select an answer!');
                return;
            }

            const questionId = questions[currentQuestionIndex].question_id;
            userAnswers[questionId] = selectedOption.value;

            currentQuestionIndex++;
            if (currentQuestionIndex < questions.length) {
                loadQuestion();
            } else {
                submitQuiz();
            }
        });

        // Load the very first question when the page opens
        loadQuestion();

    } else {
        // This part runs if a topic has no questions.
        quizContainer.innerHTML = `
            <div class="quiz-header">
                <h1>No Questions Available</h1>
                <p>There are no questions for this topic yet. Please check back later.</p>
                <br>
                <a href="/dashboard" class="btn btn-secondary">Back to Dashboard</a>
            </div>
        `;
    }
});
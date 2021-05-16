let inputIndex = 0;
/**
 * Adds a new question
 */
function addQuestion() {

    let section = document.createElement('div');
    section.classList.add('question');

    // creating new input field
    let question = document.createElement('input');
    question.type = 'text';
    question.placeholder = 'Insert question';
    question.id = ++inputIndex;
    // question.classList.add('form-control');
    question.required = true;

    // creating the button to add a new response 
    let answerButton = document.createElement('button');
    answerButton.type = 'button';
    answerButton.classList.add('btn', 'btn-primary');
    answerButton.onclick = addAnswer;
    answerButton.id = ++inputIndex;
    answerButton.innerText = '➕';

    // creating the button to add a new response 
    let deleteQuestionButton = document.createElement('button');
    deleteQuestionButton.type = 'button';
    deleteQuestionButton.classList.add('btn', 'btn-primary');
    deleteQuestionButton.onclick = deleteQuestion;
    deleteQuestionButton.id = ++inputIndex;
    deleteQuestionButton.innerText = '🗑️';

    // adding everything to the page
    let quiz = document.getElementById('quiz');
    section.append(question, answerButton, deleteQuestionButton);
    quiz.appendChild(section);
}

/**
 * Adds a new answer for the related question
 */
function addAnswer() {
    let section = document.createElement('div');
    section.classList.add('answer', 'margin');

    let parent = document.getElementById(this.id).parentElement;

    // creating new text field
    let answer = document.createElement('input');
    answer.type = 'text';
    answer.placeholder = 'Insert answer';
    answer.id = ++inputIndex;
    answer.required = true;

    // creating new checkbox and label
    let checkbox = document.createElement('input');
    checkbox.type = 'checkbox';

    let label = document.createElement('label');
    label.innerHTML = "Correct?";

    // creating a delete button for the answer
    let deleteAnswerButton = document.createElement('button');
    deleteAnswerButton.type = 'button';
    deleteAnswerButton.classList.add('btn', 'btn-primary');
    deleteAnswerButton.onclick = deleteAnswer;
    deleteAnswerButton.id = ++inputIndex;
    deleteAnswerButton.innerText = '🗑️';

    section.append(answer, label, checkbox, deleteAnswerButton);
    parent.appendChild(section);
}

/**
 * Deletes the question and the related answers
 */
function deleteQuestion() {
    let parent = document.getElementById(this.id).parentElement;
    parent.parentElement.removeChild(parent);
}

/**
 * Deletes the answer for the related question
 */
function deleteAnswer() {
    console.log(this.id);
    let parent = document.getElementById(this.id).parentElement;
    parent.parentElement.removeChild(parent);
}

/**
 * 
 * @returns formValidationError function.
 * @see formValidationError
 */
function isFormValid() {
    // getting the data
    const questions = document.getElementById('quiz').children;
    if (questions.length <= 0){
        return formValidationError("You need to add at least a question!");
    }
    // checking that every question has at least two answers and at least one of them is correct
    for (const question of questions) {
        let flagCorrect = false;

        // check if the question has a text
        const questionText = question.children[0].value;
        if (questionText === "") {
            return formValidationError("A question has no text");
        }

        // filtering
        const answers = Array.from(question.children).filter(ans => ans.classList.contains('answer'));

        // check 1, at least two answers per question
        if (answers.length <= 1) {
            return formValidationError("A question needs at least two answers");
        }

        // looping over the answers
        for (const answer of answers) {

            let answerContainer = answer.children;

            // check 2, answer text has been provided
            if (answerContainer[0].value === "") {
                return formValidationError("An answer is blank");
            }

            // check 3, at least one answer is correct
            if (answerContainer[2].checked) {
                flagCorrect = true;
            }
        }
        if (!flagCorrect) {
            return formValidationError("At least one answer needs to be correct");
        }
    }
    return true;
}

/**
 * Error function for form validation, adds a dismissable alert with the relative error.
 * @param {string} error that caused the form to be invalid
 * @returns false
 */
function formValidationError(error) {
    // getting body
    const alertWrapper = document.getElementById('alert');

    // add a new alert if it's not present
    if (alertWrapper.children.length === 0) {
        // Creating dismissable alert container
        let alert = document.createElement('div');
        alert.classList.add('alert', 'alert-danger', 'alert-dismissible', 'fade', 'show', 'margin');
        alert.setAttribute('role', 'alert');

        // Creating error message
        let message = document.createElement('strong');
        message.innerHTML = error

        // Creating dismiss button
        let dismissButton = document.createElement('button');
        dismissButton.type = 'button';
        dismissButton.classList.add('close');
        dismissButton.setAttribute('data-dismiss', 'alert');
        dismissButton.setAttribute('aria-label', 'close');

        // adding span to dismiss button
        let dismissButtonSpan = document.createElement('span');
        dismissButtonSpan.setAttribute('aria-hidden', 'true');
        dismissButtonSpan.innerHTML = '&times;';
        dismissButton.appendChild(dismissButtonSpan);

        alert.append(message, dismissButton);
        // adding the dismissable alert to the body
        alertWrapper.appendChild(alert);
    } else {
        alertWrapper.children[0].children[0].innerHTML = error;
    }
    return false;
}

/**
 * submits the form in a json object
 */
document.getElementById('submit').addEventListener('click', () => {

    // form validation
    if (!isFormValid()) {
        return;
    }

    // getting the data from the form
    const questions = document.getElementsByClassName('question');
    const course = document.getElementById('course').value;

    // constructing the json object
    quiz = { "course": course, "questions": [] };
    for (const question of questions) {
        let tmpQuestion = { question: question.children[0].value, answers: [] };

        // filtering
        const answers = Array.from(question.children).filter(ans => ans.classList.contains('answer'));

        for (const answer of answers) {
            let tmpAnswer = { "answer": answer.firstChild.value, "correct": answer.children[2].checked };
            tmpQuestion.answers.push(tmpAnswer);
        }

        quiz.questions.push(tmpQuestion);
    }
    // sending the data to the server
    fetch(`${window.location}`, {
        method: "POST",
        body: JSON.stringify(quiz),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }) //getting the response back
        .then(function (response) {
            if (response.status !== 200) {
                console.log(`Response status was ${response.status}`)
                return;
            }

            response.json().then(function (data) {
                console.log(data);
                location.reload();
            })
        })
});
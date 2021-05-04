
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
    section.classList.add('answer');

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
    let parent = document.getElementById(this.id).parentElement;
    parent.parentElement.removeChild(parent);
}

let inputIndex = 0;

/**
 * Adds a question to 'quiz' div
 */
function addQuestion() {
    //linebreak object
    let linebreak = document.createElement('br');

    // creating new input field
    let newQuestion = document.createElement('input');
    newQuestion.type = 'text';
    newQuestion.placeholder = 'Insert question';
    // newQuestion.classList.add('form-control');
    newQuestion.id = ++inputIndex;
    newQuestion.required = true;

    // creating the button to add a new response 
    let newAnswerButton = document.createElement('button');
    newAnswerButton.type = 'button';
    newAnswerButton.classList.add('btn', 'btn-primary');
    newAnswerButton.onclick = addAnswer;
    newAnswerButton.innerText = '➕';

    // creating the button to add a new response 
    let deleteAnswerButton = document.createElement('button');
    deleteAnswerButton.type = 'button';
    deleteAnswerButton.classList.add('btn', 'btn-primary');
    deleteAnswerButton.onclick = deleteAnswer;
    deleteAnswerButton.innerText = '🗑️';
    
    // adding everything to the page
    let quiz = document.getElementById('quiz');
    quiz.append(newQuestion, newAnswerButton, deleteAnswerButton, linebreak);
}

/**
 * 
 */
function addAnswer(){
    console.log('not doing anything yet');
}

/**
 * 
 */
function deleteAnswer(){
    console.log('not doing anything yet again');
}
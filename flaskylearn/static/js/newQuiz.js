
let inputIndex = 0;

/**
 * Adds a question to "quiz" div
 */
function addQuestion() {
    //linebreak object
    let linebreak = document.createElement("br");

    // creating new input field
    let tag = document.createElement("input");
    tag.type = "text";
    tag.placeholder = "Insert question";
    tag.id = ++inputIndex;

    // creating the button to add a new 
    let newQuestionButton = document.createElement("button");
    newQuestionButton.type = "button";
    newQuestionButton.onclick = addResponseButton;
    newQuestionButton.innerText = "➕";

    // adding the input tag to 
    let element = document.getElementById("quiz");
    element.appendChild(tag);
    element.appendChild(newQuestionButton);
    element.appendChild(linebreak);
}

/**
 * 
 */
function addResponseButton(){
    console.log("not doing anything yet");
}
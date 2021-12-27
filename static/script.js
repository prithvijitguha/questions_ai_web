//find element question form and place in variable 
var question = document.getElementById('question_f')

var question_form = document.getElementById('submit_question')

var answer_box = document.getElementById('answer_box')

var answer_box_question = document.getElementById('answer_box_question')

//create fetch function get and post 
question_form.addEventListener('submit', () => {
    question_handler(question);
    event.preventDefault();
    question.disabled = true;

}
)



function question_handler(question) {
    var q_data = question.value
    answer_box.innerHTML = "Checking for answer..."
    answer_box_question.innerHTML = ""
    var mydata = {'question': question.value}

    fetch('/answers', {
        headers: {'Content-Type': 'application/json'},
        method: 'POST', 
        body: JSON.stringify(mydata)
    })
    .then(response => response.json())
    .then(result => {
        answer_box.innerHTML =  "Answer: " + result.answer
        answer_box_question.innerHTML = "Question: " + q_data.charAt(0).toUpperCase() + q_data.slice(1);
        question.disabled = false;
        question.value = ""
    })
}
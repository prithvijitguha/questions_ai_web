import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from term_frequency import relevant_data
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


#instantiate tokenizer 
#get model

model = AutoModelForQuestionAnswering.from_pretrained("./bert_small/")

tokenizer = AutoTokenizer.from_pretrained("./bert_small_token/")


@app.route('/')
def index(): 
    return render_template("index.html")

@app.route('/answers', methods=['GET', 'POST'])
def question_handler():
    if request.method == "POST":
        question = request.get_json()
        
        answer = answer_question(question['question'])
        
        
        if answer == '[SEP]' or answer is None or answer == "": 
            return jsonify(answer="Cannot answer this question")
        else:
            
            #capitalize the sentence
            answer = answer[0].upper() + answer[1:]
            #remove any [CLS] or [SEP] tags that may be present 
            answer = answer.replace("[SEP]", "").replace("[CLS]", "")
            return jsonify(answer=answer)


def answer_question(question): 
    #get data from helper function
    data = relevant_data(question)

    #tokenize question
    #inputs = tokenizer(question,data, add_special_tokens=True, truncation=True, padding=True, return_tensors="pt")

    '''
    Takes a `question` string and an `answer` string and tries to identify 
    the words within the `answer` that can answer the question. Prints them out.
    '''
    inputs = tokenizer.encode_plus(question, data, truncation=True, max_length=512, padding=True ,add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    text_tokens = tokenizer.convert_ids_to_tokens(input_ids)
    answer_start_scores, answer_end_scores = model(**inputs, return_dict=False)

    answer_start = torch.argmax(
        answer_start_scores
    )  # Get the most likely beginning of answer with the argmax of the score
    answer_end = torch.argmax(answer_end_scores) + 1  # Get the most likely end of answer with the argmax of the score

    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))

    return answer
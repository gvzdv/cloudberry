import os

from mistralai import Mistral
import time
from flask import Flask, request, jsonify, render_template


MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
model = "mistral-large-latest"

openai_client = Mistral(api_key=MISTRAL_API_KEY)

CALC_PROMPT = '''
This is a question from user.
Create a Python function to answer this request. Do not add any comments. 
Make sure that in the last line of the code you call the function and write the answer in the variable 'result'. Do not use the 'print' function.
'result' should be a string. If you made any calculations in the script, use an f-string to provide a commentary along with the calculation result. 
The script should be in triple backticks and start with word python.
'''

THOUGHT_PROMPT = '''
Answer the question from the user to the best of your ability.
'''

FINAL_PROMPT = '''
Here are the user's question and two approaches to answer it. 
The first one is a result of a Python script.
The second one is an answer suggested without the script.
Compare two options to the best of your ability and write the correct final answer without comments. 
If the question contains a request to count, calculate or compare values, consider the script option correct. Otherwise, use common sense. 
'''

# question = "how many l's are there in the sentence 'llama lives an alluring life at lollapalooza'?"  # correct
# question = "how much is 2387x9045"  # correct
# question = "what is the meaning of life?"  # correct
# question = "Which weighs more, a pound of water, two pounds of bricks, a pound of feathers, or three pounds of air?"  # correct
# question = "I’m in London and facing west, is Edinburgh to my left or my right?"  # incorrect
# question = "how many r's are there in the word strawberry?"  # correct
# question = "how many planets are there in the solar system?"  # correct
# question = "give me a list of ingredients for an omelette and tell me how many different ingredients I need"  # correct
# question = "write a sentence that contains six words"  # mostly correct
# question = "write a sentence that contains 11 words"  # incorrect
# question = "How much do 3.486 litres of milk weigh?"  # correct


def process_user_message(question):

    calculation = openai_client.chat.complete(
                                model=model,
                                messages=[
                                    {"role": "system", "content": CALC_PROMPT},
                                    {"role": "user", "content": question}
                                ]
                            )
    calc_answer = calculation.choices[0].message.content
    print(f"Script:\n{calc_answer}")
    print("----------------------------------------------")
    time.sleep(1.2)

    if calc_answer.startswith("```python") and "result" in calc_answer:
        calc_answer = calc_answer[9:-3]

        # Create a local scope dictionary to capture variables inside exec()
        local_scope = {}

        # Execute the code and populate the local scope
        exec(calc_answer, {}, local_scope)

        # Retrieve the result from the local scope
        calc_answer = local_scope['result']

    thought = openai_client.chat.complete(
                                model=model,
                                messages=[
                                    {"role": "system", "content": THOUGHT_PROMPT},
                                    {"role": "user", "content": question}
                                ]
                            )
    thought_answer = thought.choices[0].message.content
    time.sleep(1.2)

    final = openai_client.chat.complete(
                                model=model,
                                messages=[
                                    {"role": "system", "content": FINAL_PROMPT},
                                    {"role": "user", "content": f'''Question: {question}\n
                                    Python script: {calc_answer}\n
                                    Answer without the script: {thought_answer}'''}
                                ]
                            )

    final_answer = final.choices[0].message.content

    print(f"Calc:\n{calc_answer}")
    print("----------------------------------------------")
    print(f'Thought:\n{thought_answer}')
    print("----------------------------------------------")
    print(f'Final:\n{final_answer}')
    print("----------------------------------------------")

    return final_answer


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_message = data['message']

    bot_response = process_user_message(user_message)

    return jsonify({'response': bot_response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
from flask import Flask, request, jsonify, render_template , redirect, url_for
from flask_cors import CORS
import suggest_actions
from QA_generation import keyword_generation
import json
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

q_table_df=pd.DataFrame()
words_hints=[]

@app.route('/')
def input_page():
    return render_template('index.html')

@app.route('/puzzle')
def index():
    return render_template('puzzle.html')

#process the text input and return the data for crossword grid generation
@app.route('/process_input', methods=['POST','GET'])
def process_input():
    global q_table_df
    global words_hints
    if request.method == 'POST':
        data = request.json
        text_input = data['text_input']
        selected_number = data['selected_number']
        sampleGridData,sampleWords,q_table_df,words_hints=keyword_generation(text_input,selected_number)
        #sampleGridData_json = json.dumps(sampleGridData)
        #sampleWords_json = json.dumps(sampleWords)
        print(type(sampleWords),type(sampleGridData),len(sampleWords))
        return jsonify({'sampleGridData': sampleGridData, 'sampleWords': sampleWords ,'wordCount':len(sampleWords)})
    #else:
        #return jsonify({'error': 'Invalid request'})
    #return jsonify({'message': 'Data received successfully.'})


#process current state and return appropriate action suggestion
@app.route('/send_data', methods=['POST','GET'])
def send_data():
    current_state = request.json  # Assuming JSON data is sent
    # Process data here
    current_state = tuple(tuple(inner_list) for inner_list in current_state['current_state'])
    print("Received data:", current_state,type(current_state))
    result,update_score= suggest_actions.get_actions(current_state,q_table_df,words_hints)
    print("response :",result,"update_score:",update_score)
    response_data = {'message': result, 'if_update_score':update_score}
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)

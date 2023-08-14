from flask import Flask, render_template, request, jsonify
from transformers import AutoTokenizer, AutoModelForTokenClassification, BertTokenizerFast
from transformers import pipeline

app = Flask(__name__)

# Load the tokenizer and models
models = {
    "bert-base-chinese-finetuned-ner": {
        "tokenizer": BertTokenizerFast.from_pretrained("./model/bert-base-chinese-finetuned-ner"),
        "model": AutoModelForTokenClassification.from_pretrained("./model/bert-base-chinese-finetuned-ner"),
        "pipeline": None
    },
    "chinese-ner": {
        "tokenizer": AutoTokenizer.from_pretrained("./model/chinese-ner"),
        "model": AutoModelForTokenClassification.from_pretrained("./model/chinese-ner"),
        "pipeline": None
    }
}

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the input text from the form
        text = request.json['text']
        model_name = request.json['model']

        # Perform NER on the input text using the selected model
        pipeline = get_pipeline(model_name)
        ner_results = pipeline(text)
        locations = []
        # 根据选择的模型应用不同的地址提取逻辑
        if model_name == 'bert-base-chinese-finetuned-ner':
            loc_keys = ['B-LOC', 'I-LOC', 'B-ORG', 'I-ORG']
            for result in ner_results:
                if result['entity'] in loc_keys:
                    locations.append(result['word'])

        elif model_name == 'chinese-ner':
            loc_not_keys = ['LABEL_0']
            flag = 0
            for result in ner_results:
                if result['entity'] not in loc_not_keys:
                    locations.append(result['word'])
                    flag = 1
                    continue
                elif flag == 1:
                    break

        location_str = ''.join(locations)
        # Render the result on the page
        return jsonify(address=location_str)

    # Render the home page
    return render_template('index.html', models=models.keys())

def get_pipeline(model_name):
    if models[model_name]['pipeline'] is None:
        models[model_name]['pipeline'] = pipeline("ner", model=models[model_name]['model'], tokenizer=models[model_name]['tokenizer'])
    return models[model_name]['pipeline']

if __name__ == '__main__':
    app.run(host='172.16.14.233', port=5000)

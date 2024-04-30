from bson import ObjectId
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
from datetime import datetime


app = Flask(__name__)

client = MongoClient('mongodb://iqbal:iqbal@ac-scdewbe-shard-00-00.ie0bayw.mongodb.net:27017,ac-scdewbe-shard-00-01.ie0bayw.mongodb.net:27017,ac-scdewbe-shard-00-02.ie0bayw.mongodb.net:27017/?ssl=true&replicaSet=atlas-6vgddv-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0')
db = client.dbsparta_plus_week2

@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
    msg = request.args.get('msg')
    return render_template(
        'index.html',
        words=words,
        msg=msg
    )

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = '3103e4a6-bb5a-4745-8925-0e80493f421c'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for('error', keyword=keyword, suggestions=[]), code=404)
    if type(definitions[0]) is str:
        return redirect(url_for('error', keyword=keyword, suggestions=",".join(definitions)), code=404)
    status = request.args.get('status_give', 'new')
    examples = db.examples.find({'word': keyword})
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=status,
        examples=examples,
    )


@app.route('/error')
def error():
    keyword = request.args.get('keyword')
    suggested_words = request.args.get('suggestions')
    return render_template('error.html', keyword=keyword, suggested_words=suggested_words)

@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word_give')
    examples = list(db.example.find({'word': word}))
    examples = [{'_id': str(ex['_id']), 'example': ex['example']} for ex in examples]  # Ubah _id menjadi string
    return jsonify({'examples': examples})

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    word = request.form.get('word')
    example = request.form.get('example')
    db.example.insert_one({'word': word, 'example': example})
    return jsonify({'result': 'success'})

@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    word = request.form.get('word')
    example_id = request.form.get('id')
    db.example.delete_one({'word': word, '_id': ObjectId(example_id)})
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
from flask import Flask, render_template, request
import requests

app = Flask(__name__)
API_KEY = "fa02a592c8da4e30a02baf51290acfad"

@app.route('/')
def home():
    query = request.args.get('q') or 'latest'
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}&language=en'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return render_template('index.html', articles=articles, query=query)

if __name__ == '__main__':
    app.run(debug=True)

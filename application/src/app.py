from flask import Flask
from src.controller import main
app = Flask(__name__)
app.debug = True

@app.route('/')
def run():
    main.call_query()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)


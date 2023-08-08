from flask import Flask
app = Flask(__name__) 

@app.route('/') 
def hello(): 
    return 'Hello, o!3' 

def sup():
    return 'sup3'
if __name__ == '__main__': 
    app.run(debug=True, host='0.0.0.0', port=80)

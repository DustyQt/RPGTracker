from flask import Flask,render_template,request
from src.controller.manager import manager
app = Flask(__name__) 
mng = manager()

@app.route('/sup') 
def hello(): 
    return 'Hello Sense' 

@app.route('/character',methods = ['GET'])
def query(): 
    if request.method == 'GET':
        args = request.args
        res = mng.load_character(args['id'])
        return res

if __name__ == '__main__': 
    app.run(debug=True, host='0.0.0.0', port=80)

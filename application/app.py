from flask import Flask,render_template,request
from src.controller.manager import manager
app = Flask(__name__) 
mng = manager()

@app.route('/') 
def hello(): 
    return 'sup'

@app.route('/character',methods = ['GET'])
def character(): 
    if request.method == 'GET':
        args = request.args
        res = mng.load_character(args['id'])
        return render_template('character.html', char=res)
    
@app.route('/json',methods = ['GET'])
def character_json(): 
    if request.method == 'GET':
        args = request.args
        res = mng.load_character(args['id'])
        return res

if __name__ == '__main__': 
    app.run(debug=True, host='0.0.0.0', port=80)

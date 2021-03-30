from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        numero_entrado = int(request.form['numero']) 
        numero_resultante = numero_entrado + 2

        sentence = f'{numero_entrado} + 2 = {numero_resultante}'

        return render_template('index.html', sentence=sentence)
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run()
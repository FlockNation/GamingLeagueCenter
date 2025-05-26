from flask import Flask, render_template, jsonify
from simulation import run_simulation  # import the simulation function

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    result = run_simulation() 
    return jsonify(result)

if __name__ == '__main__':
    app.run()

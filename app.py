from flask import Flask, render_template, jsonify, request
from simulation import run_simulation

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    league = request.json.get('league', 'IGL')
    result = run_simulation(league)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

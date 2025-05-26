from flask import Flask, request, jsonify
import csv
import random

app = Flask(__name__)

@app.route('/simulate', methods=['POST'])
def simulate_route():
    data = request.json
    league = data.get('league', 'IGL')
    result = run_simulation(league)
    return jsonify(result)

@app.route('/calculate_overall', methods=['POST'])
def calculate_overall_route():
    data = request.json
    score_impact = data.get('score_impact')
    risk_factor = data.get('risk_factor')
    activity = data.get('activity')

    if not all(isinstance(x, int) for x in [score_impact, risk_factor, activity]):
        return jsonify({'error': 'Invalid input'}), 400

    overall = get_overall_from_csv(score_impact, risk_factor, activity)
    if overall is None:
        return jsonify({'error': 'Combination not found'}), 404

    return jsonify({'overall': overall})

def get_overall_from_csv(score_impact, risk_factor, activity, filename='gaming_league_overall.csv'):
    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (int(row['score_impact']) == score_impact and
                    int(row['risk_factor']) == risk_factor and
                    int(row['activity']) == activity):
                    return int(row['overall'])
    except:
        pass
    return None

def run_simulation(league):
    teams = ['Team A', 'Team B', 'Team C', 'Team D']
    results = {team: 0 for team in teams}

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            winner = random.choice([teams[i], teams[j]])
            results[winner] += 1

    sorted_results = sorted(results.items(), key=lambda x: -x[1])
    standings = [team for team, _ in sorted_results]

    return {
        'standings': standings,
        'playoffs': {
            'semis': [['Team A', 'Team D'], ['Team B', 'Team C']],
            'final': ['Team A', 'Team B'],
            'champion': 'Team A'
        },
        'lottery': ['Team D', 'Team C', 'Team B', 'Team A']
    }

if __name__ == '__main__':
    app.run(debug=True)

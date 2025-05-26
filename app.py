from flask import Flask, request, jsonify, send_from_directory
import csv
import random

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/simulate', methods=['POST'])
def simulate_route():
    data = request.json
    league = data.get('league', 'IGL')
    result = run_simulation()
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

def run_simulation():
    teams = ['Colorado', 'Philadelphia', 'Alaska', 'Georgia', 'Miami']
    records = {team: {'W': 0, 'L': 0} for team in teams}

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            winner = random.choice([teams[i], teams[j]])
            loser = teams[j] if winner == teams[i] else teams[i]
            records[winner]['W'] += 1
            records[loser]['L'] += 1

    sorted_records = sorted(records.items(), key=lambda x: (-x[1]['W'], x[1]['L']))
    standings = [(team, rec['W'], rec['L']) for team, rec in sorted_records]

    top4 = [team for team, _, _ in standings[:4]]
    semis = [[top4[0], top4[3]], [top4[1], top4[2]]]
    final = [random.choice(semis[0]), random.choice(semis[1])]
    champion = random.choice(final)

    bottom1 = standings[-1][0]
    lottery_order = [bottom1] + [team for team, _, _ in standings if team != bottom1]

    return {
        'standings': standings,
        'playoffs': {
            'semis': semis,
            'final': final,
            'champion': champion
        },
        'lottery': lottery_order
    }

if __name__ == '__main__':
    app.run(debug=True)

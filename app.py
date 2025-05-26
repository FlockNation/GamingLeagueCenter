from flask import Flask, request, jsonify, render_template
import csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/players', methods=['GET'])
def players_route():
    players = []
    try:
        with open('tableConvert.com_grbjkn.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            seen = set()
            for row in reader:
                player = row.get('player') or row.get('Player') or next(iter(row.values())).strip()
                if player and player not in seen:
                    seen.add(player)
                    players.append(player)
    except Exception:
        pass
    return jsonify({'players': players})

@app.route('/player_overall', methods=['POST'])
def player_overall_route():
    data = request.json
    player_name = data.get('player')

    if not player_name:
        return jsonify({'error': 'No player specified'}), 400

    overall = get_player_overall(player_name)
    if overall is None:
        return jsonify({'error': 'Player not found'}), 404

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

def get_player_overall(player_name, filename='tableConvert.com_03cn1x.csv'):
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Adjust column name if needed:
                if row.get('player') == player_name or row.get('Player') == player_name:
                    return int(row.get('overall') or row.get('Overall') or 0)
    except:
        pass
    return None

def run_simulation(league):
    teams = ['Colorado', 'Philadelphia', 'Alaska', 'Georgia', 'Miami']
    import random
    standings = [(team, random.randint(0, 20)) for team in teams]
    standings.sort(key=lambda x: x[1], reverse=True)

    playoffs = {
        'semis': [(standings[0][0], standings[3][0]), (standings[1][0], standings[2][0])],
        'final': (standings[0][0], standings[1][0]),
        'champion': standings[0][0]
    }

    lottery = [team for team, wins in reversed(standings)]

    return {
        'standings': standings,
        'playoffs': playoffs,
        'lottery': lottery
    }

if __name__ == '__main__':
    app.run(debug=True)

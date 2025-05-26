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
                if (int(row['ScoreImpact']) == score_impact and
                    int(row['RiskFactor']) == risk_factor and
                    int(row['Activity']) == activity):
                    return int(row['Overall'])
    except:
        pass
    return None

def get_player_overall(player_name):
    try:
        with open('tableConvert.com_grbjkn.csv', newline='', encoding='utf-8') as player_file, \
             open('tableConvert.com_03cn1x.csv', newline='', encoding='utf-8') as overall_file:

            player_reader = csv.DictReader(player_file)
            overall_reader = csv.DictReader(overall_file)

            players = [row['player'] for row in player_reader]
            overalls = [int(row['player_overall']) for row in overall_reader]

            if player_name in players:
                index = players.index(player_name)
                return overalls[index]
    except:
        pass
    return None

import random
from collections import defaultdict

def run_simulation(league):
    teams = ['Colorado', 'Philadelphia', 'Alaska', 'Georgia', 'Miami']
    games_per_team = 4
    team_games = defaultdict(int)
    matchups = []

    while any(team_games[t] < games_per_team for t in teams):
        t1, t2 = random.sample(teams, 2)
        if t1 == t2:
            continue
        if team_games[t1] >= games_per_team or team_games[t2] >= games_per_team:
            continue
        if (t1, t2) in matchups or (t2, t1) in matchups:
            continue

        matchups.append((t1, t2))
        team_games[t1] += 1
        team_games[t2] += 1

    wins = defaultdict(int)
    for t1, t2 in matchups:
        winner = random.choice([t1, t2])
        wins[winner] += 1

    standings = [(team, wins.get(team, 0)) for team in teams]
    standings.sort(key=lambda x: x[1], reverse=True)

    playoffs = {
        'semis': [(standings[0][0], standings[3][0]), (standings[1][0], standings[2][0])],
        'final': (standings[0][0], standings[1][0]),
        'champion': standings[0][0]
    }

    lottery = [team for team, _ in reversed(standings)]

    return {
        'matchups': matchups,
        'standings': standings,
        'playoffs': playoffs,
        'lottery': lottery
    }
    
if __name__ == '__main__':
    app.run(debug=True)

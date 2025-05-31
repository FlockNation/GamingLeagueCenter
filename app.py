from flask import Flask, request, jsonify, render_template, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
import csv
import random
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your-secret-key'
CORS(app, supports_credentials=True)

@app.route('/debug-simulation')
def debug_simulation():
    try:
        with open('simulation.py', 'r') as f:
            lines = f.readlines()[:20]  # first 20 lines
        return jsonify({'simulation_py_head': lines})
    except Exception as e:
        return jsonify({'error': str(e)})

login_manager = LoginManager()
login_manager.init_app(app)

users = {}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

    @property
    def balance(self):
        return users.get(self.id, {}).get('balance', 0)

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/place_bets')
@login_required
def place_bets_page():
    return render_template('place_bets.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400
    users[username] = {'balance': 1000}
    return jsonify({'message': 'User registered successfully', 'balance': users[username]['balance']})

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400
    if username not in users:
        return jsonify({'error': 'User not found'}), 404
    user = User(username)
    login_user(user)
    session.permanent = True
    return jsonify({'message': 'Logged in', 'balance': users[username]['balance']})

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

@app.route('/place_bet', methods=['POST'])
@login_required
def place_bet():
    data = request.json
    game = data.get('game')
    team = data.get('team')
    amount = data.get('amount')
    if not game or not team or amount is None:
        return jsonify({'error': 'Missing bet details'}), 400
    try:
        amount = int(amount)
        if amount <= 0:
            return jsonify({'error': 'Bet amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid bet amount'}), 400
    username = current_user.id
    if users[username]['balance'] < amount:
        return jsonify({'error': 'Not enough coins'}), 400
    users[username]['balance'] -= amount
    if 'bets' not in users[username]:
        users[username]['bets'] = []
    users[username]['bets'].append({'game': game, 'team': team, 'amount': amount})
    return jsonify({'message': f'Bet placed on {team} for {amount} coins.', 'balance': users[username]['balance']})

@app.route('/get_balance')
@login_required
def get_balance():
    username = current_user.id
    balance = users.get(username, {}).get('balance', 0)
    return jsonify({'balance': balance})

@app.route('/simulate', methods=['POST'])
def simulate_route():
    data = request.json
    league = data.get('league', 'SLOG').upper()
    
    print(f"Received simulation request for league: {league}")
    result = run_simulation(league)
    print("SIMULATION RESULT:", result)
    
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

from collections import defaultdict
import random

def run_simulation(league):
    league = league.upper()
    
    if league == 'SLOG':
        canada_conf = ['Vancouver', 'Montreal', 'Quebec City', 'Toronto']
        usa_conf = ['Los Angeles', 'San Jose', 'New York', 'Indiana']
        teams = canada_conf + usa_conf

        matchups = []

        for conf in [canada_conf, usa_conf]:
            for team in conf:
                opponents = [t for t in conf if t != team]
                selected_opponents = random.sample(opponents, 3)
                for opp in selected_opponents:
                    pair = tuple(sorted([team, opp]))
                    if pair not in matchups:
                        matchups.append(pair)

    else:
        teams = ['Colorado', 'Philadelphia', 'Alaska', 'Georgia', 'Miami']
        matchups = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i + 1, len(teams))]

    wins = defaultdict(int)
    for t1, t2 in matchups:
        winner = random.choice([t1, t2])
        wins[winner] += 1

    standings = [(team, wins.get(team, 0)) for team in teams]
    standings.sort(key=lambda x: x[1], reverse=True)

    if league == 'SLOG':
        playoff_teams = [team for team, _ in standings[:5]]
        seed1, seed2, seed3, seed4, seed5 = playoff_teams

        q1_winner = random.choice([seed2, seed3])
        q1_loser = seed3 if q1_winner == seed2 else seed2

        elim1_winner = random.choice([seed4, seed5])

        elim2_winner = random.choice([q1_loser, elim1_winner])

        final_teams = [seed1, q1_winner, elim2_winner]
        champion = random.choice(final_teams)

        from collections import OrderedDict

        semis = OrderedDict([
            ('Eliminator 2', (q1_loser, elim1_winner)),
            ('Eliminator 1', (seed4, seed5)),
            ('Qualifier 1', (seed2, seed3))
        ])

    else:
        team1, team2 = standings[0][0], standings[1][0]
        final_teams = (team1, team2)
        champion = random.choice(final_teams)
        semis = {}

    lottery = [team for team, _ in reversed(standings) if team not in final_teams]

    return {
        'matchups': matchups,
        'standings': standings,
        'playoffs': {
            'semis': semis,
            'final': final_teams,
            'champion': champion
        },
        'lottery': lottery
    }
    
if __name__ == '__main__':
    app.run(debug=True)

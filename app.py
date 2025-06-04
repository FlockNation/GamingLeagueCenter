from flask import Flask, request, jsonify, render_template, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session
from datetime import timedelta
import csv
import random
from collections import defaultdict
import os
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_TYPE'] = 'sqlalchemy'
CORS(app, supports_credentials=True)

uri = os.getenv("DATABASE_URL", "sqlite:///local.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
if "localhost" not in uri and "sslmode" not in uri:
    uri += "?sslmode=require"
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Unauthorized'}), 401

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    username = db.Column(db.String, primary_key=True)
    balance = db.Column(db.Integer, default=1000)

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def get_user(username):
    return User.query.filter_by(username=username).first()

def get_user_balance(username):
    user = get_user(username)
    return user.balance if user else 0

def update_user_balance(username, new_balance):
    user = get_user(username)
    if user:
        user.balance = new_balance
        db.session.commit()

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/place_bets/')
@login_required
def place_bets_page():
    return render_template('place_bets.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400
    if get_user(username):
        return jsonify({'error': 'Username already exists'}), 400
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully', 'balance': 1000})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400
    user = get_user(username)
    if not user:
        return jsonify({'error': 'Invalid username'}), 401
    login_user(user)
    session.permanent = True
    return jsonify({'message': 'Logged in', 'balance': user.balance})

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

@app.route('/check_login', methods=['GET'])
def check_login():
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'username': current_user.get_id(), 'balance': get_user_balance(current_user.get_id())})
    else:
        return jsonify({'logged_in': False})

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
        if amount <= 0 or amount > 1000000:
            return jsonify({'error': 'Bet amount must be positive and reasonable'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid bet amount'}), 400
    username = current_user.get_id()
    balance = get_user_balance(username)
    if balance < amount:
        return jsonify({'error': 'Not enough coins'}), 400
    update_user_balance(username, balance - amount)
    return jsonify({'message': f'Bet placed on {team} for {amount} coins.', 'balance': balance - amount})

@app.route('/get_balance')
@login_required
def get_balance():
    return jsonify({'balance': get_user_balance(current_user.get_id())})

@app.route('/simulate', methods=['POST'])
@login_required
def simulate_route():
    data = request.json
    league = data.get('league', 'SLOG').upper()
    result = run_simulation(league)
    return jsonify(result)

@app.route('/calculate_overall', methods=['POST'])
@login_required
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
@login_required
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
    except Exception as e:
        logging.error(f"Error reading players CSV: {e}")
    return jsonify({'players': players})

@app.route('/player_overall', methods=['POST'])
@login_required
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
    except Exception as e:
        logging.error(f"Error reading overall CSV: {e}")
    return None

def get_player_overall(player_name):
    try:
        with open('tableConvert.com_grbjkn.csv', newline='', encoding='utf-8') as player_file, \
             open('tableConvert.com_03cn1x.csv', newline='', encoding='utf-8') as overall_file:
            player_reader = list(csv.DictReader(player_file))
            overall_reader = list(csv.DictReader(overall_file))
            player_dict = {row['player']: idx for idx, row in enumerate(player_reader)}
            if player_name in player_dict:
                index = player_dict[player_name]
                if index < len(overall_reader):
                    return int(overall_reader[index]['player_overall'])
    except Exception as e:
        logging.error(f"Error reading player overall CSVs: {e}")
    return None

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
        semis = [
            {'round': 'Qualifier 1', 'teams': [seed2, seed3]},
            {'round': 'Eliminator 1', 'teams': [seed4, seed5]},
            {'round': 'Eliminator 2', 'teams': [q1_loser, elim1_winner]},
        ]
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
    logging.basicConfig(level=logging.ERROR)
    app.run(debug=True)

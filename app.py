from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

teams_IGL = [
    {"team": "Philadelphia", "players": ["Player1", "Player2", "Player3", "Player4"], "overall": random.randint(80, 95)},
    {"team": "Alaska", "players": ["Player5", "Player6", "Player7", "Player8"], "overall": random.randint(80, 95)},
    {"team": "Georgia", "players": ["Player9", "Player10", "Player11", "Player12"], "overall": random.randint(80, 95)},
    {"team": "Miami", "players": ["Player13", "Player14", "Player15", "Player16"], "overall": random.randint(80, 95)},
    {"team": "Colorado", "players": ["Player17", "Player18", "Player19", "Player20"], "overall": random.randint(80, 95)}
]

def team_strength(team):
    chemistry = random.uniform(-2, 2)
    return team['overall'] + chemistry

def simulate_match(team1, team2):
    s1 = team_strength(team1) * random.uniform(0.95, 1.05)
    s2 = team_strength(team2) * random.uniform(0.95, 1.05)
    return team1 if s1 > s2 else team2

def simulate_season(teams):
    standings = {team['team']: 0 for team in teams}
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            winner = simulate_match(teams[i], teams[j])
            standings[winner['team']] += 1
    return standings

def playoffs(standings):
    sorted_teams = sorted(standings.items(), key=lambda x: x[1], reverse=True)
    top4 = [team for team, _ in sorted_teams[:4]]
    semi1_winner = random.choice([top4[0], top4[3]])
    semi2_winner = random.choice([top4[1], top4[2]])
    champion = random.choice([semi1_winner, semi2_winner])
    return {
        "semis": [(top4[0], top4[3]), (top4[1], top4[2])],
        "final": (semi1_winner, semi2_winner),
        "champion": champion
    }

def draft_lottery(standings):
    sorted_teams = sorted(standings.items(), key=lambda x: x[1])
    weights = [5, 4, 3, 2, 1]
    entries = []
    for i, (team, _) in enumerate(sorted_teams):
        entries.extend([team] * weights[i])
    random.shuffle(entries)
    lottery = []
    while len(lottery) < 3:
        pick = random.choice(entries)
        if pick not in lottery:
            lottery.append(pick)
    return lottery

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    standings = simulate_season(teams_IGL)
    playoff_results = playoffs(standings)
    lottery = draft_lottery(standings)
    return jsonify({
        "standings": standings,
        "playoffs": playoff_results,
        "lottery": lottery
    })

if __name__ == '__main__':
    app.run()

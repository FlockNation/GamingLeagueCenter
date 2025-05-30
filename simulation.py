import random
from collections import defaultdict

def run_simulation(league):
    if league.upper() == 'SLOG':
        canada_conf = ['Vancouver', 'Montreal', 'Quebec City', 'Toronto']
        usa_conf = ['Los Angeles', 'San Jose', 'New York', 'Indiana']
        teams = canada_conf + usa_conf
    else:
        teams = ['Colorado', 'Philadelphia', 'Alaska', 'Georgia', 'Miami']

    matchups = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i + 1, len(teams))]
    wins = defaultdict(int)

    for t1, t2 in matchups:
        winner = random.choice([t1, t2])
        wins[winner] += 1

    standings = [(team, wins.get(team, 0)) for team in teams]
    standings.sort(key=lambda x: x[1], reverse=True)

    if league.upper() == 'SLOG':
        playoff_teams = [team for team, _ in standings[:5]]
        seed1 = playoff_teams[0]
        seed2 = playoff_teams[1]
        seed3 = playoff_teams[2]
        seed4 = playoff_teams[3]
        seed5 = playoff_teams[4]

        q1_winner = random.choice([seed2, seed3])
        q1_loser = seed3 if q1_winner == seed2 else seed2
        elim1_winner = random.choice([seed4, seed5])
        elim2_winner = random.choice([q1_loser, elim1_winner])
        final_teams = (seed1, q1_winner) if random.choice([True, False]) else (seed1, elim2_winner)
        champion = random.choice(final_teams)

        semis = {
            'Qualifier 1': (seed2, seed3),
            'Eliminator 1': (seed4, seed5),
            'Eliminator 2': (q1_loser, elim1_winner)
        }

    else:
        team1, team2 = standings[0][0], standings[1][0]
        final_teams = (team1, team2)
        champion = random.choice(final_teams)
        semis = None

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

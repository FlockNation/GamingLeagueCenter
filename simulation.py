import random
from collections import defaultdict

def run_simulation(league):
    league = league.upper()

    if league == 'SLOG':
        canada_conf = ['Vancouver', 'Montreal', 'Quebec City', 'Toronto']
        usa_conf = ['Los Angeles', 'San Jose', 'New York', 'Indiana']
        teams = canada_conf + usa_conf

        matchups = []
        for conf in [canada_conf, usa_conf]:
            for i in range(len(conf)):
                for j in range(i + 1, len(conf)):
                    for _ in range(3):
                        matchups.append((conf[i], conf[j]))

        wins = defaultdict(int)
        for t1, t2 in matchups:
            winner = random.choice([t1, t2])
            wins[winner] += 1

        canada_standings = [(team, wins.get(team, 0)) for team in canada_conf]
        usa_standings = [(team, wins.get(team, 0)) for team in usa_conf]

        canada_standings.sort(key=lambda x: x[1], reverse=True)
        usa_standings.sort(key=lambda x: x[1], reverse=True)

        overall_standings = [(team, wins.get(team, 0)) for team in teams]
        overall_standings.sort(key=lambda x: x[1], reverse=True)

        playoff_teams = [team for team, _ in overall_standings[:5]]
        seed1, seed2, seed3, seed4, seed5 = playoff_teams

        q1_winner = random.choice([seed2, seed3])
        q1_loser = seed3 if q1_winner == seed2 else seed2

        elim_winner = random.choice([seed4, seed5])
        q2_winner = random.choice([q1_loser, elim_winner])

        final_teams = (seed1, q1_winner, q2_winner)
        champion = random.choice(final_teams)

        semis = {
            'Qualifier 1': (seed2, seed3),
            'Eliminator': (seed4, seed5),
            'Qualifier 2': (q1_loser, elim_winner)
        }

        lottery = [team for team, _ in reversed(overall_standings) if team not in final_teams]

        return {
            'matchups': matchups,
            'standings': {
                'Canada': canada_standings,
                'USA': usa_standings
            },
            'playoffs': {
                'semis': semis,
                'final': final_teams,
                'champion': champion
            },
            'lottery': lottery
        }

    else:
        teams = ['Colorado', 'Philadelphia', 'Alaska', 'Georgia', 'Miami']
        matchups = [(teams[i], teams[j]) for i in range(len(teams)) for j in range(i + 1, len(teams))]

        wins = defaultdict(int)
        for t1, t2 in matchups:
            winner = random.choice([t1, t2])
            wins[winner] += 1

        standings = [(team, wins.get(team, 0)) for team in teams]
        standings.sort(key=lambda x: x[1], reverse=True)

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

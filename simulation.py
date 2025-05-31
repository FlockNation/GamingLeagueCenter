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
            for team in conf:
                opponents = [t for t in conf if t != team]
                selected_opponents = random.sample(opponents, 3)
                for opp in selected_opponents:
                    pair = tuple(sorted([team, opp]))
                    if pair not in matchups:
                        matchups.append(pair)

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

        seed1 = overall_standings[0][0]
        seed2 = overall_standings[1][0]
        seed3 = overall_standings[2][0]
        seed4 = overall_standings[3][0]
        seed5 = overall_standings[4][0]

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


        lottery = [team for team, _ in overall_standings[5:]]

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
        final_teams = [team1, team2]
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

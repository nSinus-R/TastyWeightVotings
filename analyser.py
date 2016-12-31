from tinydb import TinyDB, Query
import numpy as np

import IPython


def get_voted_events(team):
    query = Query()
    db = TinyDB('tastyWeighting.json')
    votings_t = db.table('votings')

    votes = votings_t.search(query.best_team == team)

    return set([v['event_id'] for v in votes])

def get_team_placements_for_events(events, teams):

    team_placements = {t: [] for t in teams}


    for event, votes in events:
        vote_dict = {v[0]:v[3] for v in votes }

        for t in teams:
            team_placements[t].append( vote_dict.get(t , np.nan))

    return team_placements

def get_events_with_votes_for_teams(event_ids, teams):

    events = {}
    for event_id in event_ids:
        events[get_event_name(event_id)] = get_averagized_teamvotes(event_id, teams)

    events = [(k,v) for k,v in events.items()]

    return events

def get_team_votings_for_events(events, teams, normalize_votes=False):

    team_votings = {t: [] for t in teams}

    for event, votes in events:

        if normalize_votes:
            #we don't have access to what was the maximum allowed score ...
            #thus, we take the maximum vote
            max_voting = get_max_vote_for_event_by_name(event)
            vote_dict = {v[0]:(v[1] / max_voting * 100) for v in votes }
        else:
            vote_dict = {v[0]:v[1] for v in votes }

        for t in teams:
            team_votings[t].append( vote_dict.get(t , np.nan))

    return team_votings

def get_averagized_teamvotes(event_id, teams=None):
    query = Query()
    db = TinyDB('tastyWeighting.json')
    votings_t = db.table('votings')

    votings =  votings_t.search((query.event_id == event_id) & (query.last_vote == True) & (query.placement != float('inf')))

    teamvotes_cumulative = {}
    teamvotes_cnt = {}
    team_placements = {}
    for v in votings:
        team_name = v['best_team']
        #skip teams we are not interested in
        if teams and team_name not in teams:
            continue
        teamvotes_cumulative[team_name] =  teamvotes_cumulative.get(team_name, 0) + v['vote']
        teamvotes_cnt[team_name] = teamvotes_cnt.get(team_name, 0) + 1
        team_placements[team_name] = v['placement']

    return [(t, teamvotes_cumulative[t] / teamvotes_cnt[t], teamvotes_cnt[t], team_placements[t]) for t in teamvotes_cumulative]


def get_event_scores(event_id):
    query = Query()
    db = TinyDB('tastyWeighting.json')
    votings = db.table('votings')

    votings = votings.search((query.event_id == event_id) & (query.last_vote == True) & (query.placement != float('inf')))

    return sorted(list(set([(v['best_team'],v['score']) for v in votings])), key=lambda x: x[1], reverse=True)


def get_event_name(event_id):
    query = Query()
    db = TinyDB('tastyWeighting.json')
    events = db.table('events')

    return events.get(query.event_id == event_id)['event_name']


def get_max_vote_for_event(event_id):
    query = Query()
    db = TinyDB('tastyWeighting.json')
    votings_t = db.table('votings')

    return  float(max([v['vote'] for v in votings_t.search(query.event_id == event_id)]))


def get_max_vote_for_event_by_name(event_name):

    query = Query()
    db = TinyDB('tastyWeighting.json')
    events_t = db.table('events')

    event_id = events_t.get(query.event_name == event_name)['event_id']

    return get_max_vote_for_event(event_id)

def get_top_voting_teams(n):
    query = Query()
    db = TinyDB('tastyWeighting.json')
    votings_t = db.table('votings')

    players_t = db.table('players')

    teams = {}
    voted_events = {}
    for v in votings_t.search((query.last_vote == True) & (query.best_team != 'no team')):
        team = v['best_team']
        if team in voted_events and v['event_id'] in voted_events[team]:
            continue
        teams[team] = teams.get(team, 0) + 1
        if team in voted_events:
            voted_events[team].append(v['event_id'])
        else:
            voted_events[team] = [v['event_id']]

    teams_sorted = sorted(teams, key=teams.get,reverse=True)
    return teams_sorted[:n]

def get_all_event_ids():
    query = Query()
    db = TinyDB('tastyWeighting.json')
    events = db.table('events')

    return  [e['event_id'] for e in events.all()]


def spawn_ipython_with_db():
    query = Query()
    db = TinyDB('tastyWeighting.json')
    votings_t = db.table('votings')
    events_t  = db.table('events')
    players_t = db.table('players')


    IPython.embed()

if __name__ == '__main__':
    spawn_ipython_with_db()

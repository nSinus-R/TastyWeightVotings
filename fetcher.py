#!/usr/bin/env python
#coding: utf-8

"""
Correlate voting to team placement
"""
import sys
import os
import requests
import json
from lxml import html
from pprint import pprint
import pickle
from functools import wraps
from tabulate import tabulate
from time import time
from tinydb import TinyDB, Query

def parse_event(event_id):
    """
    Parse the weights of an event
    """


    db = TinyDB('tastyWeighting.json')
    query = Query()
    players = db.table('players')
    events = db.table('events')
    votings = db.table('votings')


    result =  events.search(query.event_id == event_id)
    if result:
        print '[+] Found in database'
        return


    page = requests.get("https://ctftime.org/event/%d/weight/" % event_id)
    tree = html.fromstring(page.content)



    votes = map(int, tree.xpath('/html/body/div[2]/div[2]/p/span/text()'))
    # need to skip first strong link because it is a signup link
    usernames = [
        username
        for username in \
            map(unicode, tree.xpath('/html/body/div[2]/div[2]/p/strong/a/text()'))
        if username != "Sign in"
        ]
    userlinks = [
        userlink
        for userlink in \
            map(str, tree.xpath('/html/body/div[2]/div[2]/p/strong/a/@href'))
        if userlink != "/login/"
        ]

    # Let's get the teams each user is in:
    team_memberships = []
    for username, userlink in zip(usernames, userlinks):
        result = players.search(query.name == username)
        if result:
            team_memberships.append(result[0]['teams'])
        else:
            memberships = get_teams(userlink)
            players.insert({'name': username, 'teams': memberships})
            team_memberships.append(memberships)

    # We assume that each user will want to benefit their highest-ranked team
    placings = get_event_placements(event_id)
    placings_d = dict(placings)
    teams = [
        min({
            placings_d[team]
            for team in member_teams if team in placings_d
            } or {'no team': float('inf')})
        for member_teams in team_memberships
        ]

    team_names = [placings[t-1][0] if t != 'no team' else 'no team' for t in teams ]

    placements = [
        min([
            placings_d[team]
            for team in member_teams if team in placings_d
        ] or [float('inf')])
        for member_teams in team_memberships
        ]

    scorings = dict(get_event_scores(event_id))
    scores = [scorings[t] if t != 'no team' else float('inf') for t in team_names]

    voteids = []
    for u,m,t,p,s,v in zip(usernames, team_memberships, team_names, placements, scores, votes):
        last_vote = True
        if votings.search((query.username == u) &  (query.event_id == event_id)):
            last_vote = False
        id = votings.insert({'event_id': event_id, 'username': u, 'teams': m.keys(),
                             'best_team': t, 'placement': p, 'score': s, 'vote': v,
                             'last_vote': last_vote})
        voteids.append(id)

    event_json = requests.get("https://ctftime.org/api/v1/events/%d/" % event_id).json()

    id = events.insert({'event_id': event_id, 'event_name': event_json['title'], 'time': event_json['finish'], 'weight': event_json['weight'], 'vote_ids': voteids})

    return id

def get_event_placements(event_id):
    page = requests.get("https://ctftime.org/event/%d/" % event_id)
    tree = html.fromstring(page.content)
    teams = map(unicode,tree.xpath('/html/body/div/table/tr/td/a/text()'))
    scores = map(int, tree.xpath('/html/body/div/table/tr/td[2]/text()'))
    return zip(teams, scores)

def get_event_scores(event_id):
    page = requests.get("https://ctftime.org/event/%d/" % event_id)
    tree = html.fromstring(page.content)
    teams = map(unicode,tree.xpath('/html/body/div/table/tr/td/a/text()'))
    scores = map(float, tree.xpath('/html/body/div/table/tr/td[4]/text()'))
    return zip(teams, scores)

def get_teams(userlink):
    """
    Get the team from a link to a user
    """
    page = requests.get("https://ctftime.org%s" % userlink)
    tree = html.fromstring(page.content)
    teams = tree.xpath('/html/body/div[2]/table/tr/td/a/text()')
    teamlinks = tree.xpath('/html/body/div[2]/table/tr/td/a/@href')
    return dict(zip(map(unicode, teams), map(str, teamlinks)))

def get_team_placement(teamlink, eventid):
    """
    Get the placement of a team at a certain CTF
    """
    page = requests.get("https://ctftime.org%s" % teamlink)
    tree = html.fromstring(page.content)
    placement = tree.xpath(
        '//*/table/tr/td[3]/a[@href="/event/%s"]'
        '/../../td[@class="place"]/text()'
        % eventid)
    try:
        return int(placement[0])
    except IndexError:
        # did not participate, give worst rating ever
        return float('inf')


#according to @ctf_time, weight voting got implemented in 2016/02/29
def get_events_with_voting(start = 1456704000, end = None):
    end = int(time()) if not end else end



    db = TinyDB('tastyWeighting.json')
    query = Query()
    players = db.table('players')
    events = db.table('events')
    votings = db.table('votings')

    #ctftime api has a bug. limit 0 ignores the finish parameter
    url = "https://ctftime.org/api/v1/events/?limit=1000000&start=%d&finish=%d" % (start, end)
    page = requests.get(url)
    all_events = page.json()

    for event in all_events:
        #we don't care about events with unfinished voting
        if event['public_votable'] and not event['is_votable_now'] and int(event['weight']) != 0:
            print "[+] Fetching Votings results for: %s (%d)" % (event['title'], event['id'])
            id = parse_event(event['id'])
            event_votings = votings.search(query.event_id == event['id'])
            #print tabulate(event_votings, headers=["username", "member in teams", "best ranked team", "placement", "score:", "vote"])



if __name__ == "__main__":
    get_events_with_voting()
    #parse_event(int(sys.argv[1]))

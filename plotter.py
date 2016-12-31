from analyser import *

import matplotlib.pyplot as plt
import numpy as np
import itertools
import textwrap

def plot_average_normalized_vote_of_teams(teams):

    event_ids = set()
    for t in teams:
        event_ids |= get_voted_events(t)

    events = get_events_with_votes_for_teams(event_ids, teams)
    team_votings = get_team_votings_for_events(events, teams, normalize_votes=True)
    averaged_team_votings = [(tv,np.average([v for v in team_votings[tv] if str(v) != 'nan'])) for tv in team_votings]

    y = [v[1] for v in averaged_team_votings]
    x = np.arange(len(y))
    labels = ["%s" % (v[0].encode('ascii','replace')) for v in averaged_team_votings]

    plt.figure()
    plt.title('Averaged Normalized Vote by Team')

    plt.xlabel('Teams')
    plt.xticks(x + 0.4, labels, rotation=90)
    plt.axes().xaxis.set_ticks_position('none')

    plt.ylabel('Averaged Normalized Vote')

    plt.bar(x,y,0.8)
    plt.ylim(0, 100)

    plt.tight_layout()
    plt.savefig('figs/averaged_normalized_team_votes.png')
    plt.close()


def plot_team_ranks_vs_votes(team, normalize_votes = False):

    event_ids = get_voted_events(team)
    events = get_events_with_votes_for_teams(event_ids, [team])
    ranks = get_team_placements_for_events(events, [team])
    votes = get_team_votings_for_events(events, [team], normalize_votes = normalize_votes)


    if normalize_votes:
        ylabel_name = 'Normalized Vote'
        file_name   = 'figs/%s_votes_vs_ranks_normalized.png' % team
        title       = '%s (normalized)' % team
    else:
        ylabel_name = 'Vote'
        file_name   = 'figs/%s_votes_vs_ranks_absolute' % team
        title       = '%s (absolute)' % team

    plt.figure()
    plt.title(title)

    plt.plot(ranks[team],votes[team], 'o', clip_on=False)

    plt.xlabel('Rank')
    if max(ranks[team]) > 100:
        plt.xlim(0, max(ranks[team]))
    else:
        plt.xlim(0,100)

    plt.ylabel(ylabel_name)
    plt.ylim(0, 100)

    plt.tight_layout()
    plt.savefig(file_name)
    plt.close()

def plot_team_votes_and_ranks(team, normalize_votes=False):
    event_ids = get_voted_events(team)

    events = get_events_with_votes_for_teams(event_ids, [team])

    team_votings = get_team_votings_for_events(events, [team], normalize_votes = normalize_votes)
    team_placements = get_team_placements_for_events(events, [team])


    if normalize_votes:
        ylabel_name = 'Normalized Vote'
        file_name   = 'figs/%s_votes_and_ranks_normalized.png' % team
        title       = '%s (normalized)' % team
    else:
        ylabel_name = 'Vote'
        file_name   = 'figs/%s_votes_and_ranks_absolute' % team
        title       = '%s (absolute)' % team

    x = np.arange(len(events))
    fig, ax1 = plt.subplots()
    plt.title(title)
    labels = [e[0].encode('ascii','ignore') for e in events]
    labels = [ '\n'.join(textwrap.wrap(l, 20)) for l in labels ]

    ax1.plot(x, team_votings[team], 'o', marker='s', clip_on = False, color='b')
    ax1.set_ylabel(ylabel_name, color = 'b')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=90)

    ax2 = ax1.twinx()
    ax2.plot(x, team_placements[team], 'o', marker='s', clip_on = False, color='r')
    ax2.set_ylabel('Placement', color = 'r')
    ax2.set_ylim(100, 0)

    plt.tight_layout()
    plt.savefig(file_name)
    plt.close()


def plot_teamtrends(teams, normalize_votes=False):

    event_ids = set()
    for t in teams:
        event_ids |= get_voted_events(t)

    events = get_events_with_votes_for_teams(event_ids, teams)
    team_votings = get_team_votings_for_events(events, teams, normalize_votes= normalize_votes)

    if normalize_votes:
        ylabel_name = 'Normalized Vote'
        file_name   = 'figs/teamtrends_normalized.png'
    else:
        ylabel_name = 'Vote'
        file_name   = 'figs/teamtrends_absolute.png'


    marker = itertools.cycle(('o','s','^',))
    x = np.arange(len(events))
    plt.figure()
    labels = [e[0] for e in events]

    plt.xlabel('CTF')
    plt.xticks(x, labels, rotation=90)

    plt.ylabel(ylabel_name)

    for t in teams:
        plt.plot(x,team_votings[t],'o', marker=marker.next(),clip_on=False,label=t)
    lgd = plt.legend(bbox_to_anchor=(1, 0.8), loc='best', numpoints = 1)

    plt.tight_layout()
    plt.savefig(file_name, bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close()


def plot_event_votes_vs_placement(event_id):

    scores = get_event_scores(event_id)
    if not scores:
        print '[-] Missing scores for event, aborting'
        return

    teamvotes = get_averagized_teamvotes(event_id)

    final_votes = sorted([(t[3], t[0], t[1]) for t in teamvotes])

    y = [v[2] for v in final_votes]
    x = np.arange(len(y))
    labels = ["%d: %s" % (v[0], v[1].encode('ascii','replace')) for v in final_votes]


    plt.figure()
    plt.title(get_event_name(event_id))

    plt.xlabel('Teams by placement')
    plt.xticks(x + 0.4, labels, rotation=90)
    plt.axes().xaxis.set_ticks_position('none')

    plt.ylabel('Vote')

    plt.bar(x,y,0.8)
    plt.ylim(0, 100)

    plt.tight_layout()
    plt.savefig('figs/event_votings_placement_%d.png' % event_id)
    plt.close()


def plot_event_votes_vs_scores(event_id):

    scores = get_event_scores(event_id)
    if not scores:
        print '[-] Missing scores for event, aborting'
        return

    max_score = scores[0][1]
    normalized_scores = [ (s[0], (s[1] / max_score * 100)) for s in scores]

    teamvotes = get_averagized_teamvotes(event_id)

    final_votes = sorted([(dict(normalized_scores)[t[0]], t[0], t[1]) for t in teamvotes])

    x = [v[0] for v in final_votes]
    y = [v[2] for v in final_votes]

    plt.figure()
    plt.title(get_event_name(event_id))

    plt.plot(x,y, 'o', clip_on=False)

    plt.xlabel('Normalized Score')
    plt.xlim(0, 100)

    plt.ylabel('Vote')
    plt.ylim(0, 100)

    plt.tight_layout()
    plt.savefig( 'figs/event_votings_scores_%d.png' % event_id)
    plt.close()



if __name__ == '__main__':
    top10 = ['dcua', 'Dragon Sector', u'LC\u21afBC', 'p4', '217', 'Tasteless',  'TokyoWesterns', 'Eat, Sleep, Pwn, Repeat']

    top_voters = get_top_voting_teams(10)
    teams = set(top10) | set(top_voters)

    print '[+] Plotting averaged normalized votes of teams'
    plot_average_normalized_vote_of_teams(teams)


    print '[+] Plotting teamtrends'
    plot_teamtrends(teams, normalize_votes=False)
    plot_teamtrends(teams, normalize_votes=True)

    for t in teams:
        print '[+] Plotting Votes&Ranks for %s' % t
        plot_team_votes_and_ranks(t, normalize_votes=False)
        plot_team_votes_and_ranks(t, normalize_votes=True)


    for t in teams:
        print '[+] Plotting Votes/Ranks for %s' % t
        plot_team_ranks_vs_votes(t, normalize_votes=False)
        plot_team_ranks_vs_votes(t, normalize_votes=True)


    for id in get_all_event_ids():
        print '[+] Plotting data for %s (%d)' % ( get_event_name(id), id)
        plot_event_votes_vs_placement(id)
        plot_event_votes_vs_scores(id)

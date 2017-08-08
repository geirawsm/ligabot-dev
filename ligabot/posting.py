#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import ligabot.caching
import ligabot.uselog
import ligabot.config

caching = ligabot.caching
config = ligabot.config.get_config()

uselog = ligabot.uselog.uselog


def make_round_post(league, round_input, table_input, league_name,
                    active_round):
    '''
    Makes a round post based in 'round_input' and 'table_input'
    '''
    output = "**Tabell før runden:**\n\n"
    if league == '1':
        output += '######[](http://reddit.com#)\n'
    elif league == '2':
        output += '#####[](http://reddit.com#)\n'
    elif league == '3':
        output += '###[](http://reddit.com#)\n'
    output += 'Nr|Lag|K|V|U|T|M+|M-|MF|P|Møter\n'
    output += "---:|:---|:---:|---:|---:|---:|---:|---:|---:|:---|:---\n"
    for team in table_input:
        output += '{}|{}{}|{}|{}|{}|{}|{}|{}|{}|{}|{}\n'\
            .format(team['place'], team['flair'], team['team'],
                    team['matches'], team['w'], team['d'], team['l'],
                    team['plus'], team['minus'], team['diff'], team['points'],
                    team['versus'])
    output += "\n\n&nbsp;\n\n**Rundens kamper:**\n\n"
    output += "Dato|Hjemmelag||Bortelag|TV-kanal/Streaming\n"
    output += ":---|---:|:---:|:---|:---\n"
    output += '[](#kamper){}[](/kamper)'.format(
        make_round_post_matches(round_input))
    output += '\n\n###[](http://reddit.com#)\nHar du forslag til endringer '\
        'eller ser du feil i denne posten? [Si ifra her!](http://reddit.com'\
        '/message/compose/?to={}&subject=Tips%20til%20endring/feil%20i%20ru'\
        'nde-poster%20%28tl%29)'.format(config['reddit']['username'])
    return output


def make_round_post_matches(matches):
    temp_round = ''
    for match in matches:
        if match['tv2sumo']:
            match['channel'] = '{} / {}'.format(match['channel'],
                                                match['tv2sumo'])
        temp_round += '{}|({})&nbsp;{}&nbsp;({})|[{}]({})|({})&nbsp;{}'\
                      '&nbsp;({})|{}\n'.format(match['date'],
                                               match['home_table'],
                                               match['home'],
                                               match['home_form'],
                                               match['status_text'],
                                               match['status_link'],
                                               match['away_form'],
                                               match['away'],
                                               match['away_table'],
                                               match['channel'])
    return temp_round


def check_postponed_matches(table):
    '''Get postponed matches, check their date and post them'''
    global fulldate
    global postponed_file
    caching.clean_cache(postponed_file)
    postponed_matches = []
    # Check postponed matches
    # If matches within time frame, post them
    _postponed_matches = caching.read_cache(postponed_file).split('\n')
    for match in _postponed_matches:
        if match == '':
            continue
        else:
            make_list = ast.literal_eval(match)
            match = [i.strip() for i in make_list]
            match_date = '{} {}.00'.format(match[0], match[7])
            if seconds_to(fulldate, match_date) <= 259200:
                print('run postponed match: {}'.format(match))
                postponed_matches.append(match)
            else:
                print('skip this match: {}'.format(match))
    #print(make_postponed_post(postponed_matches, table))


def make_postponed_post(league, match_input, table_input):
    if len(match_input) > 1:
        output = "**Utsatte kamper:**\n\n"
    else:
        output = "**Utsatt kamp:**\n\n"
    if league == '1':
        output += '######[](http://reddit.com#)\n'
    elif league == '2':
        output += '#####[](http://reddit.com#)\n'
    elif league == '3':
        output += '###[](http://reddit.com#)\n'
    output += 'Nr|Lag|K|V|U|T|M+|M-|MF|P|Møter\n'
    output += "---:|:---|:---:|---:|---:|---:|---:|---:|---:|:---|:---\n"
    output += tableize(table_input)
    if len(match_input) > 1:
        output += "\n\n&nbsp;\n\n**Kamper:**\n\n"
    else:
        output += "\n\n&nbsp;\n\n**Kamp:**\n\n"
    output += "Dato|Hjemmelag||Bortelag|TV-kanal/Streaming\n"
    output += ":---|---:|:---:|:---|:---\n"
    output += '[](#kamper){}[](/kamper)'.format(tableize(match_input))
    output += '\n\n###[](http://reddit.com#)\nHar du forslag til endringer '\
        'eller ser du feil i denne posten? [Si ifra her!](http://reddit.com'\
        '/message/compose/?to={}&subject=Tips%20til%20endring/feil%20i%20ru'\
        'nde-poster%20%28tl%29)'.format(config['reddit']['username'])
    return output


def thread_already_created(r, league_name, round_number, subreddit):
    '''Checks if the thread has been posted earlier'''
    global liganavn
    stikkord = ['Dato', 'Hjemmelag', 'Bortelag', 'TV-kanal/Streaming']
    subreddit = r.subreddit(subreddit)
    for submission in subreddit.new(limit=40):
        if round_number in submission.title\
                and league_name in submission.title:
            if all(word.lower() in str(submission.selftext).lower()
                   for word in stikkord):
                return submission.id
        else:
            continue


def post_to_reddit(r, league_name, round_number, post_text, subreddit):
    '''
    Tries to post the 'post_text' to the 'subreddit, but will first check
    if the post already has been submitted.
    In any situation, this function will always return the submission object.
    '''
    # Check first if it already has been submitted
    _already_created = thread_already_created(r, league_name, round_number,
                                              subreddit)
    if _already_created:
        subm = r.submission(_already_created)
        uselog('Seems that this already has been posted. '
               'Got submission.id \'{}\''.format(subm.id))
        return subm
    else:
        uselog('Post doesn\'t exist, posting.')
        post_title = '{}, {}. runde'.format(league_name, round_number)
        subm = r.subreddit(subreddit).submit(
            post_title,
            selftext=post_text,
            send_replies=False,
            resubmit=False
        )
        # subm_link = 'http://redd.it/{}'.format(subm.id)
        return subm


def post_already_created(r, key_words, subm_id):
    '''Checks if the post has been posted earlier'''
#    for comment in r.submission(subm_id):
#        if round_number in submission.title and league_name in submission.title:
#            if all(word.lower() in str(submission.selftext).lower()
#                   for word in stikkord):
#                return submission.id
#        else:
#            continue


def post_match_threads(submission_object, matches):
    '''
    Makes a match thread for every match in this round

    Needs the links to the individual matches,
    gets necessary info through 'match_info' function
    Always check if the bot already has made a thread and get its id
    If not, make an id for the main comment
    '''
    for match in matches:
        match['status_link']
        key_words = []
        sys.exit()

        post_text = '**Kamptråd**\n\nKamp: {home} - {away}\n\nStart: {date}, kl '\
            '{time}\n\nDommer:[](#dommer){dommer}[](/dommer)\n\nLagoppstillinger:[](#dommer){dommer}[](/dommer)\n\n'

#Hjemme|Borte
#:---|:---
#lanslnd|alsdnalsdn
#as|sa
#ele|elele


def post_update(r, tag, new_content, submission=None, comment=None):
    '''
    Updates a submission or a comment between tags with new_content.
    '''
    if submission:
        temp_item = r.submission(submission)
        temp_content = temp_item.selftext
    elif comment:
        temp_item = r.comment(comment)
        temp_content = temp_content.body
    else:
        uselog('You didn\'t specify neither a submission or a comment.\n'
               'Tried to insert this text: \'{}\''.format(new_content))
        sys.exit()
    temp_content_kamper = re.search(r'.*\[\]\(#{tag}\)((.|\n)*)'
                                    '\[\]\(\/{tag}\).*'.format(tag=tag),
                                    temp_content,
                                    flags=re.MULTILINE | re.DOTALL).group(1)
    if temp_content_kamper == new_content:
        uselog('No changes discovered. Sleeping.')
    else:
        uselog('Discovered new scores, updating...')
        temp_content = re.sub(
            r'\[\]\(\#{tag}\)((.|\n)*)\[\]\(\/{tag}\)'.format(tag=tag),
            '[](#{tag}){new_content}[](/{tag})'.format(new_content=new_content,
                                                       tag=tag
                                                       ),
            temp_content,
            flags=re.MULTILINE | re.DOTALL
        )
        temp_item.edit(temp_content)
        uselog('Updated! Sleeping.')


if __name__ == "__main__":
    print('Running \'posting.py\' as module.')

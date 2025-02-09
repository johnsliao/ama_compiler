import os
import praw
import sqlite3
import datetime
from dotenv import load_dotenv 

load_dotenv() 

from praw.models import MoreComments

client_id = os.environ.get('REDDIT_CLIENT_ID')
client_secret = os.environ.get('REDDIT_SECRET')
password = os.environ.get('REDDIT_PASSWORD')
user_agent = os.environ.get('REDDIT_USER_AGENT')
username = os.environ.get('REDDIT_USERNAME')

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                     password=password, user_agent=user_agent,
                     username=username)
header = '''
Table of Questions and Answers. Original answer linked - Please upvote the original questions and answers. (I'm a bot.)
***
'''

footer = '''
# ---
# [Source](https://github.com/johnsliao/ama_compiler)
# '''


def compile(submission):
    """
    Parses comments and returns Q&A as a reddit-friendly table format.
    :param submission:
    :return:
    """
    comments_exist = False

    comment_text = ''
    comment_text += header
    comment_text += '\n'
    comment_text += 'Question | Answer | Link'
    comment_text += '\n'
    comment_text += '---------|----------|----------|'
    comment_text += '\n'

    author = submission.author
    for comment in submission.comments:
        if isinstance(comment, MoreComments):
            continue
        if comment.score <= 0:
            continue

        for reply in comment._replies:
            if isinstance(reply, MoreComments):
                continue
            if reply.author == author:
                answer = ' '.join([l.strip() for l in reply.body.split('\n')])
                question = ' '.join([l.strip() for l in comment.body.split('\n')])

                if answer.endswith('?'):
                    break

                if len(comment_text + question + '|' + answer + '|[Here](' + comment.permalink + ')' + footer) > 9500:
                    break

                comment_text += question + '|' + answer + '|[Here](' + comment.permalink + ')'
                comment_text += '\n'
                comments_exist = True
                break

    comment_text += footer

    if not comments_exist:
        return None

    return comment_text


if __name__ == '__main__':
    conn = sqlite3.connect('db.db')
    c = conn.cursor()

    for submission in reddit.subreddit('ama').top(limit=256, time_filter='week'):

        submission_age = datetime.datetime.now() - datetime.datetime.utcfromtimestamp(submission.created_utc)  # seconds
        if submission_age < datetime.timedelta(seconds=60 * 60 * 24):
            # Post is less than 24 hours old
            continue
        if submission_age > datetime.timedelta(seconds=60 * 60 * 24 * 7):
            # Post is older than 1 week old
            continue
        if '[Request]' in submission.title:
            continue
        if submission.score < 10:
            continue

        c.execute("select * from posts where post_id=:post_id", {"post_id": submission.id})
        if c.fetchone():
            continue

        try:
            comment_text = compile(submission)

            if not comment_text:
                continue

            submission.reply(comment_text)
            c.execute("insert into posts (date, post_id) values (?,?)", [datetime.date.today(), submission.id])
            conn.commit()
            print('Successfully added comment to {}'.format(submission.id))
            exit(1)
        except Exception as e:
            print(e)
            exit(1)

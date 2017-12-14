import os
import praw
import sqlite3
import datetime

client_id = os.environ.get('REDDIT_CLIENT_ID')
client_secret = os.environ.get('REDDIT_SECRET')
password = os.environ.get('REDDIT_PASSWORD')
user_agent = os.environ.get('REDDIT_USER_AGENT')
username = os.environ.get('REDDIT_USERNAME')

reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                     password=password, user_agent=user_agent,
                     username=username)


def compile(submission):
    """
    Parses comments and returns Q&A as a reddit-friendly table format.
    :param submission:
    :return:
    """
    comment_text = 'Question | Answer'
    comment_text += '\n'
    comment_text += '---------|----------|'
    comment_text += '\n'

    author = submission.author
    for comment in submission.comments:
        if comment.score <= 0:
            continue

        for reply in comment._replies:
            if reply.author == author:
                answer = ' '.join([l.strip() for l in reply.body.split('\n')])
                question = ' '.join([l.strip() for l in comment.body.split('\n')])

                if answer.endswith('?'):
                    break

                comment_text += question + '|' + answer
                comment_text += '\n'
                break

    return comment_text


if __name__ == '__main__':
    conn = sqlite3.connect('db.db')
    c = conn.cursor()

    for submission in reddit.subreddit('ama').hot(limit=256):
        if '[Request]' in submission.title:
            continue

        if submission.score < 10:
            continue

        c.execute("select * from posts where post_id=:post_id", {"post_id": submission.id})
        if c.fetchone():
            continue

        if datetime.datetime.now() - datetime.datetime.utcfromtimestamp(submission.created_utc) < datetime.timedelta(
                seconds=60 * 60 * 24):
            # Post is less than 24 hours old
            continue

        print(compile(submission))

# Reddit AMA Bot

## What does this bot do?
This bot makes it easier for redditors to read through the question and answers from /r/AMA.

## When will the bot post to a thread?
- Comment score must be > 0
- Comment must end with a "?"
- Submission is older than 24 hours old
- Submission is younger than 48 hours old
- Submission score must be greater than 10
- Submission is not a `[REQUEST]`
- Have not posted on the thread before (stored in a sqlite database)

## Setting up your own ama bot
1. Clone this repo
2. Get reddit [API keys](https://github.com/reddit/reddit/wiki/API).
3. Set the following environment variables:
    ```
    REDDIT_CLIENT_ID
    REDDIT_SECRET
    REDDIT_PASSWORD
    REDDIT_USER_AGENT
    REDDIT_USERNAME
    ```
4. Run the script (used Python 2.7.x)
    ```
    python app.py
    ```

import os
import time
from app.actions import parse_bot_commands, handle_command
from slackclient import SlackClient


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM


if __name__ == '__main__':
    if slack_client.rtm_connect(with_team_state=False):
        print('Boston Info Slack Bot connected and running!')
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

import json
import os

from ciscosparkbot import SparkBot
from flask import request, make_response

from codec.actions import get_whoami, send_message, get_diag, send_dial, get_last

bot_email = os.getenv("SPARK_BOT_EMAIL")
spark_token = os.getenv("SPARK_BOT_TOKEN")
bot_url = os.getenv("SPARK_BOT_URL")
bot_roomid = os.getenv("SPARK_BOT_ROOMID")
bot_app_name = os.getenv("SPARK_BOT_APP_NAME")
codec_username = os.getenv("CODEC_USERNAME")
codec_password = os.getenv("CODEC_PASSWORD")


bot = SparkBot(bot_app_name, spark_bot_token=spark_token,
               spark_bot_url=bot_url, spark_bot_email=bot_email, debug=True)


@bot.route('/codec', methods=['POST'])
def receivepostfromcodec():
    response = request.data
    try:
        # check to see if a button was clicked
        data = json.loads(request.data)
        action=data['Event']['UserInterface']['Extensions']['Widget']['Action']['Type']['Value']
        print("Received action type: {}".format(action))
    except Exception as e:
        # log any errors (brief)
        print("Request did not contain any action type: {}".format(e))
        return make_response("ok")

    # determine appropriate action based on event
    print("Attempting to determine response for received action:")
    if action == 'clicked':
        # gather some details about the clicked action
        print(data)
        button_pressed = data['Event']['UserInterface']['Extensions']['Widget']['Action']['WidgetId']['Value']

        identification = data['Event']['Identification']
        SysName = identification['SystemName']['Value']
        SysVersion = identification['SWVersion']['Value']
        msg2spark = "Received message from room **{}** (running {}).  User pressed button: **{}**".format(SysName,SysVersion,button_pressed)
        message = bot.spark.messages.create(roomId=bot_roomid, markdown=msg2spark)
        return make_response("ok")
    else:
        print("nothing to do")
        return make_response("ok")


bot.add_command('diag',
                "get the diagnostics from a codec. \
                e.g. `@{} diag 10.1.1.1`".format(bot_email.split('@')[0]),
                get_diag)
bot.add_command('dial',
                "remotely dial a URI/Number from a codec. \
                e.g. `@{} dial 10.1.1.1 loopback@cisco.com`".format(bot_email.split('@')[0]),
                send_dial)
# bot.add_command(':list',
#                "display a list of all the codecs. \
#                e.g. `@{} :list`".format(bot_email.split('@')[0]),
#                list)
bot.add_command('last', "display call history from a codec. \
                e.g. `@{} last 10.1.1.1 5`".format(bot_email.split('@')[0]),
                get_last)
bot.add_command('send',
                "send a message to a codec. \
                e.g. `@{} send 10.1.1.1 <message e.g. I will be over in 5 minutes>`".format(bot_email.split('@')[0]),
               send_message)
# bot.add_command(':question',
#                "send a yes/no question to a codec. \
#                e.g. `@{} my_codec:question Can I help you?`".format(bot_email.split('@')[0]),
#                question)
bot.add_command('whoami',
                "display codec details \
                e.g. `@{} whoami 10.1.1.1`".format(bot_email.split('@')[0]),
                get_whoami)
bot.run(host='0.0.0.0', port=5000)

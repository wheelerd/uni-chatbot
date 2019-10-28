#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot

#calling query module 
from ..query import queryChatbot 

app = Flask(__name__)
ACCESS_TOKEN = 'EAAFyaMBjoygBALqoEea3HEQKKZCgMbkXDFhQ8i23N7uRqOvJuIMHDAMIw9XyHvZAiCfE2kJW34NBu5jHnetXggtXCZCfTa5yPwB1k1hLAiwyzO90EPtwDMVW42hZAbmcjV6OakGZA9eRpujegZA8gebyEmBcUf4G3Nf6kCmIDtcdXowQetgzglFEJq2Wv7ZBL8ZD'
VERIFY_TOKEN = 'testtoken'
bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    response_sent_text = get_message()
                    querRes = queryChatbot(response_sent_text)
                    send_message(recipient_id, querRes)
    
                """#if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)"""
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message():
    sample_responses = ["cool", "nice", "Keep up", "word"]
    # return selected item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


    

if __name__ == "__main__":
    app.run()

#!/usr/bin/env python3
import os
import discord

from ..query import QueryHandler

APP_TOKEN = "NjMzMzA1MjE2OTc1ODk2NTk2.XbcNKQ.gXGIEK-Rl5VEPu9717fcWWG9S6s"
APP_SERVER = "chatbot"
BOT_CHANNEL = 633304649818046468

client = discord.Client()
queryHandler = QueryHandler()

@client.event
async def on_ready():
    print(str(client.user) + " has successfully connected to Discord.")
    for guild in client.guilds:
        if guild.name == APP_SERVER:
            break

    channel = client.get_channel(BOT_CHANNEL)
    await channel.send(">>> Chatbot now online.\nUse the prefix '!' to talk to me.")

@client.event
async def on_message(message):
    print(str(message.author) + ": " + message.content)

    # dont do anything because nothing entered is relevant to the bot
    if message.author == client.user or message.channel != client.get_channel(BOT_CHANNEL) or message.content[0] != "!":
        return # if the user is the bot or the channel is not bot-chat or there is no prefix

    # Get query response
    messageSlice = message.content[1:]
    responseText, image = queryHandler.queryChatbot(messageSlice)
    
    # Prepare image if any
    imageFile = None
    if image != None:
        byteBuffer = BytesIO()
        image.save(byteBuffer, format='PNG')
        imageFile = discord.File(byteBuffer)
    
    # Send response
    await message.channel.send(responseText, file=imageFile)
        

if __name__ == '__main__':
    client.run(APP_TOKEN)


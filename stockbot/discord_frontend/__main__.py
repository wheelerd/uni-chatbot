#!/usr/bin/env python3
import os
import discord

from ..query import queryChatbot

APP_TOKEN = "NjMzMzA1MjE2OTc1ODk2NTk2.XbcNKQ.gXGIEK-Rl5VEPu9717fcWWG9S6s"
APP_SERVER = "chatbot"
BOT_CHANNEL = 633304649818046468

client = discord.Client()

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

    if "send image" in message.content.lower():
        await message.channel.send(file=discord.File('test_image.png'))
    else:
        messageSlice = message.content[1:]
        print(messageSlice)
        queryResponse = queryChatbot(messageSlice)
        await message.channel.send(queryResponse)
        

if __name__ == '__main__':
    client.run(APP_TOKEN)


# bot.py
import os
import discord

from discord.ext import commands

token = 'NjMyMTgyNDA0MzM2ODQ0ODMx.XaBsBA.m3UM0YE0zoEuOYqkCqSQeWexNUY'
serverName = 'test'

bot = commands.Bot(command_prefix=';')

@bot.command(name='hi', help='hi')
async def help(ctx):
    response = 'hi'
    await ctx.send(response)

@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('not admin')
    
bot.run(token)


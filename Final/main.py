from os import getenv
from logging import info
import discord
from discord.ext import commands
from textblob import TextBlob
from profanity_check import predict_prob

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Print a log message when ready"""
    info(f'Logged in as {bot.user.name} ({bot.user.id})')


@bot.event
async def on_message(message):
    """Event handler for messages"""
    if message.author == bot.user:
        return

    # Check for insults in the message
    if has_insults(message.content):
        await message.delete()
        await send_insult_notification(message)
        return

    await bot.process_commands(message)

def has_insults(text):
    """Check if the text contains any profane words or phrases"""
    proba = predict_prob([text])[0]

    print(f"Probability for `{text}`: {proba}")

    if proba > 0.80:
        return True

    return False

async def send_insult_notification(message):
    """Send a notification message to the channel where the message was deleted"""
    channel = message.channel

    author = message.author.mention
    content = message.content
    notification = f"Message from {author} deleted:\n\n{content}"
    await channel.send(notification)


@bot.command()
async def analyze(ctx, message_id):
    try:
        message = await ctx.channel.fetch_message(int(message_id))
        text = message.content
        sentiment = TextBlob(text).sentiment

        # Sentiment polarity ranges from -1 to 1 (-1 being negative, 1 being positive)
        polarity = sentiment.polarity

        if polarity > 0:
            reply = "That sounds positive!"
        elif polarity < 0:
            reply = "That sounds negative!"
        else:
            reply = "That sounds neutral."

        await ctx.send(reply)

    except discord.NotFound:
        await ctx.send("Message not found.")

bot_token = getenv('DISCORD_BOT_TOKEN')
bot.run(bot_token)
import openai
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from random import choice

load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')
TOKEN = os.getenv('DISCORD_TOKEN')
completion = openai.Completion()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!",intents=intents)
start_sequence = "\nUser:"
restart_sequence = "\nBot:"
baseline = """I'm a helpful and friendly chat bot.
User: Hi! How are you?
Bot: I'm amazing, thanks! How may I help you?"""
try:
    with open('chat.log', 'r') as f: chat_log = f.read()
except FileNotFoundError:
    with open('chat.log', 'w') as f: f.write(baseline)
    with open('chat.log', 'r') as f: chat_log = f.read()

def max_length():
    lines = []
    with open('chat.log', 'r') as f: lines = f.readlines()
    with open('chat.log', 'w') as f:
        for number, line in enumerate(lines):
            if number not in [3, 4]:
                f.write(line)

def ask(question, chat_log):
    prompt_text = f'{chat_log}{start_sequence} {question}{restart_sequence}'
    response = openai.Completion.create(
    engine="davinci",
    prompt=prompt_text,
    temperature=0.9,
    max_tokens=150,
    top_p=1,
    frequency_penalty=1,
    presence_penalty=0.6,
    stop=["\n"]
    )
    story = response['choices'][0]['text']
    return str(story)

def append_to_chat_log(question, answer):
    return f'{start_sequence} {question}{restart_sequence}{answer}'

@bot.event
async def on_ready():
    print(f'{bot.user} Online!')

@bot.event
async def on_message(message):
    global chat_log

    if bot.user.mentioned_in(message):
        question = message.clean_content
        answer = ask(question, chat_log)
        current_interaction = append_to_chat_log(question, answer)
        if len(chat_log) > 1500: max_length()
        chat_log = chat_log + current_interaction
        with open('chat.log', 'a') as f: f.write(f'{current_interaction}')
        print(append_to_chat_log(question, answer))
        await message.channel.send(answer)

bot.run(TOKEN)

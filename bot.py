import aiosqlite
from discord.ext import commands
import os
import json
import re
import asyncio
import numpy as np
from PIL import Image
from io import BytesIO
from tensorflow.keras.models import load_model
import aiohttp
import discord
from discord import Button, ButtonStyle, ActionRow
from collections import deque

TOKEN = "MTE3MTQ5MjkyMDUwMzgzNjcyNA.GbDlKy.eZq-CSyV5x8OFHNQCXgKVQKMu21OavFkSnp5vA"
channel_ids = [1155883879308218419, 1155883879308218420, 1155883911738576988, 1161046968970256384, 1161046968970256384, 1161046947487031367, 1155093680911294574,1155093720304193547] 
ownerid = "1062109956129701978"
poketwo = 716390085896962058
captchachannel = 1154374370647625799
bot_prefix = "."
bot = commands.Bot(command_prefix=bot_prefix, self_bot=True)
loaded_model = load_model('model.h5', compile=False)
with open('classes.json', 'r') as f:
    classes = json.load(f)

response_queue = deque()

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.offline)
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def buy_incense(ctx):
    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send('<@716390085896962058> buy incense')
            await asyncio.sleep(2)
    await ctx.send("I bought incense in all channels.")

async def process_responses():
    while True:
        if response_queue:
            response = response_queue.popleft()
            try:
                await response()
            except Exception as e:
                print(f"Error processing response: {e}")
        await asyncio.sleep(0.5)

@bot.event
async def on_message(message):
    if message.channel.id in channel_ids:
        if len(message.embeds) > 0:
            embed = message.embeds[0]
            if "appeared!" in embed.title:
                if "human" not in message.content.lower():
                    if embed.image:
                        url = embed.image.url
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url=url) as resp:
                                if resp.status == 200:
                                    content = await resp.read()
                                    image_data = BytesIO(content)
                                    image = Image.open(image_data)
                    preprocessed_image = await preprocess_image(image)
                    predictions = loaded_model.predict(preprocessed_image)
                    classes_x = np.argmax(predictions, axis=1)
                    name = list(classes.keys())[classes_x[0]]

                    async def send_response():
                        async with message.channel.typing():
                            await asyncio.sleep(0.3)

                        await message.channel.send(f'<@716390085896962058> catch {name.lower()}')

                    response_queue.append(send_response)

        elif message.content.startswith('----join'):
            invite_link = message.content[6:]
            try:
                invite = await bot.fetch_invite(invite_link)
                await invite.accept()
                await message.channel.send('Successfully joined the server!')
            except discord.errors.NotFound:
                await message.channel.send('The invite link is invalid.')
        elif 'human' in message.content:
            print('Captcha Detected')
            member = message.guild.get_member(poketwo)
            if member:
                await member.remove_roles(discord.PermissionOverwrite(administrator=False))
                await member.kick()

                pattern = r'https://verify\.poketwo\.net/captcha/[0-9]+'
                match = re.search(pattern, message.content)
                if match:
                    url = match.group()
                    channel = bot.get_channel(captchachannel)
                    await asyncio.sleep(2)
                    await channel.send(f"<@{ownerid}> Please verify the poketwo captcha asap! {url}")
        else:
            await bot.process_commands(message)

async def preprocess_image(image):
    image = image.resize((64, 64))
    image = np.array(image)
    image = image / 255.0
    image = np.expand_dims(image, axis=0)
    return image

async def run_bot():
    while True:
        try:
            await bot.start(TOKEN)
        except Exception as e:
            print(f"Bot encountered an error: {e}")
            await asyncio.sleep(60)  # Retry after a delay

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(process_responses())
    loop.run_until_complete(run_bot())

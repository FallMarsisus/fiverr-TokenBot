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
        try:
            if data["users"][i]["id"] == int(id):
                found = True
                return (found, i)
        except KeyError:
            return(found, None)
    return (found, None)

def makeProfile(id):
    global data
    data['users'][-1]["id"] = int(id)
    data['users'][-1]["coins"] = 0
    data['users'][-1]["name"] = ""
    data["users"][-1]["toadd"] = 0  

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')     

@client.event
async def on_message(message):
    global data, prefix
    # if message.author == client.user:
    #     return

    if message.content.startswith(f'{prefix}buy'):
            await message.delete()
            value = message.content.split(" ")[1]
            if not value.isdigit() or int(value)<0:
                await message.channel.send(":no_entry: You didn't enter a right amount of coins")
                return
            else:
                value = int(value)

                qr = discord.File("qr.jpeg")
                await message.channel.send(f""":information_source: Go to https://paypal.me/{paypalUser}/{value*0.10}USD in order to get your {value} :coin:
Your coins will be given after 1 to 10 hours""", file=qr)
                
                exists = verifyIfUser(message.author.id)
                if exists[0]:
                    index = exists[1]
                else:
                    index = -1
                    data["users"].append({})
                    makeProfile(int(message.author.id))
                    
                
                data['users'][index]["id"] = int(message.author.id)
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
        count = message.content.split(" ")[2]
        
        if not count.isdigit():
            await message.channel.send("Wrong Count")
            return
        
        if user[2:-1].isdigit():     
            exists = verifyIfUser(int(user[2:-1]))
        else:
            await message.channel.send(":no_entry: Username Error ! ")
        if exists[0]:
            index = exists[1]
        else:
            index = -1
            data["users"].append({})
            makeProfile(int(user[2:-1]))
            
        data['users'][index]["coins"] += int(count)
        data['users'][index]["toadd"] = 0
        
        with open("config.json", "w") as file:
            json.dump(data, file)
           
        with open("config.json", "r") as file:
            data = json.loads(file.read())

        await message.channel.send(f":white_check_mark: Successfuly Added {count} coins to {user} ! New Sold : {data['users'][index]['coins']} :coin:.")
        
    if message.content.startswith(f"{prefix}coins"):

        exists = verifyIfUser(message.author.id)

        if exists[0]:
            index = exists[1]
        else:
            index = -1
            data["users"].append({})
            makeProfile(int(message.author.id))

        embed = discord.Embed(title="Your Dashboard", description="See your coins stats !", color=0xfdff75)
        embed.set_author(name=str(data["users"][index]["coins"]) + " coins", icon_url="https://emoji.discadia.com/emojis/23fea924-f44f-4061-b0f0-b4dab898b19c.PNG")
        embed.add_field(name="Coins :", value= str(data["users"][index]["coins"]) + " :coin:", inline=True)
        embed.add_field(name="Coins being verified :", value=str(data["users"][index]["toadd"]) + " :coin:", inline=True)
        await message.channel.send(embed=embed)

    

client.run('MTEwMzM5Njc4MDg2NDk4MzExMA.GCmsvA.m9Lf70YWrSN3B0mqoU71V2wfVKjqUukANRCr_U')


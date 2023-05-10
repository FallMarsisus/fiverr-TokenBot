import discord
import json
from views import ButtonsTokens


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

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
    data["users"][-1]["inviteLink"] = ""
    data["users"][-1]["inviteCount"] = 0
    
def saveData():
    global data
    
    with open("config.json", "w") as file:
        json.dump(data, file)
                                
    with open("config.json", "r") as file:
        data = json.loads(file.read())



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')     


@client.event
async def on_member_join(member):
    global data
    
    welcomeChat = await member.guild.fetch_channel("1105797683374989392")
    await welcomeChat.send(f":information_source: Welcome {member.mention} ! If you've been invited by someone, type **{prefix}join @itsusername**.")


@client.event
async def on_message(message):
    global data, prefix
    # if message.author == client.user:
    #     return

    if message.content.startswith(f"{prefix}join"):
        await message.delete()
        
        exists = verifyIfUser(message.author.id)
        if exists[0]:
            index = exists[1]
        else:
            index = -1
            data["users"].append({})
            makeProfile(int(message.author.id))
        
        inviter = message.content.split(" ")[1]
        if not inviter[2:-1].isdigit():
            return
        inviter = int(inviter[2:-1])
        
        exists = verifyIfUser(inviter)
        if exists[0]:
            indexI = exists[1]
        else:
            indexI = -1
            data["users"].append({})
            makeProfile(inviter)
        
        
        try:
            if data['users'][index]["invited"]:
                await message.channel.send(":no_entry: You have already been invited to the server")
            
        except KeyError:
            pass
        
        data["users"][index]["invited"] = True
        data["users"][indexI]["coins"] += 2
        data["users"][indexI]["inviteCount"] += 1
        data["users"][index]["name"] = message.author.name
        
        saveData()
        
        await message.channel.send(":information_source:")
        

    if message.content.startswith(f"{prefix}invite"):
        await message.delete()
        exists = verifyIfUser(message.author.id)
        if exists[0]:
            index = exists[1]
        else:
            index = -1
            data["users"].append({})
            makeProfile(int(message.author.id))

        try:
            if len(data["users"][index]["inviteLink"]) > 0:
                await message.channel.send(f"{message.author.name}, you can't have more than one invite link pending at the same time. Your invite code is {data['users'][index]['inviteLink']}")
                return
        except KeyError:
            pass
        

        invite_link = await message.channel.create_invite()

        data["users"][index]["inviteLink"] = str(invite_link)
        data['users'][index]["inviteCount"] = 0

        await message.channel.send(f"{message.author.name}, here is your invite link : {invite_link}")


        saveData()


    if message.content.startswith(f'{prefix}buy'):
        await message.delete()
        value = message.content.split(" ")[1]
        if not value.isdigit() or int(value)<0:
            await message.channel.send(":no_entry: You didn't enter a right amount of coins")
            return
        else:
            value = int(value)

            qr = discord.File("bankqr.png")
            await message.channel.send(f""":information_source: Scan the code and pay {value*0.1} USD in order to get your {value} :coin:
                                       They"ll be given to you after 1 to 10 hour(s )""", file=qr)
            
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
                
            saveData()
                
                
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
        
        saveData()

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


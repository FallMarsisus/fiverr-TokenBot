import discord
import json
from views import ButtonsTokens
import asyncio


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.guilds = True

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
    
    """
    welcomeChat = await member.guild.fetch_channel("1105797683374989392")
    await welcomeChat.send(f":information_source: Welcome {member.mention} ! If you've been invited by someone, type **{prefix}join @itsusername**.")
    """

@client.event
async def on_message(message):
    global data, prefix
    # if message.author == client.user:
    #     return

    if message.content.startswith(f"{prefix}acceptrules"):
        await message.delete()

        role = discord.utils.get(message.author.guild.roles, name="Validated Member")

        if len(message.content.split(" ")) == 1:
            await message.author.add_roles(role)
            welcomeMessage = await message.channel.send(f":white_check_mark: {message.author.mention}, you're now in the server, enjoy !", delete_after=100)
            await asyncio.sleep(10)
            await welcomeMessage.delete()
            return
        
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
                welcomeMessage = await message.channel.send(f":no_entry: {message.author.name}, You have already been invited to the server, please retry", delete_after=10)
                await asyncio.sleep(10)
                await welcomeMessage.delete()
                
                return
        except KeyError:
            pass

        date = message.created_at
        try:
            if data["users"][indexI]["lastInviteDate"] != date.day:
                data["users"][indexI]["todayInviteCount"] = 0
            if data["users"][indexI]["todayInviteCount"] > 9:
                welcomeMessage = await message.channel.send(f":no_entry: Sorry {message.author.name}, the person who invited you has reach its 10 invitations per day limit, please retry", delete_after=10)
                await asyncio.sleep(10)
                await welcomeMessage.delete()
                return
        except KeyError:
            data["users"][indexI]["todayInviteCount"] = 0
            pass

        data["users"][indexI]["lastInviteDate"] = date.day
        data["users"][indexI]["todayInviteCount"] +=1
        
        data["users"][index]["invited"] = True
        data["users"][indexI]["coins"] += 2
        data["users"][indexI]["inviteCount"] += 1
        data["users"][index]["name"] = message.author.name
        

        saveData()
        
        await message.author.add_roles(role)
        
        welcomeMessage = await message.channel.send(f":information_source: {message.author.name}, your invitation was taken, thanks ! Welcome on the server !", delete_after=100)
        await asyncio.sleep(10)
        await welcomeMessage.delete()

    if message.channel.id == 1102281781820010550 and message.author != client.user:
        await message.delete()

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
                await message.channel.send(f":information_source: {message.author.name}, you can't have more than one invite link pending at the same time. Your invite code is {data['users'][index]['inviteLink']}")
                return
        except KeyError:
            pass
        

        invite_link = await message.channel.create_invite()

        data["users"][index]["inviteLink"] = str(invite_link)
        data['users'][index]["inviteCount"] = 0
        data["users"][index]["name"] = message.author.name

        await message.channel.send(f":information_source: {message.author.name}, here is your invite link : {invite_link}")


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
They'll be given to you after 1 to 10 hour(s)""", file=qr)
            
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
        
            
            messageGuild = await message.guild.fetch_channel("1124767650355101809")
            await messageGuild.send(f""":information_source: {message.author.mention} has just used $buy command, after a few minutes, does it show on paypal ?""", view=ButtonsTokens(prefix, message.author, value))
                
            saveData()
                
                
            print(data)
        
        return
        
    if message.content.startswith(f"{prefix}add"):
        await message.delete()
        
        if not message.author.guild_permissions.administrator:
            await message.channel.send(f":no_entry: {message.author.mention}, you aren't allowed to do that")
            return
            
        user = message.content.split(" ")[1]
        count = message.content.split(" ")[2]
        
        if not count.isdigit():
            await message.channel.send(":no_entry: Wrong Count")
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
        
    if message.content.startswith(f"{prefix}stats"):

        exists = verifyIfUser(message.author.id)

        if exists[0]:
            index = exists[1]
        else:
            index = -1
            data["users"].append({})
            makeProfile(int(message.author.id))

        embed = discord.Embed(title="Your Dashboard", description="See your stats !", color=0xfdff75)
        embed.set_author(name=str(data["users"][index]["coins"]) + " coins", icon_url="https://emoji.discadia.com/emojis/23fea924-f44f-4061-b0f0-b4dab898b19c.PNG")
        embed.add_field(name="Coins :", value= str(data["users"][index]["coins"]) + " :coin:", inline=True)
        embed.add_field(name="Coins being verified :", value=str(data["users"][index]["toadd"]) + " :coin:", inline=True)
        try:
            embed.add_field(name="Invitations count :", value=str(data["users"][index]["inviteCount"]) + ":envelope:", inline=False)
            embed.add_field(name="Invitation link", value=data["users"][index]["inviteLink"])
        except KeyError:
            pass

        await message.channel.send(embed=embed)

    if message.content.startswith(f"{prefix}help"):
        mainEmbed = discord.Embed(title="Need Help ?", description="You're on the right place !", color=0x00ffaa)
        mainEmbed.set_footer(text="A bot made by Marsisus", icon_url="https://marsisus.alwaysdata.net/wp-content/uploads/2023/02/moiLama-150x150.jpg")
        
        simpleCommandsEmbed = discord.Embed(title='Main Commands', description="The minimal commands you have to know to use the bot.", color=0x33aaff)
        simpleCommandsEmbed.add_field(inline=False, name="**$buy** _amount_", value="Sends a link for you to pay tokens and tells an admin that you used the command")
        simpleCommandsEmbed.add_field(inline=False, name="**$invite**", value="If not already generated, creates a new personnal invite link for the server, every time you invite someone, you earn 2 :coin:")
        simpleCommandsEmbed.add_field(inline=False, name="**$coins**", value="Shows all the stats you need")
        simpleCommandsEmbed.add_field(inline=False, name="**$question _link_**", value="Use your coins to have an answer to a chegg.com question")


        await message.channel.send(embeds=(mainEmbed, simpleCommandsEmbed))
        
        
    if message.content.startswith(f'{prefix}question'):
        await message.delete()
        url = message.content.split(" ")[1]
        if not "chegg.com" in url or not "questions-and-answers" in url :
            await message.channel.send(":no_entry: You didn't enter a proper link")
            return

       
        
        exists = verifyIfUser(message.author.id)
        if exists[0]:
            index = exists[1]
        else:
            index = -1
            data["users"].append({})
            makeProfile(int(message.author.id))
            
        
        if data['users'][index]["coins"] < 1:
            await message.channel.send(f":no_entry: {message.author.mention} You don't have enough coins to do that !")
            return
    
        data["users"][index]['coins'] -= 1
    
        await message.channel.send(f""":information_source: {message.author.mention} Your link has been taken and an answer will be sent to you on DM in a few hours !""")
        
        messageGuild = await message.guild.fetch_channel("1124767830273962035")
        await messageGuild.send(f""":information_source: {message.author.mention} has just used $question command with :
{url},
use $answer on an administrator account with text and images to answer.""")
            
        saveData()
            
    if message.content.startswith(f"{prefix}answer"):
        await message.delete()
    
        if not message.author.guild_permissions.administrator:
            await message.channel.send(f":no_entry: {message.author.mention}, you aren't allowed to do that")
            return
            
        userid = message.content.split(" ")[1][2:-1]
        try:
            text = message.content.split(" ")[2:]
            
            finaltext = ''
            for i in text:
                finaltext += i
                finaltext += ' '
                
            text = finaltext
                
        except IndexError:
            text = "See Images"
            pass
        
        images = []
        for i in message.attachments:
            images.append(i.url)

        user = message.guild.get_member(int(userid))
        
        if user == None:
            await message.channel.send(f":no_entry: {message.author.mention} You didn't type an existing user")
            return
        
        await user.send(f"""Hello {user.name}, 
Here is your answer to the question you ordered :
{text}""")

            
        
        if len(images) != 0:
            await user.send(f"""Here are images :""")
        for i in images:
            await user.send(i)        
            
        await message.channel.send(f":white_check_mark: Successfuly sent the answer !")
        
        return
    

    

client.run('MTEyNDc2NTU1MjQzMTM0NTczNQ.Go2JUx.PeBRdycskO51R0kDy657C-Ff1hJQIRZzVrVo78')


import discord

class ButtonsTokens(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, prefix, user, count):
        super().__init__()
        self.prefix = prefix
        self.user = user
        self.count = count
        
    
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success) 
    async def good_button_callback(self, button, interaction):
        prefix, mention, count = self.prefix, self.user.mention, self.count
        await button.channel.send(f"{prefix}add {mention} {count}") # Send a message when the button is clicked
        await button.message.delete()
        return
        
    @discord.ui.button(label="No", style=discord.ButtonStyle.danger) 
    async def bad_button_callback(self, button, interaction):
        await button.channel.send(f"Done not giving tokens to {self.user.mention}") # Send a message when the button is clicked
        await button.message.delete()
        return

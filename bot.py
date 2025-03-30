import discord
from discord import ui, app_commands
from discord.ext import commands
import asyncio

TOKEN = "Put your discord bot token here"
SERVER = 78621768124 # put your server id here
TICKETS = 123456789012345678 # this is where all tickets will be made (tthis is a category)
PANEL = 123456789012345678 # basically the main message where users will be able to generate the tickets (put a channel id here)
SERVER_OWNER = 123456789012345678 # put your user id here
STAFF = [987654321098765432, 876543210987654321]  # put staff roles in here

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def find_ticket_creator(channel):
    for target, overwrite in channel.overwrites.items():
        if isinstance(target, discord.Member) and overwrite.read_messages and overwrite.send_messages:
            return target
    return None

class TicketActionsView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_button")
    async def close_ticket_button_callback(self, interaction, button):
        channel = interaction.channel
        user = interaction.user
        await interaction.response.defer(ephemeral=True)
        
        ticket_creator = await find_ticket_creator(channel)
        member = interaction.guild.get_member(user.id) or await interaction.guild.fetch_member(user.id)
        user_is_creator = ticket_creator and ticket_creator.id == user.id
        user_is_staff = any(role.id in STAFF for role in member.roles)
        
        if not (user_is_creator or user_is_staff or channel.permissions_for(member).manage_channels):
            await interaction.followup.send("You do not have permission to close this ticket.", ephemeral=True)
            return
        
        try:
            await channel.send(embed=discord.Embed(title="Ticket Closing", description=f"Closing in 5 seconds (by {user.mention}).", color=discord.Color.red()))
            await asyncio.sleep(5)
            await channel.delete(reason=f"Closed by {user.name}")
        except discord.Forbidden:
            await interaction.followup.send("Error: Cannot delete channel.", ephemeral=True)
        except discord.NotFound:
            pass

class TicketCreateView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket_button")
    async def create_ticket_button_callback(self, interaction, button):
        guild = interaction.guild
        user = interaction.user
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        category = guild.get_channel(TICKETS)
        if not category:
            await interaction.followup.send("Error: Ticket category not found.", ephemeral=True)
            return
        
        for chan in category.text_channels:
            if chan.topic and str(user.id) in chan.topic:
                await interaction.followup.send(f"You already have an open ticket: {chan.mention}", ephemeral=True)
                return
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        for role_id in STAFF:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        try:
            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{user.name}",
                category=category,
                overwrites=overwrites,
                topic=f"Ticket owner: {user.id}"
            )
            
            embed = discord.Embed(
                description="Thank you for opening a ticket. Please describe your issue and wait for assistance.",
                color=discord.Color.blue()
            )
            
            await ticket_channel.send(content=f"{user.mention}", embed=embed, view=TicketActionsView())
            await interaction.followup.send(f"Ticket created: {ticket_channel.mention}", ephemeral=True)
        
        except discord.Forbidden:
            await interaction.followup.send("Error: Bot lacks permissions.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Unexpected error: {e}", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(TicketCreateView())
    bot.add_view(TicketActionsView())
    try:
        await bot.tree.sync(guild=discord.Object(id=SERVER))
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="setup_ticket_panel", description="Post a ticket panel (Owner Only)")
@app_commands.guilds(discord.Object(id=SERVER))
@app_commands.check(lambda i: i.user.id == SERVER_OWNER)
async def setup_ticket_panel(interaction):
    panel_channel = interaction.guild.get_channel(PANEL)
    if not panel_channel:
        await interaction.response.send_message("Error: Panel channel not found.", ephemeral=True)
        return
    
    embed = discord.Embed(title="Support Tickets", description="Click below to create a ticket.", color=discord.Color.green())
    await panel_channel.send(embed=embed, view=TicketCreateView())
    await interaction.response.send_message(f"Ticket panel sent to {panel_channel.mention}!", ephemeral=True)

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Invalid token.")
    except Exception as e:
        print(f"Bot error: {e}")

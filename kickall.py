import discord 
from discord.ext import commands
from discord.ext.commands import has_permissions
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KickBot')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as {bot.user}')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')

@bot.command()
@has_permissions(administrator=True)
async def hello(ctx):
    await ctx.reply('Hello!')

@bot.command()
@has_permissions(administrator=True)
async def kickMembers(ctx, role: discord.Role, reason: str=None):
    """Kick all members with a specific role"""
    logger.info(f'Attempting to kick members with role: {role.name} (ID: {role.id})')
    await ctx.reply(f'Starting to kick members with role: {role.name}')
    
    # Count how many members we'll kick
    members_to_kick = [member for member in ctx.guild.members if role in member.roles]
    
    if not members_to_kick:
        await ctx.reply(f'No members found with the role {role.name}')
        return
    
    await ctx.reply(f'Found {len(members_to_kick)} member(s) to kick')
    
    # Kick process
    kicked_count = 0
    failed_count = 0
    
    for member in members_to_kick:
        try:
            logger.info(f'Kicking member: {member} (ID: {member.id})')
            await ctx.send(f'Kicking: {member.display_name} ({member.id})')
            await member.kick(reason=reason)
            kicked_count += 1
            logger.info(f'Successfully kicked: {member}')
        except discord.Forbidden:
            logger.error(f'No permission to kick: {member}')
            await ctx.send(f'❌ Failed to kick {member.display_name}: Insufficient permissions')
            failed_count += 1
        except Exception as e:
            logger.error(f'Error kicking {member}: {str(e)}')
            await ctx.send(f'❌ Failed to kick {member.display_name}: {str(e)}')
            failed_count += 1
    
    summary = f'Kick operation complete. Successfully kicked: {kicked_count}, Failed: {failed_count}'
    logger.info(summary)
    await ctx.reply(summary)

@bot.event
async def on_message(message):
    # Log all messages
    logger.info(f'Message from {message.author}: {message.content}')
    
    # Handle the kickMyRole command
    if message.content == "kickMyRole" and not message.author.bot:
        if len(message.author.roles) > 1:
            role_to_kick = message.author.roles[1]  # Second role (not @everyone)
            logger.info(f'kickMyRole triggered by {message.author}, targeting role: {role_to_kick.name}')
            await message.channel.send(f'Kicking members with role: {role_to_kick.name}')
            
            # Create a context-like object with the necessary attributes
            class FakeContext:
                def __init__(self, message):
                    self.guild = message.guild
                    self.channel = message.channel
                    self.send = message.channel.send
                    self.reply = message.reply
            
            fake_ctx = FakeContext(message)
            await kickMembers(fake_ctx, role_to_kick)
        else:
            await message.reply("You don't have any roles besides @everyone to target")
    
    # Process commands (this is crucial to make bot commands work!)
    await bot.process_commands(message)

# Error handling for the kickMembers command
@kickMembers.error
async def kickmembers_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing required argument. Usage: `.kickMembers @RoleName [reason]`")
        logger.error(f'Missing argument for kickMembers command')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("⚠️ You don't have permission to use this command")
        logger.error(f'User {ctx.author} attempted to use kickMembers without permission')
    elif isinstance(error, commands.RoleNotFound):
        await ctx.send("⚠️ Role not found")
        logger.error(f'Role not found for kickMembers command')
    else:
        await ctx.send(f"⚠️ An error occurred: {str(error)}")
        logger.error(f'Error in kickMembers command: {str(error)}')

# token
token = 'insert token here'
bot.run(token)
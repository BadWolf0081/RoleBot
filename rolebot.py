import discord
from discord.ext import commands, tasks
from discord import Embed
import asyncio

intents = discord.Intents.default()
intents.members = True  # Required for tracking members and their roles

# Define bot prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# The source server ID (the server we are checking for roles)
SOURCE_SERVER_ID = 123456789012345678  # Replace with your source server ID
CHANNEL_ID = 123456789012345678  # Replace with the channel ID where notifications will be sent

# A dictionary of target servers with their corresponding role ID mappings
# Each target server ID maps to a dictionary that maps source role IDs to target role IDs
target_servers = {
    987654321098765432: {  # Replace with actual target server ID
        123456789012345678: 987654321012345678,  # Source role ID -> Target role ID
        234567890123456789: 876543210987654321,  # Source role ID -> Target role ID
    },
    112233445566778899: {  # Another target server ID
        123456789012345678: 123456789098765432,  # Source role ID -> Target role ID
        234567890123456789: 234567890987654321,  # Source role ID -> Target role ID
    }
    # Add more target server mappings as needed
}

# Event when bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    await sync_roles.start()  # Start role synchronization on bot startup
    await remove_roles_on_startup()  # Remove roles on startup for users

# Sync roles across multiple target servers
@tasks.loop(minutes=10)  # Runs every 10 minutes (adjust as needed)
async def sync_roles():
    source_guild = bot.get_guild(SOURCE_SERVER_ID)

    if source_guild is None:
        print("Unable to find source server.")
        return

    print(f"Syncing roles from {source_guild.name} to target servers...")

    for target_server_id, role_mapping in target_servers.items():
        target_guild = bot.get_guild(target_server_id)

        if target_guild is None:
            print(f"Unable to find target server with ID {target_server_id}.")
            continue

        print(f"Syncing roles to {target_guild.name}...")

        for source_role_id, target_role_id in role_mapping.items():
            source_role = discord.utils.get(source_guild.roles, id=source_role_id)
            target_role = discord.utils.get(target_guild.roles, id=target_role_id)

            if source_role and target_role:
                for member in source_guild.members:
                    if source_role in member.roles:
                        target_member = target_guild.get_member(member.id)
                        if target_member:
                            # Ensure the user has the target role
                            if target_role not in target_member.roles:
                                await target_member.add_roles(target_role)
                                print(f"Assigned {target_role.name} to {member.name} in target server {target_guild.name}.")
                                await notify_role_change(source_guild, source_role, "added", member)
                            else:
                                print(f"{member.name} already has {target_role.name} in target server {target_guild.name}.")
                    else:
                        # Remove the role from the user if no longer in the source role
                        target_member = target_guild.get_member(member.id)
                        if target_member and target_role in target_member.roles:
                            await target_member.remove_roles(target_role)
                            print(f"Removed {target_role.name} from {member.name} in target server {target_guild.name}.")
                            await notify_role_change(source_guild, source_role, "removed", member)
            else:
                print(f"Role with ID {source_role_id} or {target_role_id} not found.")

# Remove roles from users in target servers who no longer have them on the source server (on startup)
async def remove_roles_on_startup():
    source_guild = bot.get_guild(SOURCE_SERVER_ID)

    if source_guild is None:
        print("Unable to find source server.")
        return

    print(f"Removing roles from target servers based on the source server roles...")

    for target_server_id, role_mapping in target_servers.items():
        target_guild = bot.get_guild(target_server_id)

        if target_guild is None:
            print(f"Unable to find target server with ID {target_server_id}.")
            continue

        print(f"Removing roles from {target_guild.name}...")

        for source_role_id, target_role_id in role_mapping.items():
            source_role = discord.utils.get(source_guild.roles, id=source_role_id)
            target_role = discord.utils.get(target_guild.roles, id=target_role_id)

            if source_role and target_role:
                for member in target_guild.members:
                    if target_role in member.roles and source_role not in member.roles:
                        # Remove the target role if the user no longer has the corresponding source role
                        await member.remove_roles(target_role)
                        print(f"Removed {target_role.name} from {member.name} in target server {target_guild.name}.")
                        await notify_role_change(source_guild, source_role, "removed", member)
            else:
                print(f"Role with ID {source_role_id} or {target_role_id} not found.")

# Notify via embedded message when a role is added or removed
async def notify_role_change(source_guild, source_role, action, member):
    channel = source_guild.get_channel(CHANNEL_ID)
    
    if channel is None:
        print(f"Unable to find channel with ID {CHANNEL_ID}.")
        return

    action_verb = "added" if action == "added" else "removed"
    
    embed = Embed(
        title=f"Role {action_verb}",
        description=f"Role: {source_role.name}\nUser: {member.name}",
        color=discord.Color.green() if action == "added" else discord.Color.red()
    )
    embed.set_footer(text=f"Action performed by {bot.user.name}")
    
    await channel.send(embed=embed)

@bot.command(name="sync")
async def sync(ctx):
    if ctx.author.id != YOUR_ID:  # Replace with your user ID to limit access to the bot owner
        await ctx.send("You do not have permission to use this command.")
        return

    await ctx.send("Manual sync triggered. Syncing roles...")

    await sync_roles()

# Run the bot with your token
bot.run("YOUR_BOT_TOKEN")

import discord
from discord.ext import commands
import asyncio
import requests
import tokennn

class DiscordStatusChanger:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": token,
            "User-Agent": "DiscordBot (https://discordapp.com, v1.0)",
            "Content-Type": "application/json",
            "Accept": "*/*"
        }

    def change_status(self, status, message, emoji_name, emoji_id):
        jsonData = {
            "status": status,
            "custom_status": {
                "text": message,
                "emoji_name": emoji_name,
                "emoji_id": emoji_id,
            }
        }
        r = requests.patch("https://discord.com/api/v8/users/@me/settings", headers=self.headers, json=jsonData)
        return r.status_code
    
class StatusRotator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = tokennn.TOKEN
        self.discord_status_changer = DiscordStatusChanger(self.token)
        self.is_rotating = False  # New attribute to control rotation

    @commands.command()
    async def start_rotation(self, ctx, status="dnd"):
        if not self.is_rotating:
            self.is_rotating = True
            await ctx.send("Starting status rotation...")
            await self.run_rotation(status)
        else:
            await ctx.send("Status rotation is already running.")

    @commands.command()
    async def stop_rotation(self, ctx):
        if self.is_rotating:
            self.is_rotating = False
            await ctx.send("Stopping status rotation...")
        else:
            await ctx.send("Status rotation is not currently running.")

    async def run_rotation(self, status):
        file_path = 'status.txt'
        while self.is_rotating:
            with open(file_path, 'r') as file:
                messages = [line.strip() for line in file.readlines()]

            if not messages:
                await ctx.send("No messages found in the file. Add messages to continue.")
                await asyncio.sleep(30)
                continue

            for message in messages:
                message_parts = message.split(',')

                if len(message_parts) >= 2:
                    emoji_id = None
                    emoji_name = message_parts[0].strip()

                    if emoji_name and emoji_name[0].isdigit():
                        emoji_id = emoji_name
                        emoji_name = ""

                    status_text = message_parts[1].strip()

                    status_code = self.discord_status_changer.change_status(status, status_text, emoji_name, emoji_id)
                    if status_code == 200:
                        print(f"Changed to: {status_text}")
                    else:
                        print("Failed to change status.")
                    await asyncio.sleep(10)

def setup(bot):
    bot.add_cog(StatusRotator(bot))
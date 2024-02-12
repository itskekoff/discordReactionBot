import asyncio
import logging
import random
import re
import sys
from datetime import datetime

import discord
from discord.ext import commands, tasks

from modules.configuration import Configuration, check_missing_keys
from modules.logger import Logger

config_path = "config.json"
data: Configuration = Configuration(config_path)

default_config: dict = {
    "token": "Your discord account token",
    "prefix": "cp!",
    "debug": True,
    "reaction_settings": {
        "__comment__": "Delay between adding reactions (in settings (float))",
        "reaction_delay": 1.75,
        "__comment2": "Reaction chance",
        "reaction_chance": 40,
        "__comment3__": "Mapping guild/channel list of channels and guilds in which bot will react",
        "guild_mapping": {1097895009275101244: [1180933726201454642]},
        "__comment4__": "List of guilds/channels/reaction id's and chances (bot will use this reactions)",
        "__comment5__": "Chance is value between 1 and 100 (1% - 100%)",
        "__comment6__": "If two or more reactions = 100% - will be selected using 50% 25% etc...",
        "reaction_mapping": {1097895009275101244: {
            1180933726201454642: {"<custom_name:custom_id>": 10, "unicode_emoji": 20}
        }},
    }
}

data.set_default(default=default_config)

logger = Logger()
logger.bind(server="CONFIGURATION")

if not data.file_exists(config_path):
    data.write_defaults().flush()
    logger.error("Configuration doesn't found. Re-created it.")
    sys.exit(-1)

new_config, missing_keys = check_missing_keys(config_data=data.config,
                                              default_data=default_config,
                                              ignore_paths=[["reaction_settings", "guild_mapping"],
                                                            "reaction_settings", "reaction_mapping"])

if missing_keys:
    logger.error(f"Missing keys {missing_keys} in configuration. Re-created them with default values.")
    logger.error("Restart the program to continue.")
    sys.exit(-1)

config_values = data.config

token, prefix, debug = (
    config_values["token"],
    config_values["prefix"],
    config_values["debug"],
)

reaction_settings = config_values["reaction_settings"]
reaction_delay, reaction_chance, guild_mapping, reactions_mapping = (
    reaction_settings["reaction_delay"],
    reaction_settings["reaction_chance"],
    reaction_settings["guild_mapping"],
    reaction_settings["reaction_mapping"]
)

token_pattern = re.compile(r"^([MN][\w-]{23,25})\.([\w-]{6})\.([\w-]{27,39})$")
if not token_pattern.match(token):
    logger.error("Provided discord token is not valid")
    sys.exit(-1)

bot = commands.Bot(command_prefix=prefix, case_insensitive=True, self_bot=True)
reaction_queue = asyncio.Queue()

listening: bool = False
logger.reset()


def select_reaction(reaction_mapping: dict[str, dict[str, dict[str, int]]], channel_id: int,
                    guild_id: int) -> str | None:
    channel_reactions = reaction_mapping.get(str(guild_id), {}).get(str(channel_id), {})
    if not channel_reactions:
        logger.error("No reactions for the given guild_id and channel_id")
        return None

    total_chance = sum(channel_reactions.values())
    rand = random.uniform(0, total_chance)
    current_chance = 0
    for reaction, chance in channel_reactions.items():
        current_chance += chance
        if rand < current_chance:
            return reaction

    return min(channel_reactions, key=channel_reactions.get)


@tasks.loop(seconds=reaction_delay)
async def process_reactions():
    if not reaction_queue.empty():
        message, reaction = await reaction_queue.get()
        try:
            await message.add_reaction(reaction)
            if debug:
                logger.debug("Added reaction (reaction={}, channel={}, guild={})",
                             reaction, message.channel.id, message.guild.name)
        except discord.DiscordException as e:
            logger.error("Error while adding reaction: {}", e)


@bot.event
async def on_connect():
    logger.success("Logged on as {0.user}".format(bot))
    process_reactions.start()


@bot.event
async def on_message(message: discord.Message):
    if listening and message.author != bot.user:
        if message.author != bot.user and message.guild:
            channels = guild_mapping.get(str(message.guild.id))
            if channels is None or message.channel.id not in channels:
                return
            if message.channel.id in channels and random.randint(1, 100) <= reaction_chance:
                reaction = select_reaction(reaction_mapping=reactions_mapping,
                                           guild_id=message.guild.id,
                                           channel_id=message.channel.id)
                if reaction is not None:
                    await reaction_queue.put((message, reaction))
    await bot.process_commands(message)


@bot.command(name="switch", aliases=["launch", "react"])
async def switch(ctx: commands.Context):
    global listening
    listening = not listening
    message: str = "Switched listening state (new={})".format(listening)
    logger.info(message)
    await ctx.message.edit(content=f"`{message}`")
    await ctx.message.delete(delay=5)


if __name__ == '__main__':
    file_handler = logging.FileHandler(
        f'{datetime.now().strftime("%d-%m-%Y")}-discord.log'
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    logger.info("Logging in discord account...")
    bot.run(token, log_handler=file_handler, log_formatter=formatter)

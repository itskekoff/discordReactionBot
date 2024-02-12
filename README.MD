## Description

This bot is designed to automatically react to messages in Discord based on predefined settings. It allows customization of reactions for specific guilds and channels with different probabilities. The bot works with a delay between reactions and checks the validity of the provided Discord token.

## Features

- Customizable prefix, token, and debug options.
- Reaction delay and chance settings.
- Guild and channel-specific reaction mappings.
- Valid Discord token verification.
- Advanced logging system.

## Configuration

Before running the bot, configure the required settings in `data.config`. The configuration fields are:

- `token`: The bot's Discord token.
- `prefix`: The prefix used for bot commands.
- `debug`: Boolean flag to enable debug messages.
- `reaction_settings`: Dictionary containing reaction-specific configurations such as:
  - `reaction_delay`: Time delay in seconds between reactions.
  - `reaction_chance`: The probability (1-100) of the bot reacting to a message.
  - `guild_mapping`: A dictionary defining which channels in which guilds the bot should listen to.
  - `reaction_mapping`: A nested dictionary mapping guilds and channels to their respective reactions and chances.

## Running the Bot

To run the bot, execute the main script after ensuring that all configurations are properly set.

## Commands

- `switch`, `launch`, `react`: Toggle the bot's listening state. When listening, the bot will react to messages based on the `reaction_mapping` configuration.

## Usage

1. Set up your `config.json` with the appropriate values.
2. Run the script. If the token is not valid, the script will log an error message and exit.
3. Use the command (`switch`, `launch`, `react`) to start listening to messages on the Discord servers.

## Logging

The bot uses the Loguru library for advanced logging functionalities. Logs can be found in the generated file named with the current date, for example, `12-02-2024-discord.log`.
## Dependencies

- `discord.py-self`: Python library for interacting with the Discord API.
- `loguru`: Library providing a simpler and more elegant logging experience.

Make sure all dependencies are installed before running the bot by using the `pip install -r requirements.txt` command with a provided `requirements.txt` file listing the dependencies.

## Disclaimer

This bot is intended for educational purposes only. Automated user accounts (self-bots) violate Discord's terms of service. Using this bot on Discord can result in account termination.
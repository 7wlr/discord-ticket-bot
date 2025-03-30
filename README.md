# Discord Ticket Bot

A simple Discord bot that lets users create support tickets. Staff can assist and close tickets when needed.

## Features
- Open tickets with a button click.
- Only staff and the ticket creator can see the channel.
- Close tickets easily with a button.

## Installation
### Requirements
- Python 3.8+
- `discord.py`

### Setup
1. Clone the repo:
   ```sh
   git clone https://github.com/7wlr/discord-ticket-bot.git
   cd discord-ticket-bot
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure `bot.py`:
   - Replace `TOKEN` with your bot token.
   - Set `SERVER`, `TICKETS`, `PANEL`, `SERVER_OWNER`, and `STAFF` IDs.

4. Run the bot:
   ```sh
   python bot.py
   ```

## Commands
- `/setup_ticket_panel` – Posts the ticket panel (Owner only).

## Notes
- The bot needs `Manage Channels`, `Send Messages`, and `Read Messages` permissions.
- Ensure the `message_content` intent is enabled in Discord Developer Portal.

## Contributing
Pull requests and issues are welcome!

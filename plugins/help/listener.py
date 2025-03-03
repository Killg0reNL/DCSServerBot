from __future__ import annotations
from core import EventListener, utils
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import Server, Player


class HelpListener(EventListener):
    async def onChatCommand(self, data: dict) -> None:
        server: Server = self.bot.servers[data['server_name']]
        prefix = self.bot.config['BOT']['CHAT_COMMAND_PREFIX']
        if data['subcommand'] == 'help':
            messages = [
                f'You can use the following commands:\n',
                f'"{prefix}linkme token" link your user to Discord',
                f'"{prefix}atis airport" display ATIS information',
                f'"{prefix}911 <text>"   send an alert to admins (misuse will be punished!)'
            ]
            player = server.get_player(id=data['from_id'], active=True)
            if not player:
                return
            dcs_admin = player.has_discord_roles(['DCS Admin'])
            if dcs_admin:
                messages.append(f'"{prefix}kick <name>"  kick a user')
                messages.append(f'"{prefix}restart time" restart the running mission')
                messages.append(f'"{prefix}list"         list available missions')
                messages.append(f'"{prefix}load number"  load a specific mission')
                messages.append(f'"{prefix}preset"       load a specific weather preset')
                messages.append(f'"{prefix}maintenance"  enable maintenance mode')
                messages.append(f'"{prefix}clear"        disable maintenance mode')
            game_master = player.has_discord_roles(['GameMaster'])
            if dcs_admin or game_master:
                messages.append(f'"{prefix}flag"         reads or sets a flag')
            if 'punishment' in self.bot.plugins:
                messages.append(f'"{prefix}penalty"      displays your penalty points')
                messages.append(f'"{prefix}forgive"      forgive another user for teamhits/-kills')
            if 'creditsystem' in self.bot.plugins and utils.get_running_campaign(server)[0]:
                messages.append(f'"{prefix}credits"      displays your credits')
                messages.append(f'"{prefix}donate"       donate points to another player')
                messages.append(f'"{prefix}tip"          tip a GCI with points')
            if self.bot.config.getboolean(server.installation, 'COALITIONS') and \
                    not player.has_discord_roles(['DCS Admin', 'GameMaster']):
                messages.append(f'"{prefix}join coal."   join a coalition')
                messages.append(f'"{prefix}blue"         join the blue side')
                messages.append(f'"{prefix}red"          join the red side')
                messages.append(f'"{prefix}leave"        leave a coalition')
                messages.append(f'"{prefix}password"     shows coalition password')
                messages.append(f'"{prefix}coalition"    shows your current coalition')
            player.sendUserMessage('\n'.join(messages), 30)

    async def onPlayerStart(self, data: dict) -> None:
        if data['id'] == 1:
            return
        server: Server = self.bot.servers[data['server_name']]
        player: Player = server.get_player(id=data['id'])
        prefix = self.bot.config['BOT']['CHAT_COMMAND_PREFIX']
        player.sendChatMessage(f'Use "{prefix}help" for commands.')

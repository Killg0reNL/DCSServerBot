from __future__ import annotations
import discord
import psycopg2
from contextlib import closing
from core import utils
from core.data.dataobject import DataObject, DataObjectFactory
from core.data.const import Side, Coalition
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .server import Server


@dataclass
@DataObjectFactory.register("Player")
class Player(DataObject):
    server: Server = field(compare=False)
    id: int = field(compare=False)
    name: str = field(compare=False)
    active: bool = field(compare=False)
    side: Side = field(compare=False)
    ucid: str
    banned: bool = field(compare=False)
    slot: int = field(compare=False, default=0)
    sub_slot: int = field(compare=False, default=0)
    unit_callsign: str = field(compare=False, default='')
    unit_name: str = field(compare=False, default='')
    unit_type: str = field(compare=False, default='')
    group_id: int = field(compare=False, default=0)
    group_name: str = field(compare=False, default='')
    _member: discord.Member = field(compare=False, repr=False, default=None, init=False)
    _verified: bool = field(compare=False, default=False)
    _coalition: Coalition = field(compare=False, default=None)

    def __post_init__(self):
        super().__post_init__()
        if self.id == 1:
            self.active = False
            return
        conn = self.pool.getconn()
        try:
            with closing(conn.cursor()) as cursor:
                cursor.execute('SELECT p.discord_id, CASE WHEN b.ucid IS NOT NULL THEN TRUE ELSE FALSE END AS banned, '
                               'p.manual, c.coalition FROM players p LEFT OUTER JOIN bans b ON p.ucid = b.ucid '
                               'LEFT OUTER JOIN coalitions c ON p.ucid = c.player_ucid WHERE p.ucid = %s',
                               (self.ucid, ))
                # existing member found?
                if cursor.rowcount == 1:
                    row = cursor.fetchone()
                    if row[0] != -1:
                        self.member = self._member = self.bot.guilds[0].get_member(row[0])
                        self._verified = row[2]
                    self.banned = row[1]
                    if row[3]:
                        self.coalition = Coalition.RED if row[3] == 'red' else Coalition.BLUE
                cursor.execute(
                    'INSERT INTO players (ucid, discord_id, name, last_seen) VALUES (%s, -1, %s, NOW()) ON '
                    'CONFLICT (ucid) DO UPDATE SET name=excluded.name, last_seen=excluded.last_seen',
                    (self.ucid, self.name))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.log.exception(error)
        finally:
            self.pool.putconn(conn)
        # if automatch is enabled, try to match the user
        if not self.member and self.bot.config.getboolean('BOT', 'AUTOMATCH'):
            discord_user = self.bot.match_user({"ucid": self.ucid, "name": self.name})
            if discord_user:
                self.member = discord_user

    def is_active(self) -> bool:
        return self.active

    def is_multicrew(self) -> bool:
        return self.sub_slot != 0

    def is_banned(self) -> bool:
        return self.banned

    @property
    def member(self) -> discord.Member:
        return self._member

    @member.setter
    def member(self, member: discord.Member) -> None:
        if member != self._member:
            conn = self.pool.getconn()
            try:
                with closing(conn.cursor()) as cursor:
                    cursor.execute('UPDATE players SET discord_id = %s WHERE ucid = %s',
                                   (member.id if member else -1, self.ucid))
                    conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                self.log.exception(error)
                conn.rollback()
            finally:
                self.pool.putconn(conn)
            self._member = member
        if member:
            roles = [x.name for x in member.roles]
            self.server.sendtoDCS({
                'command': 'uploadUserRoles',
                'id': self.id,
                'ucid': self.ucid,
                'roles': roles
            })

    @property
    def verified(self) -> bool:
        return self._verified

    @verified.setter
    def verified(self, verified: bool) -> None:
        conn = self.pool.getconn()
        try:
            with closing(conn.cursor()) as cursor:
                cursor.execute('UPDATE players SET manual = %s WHERE ucid = %s', (verified, self.ucid))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.log.exception(error)
            conn.rollback()
        finally:
            self.pool.putconn(conn)

    @property
    def coalition(self) -> Coalition:
        return self._coalition

    @coalition.setter
    def coalition(self, coalition: Coalition):
        self._coalition = coalition
        if coalition == Coalition.BLUE:
            side = Side.BLUE
        elif coalition == Coalition.RED:
            side = Side.RED
        else:
            side = Side.SPECTATOR
        self.server.sendtoDCS({
            "command": "setUserCoalition",
            "ucid": self.ucid,
            "coalition": side.value
        })

    def update(self, data: dict):
        conn = self.pool.getconn()
        try:
            with closing(conn.cursor()) as cursor:
                if 'id' in data:
                    # if the ID has changed (due to reconnect), we need to update the server list
                    if self.id != data['id']:
                        del self.server.players[self.id]
                        self.server.players[data['id']] = self
                        self.id = data['id']
                if 'active' in data:
                    self.active = data['active']
                if 'name' in data and self.name != data['name']:
                    self.name = data['name']
                    cursor.execute('UPDATE players SET name = %s WHERE ucid = %s', (self.name, self.ucid))
                if 'side' in data:
                    self.side = Side(data['side'])
                if 'slot' in data:
                    self.slot = int(data['slot'])
                if 'sub_slot' in data:
                    self.sub_slot = data['sub_slot']
                if 'unit_callsign' in data:
                    self.unit_callsign = data['unit_callsign']
                if 'unit_name' in data:
                    self.unit_name = data['unit_name']
                if 'unit_type' in data:
                    self.unit_type = data['unit_type']
                if 'group_name' in data:
                    self.group_name = data['group_name']
                if 'group_id' in data:
                    self.group_id = data['group_id']
                cursor.execute('UPDATE players SET last_seen = NOW() WHERE ucid = %s', (self.ucid, ))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            self.log.exception(error)
            conn.rollback()
        finally:
            self.pool.putconn(conn)

    def has_discord_roles(self, roles: list[str]) -> bool:
        return self.verified and self._member is not None and utils.check_roles(roles, self._member)

    def sendChatMessage(self, message: str, sender: str = None):
        self.server.sendtoDCS({
            "command": "sendChatMessage",
            "to": self.id,
            "from": sender,
            "message": message
        })

    def sendUserMessage(self, message: str, timeout: Optional[int] = -1):
        if self.slot <= 0:
            [self.sendChatMessage(msg) for msg in message.splitlines()]
        else:
            self.sendPopupMessage(message, timeout)

    def sendPopupMessage(self, message: str, timeout: Optional[int] = -1, sender: str = None):
        if timeout == -1:
            timeout = self.bot.config['BOT']['MESSAGE_TIMEOUT']
        self.server.sendtoDCS({
            "command": "sendPopupMessage",
            "to": self.unit_name,
            "from": sender,
            "message": message,
            "time": timeout
        })

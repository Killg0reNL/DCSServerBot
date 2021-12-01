CREATE TABLE IF NOT EXISTS version (version TEXT PRIMARY KEY);
INSERT INTO version (version) VALUES ('v1.2') ON CONFLICT (version) DO NOTHING;
CREATE TABLE IF NOT EXISTS servers (server_name TEXT PRIMARY KEY, agent_host TEXT NOT NULL, host TEXT NOT NULL DEFAULT '127.0.0.1', port BIGINT NOT NULL, chat_channel BIGINT, status_channel BIGINT, admin_channel BIGINT);
CREATE TABLE IF NOT EXISTS message_persistence (server_name TEXT NOT NULL, embed_name TEXT NOT NULL, embed BIGINT NOT NULL, PRIMARY KEY (server_name, embed_name));
CREATE TABLE IF NOT EXISTS players (ucid TEXT PRIMARY KEY, discord_id BIGINT);
CREATE TABLE IF NOT EXISTS bans (ucid TEXT PRIMARY KEY, banned_by TEXT NOT NULL, reason TEXT, banned_at TIMESTAMP NOT NULL DEFAULT NOW());
CREATE INDEX IF NOT EXISTS idx_players_discord_id ON players(discord_id);
CREATE TABLE IF NOT EXISTS missions (id SERIAL PRIMARY KEY, server_name TEXT NOT NULL, mission_name TEXT NOT NULL, mission_theatre TEXT NOT NULL, mission_start TIMESTAMP NOT NULL DEFAULT NOW(), mission_end TIMESTAMP);
CREATE TABLE IF NOT EXISTS statistics (mission_id INTEGER NOT NULL, player_ucid TEXT NOT NULL, slot TEXT NOT NULL, kills INTEGER DEFAULT 0, pvp INTEGER DEFAULT 0, deaths INTEGER DEFAULT 0, ejections INTEGER DEFAULT 0, crashes INTEGER DEFAULT 0, teamkills INTEGER DEFAULT 0, kills_planes INTEGER DEFAULT 0, kills_helicopters INTEGER DEFAULT 0, kills_ships INTEGER DEFAULT 0, kills_sams INTEGER DEFAULT 0, kills_ground INTEGER DEFAULT 0, deaths_pvp INTEGER DEFAULT 0, deaths_planes INTEGER DEFAULT 0, deaths_helicopters INTEGER DEFAULT 0, deaths_ships INTEGER DEFAULT 0, deaths_sams INTEGER DEFAULT 0, deaths_ground INTEGER DEFAULT 0, takeoffs INTEGER DEFAULT 0, landings INTEGER DEFAULT 0, hop_on TIMESTAMP NOT NULL DEFAULT NOW(), hop_off TIMESTAMP, PRIMARY KEY (mission_id, player_ucid, slot, hop_on));
CREATE INDEX IF NOT EXISTS idx_statistics_player_ucid ON statistics(player_ucid);

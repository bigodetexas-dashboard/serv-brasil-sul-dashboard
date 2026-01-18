-- Database Performance Indexes
-- Add indexes to frequently queried columns for better performance
-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_discord_id ON users(discord_id);
CREATE INDEX IF NOT EXISTS idx_users_gamertag ON users(nitrado_gamertag);
CREATE INDEX IF NOT EXISTS idx_users_kills ON users(kills DESC);
CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance DESC);
CREATE INDEX IF NOT EXISTS idx_users_playtime ON users(total_playtime DESC);
CREATE INDEX IF NOT EXISTS idx_users_verified ON users(nitrado_verified);
-- PvP kills table indexes
CREATE INDEX IF NOT EXISTS idx_pvp_timestamp ON pvp_kills(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_pvp_killer ON pvp_kills(killer_name);
CREATE INDEX IF NOT EXISTS idx_pvp_victim ON pvp_kills(victim_name);
CREATE INDEX IF NOT EXISTS idx_pvp_coords ON pvp_kills(game_x, game_z);
-- Transactions table indexes
CREATE INDEX IF NOT EXISTS idx_transactions_discord ON transactions(discord_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
-- Clan members table indexes
CREATE INDEX IF NOT EXISTS idx_clan_members_clan ON clan_members(clan_id);
CREATE INDEX IF NOT EXISTS idx_clan_members_discord ON clan_members(discord_id);
CREATE INDEX IF NOT EXISTS idx_clan_members_role ON clan_members(role);
-- Clan wars table indexes
CREATE INDEX IF NOT EXISTS idx_clan_wars_clan1 ON clan_wars(clan1_id);
CREATE INDEX IF NOT EXISTS idx_clan_wars_clan2 ON clan_wars(clan2_id);
CREATE INDEX IF NOT EXISTS idx_clan_wars_status ON clan_wars(status);
CREATE INDEX IF NOT EXISTS idx_clan_wars_expires ON clan_wars(expires_at);
-- Clan invites table indexes
CREATE INDEX IF NOT EXISTS idx_clan_invites_discord ON clan_invites(discord_id);
CREATE INDEX IF NOT EXISTS idx_clan_invites_clan ON clan_invites(clan_id);
CREATE INDEX IF NOT EXISTS idx_clan_invites_status ON clan_invites(status);
-- Bounties table indexes
CREATE INDEX IF NOT EXISTS idx_bounties_gamertag ON bounties(gamertag);
CREATE INDEX IF NOT EXISTS idx_bounties_amount ON bounties(amount DESC);
-- User items table indexes
CREATE INDEX IF NOT EXISTS idx_user_items_discord ON user_items(discord_id);
CREATE INDEX IF NOT EXISTS idx_user_items_key ON user_items(item_key);
-- User achievements table indexes
CREATE INDEX IF NOT EXISTS idx_achievements_discord ON user_achievements(discord_id);
CREATE INDEX IF NOT EXISTS idx_achievements_id ON user_achievements(achievement_id);
-- Bases table indexes
CREATE INDEX IF NOT EXISTS idx_bases_owner ON bases(owner_id);
CREATE INDEX IF NOT EXISTS idx_bases_coords ON bases(x, z);
-- User favorites table indexes
CREATE INDEX IF NOT EXISTS idx_favorites_discord ON user_favorites(discord_id);
CREATE INDEX IF NOT EXISTS idx_favorites_item ON user_favorites(item_key);
-- Shop items table indexes
CREATE INDEX IF NOT EXISTS idx_shop_category ON shop_items(category);
CREATE INDEX IF NOT EXISTS idx_shop_active ON shop_items(is_active);
CREATE INDEX IF NOT EXISTS idx_shop_price ON shop_items(price);
-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_users_gt_verified ON users(nitrado_gamertag, nitrado_verified);
CREATE INDEX IF NOT EXISTS idx_clan_members_composite ON clan_members(clan_id, discord_id);
CREATE INDEX IF NOT EXISTS idx_wars_active ON clan_wars(status, expires_at)
WHERE status = 'active';
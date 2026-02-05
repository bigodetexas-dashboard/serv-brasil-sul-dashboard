ACHIEVEMENTS_DEF = {
    "first_kill": {
        "title": "ðŸŽ¯ Primeira VÃ­tima",
        "name": "ðŸŽ¯ Primeira VÃ­tima",
        "description": "Mate seu primeiro jogador",
        "reward": "500 DZ Coins",
        "reward_value": 500,
        "category": "combat",
        "rarity": "common",
        "tier": "bronze",
        "points": 10,
        "maxProgress": 1,
        "check": lambda stats, balance, transactions: stats.get("kills", 0) >= 1,
    },
    "assassin": {
        "title": "ðŸ’€ Assassino",
        "name": "ðŸ’€ Assassino",
        "description": "Acumule 10 kills",
        "reward": "1000 DZ Coins",
        "reward_value": 1000,
        "category": "combat",
        "rarity": "rare",
        "tier": "silver",
        "points": 25,
        "maxProgress": 10,
        "check": lambda stats, balance, transactions: stats.get("kills", 0) >= 10,
    },
    "serial_killer": {
        "title": "â˜ ï¸ Serial Killer",
        "name": "â˜ ï¸ Serial Killer",
        "description": "Acumule 50 kills",
        "reward": "5000 DZ Coins",
        "reward_value": 5000,
        "category": "combat",
        "rarity": "epic",
        "tier": "gold",
        "points": 50,
        "maxProgress": 50,
        "check": lambda stats, balance, transactions: stats.get("kills", 0) >= 50,
    },
    "rich": {
        "title": "ðŸ’° Rico",
        "name": "ðŸ’° Rico",
        "description": "Acumule 10.000 DZ Coins",
        "reward": "Badges de Perfil",
        "reward_value": 0,
        "category": "social",
        "rarity": "common",
        "tier": "bronze",
        "points": 10,
        "maxProgress": 10000,
        "check": lambda stats, balance, transactions: balance >= 10000,
    },
    "millionaire": {
        "title": "ðŸ’Ž MilionÃ¡rio",
        "name": "ðŸ’Ž MilionÃ¡rio",
        "description": "Acumule 100.000 DZ Coins",
        "reward": "10000 DZ Coins",
        "reward_value": 10000,
        "category": "social",
        "rarity": "legendary",
        "tier": "platinum",
        "points": 100,
        "maxProgress": 100000,
        "check": lambda stats, balance, transactions: balance >= 100000,
    },
    "shopper": {
        "title": "ðŸ›’ Comprador",
        "name": "ðŸ›’ Comprador",
        "description": "FaÃ§a 10 compras na loja",
        "reward": "1000 DZ Coins",
        "reward_value": 1000,
        "category": "social",
        "rarity": "rare",
        "tier": "silver",
        "points": 20,
        "maxProgress": 10,
        "check": lambda stats, balance, transactions: sum(
            1 for t in transactions if t.get("type") == "purchase"
        )
        >= 10,
    },
    "veteran": {
        "title": "â° Veterano",
        "name": "â° Veterano",
        "description": "Jogue por 50 horas",
        "reward": "5000 DZ Coins",
        "reward_value": 5000,
        "category": "survival",
        "rarity": "epic",
        "tier": "gold",
        "points": 50,
        "maxProgress": 50,
        "check": lambda stats, balance, transactions: stats.get("total_playtime", 0)
        / 3600
        >= 50,
    },
    "bounty_hunter": {
        "title": "ðŸŽ¯ Matador de Aluguel",
        "name": "ðŸŽ¯ Matador de Aluguel",
        "description": "Complete 5 caÃ§adas (bumbas)",
        "reward": "2500 DZ Coins",
        "reward_value": 2500,
        "category": "combat",
        "rarity": "rare",
        "tier": "silver",
        "points": 30,
        "maxProgress": 5,
        "check": lambda stats, balance, transactions: stats.get("bounties_completed", 0)
        >= 5,
    },
}


def check_new_achievements(discord_id, current_unlocked, stats, balance, transactions):
    """
    Checks for new achievements and returns a list of (id, definition).
    """
    newly_unlocked = []
    for ach_id, ach_def in ACHIEVEMENTS_DEF.items():
        if ach_id in current_unlocked:
            continue

        if ach_def["check"](stats, balance, transactions):
            newly_unlocked.append((ach_id, ach_def))

    return newly_unlocked

class PlaystyleEngine:
    """
    Motor de Heurística para determinar o Arquétipo do jogador
    e gerar bios dinâmicas.
    """

    ARCHETYPES = {
        "shadow_legend": {
            "name": "Lenda das Sombras",
            "emoji": "🥷",
            "description": "Um predador nato que domina os campos de batalha de Chernarus.",
            "banner": "/static/images/banners/pvp_pro.png",
        },
        "engineer": {
            "name": "Engenheiro de Chernarus",
            "emoji": "🏗️",
            "description": "Mestre construtor, transformando troncos em fortalezas impenetráveis.",
            "banner": "/static/images/banners/builder.png",
        },
        "nomad": {
            "name": "Nômade Incansável",
            "emoji": "🏃",
            "description": "Suas botas conhecem cada trilha e cada segredo deste mapa vasto.",
            "banner": "/static/images/banners/explorer.png",
        },
        "fisherman": {
            "name": "Pescador de Elite",
            "emoji": "🎣",
            "description": "A paciência é sua maior arma, e o lago seu verdadeiro lar.",
            "banner": "/static/images/banners/fishing.png",
        },
        "pacifist": {
            "name": "Sobrevivente Pacifista",
            "emoji": "🌿",
            "description": "Sobrevivendo contra todas as probabilidades sem nunca derramar sangue inocente.",
            "banner": "/static/images/banners/survivor.png",
        },
        "default": {
            "name": "Recruta Bigode",
            "emoji": "🤠",
            "description": "Iniciando sua jornada nas terras indomadas do BigodeTexas.",
            "banner": "/static/images/banners/default.jpg",
        },
    }

    @staticmethod
    def determine_archetype(stats):
        """
        Determina o arquétipo com base nas métricas.
        stats: dict com kills, zombie_kills, buildings_placed, fish_caught, meters_traveled
        """
        kills = stats.get("kills", 0)
        z_kills = stats.get("zombie_kills", 0)
        buildings = stats.get("buildings_placed", 0)
        fish = stats.get("fish_caught", 0)
        distance = stats.get("meters_traveled", 0)

        # Heurística de prioridade
        if kills >= 50:
            return "shadow_legend"
        if buildings >= 100:
            return "engineer"
        if fish >= 30:
            return "fisherman"
        if distance >= 500000:  # 500km
            return "nomad"
        if z_kills >= 200 and kills == 0:
            return "pacifist"

        return "default"

    @classmethod
    def generate_bio(cls, archetype_key, stats):
        """Gera a string final da bio automática."""
        arc = cls.ARCHETYPES.get(archetype_key, cls.ARCHETYPES["default"])

        bio = f"{arc['emoji']} {arc['name']}\n\n"
        bio += f"{arc['description']}\n\n"

        # Adicionar marcos interessantes
        if stats.get("kills", 0) > 0:
            bio += f"💀 {stats['kills']} baixas confirmadas.\n"
        if stats.get("buildings_placed", 0) > 0:
            bio += f"🔨 {stats['buildings_placed']} estruturas erguidas.\n"

        return bio.strip()

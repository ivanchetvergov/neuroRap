# config.py

ARTIST_LIST = [
    "Boulevard Depo",
    "SALUKI",
    "Хаски",
    "Kai Angel",
    "PHARAOH",
    "FRIENDLY THUG 52 NGG",
    "ROCKET",
    "Mnogoznaal",
    "Toxi$",
    'MAYOT',
    "LILDRUGHILL",
    "ICEGERGERT",
    "Темный Принц"
]

# --- 1. ТЕГИ ПО УМОЛЧАНИЮ (Применяются ко всем песням, если теги Genius не найдены) ---

ARTIST_DEFAULT_TAGS = {
    "Boulevard Depo": ["Cloud Rap", "New School", "Experimental", "Vaporwave", "Abstract"],
    "SALUKI": ["Alternative Hip-Hop", "Trap", "RnB", "Melodic Rap", "Emotional"],
    "Хаски": ["Social Rap", "Industrial", "Abstract", "Lyrical", "Dark"],
    "Kai Angel": ["Rage", "Trap", "Hyperpop", "Aggressive", "Meme Rap"],
    "PHARAOH": ["Cloud Rap", "Emo Rap", "Plugg", "Dark Trap", "Melodic"],
    "FRIENDLY THUG 52 NGG": ["Drill", "Gangsta Rap", "Phonk", "Underground", "Storytelling"],
    "ROCKET": ["Cloud Rap", "Mumble Rap", "Ambient", "Spacey", "Chill"],
    "Mnogoznaal": ["Abstract Hip-Hop", "Horrorcore", "Dark Trap", "Atmospheric", "Deep"],
    "Toxi$": ["Trap", "Plug", "New School", "Energetic", "Youth"],
    'MAYOT': ["Trap", "Mumble Rap", "New School", "Street Rap", "Hard"],
    "LILDRUGHILL": ["Trap", "New School", "RnB", "Melodic Rap"],
    "ICEGERGERT": ["New School", "Melodic Rap", "Pop Trap", "Mainstream"],
    "Темный Принц": ["Trap", "New School", "Dark", "Minimalism"]
}


# --- 2. ТЕГИ АЛЬБОМОВ (Переопределяют теги по умолчанию для конкретного альбома) ---

ALBUM_TAGS = {
    "Boulevard Depo": {
        # Старые, более мрачные и атмосферные релизы
        "RAPP": ["Cloud Rap", "Atmospheric", "Dark", "Eerie"],
        "Old Blood": ["Experimental", "Vaporwave", "Cloud Rap", "Abstract", "Eerie"],
        # Коммерческий и более агрессивный период
        "RAPP2": ["Cloud Rap", "New School", "Melodic", "Aggressive"],
        # Экспериментальный, минималистичный звук
        "QUAYLE": ["Eerie", "Minimalism", "Experimental", "Abstract"],
        # Более свежий, чистый звук
        "ФУТУРОАРХАИКА" : ["Dark", "Cloud Rap", "Lyrical"]
    },

    "SALUKI": {
        # Главный, мрачный и концептуальный релиз
        "Властелин Калек (Lord of the Cripples)": ["Alternative Hip-Hop", "Emotional", "Conceptual", "Dark",
                                                   "Storytelling"],
        # Более RnB и мелодичный релиз
        "НАШИХ ГЛАЗ ФУНДАМЕНТ": ["Trap", "Melodic", "RnB", "Pop Trap", "Chill"],
        # Самый ранний, сырой Trap
        "УЛИЦА ПОДЪЕЗД ДОМ": ["Trap", "New School", "Mumble Rap"]
    },

    "Хаски": {
        # Мрачный и индустриальный звук
        "Хошхоног": ["Dark", "Industrial", "Drones", "Hardcore Hip-Hop"],
        # Более лиричный и философский релиз
        "Любимые песни (воображаемых) людей": ["Social Rap", "Lyrical", "Philosophical", "Abstract", "Conceptual"],
        # Недавний, более разнообразный
        "Локид": ["Alternative Hip-Hop", "Experimental", "Abstract"]
    },

    "Kai Angel": {
        # Хайперпоп и Rage звук
        "Heavy Metal": ["Rage", "Hyperpop", "Aggressive", "Meme Rap", "Experimental"],
        "BABY MELON": ["Rage", "Hyperpop", "Energetic"]
    },

    "PHARAOH": {
        # Главный Emo/Dark Trap релиз
        "Million Dollar Depression": ["Emo Rap", "Melodic", "Dark Trap", "Goth"],
        # Классический Cloud/Vaporwave
        "Правило": ["Cloud Rap", "Vaporwave", "Spacey", "Ambient"],
        # Агрессивный и трэповый
        "REDЯUM": ["Dark Trap", "Aggressive", "New School"]
    },

    "FRIENDLY THUG 52 NGG": {
        # Уличный, мрачный дрилл
        "Cruiser Aurora": ["Drill", "Gangsta Rap", "Phonk", "Underground", "Storytelling", "Dark"],
        # Недавний релиз
        "Montenegro": ["Drill", "Underground", "Street Rap"]
    },

    "ROCKET": {
        # Космический и атмосферный Cloud Rap
        "Swag Season": ["Cloud Rap", "Mumble Rap", "Ambient", "Spacey", "Chill"],
        # Более тёмный и агрессивный
        "Ego Trippin’": ["Dark Trap", "Aggressive", "Cloud Rap"]
    },

    "Mnogoznaal": {
        # Мрачный, атмосферный, концептуальный
        "Горе (Woe)": ["Abstract Hip-Hop", "Conceptual", "Horrorcore", "Atmospheric", "Dark"],
        # Более экспериментальный и индустриальный
        "КРУГ (Circle)": ["Experimental", "Industrial", "Storytelling", "Abstract"]
    },

    "Toxi$": {
        # Трэп и Plug
        "HOTSPOT": ["Trap", "Plug", "New School", "Energetic", "Youth"],
        "JAZZ DOLLS": ["Plug", "Ambient", "New School"]
    },

    'MAYOT': {
        # Главный релиз, классический Trap
        "Ghetto Garden": ["Trap", "New School", "Street Rap", "Hard", "Mumble Rap"],
        "ЗАПРАВКА (ZAPRAVKA)": ["Trap", "Hard", "Street Rap"]
    },

    "LILDRUGHILL": {
        # Мелодичность и RnB
        "All the songs are about money": ["Trap", "New School", "RnB", "Melodic Rap"],
        "DRUGG": ["Melodic Rap", "Pop Trap", "RnB"]
    },

}
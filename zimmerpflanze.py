import discord
from discord.ext import commands
from collections import OrderedDict  # Hier fügen wir den LRU-Cache-Import ein
from dotenv import load_dotenv
from discord.ext import tasks
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from datetime import datetime
import holidays
import os    # Um zu überprüfen, ob die Datei existiert
import json  # Für das Speichern und Laden
import yt_dlp as youtube_dl
import random
import re  # Für die Erkennung von Links
import asyncio
import requests
from bs4 import BeautifulSoup

import aiohttp
import socket



# Lade die .env-Datei
load_dotenv(dotenv_path='C:/Users/klide/Desktop/ZIMMERPFLANZE/tzimmer.env')

# Hole den API-Schlüssel aus der Umgebungsvariablen
discord_api_key = os.getenv('DISCORD_API_KEY')

# Überprüfe den API-Key
print(f"API-Key: {discord_api_key}")

# Intents definieren
intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True  # Damit der Bot neue Mitglieder erkennen kann

# Erstelle eine benutzerdefinierte Aktivität
activity = discord.Game("")

# Bot-Instanz erstellen
#intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', activity=activity, intents=intents)


# Dictionary, um zuletzt gesendete Nachrichten pro Benutzer zu speichern
user_last_messages = OrderedDict()

# Spam-Schutz-Zeitrahmen, anpassbar je nach Nachrichtengröße
def get_spam_time_frame(message):
    return 3 if len(message.content) < 10 else 5  # Kurzere Nachrichten (weniger als 10 Zeichen) haben einen kürzeren Zeitrahmen



#---------------------------------witzigenfos feiertage----------------------------
# Funktion zum Hinzufügen manueller Feiertage
def add_manual_holidays(holiday_obj):
    today = datetime.today().date()
    # Manuelle Feiertage hinzufügen
    holiday_obj[today.replace(month=12, day=24)] = "Heiligabend"
    return holiday_obj

# Funktion, um den heutigen Feiertag in Deutschland zu prüfen
def get_today_holiday():
    # Erstelle eine Instanz der Feiertage für Deutschland
    de_holidays = holidays.Germany(years=datetime.today().year)
    # Manuelle Feiertage hinzufügen
    de_holidays = add_manual_holidays(de_holidays)
    today = datetime.today().date()

    # Überprüfe, ob heute ein Feiertag ist
    if today in de_holidays:
        return de_holidays[today]
    return None

# Funktion, um den nächsten Feiertag in Deutschland zu finden
def get_next_holiday():
    # Erstelle eine Instanz der Feiertage für Deutschland
    de_holidays = holidays.Germany(years=datetime.today().year)
    # Manuelle Feiertage hinzufügen
    de_holidays = add_manual_holidays(de_holidays)
    today = datetime.today().date()

    # Suche den nächsten Feiertag
    future_holidays = [(date, name) for date, name in de_holidays.items() if date > today]
    if future_holidays:
        next_holiday_date, next_holiday_name = min(future_holidays)
        return next_holiday_name, next_holiday_date
    return None, None



# Witzige Informationen zu Feiertagen
def get_fun_fact(holiday_name):
    facts = {
        "Neujahr": "Zeit für gute Vorsätze... die spätestens in einer Woche vergessen werden. 🎉",
        "Tag der Arbeit": "Der einzige Tag im Jahr, an dem Arbeit nicht verboten ist! 💼",
        "Weihnachten": "Wer braucht schon Geschenke, wenn es Plätzchen gibt? 🍪",
        "Ostern": "Eier suchen – das Beste am Frühling! 🐣",
        "Tag der Deutschen Einheit": "Ein Tag, an dem die Mauer in unseren Herzen gefallen ist. 🏰",
        "Karfreitag": "Ein ruhiger Tag, perfekt zum Nachdenken – oder um Ostereier zu bemalen. 🐰",
    }
    # Wenn der Feiertag nicht im Dictionary ist, gebe eine allgemeine Nachricht zurück
    return facts.get(holiday_name, "Feiertage sind der perfekte Zeitpunkt für eine Auszeit! 🎉")

# Bot erstellen
intents = discord.Intents.default()
intents.messages = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)



#-----------------------------STEAM SALES  funktioniert noch nicht richtig------------------------------------------------------------------------------
# Funktion zum Abrufen der GreenManGaming-Angebote
def get_gmg_deals():
    url = "https://www.greenmangaming.com/"

    try:
        # Sende eine GET-Anfrage an die GreenManGaming-Website
        response = requests.get(url)

        # Überprüfe, ob die Anfrage erfolgreich war
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extrahiere die Angebote (dies könnte je nach der Struktur der Website variieren)
            deals = soup.find_all('div', class_='product-listing')  # Beispiel: Produktauswahl
            if deals:
                result = []
                for deal in deals[:5]:  # Nimm die ersten 5 Angebote
                    title = deal.find('a', class_='product-title').get_text(strip=True)
                    price = deal.find('div', class_='price').get_text(strip=True)
                    link = deal.find('a')['href']

                    result.append(f"**{title}**\n💸 Preis: {price}\n🔗 [Kaufen]({link})\n")

                return "\n".join(result)
            else:
                return "Keine aktuellen Angebote gefunden. 😢"
        else:
            return f"Fehler: Die Anfrage war nicht erfolgreich. Statuscode: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Fehler beim Abrufen der Angebote: {e}"

# Beispiel-Funktion für Steam-Angebote (Du kannst sie nach Bedarf anpassen)
def get_steam_sales():
    # Hier wäre ein Beispiel, wie man Steam-Angebote abfragen könnte
    # Zum Beispiel von einer API oder einer Website. Hier verwenden wir ein einfaches Beispiel.
    # (Die tatsächliche Implementierung hängt von der Quelle und der API ab, die du verwendest)

    return """
    **Steam-Angebot 1**
    💸 Preis: 10.99 USD
    🔗 [Kaufen](https://store.steampowered.com)

    **Steam-Angebot 2**
    💸 Preis: 15.99 USD
    🔗 [Kaufen](https://store.steampowered.com)
    """
#--------------------------------------------------------------------------------------------------------------------------

#---------------------------------STEAMNewGames------------------------------------------------------

# Liste von großen Entwicklern
top_developers = ['Ubisoft', 'Bethesda', 'EA', 'Square Enix', 'Activision', 'Rockstar Games', 'Naughty Dog', 'MachineGames']

# Funktion zum Abrufen der kommenden Steam-Spiele
def get_upcoming_steam_games():
    url = "https://store.steampowered.com/search/?sort_by=Released_DESC&category1=998"  # Steam-Link für kommende Spiele

    try:
        # Sende eine GET-Anfrage an die Steam-Seite für kommende Spiele
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Suche nach den Spielnamen und Erscheinungsdaten
            upcoming_games = soup.find_all('a', class_='search_result_row')
            if upcoming_games:
                result = []
                top_games = []  # Spiele von Top-Entwicklern
                other_games = []  # Spiele von anderen Entwicklern

                # Durchlaufe die ersten 10 Spiele und teile sie in Top-Entwickler und andere Spiele
                for game in upcoming_games[:10]:  # Zeige die ersten 10 Spiele
                    title = game.find('span', class_='title').get_text(strip=True)
                    release_date_tag = game.find('div', class_='col search_released')

                    # Sicherstellen, dass das Release-Datum vorhanden ist
                    if release_date_tag:
                        release_date = release_date_tag.get_text(strip=True)
                    else:
                        release_date = "Unbekannt"

                    link = game['href']
                    developer_tag = game.find('div', class_='search_developer')

                    # Versuche, den Entwickler des Spiels zu extrahieren
                    if developer_tag:
                        developer = developer_tag.get_text(strip=True)
                    else:
                        developer = "Unbekannt"

                    # Überprüfe, ob der Entwickler in der Liste der Top-Entwickler ist
                    if any(dev.lower() in developer.lower() for dev in top_developers):
                        top_games.append(f"**{title}**\n📅 Erscheinungsdatum: {release_date}\n🔗 [Mehr Infos]({link})\n")
                    else:
                        other_games.append(f"**{title}**\n📅 Erscheinungsdatum: {release_date}\n🔗 [Mehr Infos]({link})\n")

                # Kombiniere die Top-Spiele und die anderen Spiele und zeige sie an
                result = top_games + other_games

                if result:
                    return "\n".join(result)
                else:
                    return "Keine bevorstehenden Spiele gefunden. 😢"
            else:
                return "Keine bevorstehenden Spiele gefunden. 😢"
        else:
            return f"Fehler: Die Anfrage war nicht erfolgreich. Statuscode: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Fehler beim Abrufen der Steam-Spiele: {e}"

# Beispiel für den Funktionsaufruf
sales_info = get_upcoming_steam_games()
print(sales_info)

#---------------------------------GAMESTAR------------------------------------------------------
def get_gamestar_releases():
    url = "https://www.gamestar.de/releaseliste/"  # GameStar-Releaseliste-Seite

    try:
        # Sende eine GET-Anfrage an die Releaseliste-Seite
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Suche nach den Spieleinträgen innerhalb der relevanten Struktur
            games = soup.find_all('div', class_='media test-list article-list game-list p-l-1 p-r-1')

            if games:
                releases = []
                for game in games[:8]:  # Begrenzung auf die ersten 10 Spiele
                    # Titel des Spiels
                    title_tag = game.find('a', title=True)
                    title = title_tag['title'] if title_tag else "Unbekannter Titel"

                    # Link zum Spiel
                    link = f"https://www.gamestar.de{title_tag['href']}" if title_tag else "Kein Link verfügbar"

                    # Plattform(en)
                    platforms = [span.get_text(strip=True) for span in game.find_all('span', class_='label')]

                    # Genre
                    genre_tag = game.find('p', class_='info', text=lambda x: 'Genre:' in x if x else False)
                    genre = genre_tag.get_text(strip=True).replace('Genre:', '') if genre_tag else "Unbekanntes Genre"

                    # Entwickler
                    developer_tag = game.find('p', class_='info', text=lambda x: 'Entwickler:' in x if x else False)
                    developer = developer_tag.get_text(strip=True).replace('Entwickler:', '') if developer_tag else "Unbekannter Entwickler"

                    # Release-Datum
                    release_tag = game.find('p', class_='info', text=lambda x: 'Release:' in x if x else False)
                    release_date = release_tag.get_text(strip=True).replace('Release:', '') if release_tag else "Unbekanntes Release-Datum"

                    # Informationen sammeln
                    releases.append(f"🎮 **{title}**\n📅 Release: {release_date}\n📍 Plattform(en): {', '.join(platforms)}\n🎭 Genre: {genre}\n🏢 Entwickler: {developer}\n🔗 [Mehr Infos]({link})\n")

                return "\n".join(releases) if releases else "Keine Spiele gefunden. 😢"
            else:
                return "Keine Spieleinträge gefunden. 😢"
        else:
            return f"Fehler: Die Anfrage war nicht erfolgreich. Statuscode: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Fehler beim Abrufen der Releaseliste: {e}"

# Testaufruf
releases_info = get_gamestar_releases()
print(releases_info)


#---------------------------------GAME2025------------------------------------------------------

def get_top_new_games_2025_playcentral():
    url = "https://www.playcentral.de/spiele-release-2025-ps4-ps5-xbox-switch-pc-game/"
    response = requests.get(url)

    if response.status_code != 200:
        return "Fehler beim Laden der Seite. 😢"

    soup = BeautifulSoup(response.text, 'html.parser')

    # Finde das Haupt-Content-Element
    content_div = soup.find('div', class_='entry-content entry clearfix')
    if not content_div:
        return "Keine Spiele für 2025 gefunden. 😢"

    # Extrahiere Spieleinformationen aus dem Content-Bereich
    games = []
    current_month = None
    for element in content_div.find_all(['h3', 'li']):
        if element.name == 'h3':  # Monatsüberschrift
            current_month = element.get_text(strip=True)
        elif element.name == 'li' and current_month:  # Spielinformationen
            game_text = element.get_text(strip=True)
            games.append(f"📅 {current_month}: {game_text}")

    if not games:
        return "Keine Spiele für 2025 gefunden. 😢"

    return "\n".join(games)

# Teste den Code
print(get_top_new_games_2025_playcentral())


#----------------------------------Willkommen automatisch funktion funktioniert nicht ---------------------------------------
# Kanal-IDs definieren
WELCOME_CHANNEL_ID = 1268283068636991559
FIRST_MESSAGE_CHANNEL_ID = 1310651062004351046

# Dictionary, um die ersten Nachrichten pro Benutzer zu speichern
user_first_messages = {}

bot = discord.Client(intents=intents)

# Dateipfad für die Benutzerdaten
USER_DATA_FILE = "discordmitglieder.json"

# Hilfsfunktionen zum Laden und Speichern der Benutzerdaten
def load_user_data():
    try:
        if not os.path.exists(USER_DATA_FILE):
            return {}
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return {}

def save_user_data(data):
    try:
        with open(USER_DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Fehler beim Speichern der Daten: {e}")
#---------------------------------------------------------

# Pflanzenpflege-Informationen
plant_care_info = {
    "kaktus": "Kakteen sollten alle 14 Tage gegossen werden. Achte darauf, dass der Boden gut abtrocknen kann, um Wurzelfäule zu vermeiden! Stelle ihn an einen sonnigen Ort.",
    "kakteen": "Kakteen sollten alle 14 Tage gegossen werden. Achte darauf, dass der Boden gut abtrocknen kann, um Wurzelfäule zu vermeiden! Stelle ihn an einen sonnigen Ort.",
    "sukkulente": "Sukkulenten benötigen nur sehr wenig Wasser. Am besten alle 3-4 Wochen gießen und an einem sonnigen Ort platzieren. Achte darauf, dass der Boden gut abtrocknet.",
    "sukkulenten": "Sukkulenten benötigen nur sehr wenig Wasser. Am besten alle 3-4 Wochen gießen und an einem sonnigen Ort platzieren. Achte darauf, dass der Boden gut abtrocknet.",
    "orchidee": "Orchideen mögen es, wenn der Boden leicht feucht bleibt. Alle 7-10 Tage gießen und die Blätter regelmäßig mit Wasser besprühen. Stelle sie an einen hellen, aber nicht direkt sonnigen Ort.",
    "orchideen": "Orchideen mögen es, wenn der Boden leicht feucht bleibt. Alle 7-10 Tage gießen und die Blätter regelmäßig mit Wasser besprühen. Stelle sie an einen hellen, aber nicht direkt sonnigen Ort.",
    "rose": "Rosen benötigen regelmäßiges Gießen, besonders während der Blütezeit. Gieße sie etwa alle 3-4 Tage bei heißem Wetter. Vermeide Staunässe.",
    "rosen": "Rosen benötigen regelmäßiges Gießen, besonders während der Blütezeit. Gieße sie etwa alle 3-4 Tage bei heißem Wetter. Vermeide Staunässe.",
    "monstera": "Die Monstera ist eine pflegeleichte Pflanze, die alle 1-2 Wochen gegossen werden kann. Sie mag es, wenn der Boden gut abtrocknen kann, und sollte an einem hellen Ort stehen.",
    "monstera": "Die Monstera ist eine pflegeleichte Pflanze, die alle 1-2 Wochen gegossen werden kann. Sie mag es, wenn der Boden gut abtrocknen kann, und sollte an einem hellen Ort stehen.",
    "bambus": "Bambus bevorzugt feuchten Boden und sollte regelmäßig gegossen werden. Er mag es, wenn das Wasser immer leicht über dem Wurzelniveau steht. Achte darauf, dass er nicht in direkter Sonne steht.",
    "bambusse": "Bambus bevorzugt feuchten Boden und sollte regelmäßig gegossen werden. Er mag es, wenn das Wasser immer leicht über dem Wurzelniveau steht. Achte darauf, dass er nicht in direkter Sonne steht.",
    "aloe vera": "Aloe Vera ist eine Sukkulente und benötigt nur alle 3-4 Wochen Wasser. Sie bevorzugt einen sonnigen Standort und durchlässigen Boden.",
    "aloe veras": "Aloe Vera ist eine Sukkulente und benötigt nur alle 3-4 Wochen Wasser. Sie bevorzugt einen sonnigen Standort und durchlässigen Boden.",
    "lavendel": "Lavendel braucht viel Sonne und gut durchlässigen Boden. Gieße ihn alle 7-10 Tage, aber vermeide Staunässe, da er empfindlich auf zu viel Wasser reagiert.",
    "lavendels": "Lavendel braucht viel Sonne und gut durchlässigen Boden. Gieße ihn alle 7-10 Tage, aber vermeide Staunässe, da er empfindlich auf zu viel Wasser reagiert.",
    "farn": "Farne mögen es feucht und sollten regelmäßig gegossen werden, besonders im Sommer. Stelle sie an einen schattigen bis halbschattigen Ort und vermeide direkte Sonne.",
    "farne": "Farne mögen es feucht und sollten regelmäßig gegossen werden, besonders im Sommer. Stelle sie an einen schattigen bis halbschattigen Ort und vermeide direkte Sonne.",
    "gerbera": "Gerbera mag es, wenn der Boden gleichmäßig feucht gehalten wird, aber Staunässe muss vermieden werden. Stelle sie an einen sonnigen Platz und achte darauf, dass der Boden gut durchlässig ist.",
    "gerbera": "Gerbera mag es, wenn der Boden gleichmäßig feucht gehalten wird, aber Staunässe muss vermieden werden. Stelle sie an einen sonnigen Platz und achte darauf, dass der Boden gut durchlässig ist.",
    "philodendron": "Der Philodendron benötigt mäßiges Gießen und bevorzugt eine hohe Luftfeuchtigkeit. Alle 1-2 Wochen gießen reicht aus, und er sollte an einem hellen, indirekten Ort stehen.",
    "philodendronen": "Der Philodendron benötigt mäßiges Gießen und bevorzugt eine hohe Luftfeuchtigkeit. Alle 1-2 Wochen gießen reicht aus, und er sollte an einem hellen, indirekten Ort stehen.",
    "kalanchoe": "Kalanchoe ist eine Sukkulente und sollte nur alle 2-3 Wochen gegossen werden. Sie benötigt viel Licht, also stelle sie an einen sonnigen Platz.",
    "kalanchoes": "Kalanchoe ist eine Sukkulente und sollte nur alle 2-3 Wochen gegossen werden. Sie benötigt viel Licht, also stelle sie an einen sonnigen Platz.",
    "ficus": "Ficus bevorzugt regelmäßiges Gießen und einen hellen, indirekten Standort. Lass den Boden zwischen den Gießvorgängen leicht abtrocknen.",
    "ficusse": "Ficus bevorzugt regelmäßiges Gießen und einen hellen, indirekten Standort. Lass den Boden zwischen den Gießvorgängen leicht abtrocknen.",
    "geranien": "Geranien mögen es sonnig und benötigen regelmäßiges Gießen, besonders im Sommer. Sie sollten gut durchlässigen Boden haben und während der Blütezeit öfter gegossen werden.",
    "geranien": "Geranien mögen es sonnig und benötigen regelmäßiges Gießen, besonders im Sommer. Sie sollten gut durchlässigen Boden haben und während der Blütezeit öfter gegossen werden.",
    "ficus elastica": "Der Gummibaum bevorzugt mäßiges Gießen und einen hellen, aber nicht direkten Sonnenstandort. Lasse den Boden zwischen den Gießvorgängen gut abtrocknen.",
    "ficus elasticas": "Der Gummibaum bevorzugt mäßiges Gießen und einen hellen, aber nicht direkten Sonnenstandort. Lasse den Boden zwischen den Gießvorgängen gut abtrocknen.",
    "petunie": "Petunien benötigen täglich Wasser und einen sonnigen Standort. Achte darauf, dass der Boden gut abtrocknen kann, um Staunässe zu vermeiden.",
    "petunien": "Petunien benötigen täglich Wasser und einen sonnigen Standort. Achte darauf, dass der Boden gut abtrocknen kann, um Staunässe zu vermeiden.",
}


# Synonyme für Pflanzenarten
plant_synonyms = {
    "kaktus": ["kaktus", "kakteen", "kaktee", "kaktusse"],
    "sukkulente": ["sukkulente", "sukkulenten"],
    "orchidee": ["orchidee", "orchideen"],
    "rose": ["rose", "rosen"],
    "monstera": ["monstera"],
    "bambus": ["bambus", "bambusse"],
    "aloe vera": ["aloe vera", "aloe veras"],
    "lavendel": ["lavendel", "lavendels"],
    "farn": ["farn", "farne"],
    "gerbera": ["gerbera", "gerberas"],
    "philodendron": ["philodendron", "philodendronen"],
    "kalanchoe": ["kalanchoe", "kalanchoes"],
    "ficus": ["ficus", "ficusse"],
    "geranien": ["geranien"],
    "ficus elastica": ["ficus elastica", "ficus elasticas"],
    "petunie": ["petunie", "petunien"],
}

# Humorvolle Sprüche für Pflanzen (mit Einzahl und Mehrzahl)
plant_humor = {
        "kaktus": "Kakteen sind harte Gesellen! 😎",
        "kakteen": "Kakteen sind harte Gesellen! 😎",
        "rose": "Rosen sind die romantischen Klassiker! 🌹",
        "rosen": "Rosen sind die romantischen Klassiker! 🌹",
        "sukkulente": "Sukkulenten sind die Überlebenskünstler! 🌵",
        "sukkulenten": "Sukkulenten sind die Überlebenskünstler! 🌵",
        "orchidee": "Orchideen sind die Diva unter den Pflanzen! 💅",
        "orchideen": "Orchideen sind die Diva unter den Pflanzen! 💅",
        "bambus": "Bambus ist schnell und flexibel! 🌿",
        "bambusse": "Bambusse sind schnell und flexibel! 🌿",
        "lavendel": "Lavendel ist die Seele der Provence! 💜",
        "lavendels": "Lavendel ist die Seele der Provence! 💜",
        "farn": "Farne sind die geheimen Urwaldriesen! 🌿",
        "farne": "Farne sind die geheimen Urwaldriesen! 🌿",
        "gerbera": "Gerbera bringen den Frühling ins Haus! 🌸",
        "gerberas": "Gerbera bringen den Frühling ins Haus! 🌸",
        "philodendron": "Philodendren sind die Bürohelden! 🏢",
        "philodendronen": "Philodendren sind die Bürohelden! 🏢",
        "kalanchoe": "Kalanchoe ist die Blühmaschine! 🌺",
        "kalanchoes": "Kalanchoe ist die Blühmaschine! 🌺",
        "ficus": "Ficus ist der beliebte Mitbewohner! 🪴",
        "ficusse": "Ficusse sind die beliebten Mitbewohner! 🪴",
        "geranien": "Geranien bringen Farbe ins Leben! 🌷",
        "petunie": "Petunien sind die ständigen Sommerbegleiter! 🌞",
        "petunien": "Petunien sind die ständigen Sommerbegleiter! 🌞",
    }

# Pflanzenbezogene Antworten
def plant_related_response(message_content, author_name):
    # Pflanzenarten, nach denen wir suchen möchten
    plant_name = None

    # Suche nach Pflanzenarten im Text (z.B. Kaktus, Orchidee, etc.)
    for plant in plant_care_info:
        if plant in message_content.lower():
            plant_name = plant
            break

    # Rückgabe der humorvollen Antwort und des Pflegetipps für die erkannte Pflanze
    if plant_name:
        return f"@{author_name}, du hast {plant_name.capitalize()} erwähnt! {plant_humor[plant_name]} Hier ist ein nützlicher Tipp: {plant_care_info[plant_name]}"

    #Eurotainer Witz
    if "europflanze" in message_content.lower():
        return f"@{author_name}, uhhh da musst du mal beim Eurotainer vorbeischauen, er ist der Biologe der Europflanzen! 😄 Du findest seinen Kanal hier: https://www.twitch.tv/dereurotainer"



    # Wenn der Benutzer „ich liebe pflanzen“ sagt
    if "ich liebe pflanzen" in message_content.lower():
        return f"@{author_name}, oh, das freut mich sehr! Was ist deine Lieblingspflanze?"

    # Wenn der Benutzer „ich habe meine Blumen gegossen“ sagt
    if "ich habe meine blumen gegossen" in message_content.lower():
        return f"@{author_name}, es klingt, als ob du deine Pflanzen gut versorgst! Welche Pflanze hast du gegossen?"


    #wenn keine bekannte pflanze
   # if not plant_name:
       # return f"@{author_name}, das klingt interessant! Welche Pflanze hast du erwähnt?"

    return None

# Globale Variablen
voice_client = None
is_playing = False
current_song = None

# FFMPEG Optionen (kannst du nach Bedarf anpassen)
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',  # Verhindert Verbindungsabbrüche
    'options': '-vn',  # Verhindert das Abrufen von Videoinhalten, nur Audio
}

# yt-dlp Optionen
ydl_opts = {
    'format': 'bestaudio/best',  # Beste Audioqualität auswählen
    'postprocessors': [{
        'key': 'FFmpegAudio',  # Ändere dies auf 'FFmpegAudio' anstelle von 'FFmpegAudioPP'
        'preferredcodec': 'mp3',  # Audio-Format (mp3, ogg, etc.)
        'preferredquality': '192',  # Audioqualität
    }],
    'outtmpl': 'downloads/%(id)s.%(ext)s',  # Speichert die Datei temporär
    'quiet': True,  # Verhindert unnötige Ausgaben
}


# Hangman Setup
word_list = [
    "python", "discord", "bot", "hangman", "programming", "developer", "music", "chatbot", "algorithm",
    "boost", "rakete", "tor", "fliegen", "auto", "ball", "arena", "training", "season", "team", "turbo",
    "boostpad", "goal", "corner", "freestyle", "dribbling", "kickoff", "rocket", "soccar", "shot", "save",
    "demolition", "car", "aerial", "flip", "ballchasing", "offense", "defense", "ranked", "competitive", "Ascent",
]
current_word = None
guessed_letters = []
max_attempts = 6
#-----------------------------------------------------------------------------------------------------------------------------------------

#automod
# Intents und Bot-Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Datei für gebannte Wörter
BANNED_WORDS_FILE = "banned_words.json"

# -----------------------------
# Funktionen für Datei-Handling
# -----------------------------

def load_banned_words():
    """Lädt die gebannten Wörter aus einer JSON-Datei."""
    if os.path.exists(BANNED_WORDS_FILE):
        with open(BANNED_WORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_banned_words(words):
    """Speichert die gebannten Wörter in eine JSON-Datei."""
    with open(BANNED_WORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=4)

# Globale Liste gebannter Wörter
BANNED_WORDS = load_banned_words()

#---------------------------------STEAM SALES funktioniert noch nicht richtig-------------------------------------------------------------
# Command für die GreenManGaming-Angebote
@bot.command(name="gmgdeals")
async def gmgdeals(ctx):
    sales_info = get_gmg_deals()  # Funktionsaufruf zum Abrufen der Angebote
    await ctx.send(sales_info)  # Sende die Angebote als Nachricht

# Command für die Steam-Angebote
@bot.command(name="steamsales")
async def steamsales(ctx):
    sales_info = get_steam_sales()  # Funktionsaufruf für Steam-Angebote
    await ctx.send(sales_info)  # Sende die Steam-Angebote als Nachricht


#---------------------------------------------------------------------------------------------------------

#---------------------------------STEAMNEWGAMES------------------------------------------------------
@bot.command(name="steamnewgames")
async def steamnewgames(ctx):
    news_info = get_upcoming_steam_games()  # Funktionsaufruf zum Abrufen der kommenden Spiele
    await ctx.send(news_info)  # Sende die Spiele als Nachricht

#---------------------------------GAMESTAR------------------------------------------------------
@bot.command(name="topnewgames")
async def topnewgames(ctx):
    releases_info = get_gamestar_releases()
    await ctx.send(releases_info)

#---------------------------------GAME2025------------------------------------------------------
# Bot-Befehl für 2025-Spiele
@bot.command(name='topnewgames2025')
async def topnewgames2025(ctx):
    releases_info_2025 = get_top_new_games_2025_playcentral()  # Hole die Spiele für 2025

    # Falls die Spieleliste zu lang ist, teilen wir sie auf
    if len(releases_info_2025) > 2000:  # Sicherstellen, dass jede Nachricht die Grenze einhält
        chunks = [releases_info_2025[i:i + 2000] for i in range(0, len(releases_info_2025), 2000)]
        for chunk in chunks:
            await ctx.send(chunk)
    else:

        await ctx.send(releases_info_2025)  # Ausgabe der Spiele im Discord-Channel



#-------------------------------------RANK STATISTIKEN-----------------------------------------------

# Stelle sicher, dass USER_DATA_FILE am Anfang definiert ist
USER_DATA_FILE = "Epic-ID.json"  # Der Name der JSON-Datei, die verwendet wird

# Funktion zum Laden der JSON-Daten mit verbesserter Fehlerbehandlung
def load_user_data():
    try:
        # Überprüfen, ob die Datei existiert und leer ist
        if not os.path.exists(USER_DATA_FILE):
            print(f"Datei {USER_DATA_FILE} existiert nicht. Eine neue Datei wird erstellt.")
            save_user_data({})  # Erstellt eine leere Datei
            return {}

        # Datei laden
        with open(USER_DATA_FILE, "r") as file:
            data = json.load(file)
            if not data:
                print(f"Datei {USER_DATA_FILE} ist leer. Initialisiere sie mit einem leeren Objekt.")
                save_user_data({})  # Initialisiert die Datei mit einem leeren JSON-Objekt
                return {}
            return data  # Rückgabe der Daten, wenn sie vorhanden sind

    except FileNotFoundError:
        print(f"Datei {USER_DATA_FILE} nicht gefunden. Eine neue Datei wird erstellt.")
        save_user_data({})  # Erstellt die Datei, wenn sie fehlt
        return {}
    except json.JSONDecodeError as e:
        print(f"Fehler beim Dekodieren der JSON-Datei: {e}. Die Datei wird als leer behandelt.")
        save_user_data({})  # Repariert die Datei, indem sie neu initialisiert wird
        return {}
    except Exception as e:
        print(f"Unbekannter Fehler: {e}")
        return {}

# Funktion zum Speichern der Benutzerdaten in einer JSON-Datei
def save_user_data(data):
    try:
        # Daten in die Datei schreiben
        with open(USER_DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
            print(f"Daten erfolgreich gespeichert: {data}")

        # Überprüfen, ob die Datei tatsächlich Daten enthält
        if os.path.exists(USER_DATA_FILE):
            print("Die Datei wurde erfolgreich erstellt!")
            with open(USER_DATA_FILE, "r") as file:
                content = file.read()
                print(f"Inhalt der gespeicherten Datei: {content}")
        else:
            print("Die Datei wurde nicht erstellt.")
    except Exception as e:
        print(f"Fehler beim Speichern der Datei: {e}")

# Beispiel, wie Benutzerdaten gespeichert werden könnten
def example_usage():
    user_data = load_user_data()  # Lade Benutzerdaten

    # Hier fügst du dem Benutzer etwas hinzu, z.B. einen Rang für einen Modus
    user_data['123456789'] = {"name": "SpielerName", "rank": "Diamond"}

    # Speichern der neuen Daten
    save_user_data(user_data)

# Beispielaufruf der Beispielnutzung
example_usage()


# Emojis für die Spielmodi und Ränge
MODUS_EMOJIS = {
    "🎮": "1v1",
    "👫": "2v2",
    "👨‍👨‍👦‍👦": "3v3",
    "🏀": "Basketball",
    "❄️": "Schneefrei",
    "🔧": "Rumble"
}

RANK_EMOJIS = {
    "🟤": "Bronze",
    "⚪": "Silber",
    "🟡": "Gold",
    "🟢": "Platin",
    "🔵": "Diamant",
    "🟣": "Champion",
    "🟠": "Grand Champion",
    "✨": "SSL"
}

USER_DATA_FILE = "Epic-ID.json"  # Die JSON-Datei, die die Benutzerdaten speichert

# Funktion zum Laden der Benutzerdaten
def load_user_data():
    try:
        if not os.path.exists(USER_DATA_FILE):
            print(f"Datei {USER_DATA_FILE} existiert nicht. Eine neue Datei wird erstellt.")
            save_user_data({})  # Erstellt eine leere Datei
            return {}

        with open(USER_DATA_FILE, "r") as file:
            data = json.load(file)
            return data if data else {}  # Rückgabe der Daten oder ein leeres Dictionary
    except FileNotFoundError:
        print(f"Datei {USER_DATA_FILE} nicht gefunden. Eine neue Datei wird erstellt.")
        save_user_data({})  # Erstellt die Datei, wenn sie fehlt
        return {}
    except json.JSONDecodeError as e:
        print(f"Fehler beim Dekodieren der JSON-Datei: {e}. Die Datei wird als leer behandelt.")
        return {}
    except Exception as e:
        print(f"Unbekannter Fehler: {e}")
        return {}

# Funktion zum Speichern der Benutzerdaten
def save_user_data(data):
    try:
        with open(USER_DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
            print(f"Daten erfolgreich gespeichert: {data}")
    except Exception as e:
        print(f"Fehler beim Speichern der Datei: {e}")


@bot.command(name="setup_rank")
async def setup_rank(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author  # Falls kein Benutzer angegeben ist, wird der Befehl für den Aufrufer ausgeführt

    embed = discord.Embed(
        title=f"Rocket League Rang Setup für {member.display_name}",
        description=(
            "Wähle bitte für jeden Modus deinen Rang aus:\n"
            "1️⃣ **Wähle einen Modus:**\n"
            "🎮 - 1v1\n👫 - 2v2\n👨‍👨‍👦‍👦 - 3v3\n🏀 - Basketball\n❄️ - Schneefrei\n🔧 - Rumble\n\n"
            "2️⃣ **Wähle deinen Rang:**\n"
            "🟤 - Bronze\n⚪ - Silber\n🟡 - Gold\n🟢 - Platin\n🔵 - Diamant\n🟣 - Champion\n🟠 - Grand Champion\n✨ - SSL"
        ),
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=embed)

    # Reaktionen für Modi und Ränge hinzufügen
    for emoji in MODUS_EMOJIS:
        await message.add_reaction(emoji)
    for emoji in RANK_EMOJIS:
        await message.add_reaction(emoji)

    def check_modus(reaction, user):
        return user == member and str(reaction.emoji) in MODUS_EMOJIS

    def check_rank(reaction, user):
        return user == member and str(reaction.emoji) in RANK_EMOJIS

    try:
        user_data = load_user_data()
        user_id = str(member.id)

        # Falls der Benutzer noch keine Daten hat, initialisieren wir sie
        if user_id not in user_data:
            user_data[user_id] = {
                "epic_id": None,  # Dies kann später mit der Epic-ID aktualisiert werden
                "ranks": {}  # Hier werden die Ränge gespeichert
            }
            print(f"Benutzerdaten für {member.display_name} initialisiert.")

        # Erstellen eines leeren Modus-Rank-Setups
        rank_selections = {}

        # Modus auswählen
        for mode_emoji, mode in MODUS_EMOJIS.items():
            await ctx.send(f"{member.mention}, wähle deinen Rang für den Modus **{mode}**.")
            try:
                modus_reaction, _ = await bot.wait_for("reaction_add", timeout=120.0, check=check_modus)
                modus = MODUS_EMOJIS[str(modus_reaction.emoji)]

                # Rang auswählen
                await ctx.send(f"{member.mention}, wähle nun deinen Rang für **{modus}**.")
                rank_reaction, _ = await bot.wait_for("reaction_add", timeout=120.0, check=check_rank)
                rank = RANK_EMOJIS[str(rank_reaction.emoji)]

                # Speichern der Auswahl
                rank_selections[modus] = rank
                print(f"Modus: {modus}, Rang: {rank}")

            except asyncio.TimeoutError:
                await ctx.send(f"⚠️ Zeitüberschreitung! Bitte versuche es später erneut.")
                return  # Stoppt den weiteren Ablauf, wenn eine Zeitüberschreitung passiert

        # Hier speichern wir die Ränge für den Benutzer
        user_data[user_id]["ranks"] = rank_selections
        save_user_data(user_data)

        # Tabelle der Ränge als Embed anzeigen
        rank_table = "\n".join([f"**{mode}**: {rank}" for mode, rank in rank_selections.items()])
        await ctx.send(f"{member.mention}, deine Rang-Auswahl:\n{rank_table}")
    except Exception as e:
        await ctx.send(f"⚠️ Fehler: {e}")


#command rank sehen
@bot.command(name="rlrank")
async def show_rank(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author  # Falls kein Benutzer angegeben ist, wird der Befehl für den Aufrufer ausgeführt

    user_data = load_user_data()  # Benutzerdaten laden
    user_id = str(member.id)

    # Überprüfen, ob der Benutzer existiert und die Ränge für den Benutzer vorhanden sind
    if user_id in user_data and "ranks" in user_data[user_id]:
        ranks = user_data[user_id]["ranks"]

        # Anzeige der Ränge für den Benutzer
        rank_table = "\n".join([f"**{mode}**: {rank}" for mode, rank in ranks.items()])
        await ctx.send(f"{member.mention}, hier sind deine Ränge:\n{rank_table}")
    else:
        await ctx.send(f"{member.mention} hat noch keine Ränge für die Spielmodi festgelegt.")


#----------------------------------------------------------------------------------------------------------------


#----------------------------------Willkommen automatisch funktion funktioniert nicht---------------------------------------
# Event, wenn ein Mitglied dem Server beitritt
@bot.event
async def on_member_join(member):
    # Überprüfen, ob der Kanal existiert
    welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        await welcome_channel.send(f"Willkommen {member.mention}! Schön, dass du hier bist! 🎉")
    else:
        print(f"Willkommenskanal mit ID {WELCOME_CHANNEL_ID} konnte nicht gefunden werden.")

# Event, wenn eine Nachricht gesendet wird
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == FIRST_MESSAGE_CHANNEL_ID:
        user_data = load_user_data()  # Benutzerdaten laden
        if str(message.author.id) not in user_data:
            await message.channel.send(f"Hallo {message.author.mention}! Willkommen im Chat! 🎉")
            user_data[str(message.author.id)] = {"name": message.author.name, "first_message": True}
            save_user_data(user_data)  # Benutzerdaten speichern

    await bot.process_commands(message)
# ------------------------------------------------------------------------------------------------


#------------------------MITGLIEDER ANZAHL------------------------------------------------------
@bot.event
async def on_ready():
    print(f"Bot {bot.user} ist online und bereit!")

# Command: Mitgliederanzahl anzeigen
@bot.command(name="mitgliederanzahl")
async def mitgliederanzahl(ctx):
    # Anzahl der Mitglieder des Servers holen
    member_count = ctx.guild.member_count
    # Antwort an den Benutzer senden
    await ctx.send(f"👥 Dieser Server hat aktuell **{member_count} Mitglieder**!")

#---------------------------------------------------------------------------------------------------

#----------------------------witzigenfos feiertage-----------------------------------
# Event: Feiertagsnachricht posten
@tasks.loop(hours=24)  # Führt den Code alle 24 Stunden aus
async def check_for_holiday():
    holiday_name = get_today_holiday()

    if holiday_name:
        # Witzige Information zum Feiertag holen
        fun_fact = get_fun_fact(holiday_name)

        # Kanal-ID hier anpassen (der Kanal, in dem die Nachricht gesendet wird)
        channel = bot.get_channel(1268292415089803386)  # Deine Kanal-ID
        if channel:
            await channel.send(f"🎉 Heute ist {holiday_name}! {fun_fact}")

# Event: Bot ist bereit
@bot.event
async def on_ready():
    print(f"Bot {bot.user} ist online und bereit!")
    check_for_holiday.start()  # Startet den Feiertags-Check

# Command: Feiertag-Check
@bot.command(name="feiertag")
async def feiertag(ctx):
    # Überprüfen, ob heute ein Feiertag ist
    holiday_name = get_today_holiday()

    if holiday_name:
        # Witzige Information zum Feiertag holen
        fun_fact = get_fun_fact(holiday_name)
        await ctx.send(f"🎉 Heute ist {holiday_name}! {fun_fact}")
    else:
        # Kein Feiertag heute, den nächsten anstehenden Feiertag anzeigen
        next_holiday_name, next_holiday_date = get_next_holiday()
        if next_holiday_name:
            await ctx.send(f"Heute ist kein Feiertag. Der nächste Feiertag ist {next_holiday_name} am {next_holiday_date.strftime('%d.%m.%Y')}! 🎉")
        else:
            await ctx.send("Es sind keine weiteren Feiertage in diesem Jahr geplant.")



#---------------------------------------------------------------------------------------
@bot.event
async def on_ready():
    print(f'Wir sind eingeloggt als {bot.user}')









# ------------------------------------------------------------------------------------------------


@bot.command(name="play")
async def play_song(ctx, *, song_name: str):
    global current_song, is_playing, voice_client

    if voice_client is None or not voice_client.is_connected():
        # Verbinde den Bot mit dem Sprachkanal des Benutzers
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
        else:
            await ctx.send("Du musst in einem Sprachkanal sein, damit ich Musik abspielen kann!")
            return

    # yt-dlp Optionen
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,  # Nur ein Video abspielen, keine Playlists
        'quiet': False,  # Detaillierte Ausgaben für Fehlerbehebung
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Speicherort für temporäre Dateien
    }

    try:
        # Sucht nach dem Song auf YouTube mit dem korrekten Songnamen
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=False)  # Sucht nach dem Song
            entries = info['entries']  # Alle Ergebnisse der Suche
            if not entries:
                await ctx.send("Kein Song gefunden.")
                return

            # Wählen des ersten Ergebnisses
            video = entries[0]
            url2 = video['url']
            title = video['title']

            # Zeigt den Titel des Songs an und fragt den Benutzer, ob es der richtige Song ist
            await ctx.send(f"Spiele jetzt: **{title}**! Ist das der richtige Song? (Antwort mit 'Ja' oder 'Nein')")

            # Benutzerantwort abwarten
            def check(m):
                return m.author == ctx.author and m.content.lower() in ['ja', 'nein']

            msg = await bot.wait_for('message', check=check)

            if msg.content.lower() == 'ja':
                # Wenn der Song korrekt ist, spiele ihn ab
                voice_client.play(discord.FFmpegPCMAudio(url2), after=lambda e: print(f"done {e}"))
                current_song = song_name
                is_playing = True
            else:
                await ctx.send("Suche einen anderen Song...")

    except Exception as e:
        await ctx.send(f"Fehler beim Abspielen des Songs: {e}")
        print(f"Fehler beim Abspielen: {e}")

# Musiksteuerung
@bot.command(name="pause")
async def pause_music(ctx):
    global is_playing
    if is_playing and voice_client:
        voice_client.pause()
        is_playing = False
        await ctx.send("Musik pausiert.")

@bot.command(name="resume")
async def resume_music(ctx):
    global is_playing
    if not is_playing and voice_client:
        voice_client.resume()
        is_playing = True
        await ctx.send("Musik fortgesetzt.")

@bot.command(name="stop")
async def stop_music(ctx):
    global is_playing
    if voice_client:
        voice_client.stop()
        await voice_client.disconnect()
        is_playing = False
        await ctx.send("Musik gestoppt und Bot vom Sprachkanal getrennt.")




#Bot Statusanzeige
# Setting `Playing ` status
#await bot.change_presence(activity=discord.Game(name="a game")

# Setting `Streaming ` status
#await bot.change_presence(activity=discord.Streaming(name="My Stream", url=my_twitch_url)

# Setting `Listening ` status
#await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="a song")

# Setting `Watching ` status
#await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="a movie")

#beispiel
#@bot.event
#async def on_ready():
#    activity = discord.Game(name="Netflix", type=3)
#    await bot.change_presence(status=discord.Status.idle, activity=activity)
#    print("Bot is ready!")


@bot.event
async def on_ready():
    activity = activity = discord.Activity(type=discord.ActivityType.watching, name="Studiert im Pflanzen Lexika")
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print("ZIMMERPFLANZE ist erblüht!")



@bot.command(name="hallo")
async def hello(ctx):
    # ID des speziellen Benutzers 1 (mein Gebieter)
    special_user_id_1 = 697482476423217192
    # ID des speziellen Benutzers 2 Rampi (Freund von Klide)
    special_user_id_2 = 396121690578616331
    # ID des speziellen Benutzers Tainer
    special_user_id_3 = 807713388851363880

    # Wenn der Absender des Befehls der erste spezielle Benutzer ist
    if ctx.author.id == special_user_id_1:
        # Antworte mit einer speziellen Nachricht für diesen Benutzer
        await ctx.send(f"Hallo mein Gebieter bitte gieß mich ich brauche Wasser {ctx.author.mention}!")
    # Wenn der Absender des Befehls der zweite spezielle Benutzer ist
    elif ctx.author.id == special_user_id_2:
        # Antworte mit einer speziellen Nachricht für diesen Benutzer
        await ctx.send(f"Seid gegrüßt mein AALiger Freund von Klide, schön dass du da bist {ctx.author.mention}! @all schaut doch mal bei ihm auf Twitch vorbei: https://www.twitch.tv/rampvgegaming")
    elif ctx.author.id == special_user_id_3:
        await ctx.send(f"Hallo Edler Herr, Was ein Blumiger Anblick dich hier anzutreffen {ctx.author.mention}! @all schaut doch mal bei ihm auf Twitch vorbei: https://www.twitch.tv/dereurotainer")
    else:
        # Für alle anderen Benutzer antworte mit ihrem normalen Namen
        await ctx.send(f"Hallo {ctx.author.display_name}!")



# Hangman Spiel starten
@bot.command()
async def hangman(ctx):
    global current_word, guessed_letters, max_attempts

    current_word = random.choice(word_list)  # Zufälliges Wort auswählen
    guessed_letters = []  # Leere die Liste der geratenen Buchstaben
    max_attempts = 6  # Maximal 6 Versuche
    await ctx.send(f"Das Hangman-Spiel startet! Rate einen Buchstaben! Das Wort hat {len(current_word)} Buchstaben.")

# Hangman Buchstaben raten
@bot.command()
async def guess(ctx, letter: str):
    global current_word, guessed_letters, max_attempts

    letter = letter.lower()
    if len(letter) != 1 or not letter.isalpha():
        await ctx.send("Bitte gib nur einen gültigen Buchstaben ein!")
        return

    # Überprüfen, ob der Buchstabe schon geraten wurde
    if letter in guessed_letters:
        await ctx.send(f"Du hast den Buchstaben {letter} bereits geraten!")
        return

    guessed_letters.append(letter)

    # Überprüfen, ob der Buchstabe im Wort ist
    if letter in current_word:
        await ctx.send(f"Richtig! Der Buchstabe {letter} ist im Wort.")
    else:
        await ctx.send(f"Falsch! Der Buchstabe {letter} ist nicht im Wort.")
        max_attempts -= 1

    # Zeige das aktuelle Wort und die verbleibenden Versuche
    displayed_word = ''.join([letter if letter in guessed_letters else '_' for letter in current_word])
    await ctx.send(f"Aktuelles Wort: {displayed_word}")
    await ctx.send(f"Verbleibende Versuche: {max_attempts}")

    # Überprüfen, ob das Wort vollständig erraten wurde
    if displayed_word == current_word:
        await ctx.send(f"Herzlichen Glückwunsch! Du hast das Wort {current_word} erraten!")
        current_word = None  # Setze das Wort zurück
        max_attempts = 6  # Setze die Versuche zurück

    # Überprüfen, ob der Benutzer verloren hat
    if max_attempts == 0:
        await ctx.send(f"Du hast verloren! Das Wort war {current_word}.")
        current_word = None  # Setze das Wort zurück
        max_attempts = 6  # Setze die Versuche zurück

# Tic-Tac-Toe Spiel starten
@bot.command()
async def tictactoestart(ctx):
    global game_over, board, players, current_player

    if game_over:
        game_over = False
        board = [' ' for _ in range(9)]  # Leere das Brett
        players = []  # Keine Spieler, es müssen zwei Spieler beitreten
        current_player = 'X'  # Spieler X startet
        await ctx.send("Das Spiel startet! Spieler X, du kannst mit !join beitreten. Sobald zwei Spieler beitreten, wird das Spiel beginnen.")
    else:
        await ctx.send("Ein Spiel läuft bereits! Beende das aktuelle Spiel mit !end und starte ein neues.")

# Tic-Tac-Toe Join
@bot.command()
async def join(ctx):
    global players

    if len(players) < 2:
        if ctx.author not in players:
            players.append(ctx.author)
            if len(players) == 1:
                await ctx.send(f"{ctx.author.display_name} ist dem Spiel beigetreten! Es ist jetzt Spieler O's Zug.")
            else:
                await ctx.send(f"{ctx.author.display_name} ist dem Spiel beigetreten! Es ist jetzt Spieler X's Zug.")
        else:
            await ctx.send(f"Du bist bereits im Spiel, {ctx.author.display_name}!")
    else:
        await ctx.send("Es sind bereits zwei Spieler im Spiel. Du kannst nicht mehr beitreten.")

# Tic-Tac-Toe End
@bot.command()
async def end(ctx):
    global game_over, board, players
    game_over = True
    board = [' ' for _ in range(9)]
    players = []
    await ctx.send("Das Spiel wurde beendet.")

# Tic-Tac-Toe Move
@bot.command()
async def move(ctx, position: int):
    global game_over, players, current_player, board

    if len(players) < 2:
        await ctx.send("Es müssen mindestens zwei Spieler teilnehmen! Starte das Spiel mit !tictactoestart und der zweiten Person, die mit !join beitritt.")
        return

    if game_over:
        await ctx.send("Das Spiel ist bereits beendet. Starte ein neues mit !tictactoestart.")
        return

    if ctx.author != players[0] and ctx.author != players[1]:
        await ctx.send(f"Du bist nicht im Spiel, {ctx.author.display_name}! Um mitzumachen, schreibe !join.")
        return

    if ctx.author == players[0] and current_player == 'O':
        await ctx.send(f"Es ist nicht dein Zug, {ctx.author.display_name}. Es ist Spieler X's Zug.")
        return
    elif ctx.author == players[1] and current_player == 'X':
        await ctx.send(f"Es ist nicht dein Zug, {ctx.author.display_name}. Es ist Spieler O's Zug.")
        return

    try:
        position -= 1  # Um 1-basiert in eine 0-basierten Index umzuwandeln
        if board[position] != ' ':
            await ctx.send(f"Die Position {position+1} ist bereits besetzt! Versuch es noch mal.")
            return
        board[position] = current_player
    except (IndexError, ValueError):
        await ctx.send("Bitte gib eine gültige Position zwischen 1 und 9 ein.")
        return

    # Anzeige des Spiels nach dem Zug
    await show_board(ctx)

    # Überprüfen, ob es einen Gewinner gibt
    if check_winner():
        await ctx.send(f"Spieler {current_player} hat gewonnen! Herzlichen Glückwunsch!")
        game_over = True
        return

    # Überprüfen auf Unentschieden
    if ' ' not in board:
        await ctx.send("Es ist ein Unentschieden!")
        game_over = True
        return

    # Wechsel zum nächsten Spieler
    current_player = 'O' if current_player == 'X' else 'X'
    await ctx.send(f"Jetzt ist Spieler {current_player} dran.")

# Funktion zum Anzeigen des Tic-Tac-Toe Boards
async def show_board(ctx):
    board_str = f"""
    {board[0]} | {board[1]} | {board[2]}
    ---------
    {board[3]} | {board[4]} | {board[5]}
    ---------
    {board[6]} | {board[7]} | {board[8]}
    """
    await ctx.send(f"```\n{board_str}\n```")

# Funktion zum Überprüfen des Gewinners
def check_winner():
    # Alle Gewinnmöglichkeiten für Tic-Tac-Toe (Horizontale, Vertikale, Diagonal)
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertikal
        [0, 4, 8], [2, 4, 6]  # Diagonal
    ]

    for combination in winning_combinations:
        if board[combination[0]] == board[combination[1]] == board[combination[2]] != ' ':
            return True
    return False

# Event-Handling und AutoMod
# -----------------------------



@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Blockiere gebannte Wörter
    for word in BANNED_WORDS:
        if word in message.content.lower():
            await message.delete()
            await message.channel.send(
                f"⚠️ {message.author.mention}, bitte halte dich an die Serverregeln!"
            )
            return

    # --- Link-Blockierung: Nur Admins und "Linksender"-Rolle dürfen Links posten ---
    link_regex = re.compile(r'https?://(?:www\.)?\S+')  # Regex zum Erkennen von Links
    if link_regex.search(message.content):  # Prüft, ob ein Link enthalten ist
        # Überprüfe, ob der Benutzer Admin oder "Linksender"-Rolle hat
        if not message.author.guild_permissions.administrator and "Linksender" not in [role.name for role in message.author.roles]:
            await message.delete()
            await message.channel.send(
                f"🚫 {message.author.mention}, das Posten von Links ist nur Administratoren und Benutzern mit der Rolle 'Linksender' erlaubt!"
            )
            return

    await bot.process_commands(message)


@bot.command() # Dies ist ein Dekorator, der den Befehl als Bot-Befehl registriert
async def commandlist(ctx): # Definiert den Befehl mit dem Namen "commandlist"
    commands = """
    **Verfügbare Befehle:**

    !europflanze - Los schnell klick auf seinem Twitch Link und sei dabei!
    !hallo - Begrüßt den Benutzer.
    !play [Songname] - Spielt ein Musikstück ab.
    !pause - Pausiert die Musik.
    !resume - Setzt die Musik fort.
    !stop - Stoppt die Musik und trennt den Bot vom Sprachkanal.

    !hangman - Startet ein Hangman-Spiel.
    !guess [Buchstabe] - Rate einen Buchstaben im Hangman-Spiel.
    !tictactoestart - Startet ein Tic-Tac-Toe-Spiel.
    !join - Tritt einem Tic-Tac-Toe-Spiel bei.
    !move [Position] - Mache einen Zug im Tic-Tac-Toe-Spiel (Position 1-9).
    !end - Beendet das Tic-Tac-Toe-Spiel.

    **Rocket League Befehle:**

    !rlrank - Zeigt die Rangliste des Benutzers in den verschiedenen Spielmodi an.
    !setup_rank @Benutzernamen - Setzt die Ränge für einen Benutzer in den verschiedenen Spielmodi.

    !feiertag - Zeigt dir den bevorstehenden Feiertag an.
    !mitgliederanzahl - Zeigt die aktuelle Anzahl der Teilnehmer auf diesem Server.

    **Game Angebote Befehle:**

    !steamsales - TOP ANGEBOTE AUF STEAM.
    !gmgdeals - Zeigt Angebote AUF greenmangaming.

     **Game NEWS Befehle:**

    !topnewgames - Zeigt Neue Games aus dem Jahr 2024 Quelle : Gamestar.
    !topnewgames2025 - Zeigt Neue Games aus dem Jahr 2025 Quelle: playcentral.

    """
    await ctx.send(commands)  # Diese Zeile sendet die Nachricht


#Bann_words Automod # Befehle zur Verwaltung
@bot.command(name="add_word")
@commands.has_permissions(administrator=True)
async def add_banned_word(ctx, *, word: str):
    """Fügt ein neues gebanntes Wort hinzu und speichert es."""
    if word.lower() not in BANNED_WORDS:
        BANNED_WORDS.append(word.lower())
        save_banned_words(BANNED_WORDS)
        await ctx.send(f"✅ '{word}' wurde zur Liste der gebannten Wörter hinzugefügt.")
    else:
        await ctx.send(f"'{word}' ist bereits in der Liste.")

@bot.command(name="remove_word")
@commands.has_permissions(administrator=True)
async def remove_banned_word(ctx, *, word: str):
    """Entfernt ein gebanntes Wort und aktualisiert die Datei."""
    if word.lower() in BANNED_WORDS:
        BANNED_WORDS.remove(word.lower())
        save_banned_words(BANNED_WORDS)
        await ctx.send(f"✅ '{word}' wurde aus der Liste der gebannten Wörter entfernt.")
    else:
        await ctx.send(f"'{word}' ist nicht in der Liste.")

@bot.command(name="list_words")
@commands.has_permissions(administrator=True)
async def list_banned_words(ctx):
    """Listet alle gebannten Wörter."""
    if BANNED_WORDS:
        await ctx.send("📝 Gebannte Wörter:\n" + ", ".join(BANNED_WORDS))
    else:
        await ctx.send("Die Liste der gebannten Wörter ist leer.")

#spam schutz z.b. hallo x3

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Hole die letzten Nachrichteninformationen des Nutzers
    user_id = message.author.id
    current_time = message.created_at.timestamp()

    # Hole den Spam-Schutz-Zeitrahmen für diese Nachricht
    spam_time_frame = get_spam_time_frame(message)

    # Überprüfe, ob der Benutzer kürzlich dieselbe Nachricht gesendet hat
    if user_id in user_last_messages:
        last_msg, last_time = user_last_messages[user_id]

        # Gleiche Nachricht innerhalb des Zeitrahmens (3 Sekunden für kurze Nachrichten und 5 Sekunden für längere)
        if message.content == last_msg and current_time - last_time < spam_time_frame:
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention}, bitte spamme nicht!")
            return

    # Speichere die aktuelle Nachricht und deren Zeitpunkt
    user_last_messages[user_id] = (message.content, current_time)

    # Nachrichten von inaktiven Nutzern automatisch entfernen, wenn der Cache zu groß wird (mehr als 1000 Nachrichten)
    if len(user_last_messages) > 1000:
        user_last_messages.popitem(last=False)  # Entfernt die älteste Nachricht

    await bot.process_commands(message)  # Wichtige Zeile, damit Befehle weiterhin funktionieren


#spieler kanal wechseln
@bot.command(name="switch")
@commands.has_permissions(administrator=True)  # Nur Administratoren dürfen diesen Befehl ausführen
async def switch_user(ctx, user: discord.User, channel_id: str):
    """Bewegt einen Benutzer zwischen einem Text-Channel oder Voice-Channel."""

    # Hole den Channel anhand der Channel-ID
    channel = ctx.guild.get_channel(int(channel_id))

    # Überprüfe, ob der Channel existiert
    if channel is None:
        await ctx.send(f"❌ Der Channel mit der ID '{channel_id}' wurde nicht gefunden!")
        return

    # Wenn der Channel ein Voice-Channel ist
    if isinstance(channel, discord.VoiceChannel):
        # Überprüfe, ob der Benutzer bereits in einem Voice-Channel ist
        if user.voice is None:
            await ctx.send(f"❌ {user.mention} ist nicht in einem Voice-Channel und kann daher nicht verschoben werden.")
        else:
            try:
                # Verschiebe den Benutzer in den Voice-Channel
                await user.move_to(channel)
                await ctx.send(f"✅ {user.mention} wurde erfolgreich in den Voice-Channel '{channel.name}' verschoben.")
            except discord.Forbidden:
                await ctx.send("❌ Ich habe nicht genug Berechtigungen, um diesen Benutzer zu verschieben!")
            except discord.HTTPException as e:
                await ctx.send(f"❌ Fehler beim Verschieben des Benutzers: {e}")

    # Wenn der Channel ein Text-Channel ist
    elif isinstance(channel, discord.TextChannel):
        # Überprüfe, ob der Benutzer bereits im Text-Channel ist
        if user in channel.members:
            await ctx.send(f"✅ {user.mention} ist bereits im Text-Channel '{channel.name}'.")
        else:
            try:
                # Sende eine Nachricht und weise den Benutzer darauf hin, dass er wechseln soll
                await ctx.send(f"⚠️ {user.mention}, bitte gehe in den Text-Channel '{channel.name}'!")
                await channel.send(f"👋 {user.mention} wurde zu mir hergerufen!")
            except discord.Forbidden:
                await ctx.send("❌ Ich habe nicht genug Berechtigungen, um eine Nachricht zu senden!")
            except discord.HTTPException as e:
                await ctx.send(f"❌ Fehler beim Senden der Nachricht: {e}")

#pflanzenfakten

@bot.event
async def on_message(message):
    # Sicherstellen, dass der Bot nicht auf andere Bots reagiert
    if message.author.bot:
        return

    # Reagiere auf pflanzenbezogene Nachrichten
    plant_response = plant_related_response(message.content, message.author.display_name)

    if plant_response:
        # Antwort an den Channel senden
        await message.channel.send(plant_response)

    # Weiterverarbeitung von Befehlen
    await bot.process_commands(message)




# Bot starten
bot.run(discord_api_key)

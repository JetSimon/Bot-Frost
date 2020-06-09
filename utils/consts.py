import os
import platform
import random
import sys

import discord
import pytz
from discord.ext.commands import BucketType
from dotenv import load_dotenv

from utils.misc import on_prod_server

print(f"### Platform == {platform.platform()} ###")

if "Windows" in platform.platform():
    print("### Windows environment set ###")
    load_dotenv(dotenv_path="variables.env")
elif "Linux" in platform.platform():
    if on_prod_server():
        print("### Production environment set ###")
        load_dotenv(dotenv_path="/home/botfrost/bot/variables.env")
    elif not on_prod_server():
        print("### Test environment set ###")
        load_dotenv(dotenv_path="/home/botfrost/bot/variables.env")
else:
    print(f"Unknown Platform: {platform.platform()}")

# Cooldown rates for commands
CD_GLOBAL_RATE = os.getenv("global_rate")
CD_GLOBAL_PER = os.getenv("global_per")
CD_GLOBAL_TYPE = BucketType.user

# Discord Bot Tokens
TEST_TOKEN = os.getenv("TEST_TOKEN")
PROD_TOKEN = os.getenv("DISCORD_TOKEN")
BACKUP_TOKEN = os.getenv("BACKUP_TOKEN")

# SQL information
SQL_HOST = os.getenv("sqlHost")
SQL_USER = os.getenv("sqlUser")
SQL_PASSWD = os.getenv("sqlPass")
SQL_DB = os.getenv("sqlDb")

# Reddit Bot Info
REDDIT_CLIENT_ID = os.getenv("reddit_client_id")
REDDIT_SECRET = os.getenv("reddit_secret")
REDDIT_PW = os.getenv("reddit_pw")

# SSH Information
SSH_HOST = os.getenv("ssh_host")
SSH_USER = os.getenv("ssh_user")
SSH_PW = os.getenv("ssh_pw")

# Twitter variables
TWITTER_CONSUMER_KEY = os.getenv("twitter_consumer_key")
TWITTER_CONSUMER_SECRET = os.getenv("twitter_consumer_secret")
TWITTER_TOKEN_KEY = os.getenv("twitter_token_key")
TWITTER_TOKEN_SECRET = os.getenv("twitter_token_secret")

# Headers for `requests`
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'}

# Embed titles
EMBED_TITLE_HYPE = "Nebraska Football Hype Squad 📈 ⚠ ⛔"

# Consistent timezone
TZ = pytz.timezone("US/Central")

# Discord Roles
ROLE_ADMIN_PROD = 440639061191950336
ROLE_ADMIN_TEST = 606301197426753536
ROLE_MOD_PROD = 443805741111836693
ROLE_POTATO = 583842320575889423
ROLE_ASPARAGUS = 583842403341828115
ROLE_LILRED = 464903715854483487
ROLE_RUNZA = 485086088017215500
ROLE_MEME = 448690298760200195
ROLE_ISMS = 592425861534449674
ROLE_PACKER = 609409451836964878
ROLE_PIXEL = 633698252809699369
ROLE_AIRPOD = 633702209703378978
ROLE_GUMBY = 459569717430976513
ROLE_MINECRAFT = 661409899481268238
ROLE_HYPE_MAX = 682380058261979176
ROLE_HYPE_SOME = 682380101077434480
ROLE_HYPE_NO = 682380119666720789

# Discord Channels
CHAN_HOF_PROD = 487431877792104470
CHAN_HOF_TEST = 606655884340232192
CHAN_DBL_WAR_ROOM = 538419127535271946
CHAN_WAR_ROOM = 525519594417291284
CHAN_BOTLOGS = 458474143403212801
CHAN_SCOTT = 507520543096832001
CHAN_RULES = 651523695214329887
CHAN_NORTH_BOTTTOMS = 620043869504929832
CHAN_RADIO_PROD = 660610967733796902
CHAN_RADIO_TEST = 595705205069185050
CHAN_SCOTTS_BOTS = 593984711706279937
CHAN_POLITICS = 504777800100741120
CHAN_MINECRAFT_ADMIN = 662110504843739148
CHAN_TWITTERVERSE = 636220560010903584
CHAN_TEST_SPAM = 595705205069185047

CHAN_BANNED = (CHAN_BOTLOGS, CHAN_RULES, CHAN_POLITICS, CHAN_MINECRAFT_ADMIN, CHAN_TWITTERVERSE, CHAN_HOF_PROD, CHAN_RULES)
CHAN_STATS_BANNED = (CHAN_DBL_WAR_ROOM, CHAN_WAR_ROOM)

# Reactions
REACTION_HYPE_MAX = "📈"
REACTION_HYPE_SOME = "⚠"
REACTION_HYPE_NO = "⛔"

REACITON_HYPE_SQUAD = (REACTION_HYPE_MAX, REACTION_HYPE_SOME, REACTION_HYPE_NO)

# Servers/guilds
GUILD_PROD = 440632686185414677
GUILD_TEST = 595705205069185045

# Member ID
TEST_BOT_MEMBER = 595705663997476887
PROD_BOT_MEMBER = 593949013443608596

# Footer texts
FOOTER_SECRET = "These messages are anonymous and there is no way to verify messages are accurate."
FOOTER_BOT = "Created by Bot Frost"


# bet_emojis = ["⬆", "⬇", "❎", "⏫", "⏬", "❌", "🔼", "🔽", "✖"]


async def change_my_nickname(client, ctx):
    nicks = ("Bot Frost", "Mario Verbotzco", "Adrian Botinez", "Bot Devaney", "Mike Rilbot", "Robo Pelini", "Devine Ozigbot", "Mo Botty", "Bot Moos", "Luke McBotfry", "Bot Diaco", "Rahmir Botson",
             "I.M. Bott", "Linux Phillips", "Dicaprio Bottle", "Bryce Botheart", "Jobot Chamberlain", "Bot Bando", "Shawn Botson", "Zavier Botts", "Jimari Botler", "Bot Gunnerson", "Nash Botmacher",
             "Botger Craig", "Dave RAMington", "MarLAN Lucky", "Rex Bothead", "Nbotukong Suh", "Grant Bostrom", "Ameer Botdullah", "Botinic Raiola", "Vince Ferraboto", "economybot",
             "NotaBot_Human", "psybot", "2020: the year of the bot")

    try:
        print("~~~ Attempting to change nickname...")
        await client.user.edit(username=random.choice(nicks))
        print(f"~~~ Changed nickname to {client.user.display_name}")
    except discord.HTTPException as err:
        err_msg = "~~~ !!! " + str(err).replace("\n", " ")
        print(err_msg)
    except:
        print(f"~~~ !!! Unknown error!", sys.exc_info()[0])


async def change_my_status(client, ctx=None):
    statuses = (
        "Husker Football 24/7",
        "Currently beating Florida 62-24",
        "Currently giving up 400 yards rushing to one guy",
        "Attempting a swing pass for -1 yards",
        "Missing a PAT or a missing a 21 yard FG",
        "Getting wasted in Haymarket"
    )
    try:
        print("~~~ Attempting to change status...")
        new_activity = random.choice(statuses)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=new_activity))
        print(f"~~~ Changed status to '{new_activity}'")
    except AttributeError as err:
        err_msg = "~~~ !!! " + str(err).replace("\n", " ")
        print(err_msg)
    except discord.HTTPException as err:
        err_msg = "~~~ !!! " + str(err).replace("\n", " ")
        print(err_msg)
    except:
        print(f"~~~ !!! Unknown error!", sys.exc_info()[0])

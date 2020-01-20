import discord
import os
import platform
import random
import sys

import pytz
from discord.ext.commands import BucketType
from dotenv import load_dotenv

import logging

print(f"### Platform == {platform.platform()} ###")

if "Windows" in platform.platform():
    print("### Windows environment set ###")
    load_dotenv(dotenv_path="variables.env")
elif "Linux" in platform.platform():
    if sys.argv[1] == "prod":
        print("### Production environment set ###")
        load_dotenv(dotenv_path="/home/botfrost/bot/variables.env")
    elif sys.argv[1] == "test":
        print("### Test environment set ###")
        load_dotenv(dotenv_path="/home/botfrost/bot/variables.env")
else:
    print(f"Unknown Platform: {platform.platform()}")

# Cooldown rates for commands
_global_rate = os.getenv("global_rate")
_global_per = os.getenv("global_per")
_global_type = BucketType.user

# Discord Bot Tokens
test_token = os.getenv("TEST_TOKEN")
prod_token = os.getenv("DISCORD_TOKEN")
backup_token = os.getenv("BACKUP_TOKEN")

# SQL information
host = os.getenv("sqlHost")
user = os.getenv("sqlUser")
passwd = os.getenv("sqlPass")
db = os.getenv("sqlDb")

# Reddit Bot Info
reddit_client_id = os.getenv("reddit_client_id")
reddit_secret = os.getenv("reddit_secret")
reddit_pw = os.getenv("reddit_pw")

# SSH Information
ssh_host = os.getenv("ssh_host")
ssh_user = os.getenv("ssh_user")
ssh_pw = os.getenv("ssh_pw")

# print("* ", _global_rate, _global_per, _global_type, test_token, prod_token, backup_token, host, user, passwd, db, reddit_client_id, reddit_secret, reddit_pw, ssh_host, ssh_user, ssh_pw,
# sep="\n* ", end="\n\n")

# Headers for `requests`
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'}

# Consistent timezone
tz = pytz.timezone("US/Central")

# Discord Roles
role_admin_prod = 440639061191950336
role_admin_test = 606301197426753536
role_mod_prod = 443805741111836693
role_potato = 583842320575889423
role_asparagus = 583842403341828115
role_lilred = 464903715854483487
role_runza = 485086088017215500
role_meme = 448690298760200195
role_isms = 592425861534449674
role_packer = 609409451836964878
role_pixel = 633698252809699369
role_airpod = 633702209703378978
role_gumby = 459569717430976513
role_minecraft = 661409899481268238

# Discord Channels
chan_HOF_prod = 487431877792104470
chan_HOF_test = 606655884340232192
chan_dbl_war_room = 538419127535271946
chan_war_room = 525519594417291284
chan_botlogs = 458474143403212801
chan_scott = 507520543096832001
chan_rules = 651523695214329887
chan_radio_prod = 660610967733796902
chan_radio_test = 595705205069185050

# Servers/guilds
guild_prod = 440632686185414677
guild_test = 595705205069185045
# bet_emojis = ["⬆", "⬇", "❎", "⏫", "⏬", "❌", "🔼", "🔽", "✖"]


async def change_my_nickname(client, ctx):
    nicks = ("Bot Frost", "Mario Verbotzco", "Adrian Botinez", "Bot Devaney", "Mike Rilbot", "Robo Pelini", "Devine Ozigbot", "Mo Botty", "Bot Moos", "Luke McBotfry", "Bot Diaco", "Rahmir Botson",
             "I.M. Bott", "Linux Phillips", "Dicaprio Bottle", "Bryce Botheart", "Jobot Chamberlain", "Bot Bando", "Shawn Botson", "Zavier Botts", "Jimari Botler", "Bot Gunnerson", "Nash Botmacher",
             "Botger Craig", "Dave RAMington", "MarLAN Lucky", "Rex Bothead", "Nbotukong Suh", "Grant Bostrom", "Ameer Botdullah", "Botinic Raiola", "Vince Ferraboto", "economybot",
             "NotaBot_Human", "psybot", "2020: the year of the bot")

    try:
        print("~~~ Attempting to change nickname...")
        await client.user.edit(username=random.choice(nicks))
        print(f"~~~ Changed nickname to {client.user.username}")

        if ctx:
            await ctx.send(f"Myw new name is... 🥁🥁🥁 {client.user.username}!")
    except discord.HTTPException as err:
        err_msg = "~~~ !!! " + str(err).replace("\n", " ")
        print(err_msg)
        if ctx:
            await ctx.send(err_msg)
    except:
        print(f"Unknown error!")


async def change_my_status(client, ctx=None):
    statuses = ("Husker Football 24/7", "Currently beating Florida 62-24", "Currently giving up 400 yards rushing to one guy", "Attempting a swing pass for -1 yards")
    try:
        print("~~~ Attempting to change status...")
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(statuses)))
        print(f"~~~ Changed status to {client.user.username}")

        if ctx:
            await ctx.send(f"My new status is... 🥁🥁🥁 {client.user.username}!")
    except discord.HTTPException as err:
        err_msg = "~~~ !!! " + str(err).replace("\n", " ")
        print(err_msg)
        if ctx:
            await ctx.send(err_msg)
    except:
        print(f"Unknown error!")


def establish_logger(category: int):
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] [%(levelname)s]: %(message)s",
        datefmt="%d-%b-%y %H:%M:%S"
    )


def print_log(category: int, message: str):
    if category == logging.DEBUG:
        logging.debug(msg=message)
    elif category == logging.INFO:
        logging.info(msg=message)
    elif category == logging.WARNING:
        logging.warning(msg=message)
    elif category == logging.ERROR:
        logging.error(msg=message)
    elif category == logging.CRITICAL:
        logging.critical(msg=message)

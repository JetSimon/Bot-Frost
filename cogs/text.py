import asyncio
import random
import re
import typing
from datetime import datetime, timedelta

import discord
import markovify
import requests
from discord.ext import commands

from utils.client import client
from utils.consts import CD_GLOBAL_RATE, CD_GLOBAL_PER, CD_GLOBAL_TYPE, CHAN_BANNED
from utils.consts import FOOTER_BOT
from utils.consts import TZ
from utils.embed import build_embed
from utils.games import ScheduleBackup
from utils.games import Venue
from utils.mysql import process_MySQL
from utils.mysql import sqlRecordTasks
from utils.thread import send_message


class TextCommands(commands.Cog):
    @commands.command(aliases=["cd", ])
    @commands.cooldown(rate=CD_GLOBAL_RATE, per=CD_GLOBAL_PER, type=CD_GLOBAL_TYPE)
    async def countdown(self, ctx, *, team=None):
        """ Countdown to the most current or specific Husker game """
        edit_msg = await ctx.send("Loading...")
        now_cst = datetime.now().astimezone(tz=TZ)

        def convert_seconds(n):
            secs = n % (24 * 3600)
            hour = secs // 3600
            secs %= 3600
            mins = secs // 60

            return hour, mins

        async def send_countdown(days: int, hours: int, minutes: int, opponent: str, datetime: datetime):
            await edit_msg.edit(content=f"📢 📅:There are __[ {days} days, {hours} hours, {minutes} minutes ]__ until the __[ {opponent} ]__ game at __[ {datetime.strftime('%B %d, %Y %I:%M %p')} ]__")

        games, stats = ScheduleBackup(year=now_cst.year)

        if team is None:
            for game in games:
                if game.game_date_time > now_cst:
                    diff = game.game_date_time - now_cst
                    diff_cd = convert_seconds(diff.seconds)
                    await send_countdown(diff.days, diff_cd[0], diff_cd[1], game.opponent, game.game_date_time)
                    break
        else:
            team = str(team)

            for game in games:
                if team.lower() == game.opponent.lower():
                    diff = game.game_date_time - now_cst
                    diff_cd = convert_seconds(diff.seconds)
                    await send_countdown(diff.days, diff_cd[0], diff_cd[1], game.opponent, game.game_date_time)
                    break

    @commands.command(aliases=["mkv"])
    @commands.cooldown(rate=CD_GLOBAL_RATE, per=CD_GLOBAL_PER, type=CD_GLOBAL_TYPE)
    async def markov(self, ctx, *sources: typing.Union[discord.Member, discord.TextChannel]):
        """ Attempts to create a meaningful sentence from provided sources. If no source is provided, attempt to create a meaningful sentence from current channel. If a bot is provided as a source, a quote from Scott Frost will be used. If a Discord Member (@mention) is provided, member's history in the current channel will be used. """

        edit_msg = await ctx.send("Thinking...")
        source_data = ""
        messages = []

        CHAN_HIST_LIMIT = 2250

        def check_message(auth: discord.Member, msg: discord.Message = None, bot_provided: bool = False):
            if bot_provided:
                f = open("resources/scofro.txt", "r")
                return re.sub(r'[^\x00-\x7f]', r'', f.read())
            else:

                if not auth.bot and msg.channel.id not in CHAN_BANNED and not [ele for ele in client.all_commands.keys() if (ele in msg.content)]:
                    return "\n" + str(msg.content.capitalize())

            return ""

        def cleanup_source_data(source_data: str):
            regex_strings = [
                r"(<@\d{18}>|<@!\d{18}>|<:\w{1,}:\d{18}>|<#\d{18}>)",  # All Discord mentions
                r"((Http|Https|http|ftp|https)://|)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"  # All URLs
            ]

            new_source_data = source_data

            for regex in regex_strings:
                new_source_data = re.sub(regex, "", new_source_data, flags=re.IGNORECASE)

            regex_new_line = r"(\r\n|\r|\n){1,}"  # All new lines
            new_source_data = re.sub(regex_new_line, "\n", new_source_data, flags=re.IGNORECASE)

            regex_front_new_line = r"^\n"
            new_source_data = re.sub(regex_front_new_line, "", new_source_data, flags=re.IGNORECASE)

            regex_multiple_whitespace = r"\s{2,}"
            new_source_data = re.sub(regex_multiple_whitespace, " ", new_source_data, flags=re.IGNORECASE)

            return new_source_data

        if not sources:
            messages = await ctx.message.channel.history(limit=CHAN_HIST_LIMIT).flatten()
            for msg in messages:
                if not msg.author.bot:
                    # source_data += check_message(auth=ctx.message.author, msg=msg, bot_provided=msg.author.bot)
                    source_data += check_message(auth=ctx.message.author, msg=msg, bot_provided=False)
        else:
            if len(sources) > 3:
                await edit_msg.edit(content=edit_msg.content + "Please be patient. Processing might take awhile.")

            for source in sources:
                if type(source) == discord.Member:
                    if source.bot:
                        # source_data += check_message(auth=ctx.message.author, bot_provided=item.bot)
                        continue
                    else:
                        try:
                            messages = await ctx.message.channel.history(limit=CHAN_HIST_LIMIT).flatten()
                            for msg in messages:
                                if msg.author == source:
                                    # source_data += check_message(auth=msg.author, msg=msg, bot_provided=msg.author.bot)
                                    source_data += check_message(auth=msg.author, msg=msg, bot_provided=False)
                        except discord.errors.Forbidden:
                            continue
                elif type(source) == discord.TextChannel:
                    messages = await source.history(limit=CHAN_HIST_LIMIT).flatten()
                    for msg in messages:
                        # source_data += check_message(auth=msg.author, msg=msg, bot_provided=msg.author.bot)
                        source_data += check_message(auth=msg.author, msg=msg, bot_provided=False)

        if source_data:
            source_data = cleanup_source_data(source_data)
        else:
            raise ValueError(f"The Markov chain not processed successfully. The new Markov bot does not include any bot responses. Please try again. ")

        chain = markovify.NewlineText(source_data, well_formed=True)
        punctuation = ("!", ".", "?", "...")

        sentence = chain.make_sentence(max_overlap_ratio=.9, max_overlap_total=27, min_words=7, tries=100) + random.choice(punctuation)

        if sentence is None:
            raise ValueError(f"The Markov chain not processed successfully. Please try again. ")
        else:
            await edit_msg.edit(content=sentence)

    @commands.group()
    @commands.cooldown(rate=CD_GLOBAL_RATE, per=CD_GLOBAL_PER, type=CD_GLOBAL_TYPE)
    async def weather(self, ctx):
        """ Current weather for the next game day location """

        if ctx.invoked_subcommand:
            return

        venues = Venue()
        embed = None
        edit_msg = None
        _venue_name = None
        _weather = None
        _x = None
        _y = None
        _opponent = None

        edit_msg = await ctx.send("Loading...")

        season, season_stats = ScheduleBackup(year=datetime.now().year)
        # season = reversed(season)

        for game in season:
            now_cst = datetime.now().astimezone(tz=TZ)

            if now_cst < game.game_date_time.astimezone(tz=TZ):
                if game.location == "Memorial Stadium":
                    _venue_name = venues[207]["name"]
                    _x = venues[207]["location"]["x"]
                    _y = venues[207]["location"]["y"]
                else:
                    for venue in venues:
                        if venue["city"].lower() == game.location[0].lower() and venue["state"].lower() == game.location[1].lower():
                            _venue_name = venue['name']
                            _x = venue['location']['x']
                            _y = venue['location']['y']
                            break

                r = requests.get(url=f"https://api.weatherbit.io/v2.0/current?key={'39b7915267f04d5f88fa5fe6be6290e6'}&lang=en&units=I&lat={_x}&lon={_y}")
                _weather = r.json()

                embed = discord.Embed(
                    title=f"Weather Forecast for the __[ {game.opponent} ]__ in __[ {_venue_name} / {_weather['data'][0]['city_name']}, {_weather['data'][0]['state_code']} ]__",
                    color=0xFF0000)  # ,
                # description=f"Nebraska's next opponent is __[ {game.opponent} ]__")

                break

        if embed is None:
            await ctx.send("The season is over! No upcoming games found.")
            return

        embed.set_thumbnail(url=f"https://www.weatherbit.io/static/img/icons/{_weather['data'][0]['weather']['icon']}.png")
        embed.set_footer(text="There is a daily 500 call limit to the API used for this command. Do not abuse it.")
        embed.add_field(name="Temperature", value=f"{_weather['data'][0]['temp']} F", inline=False)
        embed.add_field(name="Cloud Coverage", value=f"{_weather['data'][0]['clouds']}%", inline=False)
        embed.add_field(name="Wind Speed", value=f"{_weather['data'][0]['wind_spd']} MPH / {_weather['data'][0]['wind_cdir']}", inline=False)
        embed.add_field(name="Snow Chance", value=f"{_weather['data'][0]['snow']:.2f}%", inline=False)
        embed.add_field(name="Precipitation Chance", value=f"{_weather['data'][0]['precip'] * 100:.2f}%", inline=False)

        if edit_msg is not None:
            await edit_msg.edit(content="", embed=embed)
        else:
            await ctx.send(embed=embed)

    @commands.command(name="24hours", aliases=["24", "24hrs", ])
    @commands.cooldown(rate=CD_GLOBAL_RATE, per=CD_GLOBAL_PER, type=CD_GLOBAL_TYPE)
    async def _24hours(self, ctx):
        """ You have 24 hours to cheer or moam about the game """
        games = ScheduleBackup(year=datetime.now().year)

        for index, game in enumerate(reversed(games)):
            game_dt_cst = game.game_date_time.astimezone(tz=TZ)
            now_cst = datetime.now().astimezone(tz=TZ)
            _24hourspassed = game_dt_cst + timedelta(days=1)
            _24hourspassed = _24hourspassed.astimezone(tz=TZ)

            if now_cst > game_dt_cst:
                try:
                    i = len(games) - (index + 1) if index < len(games) else len(games) - index
                    next_opponent = games[i + 1].opponent  # Should avoid out of bounds

                    if now_cst < _24hourspassed:
                        await ctx.send(f"You have 24 hours to #moaming the __[ {game.opponent} ]__ game! That ends in __[ {_24hourspassed - now_cst} ]__!")
                    else:
                        await ctx.send(f"The 24 hours are up! No more #moaming. Time to focus on the __[ {next_opponent} ]__ game!")
                    break
                except IndexError:
                    await ctx.send("The season is over! No upcoming games found.")
                    return

    @commands.command()
    @commands.cooldown(rate=CD_GLOBAL_RATE, per=CD_GLOBAL_PER, type=CD_GLOBAL_TYPE)
    async def whenjoined(self, ctx, who: discord.Member):
        """ When did you join the server? """
        from utils.client import client

        def sort_second(val):
            return val[1]

        users = client.get_all_members()
        users_sorted = []

        for user in users:
            users_sorted.append([user.name, user.joined_at])

        users_sorted.sort(key=sort_second)

        count = 10

        if not who:
            earliest = "```\n"
            for index, user in enumerate(users_sorted):
                if index < count:
                    earliest += f"#{index + 1:2} - {user[1]}: {user[0]}\n"
            earliest += "```"
            await ctx.send(earliest)
        else:
            for user in users_sorted:
                if user[0] == who.display_name:
                    await ctx.send(f"`{who.display_name} joined at {user[1]}`")
                    return

    @commands.command(aliases=["8b", ])
    @commands.cooldown(rate=CD_GLOBAL_RATE, per=CD_GLOBAL_PER, type=CD_GLOBAL_TYPE)
    async def eightball(self, ctx):
        """ Ask a Magic 8-Ball a question. """
        eight_ball = [
            'As I see it, yes.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Coach V\'s cigar would like this!',
            'Concentrate and ask again.',
            'Definitely yes!',
            'Don’t count on it...',
            'Frosty!',
            'Fuck Iowa!',
            'It is certain.',
            'It is decidedly so.',
            'Most likely...',
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good and reply hazy',
            'Scott Frost approves!',
            'These are the affirmative answers.',
            'Try again...',
            'Without a doubt.',
            'Yes – definitely!',
            'You may rely on it.'
        ]

        random.shuffle(eight_ball)

        embed = build_embed(
            title="BotFrost Magic 8-Ball :8ball: says...",
            description="These are all 100% accurate. No exceptions! Unless an answer says anyone other than Nebraska is good.",
            fields=[
                ["Response", random.choice(eight_ball)]
            ],
            thumbnail="https://i.imgur.com/L5Gpu0z.png",
            footer=FOOTER_BOT
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=CD_GLOBAL_RATE, per=CD_GLOBAL_PER, type=CD_GLOBAL_TYPE)
    async def police(self, ctx, baddie: discord.Member):
        await ctx.send(f"**"
                       f"🚨 NANI 🚨\n"
                       f"\t🚨 THE 🚨\n"
                       f"\t\t🚨 FUCK 🚨\n"
                       f"\t\t\t🚨 DID 🚨\n"
                       f"\t\t\t\t🚨 YOU 🚨\n"
                       f"\t\t\t🚨 JUST 🚨\n"
                       f"\t\t🚨 SAY 🚨\n"
                       f"\t🚨 {baddie.mention} 🚨\n"
                       f"🏃‍♀️💨 🔫🚓🔫🚓🔫🚓"
                       f"\n"
                       f"👮‍📢 Information ℹ provided in the VIP 👑 Room 🏆 is intended for Husker247 🌽🎈 members only ‼🔫. "
                       f"Please do not copy ✏ and paste 🖨 or summarize this content elsewhere‼ Please try to keep all replies in this thread 🧵 for Husker247 members only! "
                       f"🚫 ⛔ 👎 🙅‍♀️Thanks for your cooperation. 😍🤩😘 **")

    @commands.command(aliases=["ud", ])
    @commands.cooldown(rate=CD_GLOBAL_RATE, per=CD_GLOBAL_PER, type=CD_GLOBAL_TYPE)
    async def urbandictionary(self, ctx, *, word: str):
        from bs4 import BeautifulSoup
        r = requests.get(f"http://www.urbandictionary.com/define.php?term={word}")
        soup = BeautifulSoup(r.content, features="html.parser")
        try:
            definition = soup.find("div", attrs={"class": "meaning"}).text
        except AttributeError:
            definition = f"Sorry, we couldn't find: {word}"

        if len(definition) > 1024:
            definition = definition[:1020] + "..."

        import urllib.parse

        await ctx.send(
            embed=build_embed(
                title=f"Urban Dictionary Definition",
                inline=False,
                fields=[
                    [word, definition],
                    ["Link", f"https://www.urbandictionary.com/define.php?term={urllib.parse.quote(string=word)}"]
                ]
            )
        )

    @commands.command(aliases=["rm", ])
    @commands.cooldown(rate=CD_GLOBAL_RATE, per=CD_GLOBAL_PER, type=CD_GLOBAL_TYPE)
    async def remind(self, ctx, who: typing.Union[discord.TextChannel, discord.Member], when: str, *, message: str):
        """ Set a reminder for yourself or channel. Time format examples: 1d, 7h, 3h30m, 1d7h,15m """
        d_char = "d"
        h_char = "h"
        m_char = "m"
        s_char = "s"

        if type(who) == discord.Member and not ctx.author == who:
            await ctx.send("You cannot set reminders for anyone other than yourself!")
            return
        elif type(who) == discord.TextChannel and who.id in CHAN_BANNED:
            await ctx.send(f"You cannot set reminders for {who}!")
            return

        today = datetime.today()  # .astimezone(tz=TZ)

        def get_value(which: str, from_when: str):
            import re

            if which in from_when:
                raw = from_when.split(which)[0]
                if raw.isnumeric():
                    return int(raw)
                else:
                    try:
                        findall = re.findall(r"\D", raw)[-1]
                        return int(raw[raw.find(findall) + 1:])
                    except:
                        return 0
            else:
                return 0

        days = get_value(d_char, when)
        hours = get_value(h_char, when)
        minutes = get_value(m_char, when)
        seconds = get_value(s_char, when)

        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        min_timer_allowed = 5

        if delta.total_seconds() < min_timer_allowed:
            raise ValueError(f"The duration entered is too short! The minimum allowed timer is {min_timer_allowed} seconds.")

        try:
            raw_when = today + delta
        except ValueError:
            raise ValueError("The duration entered is too large!")

        duration = raw_when - today

        alert = today + duration

        await ctx.send(f"Setting a timer for [{who}] in [{duration.total_seconds()}] seconds. The timer will go off at [{alert.strftime('%x %X')}].")
        author = f"{ctx.author.name}#{ctx.author.discriminator}"
        process_MySQL(sqlRecordTasks, values=(who.id, message, str(alert), 1, author))

        import nest_asyncio
        nest_asyncio.apply()
        asyncio.create_task(
            send_message(
                thread=1,
                duration=duration.total_seconds(),
                who=who,
                message=message,
                author=ctx.author,
                flag=str(alert)
            )
        )


def setup(bot):
    bot.add_cog(TextCommands(bot))

# print("### Text Commands loaded! ###")

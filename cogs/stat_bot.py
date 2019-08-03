import requests
from requests.exceptions import HTTPError
from discord.ext import commands
import discord
from bs4 import BeautifulSoup
import json
from ftfy import fix_text

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
husker_schedule = []

class StatBot(commands.Cog, name="CFB Stats"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def stats(self, ctx, year, *, name):
        """ Returns the current season's stats for searched player. """
        pass
        
    @commands.command()
    async def poll(self, ctx):
        """ Returns current Top 25 ranking from the Coach's Poll, AP Poll, and College Football Playoff ranking. """
        # Coaches Poll
        # AP Poll
        # CFP Ranking
        pass
    
    @commands.command()
    async def roster(self, ctx, ear=2019):
        """ Returns the current roster. """
        pass
        
    @commands.command()
    async def boxscore(self, ctx):
        """ Returns the box score of the searched for game. """
        pass
        
    @commands.command()
    async def lastplays(self, ctx):
        pass
    
    @commands.command(aliases=["sched",])
    async def schedule(self, ctx, year=2019):
        """ Returns the Nebraska Huskers football schedule. """
        url = "http://www.huskers.com/SportSelect.dbml?DB_OEM_ID=100&SPID=22&SPSID=3&q_season=" + str(year)

        page = None

        try:
            page = requests.get(headers=headers, url=url)
            page.raise_for_status()
        except HTTPError as http_err:
            print("HTTP error occurred: {}".format(http_err))
        except Exception as err:
            print("Other error:".format(err))

        soup = BeautifulSoup(page.text, 'html.parser')
        find_json = soup.find_all('script')

        temp_str = find_json[1].string
        # This is so ghetto
        # front = "    window.__INITIAL_STATE__ = \'{\"site\":  "
        # end = ",\"status\":\"success\", \"time\":\"08/02/2019 19:25\"}\';  "
        # print("{} {}".format(len(front), len(end)))
        temp_str = temp_str[42:-51]
        fix_text(temp_str)
        temp_str = temp_str.replace("\\", "\\\\")
        # print(">>{}<<".format(temp_str[23772-5:23772+5]))

        husker_schedule = json.loads(temp_str)

        dump = False

        if dump:
            with open("husker_schedule.json", "w") as fp:
                json.dump(husker_schedule, fp, sort_keys=True, indent=4)
                # fp.write(temp_str)
            fp.close()

        for e in husker_schedule:
            print(e['events'])


def setup(bot):
    bot.add_cog(StatBot(bot))
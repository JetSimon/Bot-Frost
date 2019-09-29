import discord
from discord.ext import commands
import json
import dateutil
import datetime
import config
import requests
import mysql
import pytz

bet_emojis = ["⬆", "⬇", "❎", "⏫", "⏬", "❌", "🔼", "🔽", "✖"]


# Load season bets
def load_season_bets():
    f = open('season_bets.json', 'r')
    temp_json = f.read()
    config.season_bets = json.loads(temp_json)
    f.close()


# Allows the ability to load next opponent for sub commands.
def store_next_opponent():
    # Open previously generated JSON from $schedule.
    # To refresh change dump = True manually
    f = open('husker_schedule.json', 'r')
    temp_json = f.read()
    husker_schedule = json.loads(temp_json)
    f.close()

    # Find first game that is scheduled after now()
    counter = 1
    for events in husker_schedule:
        # The date/time is stored in ISO 8601 format. It sucks. Take raw data and manually convert it to the default format.
        check_date_raw = dateutil.parser.parse(events["start_date"])
        check_date = datetime.datetime(day=check_date_raw.day, month=check_date_raw.month, year=check_date_raw.year, hour=check_date_raw.hour, minute=check_date_raw.minute)

        check_now = datetime.datetime.now()

        if check_now < check_date:
            if events["home_team"] != "Nebraska":
                config.current_game.append(events["home_team"])
            else:
                config.current_game.append(events["away_team"])
            config.current_game.append(check_date)
            config.current_game.append(counter)
            break
        # Used for navigating season_bets JSON
        counter += 1

    print(config.current_game)


class BetCommands(commands.Cog, name="Betting Commands"):
    @commands.command()
    async def bet(self, ctx, cmd=None, *, team=None):
        """ Allows users to place bets for Husker games.

        Command usage:
        $bet: show default message and place bets.
        $bet all: show all current bets.
        $bet lines: shows the current lines.
        $bet show <optional, team>: show your most recent bet or bet for another team
        $bet winners <team>: show all the winners of a specific game.
        """
        dbAvailable = config.pingMySQL()
        if not dbAvailable:
            await ctx.send("The MySQL database is currently unavailable. Please try again later.")
            return

        # Creates the embed object for all messages within method
        embed = discord.Embed(title="Husker Game Betting", description="How do you think the Huskers will do in their next game? Place your bets below!", color=0xff0000)
        embed.set_thumbnail(url="https://i.imgur.com/THeNvJm.jpg")
        embed.set_footer(text=config.bet_footer)

        # Load next opponent and bets
        store_next_opponent()
        load_season_bets()

        raw_username = "{}".format(ctx.author)

        # Outputs the betting message to allow the user to see the upcoming opponent and voting reactions.
        if cmd is None:
            if not team:
                team = config.current_game[0].lower()

            url = "https://api.collegefootballdata.com/lines?year={}&week={}&seasonType=regular&team=nebraska".format(config.current_game[1].year, config.current_game[2])
            try:
                r = requests.get(url)
                game_data_raw = r.json()
            except:
                await ctx.send("An error occurred retrieving line data.")
                return

            lines = {}
            try:
                for lines_raw in game_data_raw:
                    lines = lines_raw["lines"]
            except:
                print("No lines available")

            game_dt_raw = config.current_game[1]
            game_dt_utc = pytz.timezone("UTC").localize(game_dt_raw)
            tz_target = pytz.timezone("CST6CDT")
            game_dt_cst = game_dt_utc.astimezone(tz_target)

            embed.add_field(name="Opponent", value="{}\n{}".format(config.current_game[0],game_dt_cst.strftime("%B %d, %Y at %H:%M %p CST")), inline=False)
            embed.add_field(name="Rules", value="1. All bets must be placed prior to kick off.\n2. The final odds are used for scoring purposes.\n3. Only one bet per user per game.\n4. Bets are stored by __Discord__ username.")
            embed.add_field(name="Scoring", value="1 Point : winning or losing the game.\n2 Points: covering or not covering the spread and total points.", inline=False)
            embed.add_field(name="Usage", value="$bet - Show this command\n$bet show - Shows your currently placed bets\n$bet all - Shows the current breakout of all bets placed\n$bet winners [opponent] - Shows the winners for the selected opponent.")

            if lines:
                embed.add_field(name="Spread ({})".format(lines[0]["provider"]), value="{}".format(lines[0]["formattedSpread"]), inline=False)
                embed.add_field(name="Total Points/Over Under ({})".format(lines[0]["provider"]), value="{}".format(lines[0]["overUnder"]), inline=False)
            else:
                embed.add_field(name="Spread (TBD)", value="TBD")
                embed.add_field(name="Total Points/Over Under (TBD)", value="TBD")

            embed.add_field(name="Vote Instructions", value="Bets winning (⬆) or losing (⬇) the game. Clear bet (❎).\nBets over (⏫) or under (⏬) on the spread. Clear bet (❌).\nBets over (🔼) or under (🔽) on total points. Clear bet (✖).\n", inline=False)

            # Store message sent in an object to allow for reactions afterwards
            check_now_raw = datetime.datetime.now()
            check_now = dateutil.parser.parse(str(check_now_raw))

            msg_sent = await ctx.send(embed=embed)
            check_game_datetime = config.current_game[1]
            if check_now < check_game_datetime:
                for e in bet_emojis:
                    await msg_sent.add_reaction(e)
            else:
                print("Reactions not applied because datetime is after kickoff.")

        # Show the user's current bet(s)
        elif cmd == "show":
            userBetWin = "N/A"
            userBetSpread = "N/A"
            userBetMoneyline = "N/A"

            if team:
                if team:
                    with mysql.sqlConnection.cursor() as cursor:
                        cursor.execute(config.sqlRetrieveGameNumber, (team.lower()))
                        gameNumber = cursor.fetchone()
                    mysql.sqlConnection.commit()
                    gameNumber = int(gameNumber["game_number"])

                    with mysql.sqlConnection.cursor() as cursor:
                        cursor.execute(config.sqlRetrieveSpecificBet, (gameNumber, raw_username))
                        checkUserBet = cursor.fetchone()
                    mysql.sqlConnection.commit()

                    if checkUserBet["win"] == 1:
                        userBetWin = "Win"
                    elif checkUserBet["win"] == 0:
                        userBetWin = "Lose"

                    if checkUserBet["spread"] == 1:
                        userBetSpread = "Over"
                    elif checkUserBet["spread"] == 0:
                        userBetSpread = "Under"

                    if checkUserBet["moneyline"] == 1:
                        userBetMoneyline = "Over"
                    elif checkUserBet["moneyline"] == 0:
                        userBetMoneyline = "Under"

                    try:
                        lastUpdate = checkUserBet["date_updated"]
                    except:
                        lastUpdate = "N/A"

                    opponentName = team.title()
                else:
                    await ctx.send("You have no bets for the next game against {}. Check out `$bet` to place your bets!".format(team.title()))
                    return
            else:
                with mysql.sqlConnection.cursor() as cursor:
                    cursor.execute(config.sqlRetrieveBet, (raw_username))
                    userBetsDict = cursor.fetchall()
                mysql.sqlConnection.commit()

                checkUserBet = userBetsDict[len(userBetsDict) - 1]

                if checkUserBet["game_number"] == config.current_game[2]:
                    if checkUserBet["win"] == 1:
                        userBetWin = "Win"
                    elif checkUserBet["win"] == 0:
                        userBetWin = "Lose"

                    if checkUserBet["spread"] == 1:
                        userBetSpread = "Over"
                    elif checkUserBet["spread"] == 0:
                        userBetSpread = "Under"

                    if checkUserBet["moneyline"] == 1:
                        userBetMoneyline = "Over"
                    elif checkUserBet["moneyline"] == 0:
                        userBetMoneyline = "Under"

                    try:
                        lastUpdate = checkUserBet["date_updated"]
                    except:
                        lastUpdate = "N/A"

                    opponentName = config.current_game[0].title()
                else:
                    await ctx.send("You have no bets for the next game against {}. Check out `$bet` to place your bets!".format(config.current_game[0].title()))
                    return

            embed.add_field(name="Author", value=raw_username, inline=False)
            embed.add_field(name="Opponent", value=opponentName, inline=False)
            embed.add_field(name="Win or Loss", value=userBetWin, inline=True)
            embed.add_field(name="Spread", value=userBetSpread, inline=True)
            embed.add_field(name="Over/Under Total Points", value=userBetMoneyline, inline=True)
            embed.add_field(name="Time Placed", value=lastUpdate)
            await ctx.send(embed=embed)

        # Show all bets for the current game
        elif cmd == "all":
            with mysql.sqlConnection.cursor() as cursor:
                cursor.execute(config.sqlRetrieveAllBet, (config.current_game[2]))
                userBetsDict = cursor.fetchall()
            mysql.sqlConnection.commit()

            total_wins = 0
            total_losses = 0
            total_cover_spread = 0
            total_not_cover_spread = 0
            total_cover_moneyline = 0
            total_not_cover_moneyline = 0

            for userBet in userBetsDict:
                if userBet["win"] == 1:
                    total_wins += 1
                elif userBet["win"] == 0:
                    total_losses += 1

                if userBet["spread"] == 1:
                    total_cover_spread += 1
                elif userBet["spread"] == 0:
                    total_not_cover_spread += 1

                if userBet["moneyline"] == 1:
                    total_cover_moneyline += 1
                elif userBet["moneyline"] == 0:
                    total_not_cover_moneyline += 1

            total_winorlose = total_losses + total_wins
            total_spread = total_cover_spread + total_not_cover_spread
            total_moneyline = total_cover_moneyline + total_not_cover_moneyline

            # Creates the embed object for all messages within method
            embed = discord.Embed(title="Husker Game Betting", color=0xff0000)
            embed.set_thumbnail(url="https://i.imgur.com/THeNvJm.jpg")
            embed.set_footer(text=config.bet_footer)

            embed.add_field(name="Opponent", value=config.current_game[0], inline=False)
            if total_wins and total_winorlose:
                embed.add_field(name="Wins", value="{} ({:.2f}%)".format(total_wins, (total_wins / total_winorlose) * 100))
                embed.add_field(name="Losses", value="{} ({:.2f}%)".format(total_losses, (total_losses / total_winorlose) * 100))
            else:
                embed.add_field(name="Wins", value="{} ({:.2f}%)".format(total_wins, 0))
                embed.add_field(name="Losses", value="{} ({:.2f}%)".format(total_losses, 0))

            if total_cover_spread and total_spread:
                embed.add_field(name="Cover Spread", value="{} ({:.2f}%)".format(total_cover_spread, (total_cover_spread / total_spread) * 100))
                embed.add_field(name="Not Cover Spread", value="{} ({:.2f}%)".format(total_not_cover_spread, (total_not_cover_spread / total_spread) * 100))
            else:
                embed.add_field(name="Cover Spread", value="{} ({:.2f}%)".format(total_cover_spread, 0))
                embed.add_field(name="Not Cover Spread", value="{} ({:.2f}%)".format(total_not_cover_spread, 0))

            if total_cover_spread and total_not_cover_moneyline:
                embed.add_field(name="Total Points Over", value="{} ({:.2f}%)".format(total_cover_moneyline, (total_cover_moneyline / total_moneyline) * 100))
                embed.add_field(name="Total Points Under", value="{} ({:.2f}%)".format(total_not_cover_moneyline, (total_not_cover_moneyline / total_moneyline) * 100))
            else:
                embed.add_field(name="Total Points Over", value="{} ({:.2f}%)".format(total_cover_moneyline, 0))
                embed.add_field(name="Total Points Under", value="{} ({:.2f}%)".format(total_not_cover_moneyline, 0))

            await ctx.send(embed=embed)

        # Show all winners for game
        elif cmd == "winners":
            if not team:
                await ctx.send("You must include a team. Example: `$bet winners south alabama`")
                return

            # Need to add check if command is run the day after the game
            with mysql.sqlConnection.cursor() as cursor:
                cursor.execute(config.sqlGetWinWinners, team)
                winners_winorlose = cursor.fetchall()

                cursor.execute(config.sqlGetSpreadWinners, team)
                winners_spread = cursor.fetchall()

                cursor.execute(config.sqlGetMoneylineWinners, team)
                winners_moneyline = cursor.fetchall()

            mysql.sqlConnection.commit()

            def flattenList(param):
                flat = ""
                for item in param:
                    flat += item["user"] + "\n"
                if not flat:
                    flat = "N/A"
                return flat

            winners_winorlose = flattenList(winners_winorlose)
            winners_spread = flattenList(winners_spread)
            winners_moneyline = flattenList(winners_moneyline)

            embed.add_field(name="Win or Lose Winners", value=winners_winorlose)
            embed.add_field(name="Spread Winners", value=winners_spread)
            embed.add_field(name="Total Points Winners", value=winners_moneyline)

            await ctx.send(embed=embed)

        # Show the current leader board. +/- 1 point for winorlose, +/- 2 points for spread and total points
        elif cmd == "leaderboard" or cmd == "lb":
            with mysql.sqlConnection.cursor() as cursor:
                cursor.execute(config.sqlLeaderboard)
                sqlLeaderboard = cursor.fetchmany(size=10)
            mysql.sqlConnection.commit()

            with mysql.sqlConnection.cursor() as cursor:
                cursor.execute(config.sqlAdjustedLeaderboard)
                sqlAverageLeaderboard = cursor.fetchmany(size=10)
            mysql.sqlConnection.commit()

            strLeader = ""
            for user in sqlLeaderboard:
                strLeader += "[{} pts] {}\n".format(int(user["total_points"]), user["user"])

            strAdjustedLeader = ""
            for user in sqlAverageLeaderboard:
                strAdjustedLeader += "[{} pts] {}\n".format(int(user["avg_pts_per_game"]), user["user"])

            embed.add_field(name="Top 10 Ranking", value=strLeader)
            embed.add_field(name="Top 10 Average Points Ranking", value=strAdjustedLeader)
            await ctx.send(embed=embed)

        # Show the current lines if available
        elif cmd == "lines" or cmd == "line" or cmd == "l":
            url = "https://api.collegefootballdata.com/lines?year={}&week={}&seasonType=regular&team=nebraska".format(config.current_game[1].year, config.current_game[2])
            try:
                r = requests.get(url)
                game_data_raw = r.json()
            except:
                await ctx.send("An error occurred retrieving line data.")
                return

            lines = {}
            try:
                for lines_raw in game_data_raw:
                    lines = lines_raw["lines"]
            except:
                print("No lines available")

            if lines:
                embed.add_field(name="Spread ({})".format(lines[0]["provider"]), value="{}".format(lines[0]["formattedSpread"]), inline=False)
                embed.add_field(name="Total Points/Over Under ({})".format(lines[0]["provider"]), value="{}".format(lines[0]["overUnder"]), inline=False)
            else:
                embed.add_field(name="Spread", value="TBD")
                embed.add_field(name="Total Points/Over Under", value="TBD")

            await ctx.send(embed=embed)

        else:
            embed.add_field(name="Error", value="Unknown command. Please reference `$help bet`.")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BetCommands(bot))

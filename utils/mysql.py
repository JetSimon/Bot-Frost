import pymysql.cursors

sqlDatabaseTimestamp = """\
INSERT INTO bot_connections (user, connected, timestamp)
VALUES (%s, %s, %s)"""

sqlLogError = """\
INSERT INTO bot_error_log (user, error)
VALUES (%s, %s)"""

sqlLogUser = """\
INSERT INTO bot_user_log (user, event, comment)
VALUES (%s, %s, %s)"""

sqlLeaderboard = """\
SELECT  
user,  
COUNT(*) as num_games_bet_on,  
SUM(CASE b.win WHEN g.win THEN 1 ELSE 0 END) as correct_wins,  
SUM(CASE b.spread WHEN g.spread THEN 1 ELSE 0 END) as correct_spreads,  
SUM(CASE b.moneyline WHEN g.moneyline THEN 1 ELSE 0 END) as correct_moneylines,  
SUM(CASE b.win WHEN g.win THEN 1 ELSE 0 END + CASE b.spread WHEN g.spread THEN 2 ELSE 0 END + CASE b.moneyline WHEN g.moneyline THEN 2 ELSE 0 END) as total_points  
FROM bets b  
INNER JOIN games g  
ON (b.game_number =  g.game_number)  
WHERE g.finished = true  
GROUP BY user  
ORDER BY total_points DESC;"""

sqlAdjustedLeaderboard = """\
SELECT  
user,  
COUNT(*) as num_games_bet_on,  
SUM(CASE b.win WHEN g.win THEN 1 ELSE 0 END) as correct_wins,  
SUM(CASE b.spread WHEN g.spread THEN 1 ELSE 0 END) as correct_spreads,  
SUM(CASE b.moneyline WHEN g.moneyline THEN 1 ELSE 0 END) as correct_moneylines,  
SUM(CASE b.win WHEN g.win THEN 1 ELSE 0 END + CASE b.spread WHEN g.spread THEN 2 ELSE 0 END + CASE b.moneyline WHEN g.moneyline THEN 2 ELSE 0 END) / COUNT(*) as avg_pts_per_game  
FROM bets b  
INNER JOIN games g  
ON (b.game_number =  g.game_number)  
WHERE g.finished = true  
GROUP BY user  
ORDER BY avg_pts_per_game DESC;"""

sqlGetWinWinners = """\
SELECT b.user FROM
    bets b INNER JOIN games g ON (b.game_number =  g.game_number)
WHERE
    b.win = g.win AND g.opponent = %s;
"""

sqlGetSpreadWinners = """\
SELECT b.user FROM
    bets b INNER JOIN games g ON (b.game_number =  g.game_number)
WHERE
    b.spread = g.spread AND g.opponent = %s;
"""

sqlGetMoneylineWinners = """\
SELECT b.user 
FROM bets b 
INNER JOIN games g 
ON (b.game_number =  g.game_number)
WHERE b.moneyline = g.moneyline AND g.opponent = %s;
"""

sqlInsertWinorlose = """\
INSERT INTO bets (game_number, user, win, date_updated) 
VALUES  (%s, %s, %s, NOW()) 
ON DUPLICATE KEY UPDATE  win=%s;
"""

sqlInsertSpread = """\
INSERT INTO bets (game_number, user, spread, date_updated) 
VALUES  (%s, %s, %s, NOW()) 
ON DUPLICATE KEY UPDATE  spread=%s;
"""

sqlInsertMoneyline = """\
INSERT INTO bets (game_number, user, moneyline, date_updated) 
VALUES  (%s, %s, %s, NOW()) 
ON DUPLICATE KEY UPDATE  moneyline=%s;
"""

sqlRetrieveBet = """\
SELECT * FROM bets b WHERE b.user = %s;
"""

sqlRetrieveSpecificBet = """\
SELECT * FROM bets b WHERE b.game_number = %s AND b.user = %s;
"""

sqlRetrieveGameNumber = """\
SELECT g.game_number FROM games g WHERE g.opponent = %s;
"""

sqlRetrieveAllBet = """\
SELECT * FROM bets b WHERE b.game_number = %s;
"""

sqlUpdateScores = """\
INSERT INTO games (game_number, score, opponent_score)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE score=%s, opponent_score=%s
"""

sqlUpdateAllBetCategories = """\
INSERT INTO games (game_number, finished, win, spread, moneyline)
VALUES (%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE finished=%s, win=%s, spread=%s, moneyline=%s
"""

sqlRetrieveGameInfo = """\
SELECT * FROM games g WHERE g.game_number = %s;
"""

sqlRetrieveCrystalBallLastRun = """\
SELECT last_run FROM cb_lastrun
"""

sqlUpdateCrystalLastRun = """\
INSERT INTO cb_lastrun (last_run)
VALUES (%s)
"""

sqlUpdateCrystalBall = """\
INSERT INTO crystal_balls (first_name, last_name, full_name, photo, prediction, result)
VALUES (%s, %s, %s, %s, %s, %s)
"""

sqlRetrieveRedditInfo = """\
SELECT * FROM subreddit_info;
"""

sqlUpdateLineInfo = """\
INSERT INTO games (game_number, spread_value, moneyline_value)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE spread_value=%s, moneyline_value=%s
"""

sqlRetrieveTriviaQuestions = """\
SELECT * FROM trivia
"""

sqlInsertTriviaScore = """\
INSERT INTO trivia_scores (user, score)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE score=score+%s
"""

sqlZeroTriviaScore = """\
INSERT INTO trivia_scores (user, score)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE score=score+%s
"""

sqlRetrieveTriviaScores = """\
SELECT * FROM trivia_scores ORDER BY score DESC
"""

sqlClearTriviaScore = """\
TRUNCATE TABLE trivia_scores
"""

sqlTeamIDs = """
SELECT id, name FROM team_ids ORDER BY name ASC
"""


def process_MySQL(query: str, **kwargs):
    from utils.consts import host, passwd, db, user

    try:
        sqlConnection = pymysql.connect(
            host=host,
            user=user,
            password=passwd,
            db=db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"%%% Connected to the MySQL Database! %%%\n"
              f"%%% Preparing to execute `{repr(query)}`{' and `' + repr(kwargs) + '`' if kwargs else ''}")
    except:
        print(f"Unable to connect to the `{db}` database.")
        return

    result = None

    try:
        with sqlConnection.cursor() as cursor:
            if not "fetch" in kwargs:
                if not "values" in kwargs:
                    cursor.execute(query=query)
                else:
                    cursor.execute(query=query, args=kwargs["values"])
            else:
                if kwargs["fetch"] == "one":
                    cursor.execute(query=query)
                    result = cursor.fetchone()
                elif kwargs["fetch"] == "many":
                    if not "size" in kwargs:
                        raise ValueError("Fetching many requires a `size` kwargs.")
                    cursor.execute(query=query)
                    result = cursor.fetchmany(many=kwargs["size"])
                elif kwargs["fetch"] == "all":
                    cursor.execute(query=query)
                    result = cursor.fetchall()

        sqlConnection.commit()

    except:
        raise ConnectionError("Error occurred opening the MySQL database.")
    finally:
        print(f"%%% Closing connection to the MySQL Database! %%%")
        sqlConnection.close()
        if result:
            return result
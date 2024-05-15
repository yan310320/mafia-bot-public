import sqlite3
from random import shuffle

con = sqlite3.connect('db.db')
cur = con.cursor()


def insert_player(player_id, username):
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f'INSERT INTO(player_id, username) VALUES("{player_id}", "{username}")'
    con.commit()
    con.close()


def players_amount():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = 'SELECT * FROM players'
    cur.execute(sql)
    result = cur.fetchall()
    con.commit()
    con.close()
    return len(result)


def get_mafia_usernames():
    con = sqlite3.connect('db.db')
    cur = con.cursor()

    sql = f'SELECT username FROM players WHERE role = "mafia"'
    cur.execute(sql)
    mafias = cur.fetchall()
    mafia_names = ''
    for maf in mafias:
        name = maf[0]
        mafia_names += name + '\n'
    con.close()
    return mafia_names


def get_all_alive():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f'SELECT username FROM players WHERE dead = 0'
    cur.execute(sql)
    alive_players = cur.fetchall()
    con.close()
    alive_players = [row[0] for row in alive_players]
    return alive_players


def set_roles(players):
    game_roles = ['citizen'] * players
    mafias = int(players * 0.3)
    for i in range(mafias):
        game_roles[i] = 'mafia'
    shuffle(game_roles)
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f'SELECT player_id FROM players'
    cur.execute(sql)
    player_ids = cur.fetchall()
    for role, row in zip(game_roles, player_ids):
        sql = f'UPDATE players SET role = "{role}"'
        cur.execute(sql)
    con.commit()
    con.close()


def get_players_roles():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f'SELECT player_id, role FROM players'
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data


def vote(type, username, player_id):
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    cur.execute(f'''SELECT username 
                    FROM players 
                    WHERE player_id = {player_id}
                    AND dead = 0
                    AND voted = 0''')
    can_vote = cur.fetchone()
    if (can_vote):
        cur.execute(
            f'''UPDATE players
                SET {type} = {type} + 1
                WHERE username = "{username}"'''
        )
        cur.execute(
            f'''UPDATE players
                SET voted = 1
                WHERE player_id = "{player_id}"'''
        )
        con.commit()
        con.close()
        return True
    con.close
    return True

def mafia_kill():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(
        f'''SELECT MAX(mafia_vote)
            FROM players'''
    )
    max_votes = cur.fetchone() [0]
    cur.execute(
        f'''SELECT COUNT(*)
            FROM players
            WHERE role = "mafia"
            AND dead = 0'''
    )
    mafia_alive = cur.fetchone() [0]

    if (max_votes == mafia_alive):
        cur.execute(
            f'''SELECT username
                FROM players
                WHERE mafia_vote = {max_votes}'''
        )
        username_killed = cur.fetchone() [0]
        cur.execute(
            f'''UPDATE players
                SET dead = 1
                WHERE username = "{username_killed}"'''
        )
        con.commit()
    con.close()
    return username_killed

def citizens_kill():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    cur.execute(f'''
                    SELECT MAX (citizen_vote)
                    FROM players
                 ''')
    max_votes = cur.fetchone()[0]
    cur.execute(f'''
                    SELECT COUNT(*)
                    WHERE citizen_vote = max_votes
                    FROM players
                 ''')
    max_votes_count = cur.fetchone()[0]
    # проверяем, что только 1 человек с макс. кол-вом голосов
    cur.execute(f'''
                    SELECT username
                    WHERE citizen_vote = max_votes
                    FROM player
                 ''')
    username_killed = cur.fetchone()[0]
        # обновляем по полученному нику столбец dead на 1
        # сохраняем изменения
    # отключаемся от бд
    # возвращаем ник изгнанного человека

def clear(dead=False):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f'''
                UPDATE players
                SET citizen_vote = 0,
                SET mafia_vote = 0,
                SET voted = 0
            '''
    if dead:
        sql += ', SET dead = 0'
    cur.execute(sql)
    con.commit()
    con.close()

def check_winner():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f'''SELECT COUNT(*) FROM players
            WHERE role = "mafia" AND dead = 0'''
    cur.execute(sql)
    mafia_alive = cur.fetchone()[0]
    sql = f'''SELECT COUNT(*) FROM players
            WHERE role != "mafia" AND dead = 0'''
    citizen_alive = cur.fetchone()[0]
    if mafia_alive >= citizen_alive:
        return 'Мафия'
    elif mafia_alive == 0:
        return 'Мирные жители'
    
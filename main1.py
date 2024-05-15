from telebot import TeleBot
import db

from time import sleep
from random import choice

players = []
game = False
night = False
TOKEN = '6448798384:AAHZ251H12Jl-DYfRmSrPRcCloHmuGIePok'
bot = TeleBot(TOKEN)


def get_killed(night):
    if not night:
        username_killed = db.citizens_kill()
        return f'Мирные жители выгнали: {username_killed}'
    username_killed = db.mafia_kill()
    return f'Мафия убила: {username_killed}'


def game_loop(message):
    global game, night
    bot.send_message(message.chat.id,
                     text="Welcome to the mafia game!\nYou have 1 minute for look through the players!")
    sleep(60)
    while True:
        if not night:
            bot.send_message(message.chat.id,
                             text="The city is waking up!\nIt is the day now!")
        else:
            bot.send_message(message.chat.id,
                             text="The city is falling down to sleep!\nThe mafia is waking up!\nIt is the night now!")
        winner = db.check_winner()
        if winner == 'Мафия' or winner == 'Мирные жители':
            game = False
            bot.send_message(message.chat.id,
                             text=f'Игра окончена.\n Победили: {winner}')
            return
        db.clear(dead=False)
        night = not night
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id,
                         text=f"In the game now:\n{alive}")
        sleep(60)

# Подтверждение начала игры в личном чате


@bot.message_handler(func=lambda mes: mes.text.lower() == "готов играть"
                     and mes.chat.type == "private")
def send_text(message):
    bot.send_message(message.chat.id,
                     f'{message.from_user.first_name} играет')
    db.insert_player(player_id=message.from_user.id,
                     username=message.from_user.first_name)
    bot.send_message(message.chat.id,
                     'Вы добавлены в игру!')


# Сообщение о готовности игры в групповом чате
@bot.message_handler(commands=["play"])
def game_on(message):
    if not game:
        bot.send_message(message.chat.id,
                         'Если хотите играть\nПишите "готов играть" в ЛС боту')


@bot.message_handler(commands=["start"])
def game_start(message):
    global game
    players = db.players_amount()
    if (players >= 4) and (not game):
        db.set_roles(players)
        players_roles = db.get_players_roles()
        mafia_usernames = db.get_mafia_usernames()
        print(players_roles)
        for player_id, role in players_roles:
            bot.send_message(player_id, text=role)
            if (role == "mafia"):
                bot.send_message(player_id,
                                 text=f"Все члены мафии:\n {mafia_usernames}")
        game = True
        bot.send_message(message.chat.id,
                         text="The game started")
        return
    bot.send_message(message.chat.id,
                     text="[:Error:] Not enough people or game already started!")


@bot.message_handler(commands=['vote'])
def kick(message):
    # получаем имя за кого будем голосовать на выбывание днем
    username = ' '.join(message.text.split()[1:])
    # получаем список живых игроков
    usernames = db.get_all_alive()
    # проверяем время суток (день)
    if not night:
        # проверяем находится ли человек из голосования в списке живых
        if username not in usernames:
            # если нет
            bot.send_message(message.chat.id,
                             text='[:Error:] No such username or player already has left the game!')
            return
        # если да, то вносим изменения в БД и возвращаем смогли ли мы изменить
        voted = db.vote(type='citizen_vote',
                        username=username,
                        player_id=message.from_user.id)
        if voted:
            # если да
            bot.send_message(message.chat.id,
                             text='Your vote has been accepted')
            return
        # если нет
        bot.send_message(message.chat.id,
                         text='For now, you cannot vote')
        return
    # если сейчас ночь
    bot.send_message(message.chat.id,
                     text="It's night, you can't vote for now!")


@bot.message_handler(commands=['kill'])
def kill(message):
    # получаем имя за кого будем голосовать за убийсвто ночью
    username = ' '.join(message.text.split()[1:])
    # получаем список живых игроков
    usernames = db.get_all_alive()
    # получаем спискок имен мафий
    mafia_usernames = db.get_mafia_usernames()
    # если сейчас ночь и имя голосовавшего среди мафий
    if night and message.from_user.first_name in mafia_usernames:
        # проверяем находится ли человек из голосования в списке живых
        if username not in usernames:
            # если нет
            bot.send_message(message.chat.id,
                             text='Такого имени нету или игрок уже выбыл')
            return
         # если да, то вносим изменения в БД и возвращаем смогли ли мы изменить
        voted = db.vote(type='mafia_vote',
                        username=username,
                        player_id=message.from_user.id)
        if voted:
            # если да
            bot.send_message(message.chat.id,
                             text='Ваш голос принят!')
            return
        # если нет
        bot.send_message(message.chat.id,
                         text='У вас больше нет права на голосование')
        return
    # если день или имя человека не из мафий
    bot.send_message(message.chat.id,
                     text='Сейчас нельзя убивать, поскольку день')


if __name__ == '__main__':
    bot.infinity_polling()

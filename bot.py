import asyncio
import random
import discord

leading_user = ''
users_playing = []
channel_dict = dict()


def bot(token):
    class CommandHandler:

        # constructor
        def __init__(self, client):
            self.client = client
            self.commands = []

        def add_command(self, command):
            self.commands.append(command)

        def command_handler(self, message):
            for command in self.commands:
                if message.content.startswith(command['trigger']):
                    args = message.content.split(' ')
                    if args[0] == command['trigger']:
                        args.pop(0)
                        if command['args_num'] == 0:
                            answer = str(command['function'](message, self.client, args))
                            if answer != 'None':
                                return message.channel.send(answer)
                            break
                        else:
                            if len(args) >= command['args_num']:
                                answer = str(command['function'](message, self.client, args))
                                if answer != 'None':
                                    return message.channel.send(answer)
                                break
                            else:
                                return message.channel.send('command "{}" requires {} argument(s) "{}"'
                                                            .format(command['trigger'], command['args_num'],
                                                                    ', '.join(command['args_name'])))
                                break
                    else:
                        break

    # create discord client
    discord_client = discord.Client()

    # create the CommandHandler object and pass it the client
    ch = CommandHandler(discord_client)

    def check():
        need_direct_channel = []
        if leading_user not in channel_dict.keys():
            need_direct_channel.append(leading_user)
        for user in users_playing:
            if user not in channel_dict.keys():
                need_direct_channel.append(user)
        return need_direct_channel

    def commands_command(message, client, args):
        try:
            count = 1
            coms = '**Commands List**\n'
            for command in ch.commands:
                coms += '{}) {} : {}\n\n'.format(count, command['trigger'], command['description'])
                count += 1
            return coms
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': '!commands',
        'function': commands_command,
        'args_num': 0,
        'args_name': [],
        'description': 'Prints a list of all the commands!'
    })

    def get_dict_roles(auto=True, mas=[]):
        if auto:
            global users_playing
            count_players = len(users_playing)
            if count_players < 6:
                return None
            elif count_players == 6:
                count_roles = {'Мирный': 4, 'Мафия': 0, 'Дон': 1, 'Комиссар': 1, 'Доктор': 0}
            else:
                maf = (count_players // 4) + 1
                wh = count_players - maf
                count_roles = {'Мирный': wh - 2, 'Мафия': maf - 1, 'Дон': 1, 'Комиссар': 1, 'Доктор': 1}
            return count_roles

        if len(mas) == 5:
            new_mas = list(map(int, mas))
            return {'Мирный': new_mas[0], 'Мафия': new_mas[1], 'Дон': new_mas[2], 'Комиссар': new_mas[3],
                    'Доктор': new_mas[4]}
        return None

    async def send_roles(res_dict):
        res_str = ''
        for pair in res_dict.keys():
            await channel_dict[pair[1]].send("{} - **{}**".format(pair[1].mention, res_dict[pair].upper()))
            res_str += "{}) {} - **{}**\n".format(pair[0], pair[1].mention, res_dict[pair].upper())
        await channel_dict[leading_user].send(res_str)

    def hanging_roles_auto(message, client, args):
        try:
            global leading_user
            global users_playing

            count = len(users_playing)
            if count < 6:
                return "Минимальное количество игроков: 6\nНе хватает {} игроков".format(6 - count)
            if leading_user == '':
                return "Выберите ведущего командой: !leading_me"

            need_direct = check()
            if len(need_direct) == 0:

                dict_roles = get_dict_roles()

                if dict_roles is not None:
                    list_of_players = []

                    for key in dict_roles.keys():
                        for i in range(dict_roles[key]):
                            list_of_players.append(key)

                    res = dict()
                    i = 1
                    while len(list_of_players) != 0:
                        random_index = random.randint(0, len(list_of_players) - 1)
                        res[(i, users_playing[i - 1])] = list_of_players[random_index]
                        list_of_players.pop(random_index)
                        i += 1

                    asyncio.run(send_roles(res))

                    return 'Роли выданы'
            else:
                if need_direct == 1:
                    return "{}, напиши мне в личные сообщения что-нибудь".format(need_direct[0].mention)
                else:
                    return "Эти пользователи должны написать мне в личные сообщения: {}".format(
                        ', '.join(map(lambda x: x.mention, need_direct))
                    )
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': '!start_auto',
        'function': hanging_roles_auto,
        'args_num': 0,
        'args_name': [],
        'description': 'Starts auto handing out roles'
    })

    def hanging_roles(message, client, args):
        try:
            global leading_user
            global users_playing

            count = len(users_playing)
            if leading_user == '':
                return "Выберите ведущего командой: !leading_me"
            need_direct = check()

            if len(need_direct) == 0:

                dict_roles = get_dict_roles(auto=False, mas=args)
                if dict_roles is not None:
                    list_of_players = []
                    for key in dict_roles.keys():
                        for i in range(dict_roles[key]):
                            list_of_players.append(key)
                    res = dict()
                    i = 1
                    if len(list_of_players) < count:
                        return "Не верно введено кол-во ролей. Не хватает {} ролей игрокам"\
                            .format(abs(count - len(list_of_players)))
                    if len(list_of_players) > count:
                        return "Не верно введено кол-во ролей. Введено на {} ролей больше."\
                            .format(abs(count - len(list_of_players)))
                    while len(list_of_players) != 0:
                        random_index = random.randint(0, len(list_of_players) - 1)
                        res[(i, users_playing[i - 1])] = list_of_players[random_index]
                        list_of_players.pop(random_index)
                        i += 1

                    asyncio.run(send_roles(res))

                    return 'Роли выданы'
            else:
                if need_direct == 1:
                    return "{}, напиши мне в личные сообщения что-нибудь".format(need_direct[0].mention)
                else:
                    return "Эти пользователи должны написать мне в личные сообщения: {}".format(
                        ', '.join(map(lambda x: x.mention, need_direct))
                    )

        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': '!start_not_auto',
        'function': hanging_roles,
        'args_num': 5,
        'args_name': ['<кол-во мирных>', '<кол-во мафии>', '<наличие дона>', '<наличие комиссара>',
                      '<наличие доктора>'],
        'description': 'Starts handing out roles'
    })

    def add_leading_user(message, client, args):
        try:
            global leading_user
            global users_playing

            user = message.author
            if user in users_playing:

                leading_user = user

                return "{} is already in player list!".format(user.mention)
            elif user == leading_user:
                return "{} is already leading user!".format(leading_user.mention)
            else:
                leading_user = user
                return "{} is new leading user".format(user.mention)
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': '!leading_me',
        'function': add_leading_user,
        'args_num': 0,
        'args_name': [],
        'description': 'Adds leading user'
    })

    def add_player(message, client, args):
        try:
            global leading_user
            global users_playing

            user = message.author
            if user == leading_user:


                users_playing.append(user)


                return "{} is leading user, he cannot be player".format(user.mention)
            elif user not in users_playing:
                users_playing.append(user)
                return "{} has been added to player list".format(user.mention)
            else:
                return "{} is already added".format(user.mention)
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': '!add_me',
        'function': add_player,
        'args_num': 0,
        'args_name': [],
        'description': 'Adds author to player list'
    })

    def delete_player(message, client, args):
        try:
            global users_playing

            user = message.author
            if user not in users_playing:
                return "{} is not in the list.".format(user.mention)
            else:
                users_playing.remove(user)
                return "{} has been removed from player list".format(user.mention)
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': '!remove_me',
        'function': delete_player,
        'args_num': 0,
        'args_name': [],
        'description': 'Removes author to player list'
    })

    def print_list_players(message, client, args):
        try:
            global users_playing
            global leading_user

            res = ''
            res += "Leading user is **{}**\n".format("nobody " if leading_user == '' else leading_user.name)
            if len(users_playing) == 0:
                res += "**Players List is empty**"
                return res
            users = '**Players List**\n'
            count = 1
            for user in users_playing:
                users += "{}) {}\n".format(count, user.name)
                count += 1
            return res + users
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': '!list',
        'function': print_list_players,
        'args_num': 0,
        'args_name': [],
        'description': 'Prints list of players of current game'
    })

    def clear_list_players(message, client, args):
        try:
            global users_playing
            global leading_user

            users_playing.clear()
            global leading_user
            leading_user = ''
            return "Players List has been cleared"
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': '!clear_list',
        'function': clear_list_players,
        'args_num': 0,
        'args_name': [],
        'description': 'Clears list of players of current game'
    })

    def clear_leading(message, client, args):
        try:
            global leading_user
            leading_user = ''
            return "Leading User has been cleared"
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': '!clear_leading',
        'function': clear_leading,
        'args_num': 0,
        'args_name': [],
        'description': 'Clears list of players of current game'
    })

    # bot is ready
    @discord_client.event
    async def on_ready():
        try:
            print(discord_client.user.name)
            print(discord_client.user.id)
        except Exception as e:
            print(e)

    # on new message
    @discord_client.event
    async def on_message(message):
        # if the message is from the bot itself ignore it
        if message.author == discord_client.user:
            pass
        else:
            # try to evaluate with the command handler
            try:
                if "direct message with" in str(message.channel).lower():
                    global channel_dict
                    channel_dict[message.author] = message.channel
                await ch.command_handler(message)
            # message doesn't contain a command trigger
            except TypeError as e:
                pass
            # generic python error
            except Exception as e:
                print(e)

    # start bot
    discord_client.run(token)

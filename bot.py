import random
import discord


class Bot:
    leading_user = ''
    users_playing = []

    class CommandHandler:
        def __init__(self, client):
            self.client = client
            self.commands = []

        def add_command(self, command):
            self.commands.append(command)

        def command_handler(self, message, dis_bot):
            for command in self.commands:
                if sum([message.content.startswith(cm) for cm in command['trigger']]) > 0:
                    args = message.content.split(' ')
                    if args[0] in command['trigger']:
                        args.pop(0)
                        if command['args_num'] == 0:
                            return command['function'](dis_bot, message, self.client, args)
                            break
                        else:
                            if len(args) >= command['args_num']:
                                return command['function'](dis_bot, message, self.client, args)
                                break
                            else:
                                return [(message.channel,
                                         'command "{}" requires {} argument(s) "{}"'.format
                                         (command['trigger'], command['args_num'], ', '.join(command['args_name'])))]
                                break
                    else:
                        break

    discord_client = discord.Client()
    ch = CommandHandler(discord_client)
    channel_dict = dict()

    # -----------------------CommandList--------------------------
    def commands_command(self, message, client, args):
        try:
            count = 1
            command_list_str = '**Commands List**\n'
            for command in self.ch.commands:
                command_list_str += '{}) **{}** :\t {}\n\n'.format(count,
                                                       ', '.join([cm for cm in command['trigger']]),
                                                       command['description'])
                count += 1
            return Bot.default_channel_message(message, command_list_str)
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!commands', '!cm'],
        'function': commands_command,
        'args_num': 0,
        'args_name': [],
        'description': 'Prints a list of all the commands!'
    })

    # ------------------------------------------------------------

    @staticmethod
    def default_channel_message(message, msg):
        return [(message.channel, msg)]

    def check_users_channels(self):
        need_direct_channel = []
        if self.leading_user not in self.channel_dict.keys():
            need_direct_channel.append(self.leading_user)
        for user in self.users_playing:
            if user not in self.channel_dict.keys():
                need_direct_channel.append(user)
        return need_direct_channel

    def get_dict_roles(self, auto=True, mas=[]):
        if auto:
            count_players = len(self.users_playing)
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

    def create_message_roles(self, dict_roles):
        list_of_roles = []

        for key in dict_roles.keys():
            for i in range(dict_roles[key]):
                list_of_roles.append(key)

        users_roles = dict()
        i = 1
        while len(list_of_roles) != 0:
            random_index = random.randint(0, len(list_of_roles) - 1)
            users_roles[(i, self.users_playing[i - 1])] = list_of_roles[random_index]
            list_of_roles.pop(random_index)
            i += 1

        return_list = []
        leading_msg = ''
        for (index, user) in users_roles.keys():
            return_list.append(
                (self.channel_dict[user], "{} - **{}**".format(user.mention, users_roles[(index, user)].upper()))
            )
            leading_msg += "{}) {} - **{}**\n".format(index, user.mention, users_roles[(index, user)].upper())
        return_list.append(
            (self.channel_dict[self.leading_user], leading_msg)
        )

        return return_list

    # --------------------Hanging Roles Auto----------------------
    def hanging_roles_auto(self, message, client, args):
        try:
            count = len(self.users_playing)
            if count < 6:
                return Bot.default_channel_message(
                    message,
                    "Минимальное количество игроков: 6\nНе хватает {} игроков".format(6 - count)
                )
            if self.leading_user == '':
                return Bot.default_channel_message(message, "Выберите ведущего командой: !leading_me")

            need_direct = self.check_users_channels()
            if len(need_direct) == 0:

                dict_roles = self.get_dict_roles()

                if dict_roles is not None:
                    msg = self.create_message_roles(dict_roles)
                    msg.append(
                        (message.channel, 'Роли выданы')
                    )
                    return msg
            else:
                if need_direct == 1:
                    return Bot.default_channel_message(
                        message,
                        "{}, напиши мне в личные сообщения что-нибудь".format(need_direct[0].mention)
                    )
                else:
                    return Bot.default_channel_message(
                        message,
                        "Эти пользователи должны написать мне в личные сообщения: {}".format(
                            ', '.join(map(lambda x: x.mention, need_direct))
                        )
                    )
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!start_auto', '!st_au'],
        'function': hanging_roles_auto,
        'args_num': 0,
        'args_name': [],
        'description': 'Starts auto handing out roles'
    })

    # ------------------------------------------------------------

    # --------------------Hanging Roles Not Auto------------------
    def hanging_roles_not_auto(self, message, client, args):
        try:
            count = len(self.users_playing)
            if self.leading_user == '':
                return Bot.default_channel_message(message, "Выберите ведущего командой: !leading_me")

            need_direct = self.check_users_channels()
            if len(need_direct) == 0:
                dict_roles = self.get_dict_roles(auto=False, mas=args)
                if dict_roles is not None:
                    list_count = sum(list(map(int, args)))
                    dif = abs(count - list_count)
                    s = ''
                    if list_count < count:
                        s = "Не верно введено кол-во ролей. Не хватает {} ролей игрокам" \
                            .format(dif)
                    if list_count > count:
                        s = "Не верно введено кол-во ролей. Введено на {} ролей больше." \
                            .format(dif)
                    if s != '':
                        return [(message.channel, s)]

                    msg = self.create_message_roles(dict_roles)
                    msg.append(
                        (message.channel, 'Роли выданы')
                    )
                    return msg
            else:
                if need_direct == 1:
                    return Bot.default_channel_message(
                        message,
                        "{}, напиши мне в личные сообщения что-нибудь".format(need_direct[0].mention)
                    )
                else:
                    return Bot.default_channel_message(
                        message,
                        "Эти пользователи должны написать мне в личные сообщения: {}".format(
                            ', '.join(map(lambda x: x.mention, need_direct))
                        )
                    )

        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!start_not_auto', '!st_n_au'],
        'function': hanging_roles_not_auto,
        'args_num': 5,
        'args_name': ['<кол-во мирных>', '<кол-во мафии>', '<наличие дона>', '<наличие комиссара>',
                      '<наличие доктора>'],
        'description': 'Starts handing out roles'
    })

    # ------------------------------------------------------------

    # --------------------Add leading user------------------------
    def add_leading_user(self, message, client, args):
        try:
            user = message.author
            if user in self.users_playing:
                self.leading_user = user
                self.users_playing.remove(user)
                return Bot.default_channel_message(
                    message, "{} is new leading user, but was removed from player list!".format(user.mention)
                )
            elif user == self.leading_user:
                return Bot.default_channel_message(message,
                                                   "{} is already leading user!".format(self.leading_user.mention)
                                                   )
            else:
                self.leading_user = user
                return Bot.default_channel_message(message, "{} is new leading user".format(user.mention))
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!leading_me', '!lm'],
        'function': add_leading_user,
        'args_num': 0,
        'args_name': [],
        'description': 'Adds leading user'
    })

    # ------------------------------------------------------------

    # --------------------Add player -----------------------------
    def add_player(self, message, client, args):
        try:
            user = message.author
            if user == self.leading_user:
                self.users_playing.append(user)
                self.leading_user = ''

                return Bot.default_channel_message(
                    message,
                    "{} has been added to player list, but leading user has cleared".format(user.mention))
            elif user not in self.users_playing:
                self.users_playing.append(user)
                return Bot.default_channel_message(message, "{} has been added to player list".format(user.mention))
            else:
                return Bot.default_channel_message(message, "{} is already added".format(user.mention))
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!add_me', '!am'],
        'function': add_player,
        'args_num': 0,
        'args_name': [],
        'description': 'Adds author to player list'
    })

    # ------------------------------------------------------------

    # --------------------Remove player --------------------------
    def delete_player(self, message, client, args):
        try:
            user = message.author
            if user not in self.users_playing:
                return Bot.default_channel_message(message, "{} is not in the list.".format(user.mention))
            else:
                self.users_playing.remove(user)
                return Bot.default_channel_message(message, "{} has been removed from player list".format(user.mention))
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!remove_me', '!rm'],
        'function': delete_player,
        'args_num': 0,
        'args_name': [],
        'description': 'Removes author to player list'
    })

    # ------------------------------------------------------------

    # --------------------Remove player by index -----------------
    def delete_player_by_index(self, message, client, args):
        try:
            if len(self.users_playing) == 0:
                return Bot.default_channel_message(message, "**List is empty!**")
            num = int(args[0])
            if num < 1 or num > len(self.users_playing):
                return Bot.default_channel_message(message,
                                                   "**Wrong num** of player, you can use only 1-{} nums".format(
                                                       len(self.users_playing)
                                                   ))
            user = self.users_playing[num - 1]
            self.users_playing.remove(user)
            return Bot.default_channel_message(message, "{} has been removed from player list".format(user.mention))
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!remove_index', '!ri'],
        'function': delete_player_by_index,
        'args_num': 1,
        'args_name': ['index_player'],
        'description': 'Removes player by index from list'
    })

    # ------------------------------------------------------------

    # --------------------Print list players ---------------------
    def print_list_players(self, message, client, args):
        try:
            res = ''
            res += "Leading user is **{}**\n".format("nobody " if self.leading_user == '' else self.leading_user.name)
            if len(self.users_playing) == 0:
                res += "**Players List is empty**"
                return Bot.default_channel_message(message, res)
            users = '**Players List**\n'
            count = 1
            for user in self.users_playing:
                users += "{}) {}\n".format(count, user.name)
                count += 1
            return Bot.default_channel_message(message, res + users)
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!list', '!l'],
        'function': print_list_players,
        'args_num': 0,
        'args_name': [],
        'description': 'Prints list of players of current game'
    })

    # ------------------------------------------------------------

    # --------------------Clear list players ---------------------
    def clear_list_players(self, message, client, args):
        try:
            self.users_playing.clear()
            self.leading_user = ''
            return Bot.default_channel_message(message, "Players List has been cleared")
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!clear_list', '!cll'],
        'function': clear_list_players,
        'args_num': 0,
        'args_name': [],
        'description': 'Clears list of players of current game'
    })

    # ------------------------------------------------------------

    # --------------------Clear leading user ---------------------
    def clear_leading(self, message, client, args):
        try:
            self.leading_user = ''
            return Bot.default_channel_message(message, "Leading User has been cleared")
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!clear_leading', '!cllead'],
        'function': clear_leading,
        'args_num': 0,
        'args_name': [],
        'description': 'Clears list of players of current game'
    })

    # ------------------------------------------------------------

    # --------------------Shuffle player list---------------------
    def shuffle_list(self, message, client, args):
        try:
            random.shuffle(self.users_playing)
            return Bot.default_channel_message(message, "Players List has shuffled")
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!shuffle', '!sh'],
        'function': shuffle_list,
        'args_num': 0,
        'args_name': [],
        'description': 'Shuffle player list'
    })

    # ------------------------------------------------------------

    def start(self, token):
        self.discord_client.run(token)


bot = Bot()


@Bot.discord_client.event
async def on_ready():
    try:
        print("BotName={} (userID={})".format(bot.discord_client.user.name, bot.discord_client.user.id))
    except Exception as e:
        print(e)


# on new message
@Bot.discord_client.event
async def on_message(message):
    # if the message is from the bot itself ignore it
    if message.author == bot.discord_client.user:
        pass
    else:
        # try to evaluate with the command handler
        try:
            if "direct message with" in str(message.channel).lower():
                bot.channel_dict[message.author] = message.channel
            answers = Bot.ch.command_handler(message, bot)
            for channel, msg in answers:
                if str(msg) != 'None':
                    print("{}: \"{}\"".format(channel.name, msg))
                    await channel.send(str(msg))
        # message doesn't contain a command trigger
        except TypeError as e:
            pass
        # generic python error
        except Exception as e:
            print(e)


def start(token):
    bot.discord_client.run(token)

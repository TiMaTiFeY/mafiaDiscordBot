import random
import discord
from enum import Enum


class Event(Enum):
    SEND = 1
    RENAME = 2



class Bot:
    class GuildInfo:
        def __init__(self, leading_user='', users_playing=[]):
            self.leading_user = leading_user
            self.users_playing = users_playing.copy()

        def __str__(self):
            return "LEAD: (" + str(self.leading_user) + "); " + str(list(map(lambda x: x.name, self.users_playing)))

        def __repr__(self):
            return "LEAD: (" + str(self.leading_user) + "); " + str(list(map(lambda x: x.name, self.users_playing)))

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
                        guild_id = message.guild.id
                        if command['args_num'] == 0:
                            return command['function'](dis_bot, message, guild_id, self.client, args)
                            break
                        else:
                            if len(args) >= command['args_num']:
                                return command['function'](dis_bot, message, guild_id, self.client, args)
                                break
                            else:
                                return [(Event.SEND, (message.channel,
                                         'command "{}" requires {} argument(s) "{}"'.format
                                         (command['trigger'], command['args_num'], ', '.join(command['args_name']))))]
                                break
                    else:
                        break

    guilds_inf = dict()
    discord_client = discord.Client()
    ch = CommandHandler(discord_client)

    # -----------------------CommandList--------------------------
    def commands_command(self, message, guild_id, client, args):
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
        return [(Event.SEND, [(message.channel, msg)])]

    def get_dict_roles(self, guild_id, auto=True, mas=[]):
        if auto:
            count_players = len(self.guilds_inf[guild_id].users_playing)
            if count_players < 6:
                return None
            elif count_players == 6:
                count_roles = {'Мирный': 4, 'Мафия': 0, 'Дон мафии': 1, 'Комиссар': 1, 'Доктор': 0}
            else:
                maf = (count_players // 4) + 1
                wh = count_players - maf
                count_roles = {'Мирный': wh - 2, 'Мафия': maf - 1, 'Дон мафии': 1, 'Комиссар': 1, 'Доктор': 1}
            return count_roles

        if len(mas) == 5:
            new_mas = list(map(int, mas))
            return {'Мирный': new_mas[0], 'Мафия': new_mas[1], 'Дон мафии': new_mas[2], 'Комиссар': new_mas[3],
                    'Доктор': new_mas[4]}

        return None

    def create_message_roles(self, dict_roles, guild_id):
        list_of_roles = []

        for key in dict_roles.keys():
            for i in range(dict_roles[key]):
                list_of_roles.append(key)

        users_roles = dict()
        i = 1
        while len(list_of_roles) != 0:
            random_index = random.randint(0, len(list_of_roles) - 1)
            users_roles[(i, self.guilds_inf[guild_id].users_playing[i - 1])] = list_of_roles[random_index]
            list_of_roles.pop(random_index)
            i += 1

        return_list = []
        leading_msg = ''
        for (index, user) in users_roles.keys():
            return_list.append(
                (Event.SEND, (user, "{} - **{}**".format(user.mention, users_roles[(index, user)].upper())))
            )
            leading_msg += "{}) {} - **{}**\n".format(index, user.mention, users_roles[(index, user)].upper())
        return_list.append(
            (Event.SEND, (self.guilds_inf[guild_id].leading_user, leading_msg))
        )

        return return_list

    # --------------------Hanging Roles Auto----------------------
    def hanging_roles_auto(self, message, guild_id, client, args):
        try:
            count = len(self.guilds_inf[guild_id].users_playing)
            if count < 6:
                return Bot.default_channel_message(
                    message,
                    "Минимальное количество игроков: 6\nНе хватает {} игроков".format(6 - count)
                )
            if self.guilds_inf[guild_id].leading_user == '':
                return Bot.default_channel_message(message, "Выберите ведущего командой: !leading_me")

            dict_roles = self.get_dict_roles(guild_id=guild_id)

            if dict_roles is not None:
                msg = self.create_message_roles(dict_roles, guild_id)
                text = '**Роли выданы:**\n'
                for role, count in dict_roles.items():
                    if count > 0:
                        text += "**{}**: {};\n".format(role.upper(), count)
                msg.append((Event.SEND, (message.channel, text)))
                return msg
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
    def hanging_roles_not_auto(self, message, guild_id, client, args):
        try:
            count = len(self.guilds_inf[guild_id].users_playing)
            if self.guilds_inf[guild_id].leading_user == '':
                return Bot.default_channel_message(message, "Выберите ведущего командой: !leading_me")

            dict_roles = self.get_dict_roles(auto=False, mas=args, guild_id=guild_id)
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
                    return Bot.default_channel_message(message, s)

                msg = self.create_message_roles(dict_roles, guild_id)
                text = '**Роли выданы:**\n'
                for role, count in dict_roles.items():
                    if count > 0:
                        text += "**{}**: {};\n".format(role.upper(), count)
                msg.append((Event.SEND, (message.channel, text)))
                return msg

        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!start_not_auto', '!st_n_au'],
        'function': hanging_roles_not_auto,
        'args_num': 5,
        'args_name': ['<кол-во мирных>', '<кол-во мафии>', '<наличие дона мафии 0/1>', '<наличие комиссара 0/1>',
                      '<наличие доктора 0/1>'],
        'description': 'Starts handing out roles'
    })

    # ------------------------------------------------------------

    # --------------------Add leading user------------------------
    def add_leading_user(self, message, guild_id, client, args):
        try:
            user = message.author
            if user in self.guilds_inf[guild_id].users_playing:
                self.guilds_inf[guild_id].leading_user = user
                self.guilds_inf[guild_id].users_playing.remove(user)
                return Bot.default_channel_message(
                    message, "{} is new leading user, but was removed from player list!".format(user.mention)
                )
            elif user == self.guilds_inf[guild_id].leading_user:
                return Bot.default_channel_message(message,
                                                   "{} is already leading user!".format(
                                                       self.guilds_inf[guild_id].leading_user.mention)
                                                   )
            else:
                self.guilds_inf[guild_id].leading_user = user
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
    def add_player(self, message, guild_id, client, args):
        try:
            user = message.author
            if user == self.guilds_inf[guild_id].leading_user:
                self.guilds_inf[guild_id].users_playing.append(user)
                self.guilds_inf[guild_id].leading_user = ''

                return Bot.default_channel_message(
                    message,
                    "{} has been added to player list, but leading user has cleared".format(user.mention))
            elif user not in self.guilds_inf[guild_id].users_playing:
                self.guilds_inf[guild_id].users_playing.append(user)
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
    def delete_player(self, message, guild_id, client, args):
        try:
            user = message.author
            if user not in self.guilds_inf[guild_id].users_playing:
                return Bot.default_channel_message(message, "{} is not in the list.".format(user.mention))
            else:
                self.guilds_inf[guild_id].users_playing.remove(user)
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
    def delete_player_by_index(self, message, guild_id, client, args):
        try:
            if len(self.guilds_inf[guild_id].users_playing) == 0:
                return Bot.default_channel_message(message, "**List is empty!**")
            num = int(args[0])
            if num < 1 or num > len(self.guilds_inf[guild_id].users_playing):
                return Bot.default_channel_message(message,
                                                   "**Wrong num** of player, you can use only 1-{} nums".format(
                                                       len(self.guilds_inf[guild_id].users_playing)
                                                   ))
            user = self.guilds_inf[guild_id].users_playing[num - 1]
            self.guilds_inf[guild_id].users_playing.remove(user)
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
    def print_list_players(self, message, guild_id, client, args):
        try:
            res = ''
            res += "Leading user is **{}**\n".format(
                "nobody " if self.guilds_inf[guild_id].leading_user == '' else
                self.guilds_inf[guild_id].leading_user.name
            )
            if len(self.guilds_inf[guild_id].users_playing) == 0:
                res += "**Players List is empty**"
                return Bot.default_channel_message(message, res)
            users = '**Players List**\n'
            count = 1
            for user in self.guilds_inf[guild_id].users_playing:
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
    def clear_list_players(self, message, guild_id, client, args):
        try:
            self.guilds_inf[guild_id].users_playing.clear()
            self.guilds_inf[guild_id].leading_user = ''
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
    def clear_leading(self, message, guild_id, client, args):
        try:
            self.guilds_inf[guild_id].leading_user = ''
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
    def shuffle_list(self, message, guild_id, client, args):
        try:
            random.shuffle(self.guilds_inf[guild_id].users_playing)
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

    # --------------------Rename users by game ---------------------
    def rename_players(self, message, guild_id, client, args):
        try:
            res_dict = dict()
            for i, user in enumerate(self.guilds_inf[guild_id].users_playing, 1):
                res_dict[user] = "0{} {}".format(i, user.name)
            if self.guilds_inf[guild_id].leading_user != '':
                res_dict[self.guilds_inf[guild_id].leading_user] = \
                    "Ведущий {}".format(self.guilds_inf[guild_id].leading_user.name)
            return [(Event.RENAME, res_dict), Bot.default_channel_message(message, 'Nicknames was changed')[0]]
        except Exception as e:
            print(e)

    ch.add_command({
        'trigger': ['!rename_all', '!r_all'],
        'function': rename_players,
        'args_num': 0,
        'args_name': [],
        'description': 'Rename all users by current game'
    })

    # ------------------------------------------------------------
    def start(self, token):
        self.discord_client.run(token)


bot = Bot()


@Bot.discord_client.event
async def on_ready():
    try:
        print("BotName={} (userID={})".format(bot.discord_client.user.name, bot.discord_client.user.id))
        print("Guilds: {}".format(', '.join(list(map(lambda x: '<'+x.name+'>', bot.discord_client.guilds)))))
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
            if message.guild.id not in bot.guilds_inf.keys():
                bot.guilds_inf[message.guild.id] = bot.GuildInfo()

            answers = bot.ch.command_handler(message, bot)

            for event_type, event in answers:
                if event_type == Event.SEND:
                    for channel, msg in event:
                        if str(msg) != 'None':
                            await channel.send(str(msg))
                elif event_type == Event.RENAME:
                    for user, new_name in event.items():
                        try:
                            await user.edit(nick=str(new_name))
                        except Exception as e:
                            print(e)

        # message doesn't contain a command trigger
        except TypeError as e:
            pass
        # generic python error
        except Exception as e:
            print(e)


def start(token):
    bot.discord_client.run(token)

import discord
from discord import app_commands
from collections import defaultdict

# the worst programmed discord bot in history

class Portfolio:
    def __init__(self):
        self.balance = defaultdict(lambda: 0.0)

class Account:
    def __init__(self, name, shitcoin, user_id):
        self.name = name
        self.shitcoin = shitcoin
        self.portfolio = Portfolio()
        self.user_id = user_id

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

DEV_GUILD_ID = 1045473935388573777
REAL_GUILD_ID = 464320663050518529

g_bank = []

def get_bank_account(name):
    for acc in g_bank:
        if acc.name == name:
            return acc
    return None

def read_bank_data():
    global g_bank
    g_bank = []
    ll = [x for x in open("data.obpointsave").read().strip().split("\n")]
    for l in ll:
        spl = l.split(";")
        name = spl[0]
        shitcoin = spl[1]
        user_id = int(spl[2])
        acc = Account(name, shitcoin, user_id)
        if len(spl) > 3:
            if spl[3] != "":
                balance = spl[3].split(",")
                for bb in balance:
                    if bb == "":
                        continue
                    subshitcoinname, numstr = bb.split(":")
                    acc.portfolio.balance[subshitcoinname] = float(numstr)
        g_bank.append(acc)

def write_bank_data():
    ll = []
    for acc in g_bank:
        l = acc.name + ";" + acc.shitcoin + ";" + str(acc.user_id) + ";"
        for sub, count in acc.portfolio.balance.items():
            l += sub + ":" + str(count) + ","
        ll.append(l + "\n")
    with open("data.obpointsave", "wt") as f:
        f.writelines(ll)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=REAL_GUILD_ID))
    await tree.sync(guild=discord.Object(id=DEV_GUILD_ID))
    read_bank_data()
    print("obpoints loaded!")

@tree.command(name="create", description="create your obank account!", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def create_account_command(interaction, shitcoin_name: str):
    for acc in g_bank:
        if acc.name == interaction.user.name:
            await interaction.response.send_message("looks like you have already opened an account!")
            return
    g_bank.append(Account(interaction.user.name, shitcoin_name, interaction.user.id))
    await interaction.response.send_message("account created! thank you for choosing obank:tm:")

@tree.command(name="rename", description="renames your point (please be pg13!!)", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def rename_command(interaction, new_shitcoin_name: str):
    if not new_shitcoin_name.isalnum() and ';' not in new_shitcoin_name and ':' not in new_shitcoin_name and ',' not in new_shitcoin_name and ',' not in new_shitcoin_name and '-' not in new_shitcoin_name:
        await interaction.response.send_message("please only use alphanumeric characters in the name.")
        return
    send_account = get_bank_account(interaction.user.name)
    if send_account == None:
        await interaction.response.send_message("looks like you havent opened an account yet!")
        return
    for acc in g_bank:
        if acc.shitcoin == new_shitcoin_name:
            await interaction.response.send_message("looks like that name is already taken!")
            return
    await interaction.response.send_message(f"renamed your point from {send_account.shitcoin} to {new_shitcoin_name}!")
    for acc in g_bank:
        if send_account.shitcoin in acc.portfolio.balance.keys():
            acc.portfolio.balance[new_shitcoin_name] = acc.portfolio.balance.pop(send_account.shitcoin)
    send_account.shitcoin = new_shitcoin_name
    write_bank_data()

@tree.command(name="take", description="takes n of your points from a person (no limit)", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def take_command(interaction, receiver: discord.Member, x: float):
    if x < 0.0:
        await interaction.response.send_message("you cant take negative points, use the /send command instead...")
        return
    if interaction.user.name == receiver.name:
        await interaction.response.send_message("you cant take coins from yourself...")
        return
    send_account = get_bank_account(interaction.user.name)
    recv_account = get_bank_account(receiver.name)
    if send_account == None:
        await interaction.response.send_message("looks like you havent opened an account yet!")
        return
    if recv_account == None:
        await interaction.response.send_message("looks like the person youre taking from hasnt opened an account yet!")
        return
    message = "-" + str(x) + " " + send_account.shitcoin + "s taken from <@" + str(recv_account.user_id) + ">"
    recv_account.portfolio.balance[send_account.shitcoin] -= x
    write_bank_data()
    await interaction.response.send_message(message)

@tree.command(name="takeone", description="takes one of your points from a person", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def take_one_command(interaction, receiver: discord.Member):
    if interaction.user.name == receiver.name:
        await interaction.response.send_message("you cant take coins from yourself...")
        return
    send_account = get_bank_account(interaction.user.name)
    recv_account = get_bank_account(receiver.name)
    if send_account == None:
        await interaction.response.send_message("looks like you havent opened an account yet!")
        return
    if recv_account == None:
        await interaction.response.send_message("looks like the person youre taking from hasnt opened an account yet!")
        return
    message = "-1 " + send_account.shitcoin + " from <@" + str(recv_account.user_id) + ">"
    recv_account.portfolio.balance[send_account.shitcoin] -= 1.0
    write_bank_data()
    await interaction.response.send_message(message)

@tree.command(name="send", description="sends n points to a person", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def send_command(interaction, receiver: discord.Member, x: float, shitcoin_name: str):
    if x < 0.0:
        await interaction.response.send_message("you cant send negative points, use the /take command instead...")
        return
    if interaction.user.name == receiver.name:
        await interaction.response.send_message("you cant give yourself coins...")
        return
    send_account = get_bank_account(interaction.user.name)
    recv_account = get_bank_account(receiver.name)
    if send_account == None:
        await interaction.response.send_message("looks like you havent opened an account yet!")
        return
    if recv_account == None:
        await interaction.response.send_message("looks like the person youre sending to hasnt opened an account yet!")
        return
    if shitcoin_name != send_account.shitcoin and shitcoin_name not in send_account.portfolio.balance.keys():
        await interaction.response.send_message("you dont own that point at all plebian!!1!1 start expanding your portfolio...")
        return
    if shitcoin_name != send_account.shitcoin and send_account.portfolio.balance[shitcoin_name] < n:
        await interaction.response.send_message(f"cant afford it buddy (attempting to send {n}, only own {send_account.portfolio.balance[shitcoin_name]})")
    else:
        message = "+" + str(x) + " " + shitcoin_name + "s sent to <@" + str(recv_account.user_id) + ">"
        if recv_account.shitcoin != shitcoin_name:
            recv_account.portfolio.balance[shitcoin_name] += x
        write_bank_data()
        await interaction.response.send_message(message)

@tree.command(name="sendone", description="sends one of your point to a person", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def send_one_command(interaction, receiver: discord.Member):
    if interaction.user.name == receiver.name:
        await interaction.response.send_message("you cant give yourself coins...")
        return
    send_account = get_bank_account(interaction.user.name)
    recv_account = get_bank_account(receiver.name)
    if send_account == None:
        await interaction.response.send_message("looks like you havent opened an account yet!")
        return
    if recv_account == None:
        await interaction.response.send_message("looks like the person youre sending to hasnt opened an account yet!")
        return
    message = "+1 " + send_account.shitcoin + " to <@" + str(recv_account.user_id) + ">"
    recv_account.portfolio.balance[send_account.shitcoin] += 1
    write_bank_data()
    await interaction.response.send_message(message)

@tree.command(name="portfolio", description="get someones balance", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def balance_command(interaction, receiver: discord.Member):
    acc = get_bank_account(receiver.name)
    if acc == None:
        await interaction.response.send_message("the person youre querying hasnt opened an account yet.")
        return
    embed = discord.Embed(title="portfolio", description="associated point: " + acc.shitcoin, color=0xFF5733)
    pf = ""
    for name, count in acc.portfolio.balance.items():
        if count != 0:
            pf += "* " + str(count) + " " + name + "s\n"
    embed.add_field(name="", value=pf)
    await interaction.response.send_message(embed=embed)

@tree.command(name="list", description="list every open bank account and their associated point", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def list_command(interaction):
    embed = discord.Embed(title="open accounts", color=0xFF5733)
    output = ""
    for acc in g_bank:
        output += "* " + acc.name + ": " + acc.shitcoin + "\n"
    embed.add_field(name="", value=output)
    await interaction.response.send_message(embed=embed)

@tree.command(name="total", description="get total number of type of coin in existence", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def total_command(interaction, shitcoin_name: str):
    ret = []
    for acc in g_bank:
        for name, count in acc.portfolio.balance.items():
            if count != 0 and name == shitcoin_name:
                ret.append((count, acc.user_id))
    if ret == []:
        await interaction.response.send_message("no " + shitcoin_name + "s in the entire economy!")
        return
    maxima = sorted(ret)[::-1]
    tot = sum(x[0] for x in ret)
    await interaction.response.send_message("there is in total " + str(tot) + " " + shitcoin_name + "s in existence.\nits highest holder is <@" + str(maxima[0][1]) + "> with a total holding of " + str(round(maxima[0][0] / tot * 100.0)) + "%")

@tree.command(name="exchangerate", description="get the base exchange rate between two coins", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def exchange_rate_command(interaction, point_a: str, point_b: str):
    total_a = 0
    total_b = 0
    for acc in g_bank:
        for name, count in acc.portfolio.balance.items():
            if name == point_a:
                total_a += count
            elif name == point_b:
                total_b += count
    rate = total_b / (total_a if total_a != 0 else 1)
    await interaction.response.send_message("for every " + point_a + " in existence there exist " + str(rate) + " " + point_b + "s.")

#@tree.command(name="custombelowmessage", description="set a custom message to be dm'd when anyone gets below n of your points", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
#async def set_custom_below_message(interaction, n: int, message: str):
#    await interaction.response.send_message("set message!")

@tree.command(name="manualsave", description="writes out the current bank data to a file on the server", guilds=[discord.Object(id=REAL_GUILD_ID), discord.Object(id=DEV_GUILD_ID)])
async def manual_save_command(interaction):
    write_bank_data()
    await interaction.response.send_message("saved data successfully!")

client.run("<TOKEN>")

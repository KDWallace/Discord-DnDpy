# KDWallace 2023.09.08
# A bot for discord for generating images for D&D stats including:
# - A customisable statblock in the style of a monster manual character (/playercard)
# - A generated card of an effect from The Net Libram of Random Magical Effects (NLRME) version 2.00 By Orrex, with discord buttons
#######################################################################################################################

import discord, os, random, math
from core.buttons import Wild_Surge_Buttons
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
from discord import app_commands
from discord.ext import commands

##########################################################################################################################################
#a bunch of public variables

version = 'Moose\'s Bot Slave (Simplified) V3.2.1'

#Main path for DIR navigation for files/config
PATH = (os.path.dirname(os.path.realpath(__file__)))[:-4]

class PersistentViewClient(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(command_prefix=commands.when_mentioned_or('.'),intents=intents)
    async def setup_hook(self) -> None:
        self.add_view(Wild_Surge_Buttons())
        

client = PersistentViewClient()

#function called if the bot successfully boots up and is ready for use
@client.event
async def on_ready():

    synced = await client.tree.sync()
    print(f'Synced {len(synced)} slash commands')
    print(f'   - {client.user.name} is online!')
    print(' ------------------------------------------------------------------')

@client.tree.command(name="wildsurge",description='Generates a random effect from a table of 10,000 wild surge effects')
@app_commands.describe(
    number="For setting a pre-determined effect from the table of 1-10,000 wild surges (Default = 0 for random)",
    private="For creating a response within the channel that only you can see (Default = False for visible)",
)
async def Wild_Surge(interaction: discord.Interaction, number: app_commands.Range[int,0,10000]=0, private: bool=False):
    if number == 0:
        number = None
    #print(f'{ctx.author} has rolled on the wild magic table...')
    view = Wild_Surge_Buttons()
    wsroll= view.wildsurgegen(r=number)

    if private:
        await interaction.response.send_message(view=view,ephemeral=True,file=discord.File(f'{PATH}\\resources\\files\\tmp\\wildsurge.png',filename=f'{wsroll}-hidden.png'))
    else:
        await interaction.response.send_message(view=view,file=discord.File(f'{PATH}\\resources\\files\\tmp\\wildsurge.png',filename=f'{wsroll}.png'))
    os.remove(f'{PATH}\\resources\\files\\tmp\\wildsurge.png')
#@commands.command(description='A stat gen that can be used for creating D&D 5E characters on the fly using image generation! This will include a randomly allocated alignment and your highest server rank as the monster type.\n\n.statgen <name> stats:<stat order> roll:<roll type>\n\nThe default for the name is your nickname on the server and the default roll type is the 3 best from 4d6 for each slot. The ordering is also random for these stats.\n\nThe stats can be ordered from highest to lowest rolled using stats: <stat preference order>.\nFor example: if you wanted your characters highest stats to be dexterity, charisma and wisdom like the dashing rogue you are, use:\n.statgen <optional name> stats: dex cha wis\nThis will ensure that these will be the highest stats used and the rest will be random.\n\nYou can modify the stat roll method by using roll: <prefered method>\nFor example: if you want your stats to be calculated using the best 3 rolls out of 5d6, use .statgen roll: 5\nThe lowest this can be is 3 and the default is 4.\nUse roll: array to use standard array allocation (15,14,13,12,10,8).\n\n.statgen The Moosiest Moose of all the Moose stats: str con roll:9\n\nThis would call the character "The Moosiest Moose of all the Moose", roll all of the stats using the best 3 dice from 9 6-sided dice and order the highest 2 roll sets for strength and then the second highest goes to constitution. The rest are random.')

@client.tree.command(name="playercard",description='A stat gen that can be used for creating D&D 5E characters on the fly using image generation!')
@app_commands.choices(alignment=[
        app_commands.Choice(name="Lawful Good", value="Lawful Good"),
        app_commands.Choice(name="Neutral Good", value="Neutral Good"),
        app_commands.Choice(name="Chaotic Good", value="Chaotic Good"),
        app_commands.Choice(name="Lawful Neutral", value="Lawful Neutral"),
        app_commands.Choice(name="True Neutral", value="True Neutral"),
        app_commands.Choice(name="Chaotic Neutral", value="Chaotic Neutral"),
        app_commands.Choice(name="Lawful Evil", value="Lawful Evil"),
        app_commands.Choice(name="Neutral Evil", value="Neutral Evil"),
        app_commands.Choice(name="Chaotic Evil", value="Chaotic Evil"),
        ])
@app_commands.describe(
    name="The name used on the stat card (Default is Discord name/nickname)",
    species="The species used below the name (Default is Discord handle)",
    alignment="The alignment of this creature (Default is randomised)",
    roll="Xd6 used for generating stats. The best 3 rolls are taken (Default is standard array, recommend 4d6)",
    roll_override="Override all rolls with 6 values between 0 - 99. (Will only work with 6 given values)",
    order="Prefered ordering of stats in the form Str Dex Con Wis Int Cha. Any not mentioned will be randomised",
)
async def PlayerCard(interaction: discord.Interaction, name: str = None, species: str = None, alignment: app_commands.Choice[str]=None, roll: app_commands.Range[int,3,20]=None, roll_override: str=None, order:str=None):
    #create name
    user = interaction.user
    if name == None or len(name) < 1:
        name = user.display_name.title()

    #create species
    if species == None or len(species) < 1:
        species = user.name.title()

    #create preference order
    stattypes = ['STR','DEX','CON','INT','WIS','CHA']
    pref = None
    if order != None and len(order) > 1:
        tmp = [x.upper()[:3] for x in order.split()]
        for item in tmp:
            if item in stattypes:
                if pref == None:
                    pref = [item]
                else:
                    pref.append(item)
                stattypes.remove(item)
    if pref != None and len(pref) < 6:
        random.shuffle(stattypes)
        for stat in stattypes:
            pref.append(stat)
    stattypes = ['STR','DEX','CON','INT','WIS','CHA']

    #create alignment
    if alignment == None:
        #randomises alignment
        morals = ['Good','Neutral','Evil']
        method = ['Lawful','Neutral','Chaotic']
        alignment =  random.choice(method) + ' ' + random.choice(morals)
        #custom name for neutral neutral random choice
        if alignment == 'Neutral Neutral':
            alignment = 'True Neutral'
    else:
        alignment = alignment.name

    #loads background image and crops to size
    img = Image.open(f'{PATH}\\resources\\files\\stainedcard.png')
    #defines the different fonts that are being used
    title   = ImageFont.truetype(f'{PATH}\\resources\\fonts\\MrsEavesSmallCaps.ttf',34)
    italic  = ImageFont.truetype(f'{PATH}\\resources\\fonts\\ScalaSans Italic.ttf',16)
    regular = ImageFont.truetype(f'{PATH}\\resources\\fonts\\ScalaSans Regular.ttf',17)
    #obtains the height of the title text
    h = title.getsize(name)[1]
    #draws the background
    draw = ImageDraw.Draw(img)
    draw.text((20,20),name,font=title,fill=(88, 23, 13))
    draw.text((20,h+25),f'{species}, {alignment}',font=italic,fill=(0,0,0))
    #increases the height and adds the separator to the background
    h += italic.getsize('Player')[1] + 25
    #img.paste(separator,(20,h+5))
    h += 10

    #stat generation with 4 dice rolls for each block (take the best 3)
    stats = []
    if roll_override != None and len(roll_override) > 0:
        try:
            roll_override = roll_override.split()
            if len(roll_override) == 6:
                for val in roll_override:
                    if int(val) > -1 and int(val) < 100:
                        stats.append(int(val))
                    else:
                        roll_override = None
                        break
                    random.shuffle(stats)
            else:
                roll_override = None
        except:
            roll_override = None
    if roll_override == None:
        stats = []
        if roll == None:
            stats = [15,14,13,12,10,8]
            random.shuffle(stats)
        else:
            for i in range(6):
                rolls = [0,0,0]
                ##printvals = []
                for k in range(roll):
                    rand = random.randint(1,6)
                    ##printvals.append(rand)
                    #sorts in ascending order so the lowest can be replaced if needed
                    rolls.sort()
                    if rolls[0] < rand:
                        rolls[0] = rand
                ##print(f'Rolled vals: {printvals}\t:\tUsed vals: {rolls}\t:\tResult: {sum(rolls)}')
                stats.append(sum(rolls))

    #orders the stats if there is a defined preference
    count = 0
    if pref != None:

        tmpstats = stats
        #stats in ascending order
        stats.sort()

        #reverses the ordering
        stats = stats[::-1]
        preforder = [5,5,5,5,5,5]

        #ensures that all values in pref are uppercase
        for p in pref:
            for s in stattypes:
                if s == p:
                    preforder[count] = stattypes.index(s)
                    count += 1
                    continue
        stats = [x for _,x in sorted(zip(preforder,stats))]

    #draws the names of the stat types to the background using a for loop
    x = 40
    for stat in stattypes:
        draw.text((x,h+10),stat,font=regular,fill=(0,0,0))
        x += 75

    #increases the height
    h += 10 + regular.getsize('STR')[1]

    #calculates the stat bonus for each slot
    bonus = []
    for stat in stats:
        string = ''
        if stat > 9:
            string = '+'
        string = string + str(math.floor((stat-10)/2))
        bonus.append(string)

    #draws the stat bonus underneith each stat
    x = 35
    for i in range(6):
        dx = 0
        if stats[i] < 10:
            dx = 5
        draw.text((x+dx,h+5),f'{stats[i]} ({bonus[i]})',font=regular,fill=(0,0,0))
        x += 75

    #increases the height value and adds another separator under the new stats
    h += regular.getsize('10')[1]
    #img.paste(separator,(20,h+20))

    #the image is temp saved in the \tmp folder, sent to discord and then immediatelly deleted
    img.save(f'{PATH}\\resources\\files\\tmp\\stats.png')
    if roll_override != None:
        roll = roll_override
    if roll == None:
        roll = 'Standard Array'
    else:
        roll = str(roll) + 'd6'

    await interaction.response.send_message(file=discord.File(f'{PATH}\\resources\\files\\tmp\\stats.png',filename=f'{user.name}-{roll}.png'))
    os.remove(f'{PATH}\\resources\\files\\tmp\\stats.png')

#@client.tree.command(name="src",description='Sends the latest source code of this bot to you. Enjoy!')
#async def Src(interaction: discord.Interaction):
#    await interaction.response.send_message(f'I have sent the files to your Direct Messages {interaction.user.mention}!',ephemeral=True)
#    await interaction.user.send(f"Hey {interaction.user.mention}! I grabbed the latest source code for me :smile:",file=discord.File(f'{PATH}\\DnDpy.zip',filename=f'DnDpy.zip'))


if __name__ == '__main__':
    #Basic display
    length = 75 - len(version)
    if length > 0:
        length = int(length/2)
    else:
        length = 0
    print('','='*length,version,'='*length,f'\n   - Booted at {datetime.now().strftime("%H:%M:%S")}\n   - Please wait...')
    #will attempt to obtain token from file
    print('        Obtaining token from textfile...',end='')
    try:
        #opens file containing bot token
        with open('TOKEN.txt','r') as f:
            TOKEN = f.read()

        #if there is a string in the file, assume found
        if len(TOKEN) > 1:
            print('Token found')

            #attempt to run with this token
            client.run(TOKEN)

        #if file does not contain token, raise exception
        else:
            raise FileNotFoundError()

    #exception thrown if token does not exist or is not valid
    except FileNotFoundError:
        print('\n[ERROR]:  Token not found. Please paste your bot token in the TOKEN.txt file')

    #exception related to bot
    except Exception as e:
        print(e)

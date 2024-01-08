import discord, random, os
from PIL import Image, ImageFont, ImageDraw


PATH = (os.path.dirname(os.path.realpath(__file__)))[:-8]

class Wild_Surge_Buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        #self.value = None

    def genroll(self,string,roll):
        num = '123456789'
        newline = ''
        line = string.split()
        auto = False

        for i in line:
            if 'd' in i:

                for j in num:
                    if j in i:
                        if roll == True:
                            auto = 0
                            vals = i.split('d')
                            for k in range(int(vals[0])):
                                auto += random.randint(1,int(vals[1]))
                        else:
                            auto = roll
                        i = str(auto)
                        break
            newline += i + ' '
        return newline, auto

    def wildsurgegen(self,r=None,autoroll=False,cure=False,cureautoroll=False):#,*,pref=None):
        filename = 'Wild Surge'

        #opens file and checks number of lines + saves all lines
        filelines = []
        with open(f'{PATH}\\resources\\data\\{filename}.txt','r',encoding='UTF-8') as f:
            for line in f:
                line = line.split()
                ln = ''
                for j in line[1:]:
                    ln = ln + ' ' + j
                filelines.append(ln)

        #generates number if not present
        if r == None:
            r = random.randint(1,len(filelines))
        r = int(r)

        #if the number given is out of bounds, ignore
        if r < 1 or r > len(filelines):
            print('Wildsurge val out of bounds, giving new val')
            r = random.randint(1,len(filelines))


        #print('Rolled: ' + str(r))
        filedata = filelines[r-1]

        
        #loads background image and crops to size
        img = Image.open(f'{PATH}\\resources\\files\\stained.png')
        if cure:
            h = 125
        else:
            h = 115
        img = img.crop((0,0,600,h))

        #loads stat separator made in paint.net
        separator = Image.open(f'{PATH}\\resources\\files\\statseps.png')

        #defines the different fonts that are being used
        title   = ImageFont.truetype(f'{PATH}\\resources\\fonts\\MrsEavesSmallCaps.ttf',34)
        italic  = ImageFont.truetype(f'{PATH}\\resources\\fonts\\ScalaSans Italic.ttf',16)
        regular = ImageFont.truetype(f'{PATH}\\resources\\fonts\\ScalaSans Regular.ttf',17)

        #obtains the height of the title text
        h = title.getsize(filename)[1]

        #draws the background
        draw = ImageDraw.Draw(img)

        filename = 'Wild Magic Surge'

        draw.text((20,20),filename,font=title,fill=(88, 23, 13))
        draw.text((20,h+25),f'#{r}',font=italic,fill=(0,0,0))

        #increases the height and adds the separator to the background
        h += italic.getsize('Plgq')[1] + 25
        img.paste(separator,(20,h+5))
        h += 10

        genr = False
        if autoroll != False:
            filedata,genr = self.genroll(filedata,autoroll)


        #draws the names of the stat types to the background using a for loop
        x = 20
        draw.text((x,h+10),f'{filedata[:2].upper()}{filedata[2:]}',font=italic,fill=(0,0,0))

        #increases the height
        h += 10 + regular.getsize('STR')[1]

        #increases the height value and adds another separator under the new stats
        h += regular.getsize('10')[1]

        if cure:
            string = 'This effect will last until '

            #opens file and checks number of lines + saves all lines
            filelines = []
            with open(f'{PATH}\\resources\\data\\Wild Surge Cures.txt','r',encoding='UTF-8') as f:
                for line in f:
                    line = line.split()
                    ln = ''
                    for j in line[1:]:
                        ln = ln + ' ' + j
                    filelines.append(ln)

            cure = random.choice(filelines)
            cure = cure[1].lower() + cure[2:]

            if cureautoroll:
                cure,r = self.genroll(cure,True)
            draw.text((x+3,h-5),string + cure,font=italic,fill=(0,0,0))

        #img.paste(separator,(20,h+20))

        #the image is temp saved in the \tmp folder, sent to discord and then immediatelly deleted
        img.save(f'{PATH}\\resources\\files\\tmp\\wildsurge.png')
        return r #, genr

    @discord.ui.button(label='Reroll',style=discord.ButtonStyle.blurple, custom_id='wild_surge_button:reroll')
    async def reroll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        wsroll = self.wildsurgegen()
        private = False
        isPrivate = interaction.message.attachments[0].filename

        if '-hidden' in isPrivate:
            private = True
            wsroll = str(wsroll) + '-hidden'

        #await interaction.response.delete_message()
        print(f'{interaction.user} is rerolling on the wild magic table...')
        await interaction.response.send_message(view=self, file=discord.File(f'{PATH}\\resources\\files\\tmp\\wildsurge.png',filename=f'{wsroll}.png'),ephemeral=private)
        os.remove(f'{PATH}\\resources\\files\\tmp\\wildsurge.png')

    @discord.ui.button(label='Roll Cure',style=discord.ButtonStyle.blurple, custom_id='wild_surge_button:cure')
    async def cure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        autorollcure = False
        private = False
        wsroll = interaction.message.attachments[0].filename
        if '-hidden' in wsroll:
            private = True
            wsroll = wsroll.replace('-hidden','')
        wsroll = wsroll.replace('.png','')


        print(f'{interaction.user} is rolling for a potential cure to the wild magic effect...')
        self.wildsurgegen(wsroll,False,True,autorollcure)
        await interaction.response.send_message(file=discord.File(f'{PATH}\\resources\\files\\tmp\\wildsurge.png',filename=f'{wsroll}.png'),ephemeral=private)
        os.remove(f'{PATH}\\resources\\files\\tmp\\wildsurge.png')

    @discord.ui.button(label='Docs Download',style=discord.ButtonStyle.grey, custom_id='wild_surge_button:docs')
    async def docs_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f'{interaction.user} actually wants the docs...')
        await interaction.response.send_message(file=discord.File(f'{PATH}\\resources\\files\\NLRMEv2.pdf'))


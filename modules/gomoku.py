#dummy module
import asyncio
import discord
from PIL import Image, ImageDraw, ImageFont
import io
import random
import os
from subprocess import call
import pickle
moduleFiles="gomoku"
class MainClass():
    def saveObject(self, object, objectname):
        with open("storage/%s/"%moduleFiles + objectname + "tmp", "wb") as pickleFile:
            pickler = pickle.Pickler(pickleFile)
            pickler.dump(object)
        call(['mv', "storage/%s/"%moduleFiles + objectname + "tmp", "storage/%s/"%moduleFiles + objectname])
    def loadObject(self, objectname):
        if self.saveExists(objectname):
            with open("storage/%s/"%moduleFiles + objectname, "rb") as pickleFile:
                unpickler = pickle.Unpickler(pickleFile)
                return unpickler.load()

    def saveExists(self, objectname):
        return os.path.isfile("storage/%s/"%moduleFiles + objectname)
    def __init__(self, client, modules, owners):
        if not os.path.isdir("storage/%s"%moduleFiles):
            call(['mkdir', 'storage/%s'%moduleFiles])
        self.save=None # format : { 'currently_playing':[id,id,id], 'player_game':{id:gameid} 'games':{gameid:{'White':id,'Black':id, 'hist':['h8','h9']}}}
        self.client = client
        self.modules = modules
        self.owners = owners
        self.events=['on_message', 'on_ready'] #events list
        self.command="" #command prefix (can be empty to catch every single messages)

        self.name="Gomoku"
        self.description="Module du jeu Gomoku"
        self.interactive=True
        self.color=0xffff00
        self.help="""\
 /gomoku challenge <@mention>
 => Défie le joueur mentionné pour une partie de Gomoku

 <coordonnées>
 => joue aux coordonnées spécifiées si c'est votre tour et que les coordonnées sont valides
 
"""

    async def on_ready(self):
        if self.save==None:
            if self.saveExists('save'):
                self.save=self.loadObject('save')
            else:
                self.save={'currently_playing':[], 'player_game':{}, 'games':{}}
            self.saveObject(self.save, 'save')
    async def send_reactions(self, message, reactions):
        for reaction in reactions:
            await message.add_reaction(reaction)
    async def on_message(self, message):
        if self.save!=None:
            await self.on_ready()
            if message.content.startswith('/gomoku'):
                args=message.content.split()
                if len(args)>1 and args[1]=='challenge':
                    try:
                        if not message.mentions[0].id in self.save['currently_playing']:
                            if not message.author.id in self.save['currently_playing']:
                                self.save['currently_playing'] += [message.author.id, message.mentions[0].id]
                                gameid=0
                                while True:
                                    try:
                                        self.save['games'][gameid]
                                        gameid+=1
                                    except:
                                        break
                                black=random.choice([message.author, message.mentions[0]])
                                white=[message.author, message.mentions[0]][[message.author, message.mentions[0]].index(black)-1]
                                self.save['games'].update({gameid:{'Black':black.id, 'White':white.id, 'hist':[]}})
                                self.save['player_game'].update({message.author.id:gameid, message.mentions[0].id:gameid})
                                await message.channel.send("C'est à %s de commencer"%black.mention, file=self.gen_img_from_hist(self.save['games'][gameid]['hist']))
                            else:
                                await message.channel.send(message.author.mention + ", vous êtes déjà dans une partie, finissez celle là pour commencer. ^^")
                        else:
                            await message.channel.send(message.author.mention + ", le joueur mentionné est déjà en train de jouer...")
                    except KeyError:
                        pass
                else:
                    await self.modules['help'][1].send_help(message.channel, self)
            elif message.author.id in self.save['currently_playing']:
                try:
                    gameid = self.save['player_game'][message.author.id]
                    test=None
                    if self.save['games'][gameid]['Black']==message.author.id:
                        test=len(self.save['games'][gameid]['hist'])%2==0
                    else:
                        test=len(self.save['games'][gameid]['hist'])%2!=0
                    if test:
                        test=self.get_valid_coords(message.content, self.save['games'][gameid]['hist'])
                        if test:
                            testmessage = await message.channel.send(file=self.gen_img_from_hist(self.save['games'][gameid]['hist'] + [test], test=True))
                            asyncio.ensure_future(self.send_reactions(testmessage, ['✅','❌']), loop=self.client.loop)
                            def check(reaction, user):
                                return reaction.message.id == testmessage.id and user.id == message.author.id and str(reaction.emoji) in ['✅','❌']
                            reaction, _ = await self.client.wait_for('reaction_add', check=check)
                            if str(reaction.emoji)=='✅':
                                await testmessage.delete()
                                self.save['games'][gameid]['hist'].append(test)
                                await message.channel.send(file=self.gen_img_from_hist(self.save['games'][gameid]['hist']))
                            if str(reaction.emoji)=='❌':
                                await testmessage.delete()
                except:
                    raise
    def is_win(self, grid, coords=None):
        def isWin(row,check):
            if row[check]!=None:
                for i in range(len(row)):
                    if row[i]==row[check]:
                        if i<=check and i+5>check:
                            if row[i:i+5].count(row[check])>=5:
                                return True
            return False
        def check_coords(Iline, Icase, grid):
            hor=grid[Iline]
            ver=[grid[i][Icase] for i in range(len(grid))]
            diag1=[[Iline-min(Iline,Icase) +i, Icase-min(Iline,Icase) +i]for i in range(15-max(Iline-min(Iline,Icase), Icase-min(Iline,Icase)))]
            diag2=[[Iline-min(Iline,14-Icase)+i, Icase+min(Iline,14-Icase)-i] for i in range(min(15-(Iline-min(Iline,14-Icase)), 15-(14-(Icase+min(Iline,14-Icase)))))]
            return isWin(hor, Icase) and isWin(ver, Iline) and isWin([grid[coords[1]][coords[0]] for coords in diag1], diag1.index([Iline,Icase])) and isWin([grid[coords[1]][coords[0]] for coords in diag2], diag2.index([Iline,Icase]))
        if coords==None:
            for Iline in range(len(grid)):
                for Icase in range(len(grid[Iline])):
                    return check_coords(Iline, Icase, grid)
        else:
            Iline,Icase=coords
            return check_coords(Iline, Icase, grid)
    def gen_img_from_hist(self, hist, test=False):
        return self.gen_img(self.gen_grid_from_hist(hist), test=test)
    def gen_grid_from_hist(self, hist):
        grid=[[None for i in range(15)] for i in range(15)]
        i=0
        finalturn=None
        for turn in hist:
            if i%2==0:
                grid[turn[1]][turn[0]]='Black'
            else:
                grid[turn[1]][turn[0]]='White'
            if self.is_win(grid, coords=turn):
                grid[turn[1]][turn[0]]+='W'
            i+=1
            finalturn=turn
        if finalturn:
            grid[finalturn[1]][finalturn[0]]+='L'
        return(grid)
    def get_valid_coords(self, coordsin, hist):
        try:
            coords=coordsin.upper()
            coordlist=[]
            if coords[0] in "ABCDEFGHIJKLMNO":
                coordlist.append("ABCDEFGHIJKLMNO".index(coords[0]))
            else :
                return False
            if 0<int(coords[1:])<16 :
                coordlist.append(int(coords[1:])-1)
            else:
                return False
            if not coordlist in hist:
                return coordlist
            else:
                return False
        except:
            return False
    def gen_img(self, grid, test=False):
        img=None
        if test:
            img = Image.new('RGBA', (640,640), color=(255,200,200,255))
        else:
            img = Image.new('RGBA', (640,640), color=(200,200,200,255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("assets/DejaVuSerif-Bold.ttf", size=12)
        for i in range(16):
            draw.line((i*40,20) + (i*40,620), fill=(128,128,128,255))
        for i in range(16):
            draw.line((20,i*40) + (620,i*40), fill=(128,128,128,255))
        for i in range(1,16):
            draw.text((4, 40*i -6), str(i),font=font, fill=(255,0,0,255))
        lettres="ABCDEFGHIJKLMNO"
        for i in range(1,16):
            draw.text((40*i -4, 4), lettres[i-1],font=font, fill=(255,0,0,255))
        for Iline in range(len(grid)):
            for Icase in range(len(grid[Iline])):
                #print([((Icase +1)*40 -15 ,(Iline +1) * 40 - 15),((Icase +1)*40 + 15 ,(Iline +1) * 40 + 15)])
                if grid[Iline][Icase] != None :
                    if grid[Iline][Icase].startswith('White'):
                        draw.ellipse([((Icase +1)*40 -15 ,(Iline +1) * 40 - 15),((Icase +1)*40 + 15 ,(Iline +1) * 40 + 15)], fill=(12,96,153,255))
                    if grid[Iline][Icase].startswith('Black'):
                        draw.ellipse([((Icase +1)*40 -15 ,(Iline +1) * 40 - 15),((Icase +1)*40 + 15 ,(Iline +1) * 40 + 15)], fill=(10,10,10,255))
                    if 'W' in grid[Iline][Icase][5:]:
                        draw.ellipse([((Icase +1)*40 -4 ,(Iline +1) * 40 - 4),((Icase +1)*40 + 4 ,(Iline +1) * 40 + 4)], fill=(194,45,48,255))
                    if 'L' in grid[Iline][Icase][5:]:
                        draw.ellipse([((Icase +1)*40 -17 ,(Iline +1) * 40 - 17),((Icase +1)*40 + 17 ,(Iline +1) * 40 + 17)], outline=(54,122,57,255))
                        draw.ellipse([((Icase +1)*40 -15 ,(Iline +1) * 40 - 15),((Icase +1)*40 + 15 ,(Iline +1) * 40 + 15)], outline=(54,122,57,255))
                        draw.ellipse([((Icase +1)*40 -14 ,(Iline +1) * 40 - 14),((Icase +1)*40 + 14 ,(Iline +1) * 40 + 14)], outline=(54,122,57,255))
                        draw.ellipse([((Icase +1)*40 -13 ,(Iline +1) * 40 - 13),((Icase +1)*40 + 13 ,(Iline +1) * 40 + 13)], outline=(54,122,57,255))
                        draw.ellipse([((Icase +1)*40 -12 ,(Iline +1) * 40 - 12),((Icase +1)*40 + 12 ,(Iline +1) * 40 + 12)], outline=(54,122,57,255))
        tmpstr="/tmp/%s.png"%random.randint(1,10000000)
        img.save(tmpstr, "PNG")
        return discord.File(tmpstr)
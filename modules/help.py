import discord

from modules.base import BaseClass


class MainClass(BaseClass):
    name = "Aide"
    help_active = True
    help = {
        "description": "Module d'aide",
        "commands": {
            "`{prefix}{command} list`": "Affiche une liste des modules ainsi qu'une desription",
            "`{prefix}{command} <module>`": "Affiche l'aide sépcifique d'un module"# ,
            # "`{prefix}{command} all`": "Affiche l'aide de tous les modules"
        }
    }
    color = 0x3c9653
    command_text = "help"

    async def com_list(self, message, args, kwargs):
        embed = discord.Embed(title="[Aide] - Liste des modules", color=self.color)
        for moduleName in list(self.client.modules.keys()):
            if self.client.modules[moduleName]["initialized_class"].help_active and \
                    await self.auth(message.author, moduleName):
                embed.add_field(
                    name=moduleName.capitalize(),
                    value=self.client.modules[moduleName]["initialized_class"].help["description"])
        await message.channel.send(embed=embed)

    # async def com_all(self, message, args, kwargs):
    #     for name, module in self.client.modules.items():
    #         await module["initialized_class"].send_help(message.channel)

    async def command(self, message, args, kwargs):
        if len(args) and args[0] in self.client.modules.keys():
            await self.client.modules[args[0]]["initialized_class"].send_help(message.channel)
        else :
            await self.send_help(message.channel)

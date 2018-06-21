import settings.roles
import discord
async def AddRole(client, message) :
	args = message.content.split(" ")
	if args[0] == "/role"  :
		if len(args) > 2 or len(args) == 1 :
			await client.send_message(message.channel, message.author.mention + "\n ```\nusage :\n/role list(e)\n/role <nom du rôle>```")
		elif args[1] == "liste" or args[1] == "list" :
			response = "```\nListe des roles disponibles :\n"
			for nom, idgrp in settings.roles.RoleList.items() :
				response += nom + "  =>  " + idgrp[1] + "\n"
			await client.send_message(message.channel, message.author.mention + response + "\n```")
			await client.delete_message(message)
		else :
			try :
				if discord.utils.get(message.server.roles, id=settings.roles.RoleList[args[1]][0]) in message.author.roles :
					await client.remove_roles(message.author, discord.utils.get(message.server.roles, id=settings.roles.RoleList[args[1]][0]))
					await client.send_message(message.channel, message.author.mention + ", vous avez perdu le rôle " + args[1] +".")
					await client.delete_message(message)
				else :
					await client.add_roles(message.author, discord.utils.get(message.server.roles, id=settings.roles.RoleList[args[1]][0]))
					await client.send_message(message.channel, message.author.mention + ", vous avez reçu le rôle " + args[1] +".")
					await client.delete_message(message)
			except KeyError:
				await client.send_message(message.channel, message.author.mention + ", ce rôle n'est pas disponnible à l'auto-attribution. Vous pouvez avoir la liste des rôles disponnible grâce à la commande /role liste .")
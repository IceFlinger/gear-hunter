#!/usr/bin/env python
import json
import requests
import sys
import configparser

host="https://app.splatoon2.nintendo.net"
app_head = {
	'Host': 'app.splatoon2.nintendo.net',
	'x-unique-id': '54785545369741597536', # random 19-20 digit token. used for splatnet store
	'x-requested-with': 'XMLHttpRequest',
	'x-timezone-offset': '0',
	'User-Agent': 'Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
	'Accept': '*/*',
	'Referer': 'https://app.splatoon2.nintendo.net/home',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': "en-US"
}

if "--help" in sys.argv:
	print("Splatoon 2 Gear Hunter. Usage:")
	print("gearhunter.py [config file]")
	print("Defaults to gearhunter.cfg")
	sys.exit(0)
config_file = "gearhunter.cfg"
if len(sys.argv) > 1:
	config_file = sys.argv[1]
notify = False
try:
	conf = configparser.ConfigParser()
	conf.read(config_file)
	iksm = conf["gearhunter"]["iksm"]
	if len(iksm) != 40:
		print("iksm token is missing or malformed, exiting")
		exit()
	if "discord_token" in conf["gearhunter"] and "discord_user" in conf["gearhunter"]:
		if len(conf["gearhunter"]["discord_token"]) == 59:
			notify = True
			import discord
			import asyncio
			discord_token = conf["gearhunter"]["discord_token"]
			discord_user = conf["gearhunter"]["discord_user"]
		else:
			print("discord token is malformed, exiting")
			exit()
	if not "wanted_sets" in conf["gearhunter"]:
		print("Missing wanted sets from config file, exiting")
		exit()
	else:
		needed = json.loads(conf["gearhunter"]["wanted_sets"])
except ImportError as e:
	print("Configured with discord token/user but discord python module is missing, install discord.py")
	exit()
except ValueError as e:
	print("Wanted sets list is incorrectly formatted")
	exit()
except:
	print("Error while reading config file.")
	raise

s = requests.Session()
results = s.get(host + "/api/onlineshop/merchandises", headers=app_head, cookies=dict(iksm_session=iksm))
data = json.loads(results.text)
message = ""
found = False
for gear in data["merchandises"]:
	for need in needed:
		slot = (need[0]==gear["kind"])
		skill = (need[1]==gear["skill"]["name"])
		sub = (need[2]==gear["gear"]["brand"]["name"])
		if slot and skill and sub:
			print("Found gear!!!")
			found = True
			message += str(gear["gear"]["name"] + " (" + gear["gear"]["brand"]["name"] + "/" + gear["gear"]["brand"]["frequent_skill"]["name"] +") with " + gear["skill"]["name"] + " in the store\n") 
if not found:
	message = ""
	print("Found no gear")
print(message)
if notify:
	client = discord.Client()
	@client.event
	async def on_ready():
		user = discord.utils.get(client.get_all_members(), id=discord_user)
		if message != "":
			await client.send_message(user, message)
		await client.logout()
	client.run(discord_token)


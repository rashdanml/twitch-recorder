# Imports

import requests
import os
import time
import json
import sys
import subprocess
import datetime
import getopt
import random
import urllib3
import socket
from config import conf
from json import JSONDecodeError


class TwitchRecorder():
	def __init__(self):
		# Global configuration
		self.refresh = 10.0
		self.ffmpeg_path = "ffmpeg"
		self.root_path = "/home/rashy/vods" # REPLACE WITH DESIRED OUTPUT DIRECTORY

		self.username = "rashdanml" # REPLACE WITH DESIRED DEFAULT USERNAME
		self.quality = "best"

	# Check user status. #0 - online, #1 - offline, #2 - not found, #3 - error
	def check_user(self):

		info = None
		status = 3

		try:
			def getinfo(try_number=1):
				url = 'https://api.twitch.tv/helix/streams?user_login=' + self.username
				headers = {'client-id': conf.clientid, 'Authorization': 'Bearer '
						   + conf.oauthtoken, 'Accept': 'application/json'}

				try:
					info = requests.get(url, headers=headers).json()
				except (simplejson.errors.JSONDecodeError, requests.exceptions.ConnectionError, JSONDecodeError, json.decoder.JSONDecodeError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError, socket.gaierror) as e:
					time.sleep(2**try_number + random.random()*0.01)
					return getinfo(try_number=try_number+1)
				else:
					return info

			info = getinfo(try_number=1)

			if 'data' in info and info['data'] == []:
				status = 1
			else:
				if ('data' in info and info['data'][0]['user_name'].lower() == self.username and info['data'][0]['type'] == "live"):
					status = 0
		except requests.exceptions.RequestException as e:
			if e.response:
				if e.response.reason == 'Not Found' or e.response.reason == 'Unprocessable Entity':
					status = 2
		return status, info

	# Check to see user status, start recording if online.
	def loopcheck(self):
		while True:
			print(datetime.datetime.now().strftime("%Hh%Mm%Ss"),
				  " ", "Validating OAuth_Token ...", end="")
			valid = conf.validate()
			print("Done!")

			if 'status' in valid and valid['status'] == 401 and valid['message'] == "invalid access token":
				print(datetime.datetime.now().strftime("%Hh%Mm%Ss"), " ",
					  "OAuth_Token Invalid, Refreshing Token ... ", end="")
				conf.refresh()
				print("OAuth_Token Refreshed!")

			status, info = self.check_user()
			if status == 2:
				print(datetime.datetime.now().strftime("%Hh%Mm%Ss"), " ",
					  "Username not found. Invalid username or typo.")
				time.sleep(self.refresh)
			elif status == 3:
				print(datetime.datetime.now().strftime("%Hh%Mm%Ss"), " ",
					  "unexpected error. will try again in", self.refresh, "seconds.")
				time.sleep(self.refresh)
			elif status == 1:
				print(datetime.datetime.now().strftime("%Hh%Mm%Ss"), " ", self.username,
					  "currently offline, checking again in", self.refresh, "seconds.")
				time.sleep(self.refresh)
			elif status == 0:
				print(datetime.datetime.now().strftime("%Hh%Mm%Ss"), " ",
					  self.username, "online. Stream recording in session, using OAuth_Token: ", conf.oauthtoken)
				filename = self.username + " - " + datetime.datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss") + \
					" - " + info['data'][0]['title'] + ".mp4"

				# clean filename from unecessary characters
				filename = "".join(x for x in filename if x.isalnum() or x in [" ", "-", "_", "."])

				recorded_filename = os.path.join(self.recorded_path, filename)

				# start streamlink process
				subprocess.call(["streamlink", "--twitch-disable-hosting", "--twitch-disable-ads",
								 "twitch.tv/" + self.username, self.quality, "-o", recorded_filename])

				print("Recording stream is done. Fixing video file.")

				if(os.path.exists(recorded_filename) is True):
					try:
						subprocess.call([self.ffmpeg_path, '-err_detect', 'ignore_err', '-i',
										 recorded_filename, '-c', 'copy', os.path.join(self.processed_path, filename)])
						os.remove(recorded_filename)
					except Exception as e:
						print(e)
				else:
					print("Skip fixing. File not found.")

				print("Fixing is done. Going back to checking..")
				time.sleep(self.refresh)

	def run(self):
		# path to recorded stream
		self.recorded_path = os.path.join(self.root_path, "recorded", self.username, self.quality)

		# path to finished video, errors removed
		self.processed_path = os.path.join(self.root_path, "processed", self.username, self.quality)

		# create directory for recordedPath and processedPath if not exist
		if(os.path.isdir(self.recorded_path) is False):
			os.makedirs(self.recorded_path)
		if(os.path.isdir(self.processed_path) is False):
			os.makedirs(self.processed_path)

		# make sure the interval to check user availability is not less than 15 seconds
		if(self.refresh < 15):
			print("Check interval should not be lower than 15 seconds.")
			self.refresh = 15
			print("System set check interval to 15 seconds.")

		# fix videos from previous recording session
		try:
			video_list = [f for f in os.listdir(self.recorded_path) if os.path.isfile(
				os.path.join(self.recorded_path, f))]
			if(len(video_list) > 0):
				print('Fixing previously recorded files.')
			for f in video_list:
				recorded_filename = os.path.join(self.recorded_path, f)
				print('Fixing ' + recorded_filename + '.')
				try:
					subprocess.call([self.ffmpeg_path, '-err_detect', 'ignore_err', '-i',
									 recorded_filename, '-c', 'copy', os.path.join(self.processed_path, f)])
					os.remove(recorded_filename)
				except Exception as e:
					print(e)
		except Exception as e:
			print(e)

		print("Checking for", self.username, "every", self.refresh,
			  "seconds. Record with", self.quality, "quality.")
		self.loopcheck()


def main(argv):
	twitch_recorder = TwitchRecorder()
	usage_message = 'twitch-recorder.py -u <username> -q <quality>'

	try:
		opts, args = getopt.getopt(argv, "hu:q:", ["username=", "quality="])
	except getopt.GetoptError:
		print(usage_message)
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print(usage_message)
			sys.exit()
		elif opt in ("-u", "--username"):
			twitch_recorder.username = arg
		elif opt in ("-q", "--quality"):
			twitch_recorder.quality = arg

	twitch_recorder.run()


if __name__ == "__main__":
	main(sys.argv[1:])

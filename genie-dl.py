import requests
import json
import os
import eyed3
import shutil
import re
import pathlib
import argparse
import platform
from pyfiglet import Figlet
from datetime import datetime
from datetime import date
from pick import pick
from termcolor import colored
import configparser
import questionary
from utils import download

parser = argparse.ArgumentParser(description='\033[93mGENIE-DL by vank0n © 2021 vank0n (SJJeon) - All Rights Reserved.\033[0m',epilog="https://github.com/WHTJEON/genie-dl")
parser.add_argument('-c', '--download-chart',action='store_true',help = "Download Genie TOP 200 Chart")
parser.add_argument('-i','--input',default=None,required=False,help = "Download Genie Song/Album/Playlist",metavar="URL")
args = parser.parse_args()

INPUT_URL = args.input
SEARCH_AMOUNT = 20
DOWNLOAD_CHART = args.download_chart
BITRATE = '320'
EXTENSION = "mp3"
DEVICE_ID = "002ebf12-a125-5ddf-a739-67c3c5d20177"

SCRIPT_PATH=str(pathlib.Path(__file__).parent.absolute())
OUTPUT_PATH = SCRIPT_PATH + "/downloads/"

def read_config():
	global ID, PW
	config = configparser.ConfigParser()
	config_file = "%s/settings.ini"%SCRIPT_PATH
	if pathlib.Path(config_file).is_file():
		config.read(SCRIPT_PATH+'/settings.ini')
		ID = config['DEFAULT']['genie_id']
		PW = config['DEFAULT']['genie_password']
		
	else:
		print("No config file is found. Creating a new one...")
		ID = questionary.text("Enter your Genie ID: ",qmark=">").ask()
		PW = questionary.password("Enter Genie Password: ",qmark=">").ask()
		config['DEFAULT']['genie_id'] = ID
		config['DEFAULT']['genie_password'] = PW

		with open(config_file, 'w') as configfile:
			config.write(configfile)
		print("Successfully created config file!")
		
def is_win():
	if platform.system() == 'Windows':
		return True

def clean_str(str):
	if is_win():
		return re.sub(r'[\/:*?"><|]', '_', str)
	else:
		return re.sub('/', '_', str)

def divider():
	count = int(shutil.get_terminal_size().columns)
	count = count - 1
	print ('-' * count)
	
def remove(): 
	count = int(shutil.get_terminal_size().columns)
	count = count - 1
	blank =' ' * count
	print ("\033[A%s\033[A"%blank)

def decode(str):
	return requests.utils.unquote(str)

def encode(str):
	return requests.utils.quote(str)

def prettifyNUM(num):
	if len(str(num)) == 1:
		num = "%02d"%num	
	return num

def rename(file):
	f = eyed3.load(file)
	fnew = "%s. %s - %s.%s"%(prettifyNUM(f.tag.track_num[0]),f.tag.artist, f.tag.title,EXTENSION)
	os.rename(file,fnew)
	
def parse_code(url,type):
	match = re.findall('\d+',url)
	try:
		CODE = match[0]
		print("[info] URL Type: %s"%type)
		return CODE
	
	except IndexError:
		print("[error] Invalid URL: %s"%url)
		divider()
		exit()
		
def download_track(url,filename,taskname):
	download.download(url,file_name="%s.%s"%(filename,EXTENSION),name=taskname,block_size=512)
		
# Server Side

def login(username,password):
	global user_num,user_token,stm_token
	credentials = {
		"uxd": username,
		"uxx": password
	}
	response = requests.post("https://app.genie.co.kr/member/j_Member_Login.json",data=credentials).json()
	if response['Result']['RetCode'] != "0":
		LOGIN = False
		print("Authentication failed.")
		exit()
	else:
		LOGIN = True
	user_num = response['DATA0']['MemUno']
	user_token = response['DATA0']['MemToken']
	stm_token = response['DATA0']['STM_TOKEN']
	
def parse_playlist_data (seq):
	global PLAYLIST_NAME, PLAYLIST_TRACK_COUNT, PLAYLIST_TRACK_CODES, PLAYLIST_TRACK_TITLES
	api_url = "https://app.genie.co.kr/Iv3/playlist/infosong.json?seq={}".format(seq)
	response = requests.get(api_url).json()
	try:
		PLAYLIST_NAME = decode(response['DATASET']['DATA_INFO']['DATA']['PLM_TITLE'])
		PLAYLIST_TRACK_COUNT = int(decode(response['DATASET']['DATA_INFO']['DATA']['SONG_CNT']))
		PLAYLIST_TRACK_CODES = {}
		PLAYLIST_TRACK_TITLES = {}
		
		for i in range (0,PLAYLIST_TRACK_COUNT,1):
			PLAYLIST_TRACK_CODES [i] = int(decode(response['DATASET']['DATA_SONG']['DATA'][i]['SONG_ID']))
			PLAYLIST_TRACK_TITLES [i] = decode(response['DATASET']['DATA_SONG']['DATA'][i]['SONG_NAME'])
	except KeyError:
		print("[error] Unable to fetch playlist data. Check your URL")
		divider()
		exit()
		
def parse_album_data(axnm):
	global ALBUM_TRACK_CODES,ALBUM_TRACK_TITLES,ALBUM_NAME,ALBUM_TRACK_COUNT, ALBUM_DATE, ALBUM_TYPE, ALBUM_ARTIST
	response = requests.get("https://info.genie.co.kr/info/album?axnm={}".format(axnm)).json()
	try:
		ALBUM_NAME = response['album_info']['album_name']
		ALBUM_ARTIST = response['album_info']['artist_name']
		ALBUM_DATE_RAW = str(response['album_info']['album_release_dt'])
		year = ALBUM_DATE_RAW[0:4]
		month = ALBUM_DATE_RAW[4:6]
		ALBUM_DATE = "[%s.%s]"%(year,month)
		ALBUM_TYPE = decode(response['album_info']['album_type'])
		ALBUM_TRACK_COUNT = len(response['album_song_list'])
		ALBUM_TRACK_CODES = {}
		ALBUM_TRACK_TITLES = {}
		for i in range (0,ALBUM_TRACK_COUNT,1):
			ALBUM_CD = int(response['album_song_list'][i]['album_cd_no'])
			if ALBUM_CD == 1: # CD가 나눠져있는 경우 처리방법 임시로 설정.. 개선필요..
				
				ALBUM_TRACK_CODES[int(response['album_song_list'][i]['album_track_no'])]=response['album_song_list'][i]['song_id']
				ALBUM_TRACK_TITLES[int(response['album_song_list'][i]['album_track_no'])]=response['album_song_list'][i]['song_name']
			else: 
				current_count = len(ALBUM_TRACK_CODES)
#				ALBUM_TRACK_CODES[i+1]=response['album_song_list'][i]['song_id']
#				ALBUM_TRACK_TITLES[i+1]=response['album_song_list'][i]['song_name']
				ALBUM_TRACK_COUNT = current_count
		
		print("[info] Found Album: %s (%s) (%s tracks)"%(ALBUM_NAME,ALBUM_ARTIST,ALBUM_TRACK_COUNT))
		
	except KeyError:
		print("[error] Unable to fetch album data. Check your URL")
		divider()
		exit()

def parse_artist_data(xxnm):
	global ARTIST_NAME_FIX
	try:
		response = requests.get("https://info.genie.co.kr/info/artist?xxnm={}".format(xxnm)).json()
		ARTIST_NAME_FIX = response['artist_info']['artist_name']
		print("[info] Found Artist: %s"%(ARTIST_NAME_FIX))
		return ARTIST_NAME_FIX
	
	except KeyError:
		print("[error] Unable to fetch artist data. Check your URL")
		divider()
		exit()
		
def parse_track_data(xgnm,bitrate):
	global ARTIST_NAME,SONG_NAME,DOWNLOAD_URL,IS_VALID
	response = requests.get("https://stm.genie.co.kr/player/j_StmInfo.json?xgnm={}&bitrate={}&app_stm_type=normal&unm={}&uxtk={}&vmd=A&svc=DI&stk={}&udid={}&itn=Y&mts=Y&apvn=50101".format(xgnm,bitrate,user_num,user_token,stm_token,DEVICE_ID)).json()
	SUCCESS = response['Result']['RetMsg']

	try:
		DATA = response['DataSet']['DATA'][0]
		SONG_NAME = decode(DATA['SONG_NAME'])
		ARTIST_NAME = decode(DATA['ARTIST_NAME'])
		DOWNLOAD_URL = decode(DATA['STREAMING_MP3_URL'])
		IS_VALID = True
		return DOWNLOAD_URL
	
	except IndexError:
		IS_VALID = False
		
	except KeyError:
		print("[error] Unable to fetch track data. Check your URL")
		divider()
		exit()
	
	except:
		print(response)
		
def get_artist_albums(xxnm):
	global TOTAL_ALBUM_COUNT,ARTIST_ALBUMS
	api_url = "https://app.genie.co.kr/song/j_ArtistAlbumList.json?pg=1&pgsize=500&xxnm={}&otype=newest&atype=all&mts=Y".format(xxnm)
	response = requests.get(api_url).json()
	try:
		TOTAL_ALBUM_COUNT = int(response['PageInfo']['TotCount'])
		ARTIST_ALBUMS = []
		for i in range (0,TOTAL_ALBUM_COUNT,1):
			ALBUM_CODE = response['DataSet']['DATA'][i]['ALBUM_ID']
			ARTIST_ALBUMS.append(ALBUM_CODE)
	except KeyError:
		print("The following artist is unavailable to fetch albums")
		exit()
			
def download_album(axnm):
	parse_album_data(axnm)
	k = 0
	DOWNLOAD_PATH = OUTPUT_PATH+"%s/%s %s/"%(ALBUM_ARTIST,ALBUM_DATE,ALBUM_NAME)
	if not os.path.exists(DOWNLOAD_PATH):
		os.makedirs(DOWNLOAD_PATH)
	print("[info] Downloading Tracks of [%s]\n"%ALBUM_NAME)
	for i in range (1,ALBUM_TRACK_COUNT+1,1):
		k = k + 1
		try:
			parse_track_data(ALBUM_TRACK_CODES[i], BITRATE)
			if IS_VALID == False:
				print("%s. Track Unavailable. Skipping Download"%i)
			else:
				f = clean_str("%s. %s - %s"%(prettifyNUM(i),ARTIST_NAME,str(ALBUM_TRACK_TITLES[i])))
				filename = DOWNLOAD_PATH+f
				taskname = "%s. %s"%(i,ALBUM_TRACK_TITLES[i])
				download_track(DOWNLOAD_URL,filename,taskname)
		except KeyError:
			pass

def download_playlist(seq):
	parse_playlist_data(seq)
	print("[info] Downloading Playlist: %s (%s tracks)\n"%(PLAYLIST_NAME,PLAYLIST_TRACK_COUNT))
	DOWNLOAD_PATH = OUTPUT_PATH+"[Playlist] %s/"%PLAYLIST_NAME.replace(":","-")
	if not os.path.exists(DOWNLOAD_PATH):
		os.makedirs(DOWNLOAD_PATH)
	for i in range (0, PLAYLIST_TRACK_COUNT,1):
		parse_track_data (PLAYLIST_TRACK_CODES[i], BITRATE)
		if IS_VALID == False:
			print("%s. Track Unavailable. Skipping Download"%i)
		else:
			f = "%s. %s - %s"%(prettifyNUM(i+1),ARTIST_NAME,clean_str(str(PLAYLIST_TRACK_TITLES[i])))
			filename = DOWNLOAD_PATH+f
			taskname = "%s. %s"%(i+1,PLAYLIST_TRACK_TITLES[i])
			download_track(DOWNLOAD_URL,filename,taskname)

	
def download_artist(xxnm):
	get_artist_albums(xxnm)
	parse_artist_data(xxnm)
	k = 0
	for ALBUM in ARTIST_ALBUMS:
		k = k + 1
		print("[info] Downloading %s's Albums (%s/%s)"%(ARTIST_NAME_FIX,k,TOTAL_ALBUM_COUNT))
		download_album(ALBUM)
		if k != TOTAL_ALBUM_COUNT:
			divider()
		
def print_realtime_chart (start,end):
	api_url = "https://app.genie.co.kr/chart/j_RealTimeRankSongList.json?pg=1&pgsize=200"
	response = requests.get(api_url).json()
	now = datetime.now()
	today = date.today()
	d1 = today.strftime("%Y.%m.%d")
	current_hour = now.strftime("%H")
	CHART_NAME = "[Genie Realtime Chart for %s %s:00]\n"%(d1,current_hour)
	CHART = {}
	print(CHART_NAME)
	for i in range (start-1,end,1):
		TRACK_NAME = decode(response["DataSet"]['DATA'][i]['SONG_NAME'])
		ARTIST_NAME = decode(response["DataSet"]['DATA'][i]['ARTIST_NAME'])
		string = "%s. %s - %s"%(i+1,ARTIST_NAME,TRACK_NAME)
		CHART [i+1] = string
		
	for i in range (start,end+1,1):	
		print(CHART[i])
		

def download_realtime_chart(start,end):
	api_url = "https://app.genie.co.kr/chart/j_RealTimeRankSongList.json?pg=1&pgsize=200"
	response = requests.get(api_url).json()
	CHART_TRACK_CODES = []
	
	for i in range (start-1,end,1):
		TRACK_CODE = response["DataSet"]['DATA'][i]['SONG_ID']
		CHART_TRACK_CODES.append(TRACK_CODE)
	
	now = datetime.now()
	today = date.today()
	d1 = today.strftime("%y%m%d")
	current_hour = now.strftime("%H")
	
	CHART_NAME = "%s %s:00"%(d1,current_hour)
	print("[info] Downloading Real-Time Chart for %s (%s~%s)\n"%(CHART_NAME,start,end))
	k = 0
	DOWNLOAD_PATH = OUTPUT_PATH+"[Genie TOP 200] - %s/"%CHART_NAME.replace(":","_").replace(" ","_")
	if not os.path.exists(DOWNLOAD_PATH):
		os.makedirs(DOWNLOAD_PATH)
	for tracks in CHART_TRACK_CODES:
		k = k + 1
		parse_track_data(tracks, BITRATE)
		if IS_VALID == False:
			print("%s. Track Unavailable. Skipping Download"%i)
		else:
			f = "%s. %s - %s"%(prettifyNUM(k),ARTIST_NAME,SONG_NAME)
			filename = DOWNLOAD_PATH+clean_str(f)
			taskname = "%s. %s"%(k,SONG_NAME)
			download_track(DOWNLOAD_URL,filename,taskname)
			
			
def search_track(keyword,amount):
	
	api_url = "https://app.genie.co.kr/search/category/songs.json?query={}&hl=false&pagesize={}&order=false&of=POPULAR&page=1".format(encode(keyword),amount)
	response = requests.get(api_url).json()
	SONG_SEARCH_RESULTS_NAME = {}
	SONG_SEARCH_RESULTS_ARTIST = {}
	SONG_SEARCH_RESULTS_CODE = {}
	SONG_SEARCH_COUNT = int(response['searchResult']['result']['songs']['total'])
	
	if SONG_SEARCH_COUNT < amount:
		amount = SONG_SEARCH_COUNT
	
	for i in range (0,amount,1):
		try:
			SONG_SEARCH_RESULTS_NAME [i] = decode(response['searchResult']['result']['songs']['items'][i]['song_name']['original'])
			SONG_SEARCH_RESULTS_ARTIST [i] = decode(response['searchResult']['result']['songs']['items'][i]['artist_name']['original'])
			SONG_SEARCH_RESULTS_CODE [i] = int(response['searchResult']['result']['songs']['items'][i]['song_id'])
		except IndexError:
			print("d")
	print("Here are the search results for %s:\n"%keyword)
	for i in range(0,amount,1):
		RESULT_STRING = "%s. %s - %s"%(i+1,SONG_SEARCH_RESULTS_ARTIST[i],SONG_SEARCH_RESULTS_NAME[i])
		print(RESULT_STRING)
	
	divider()
	while True:
		try:
			choice = int(input("Enter Choice: \n> "))
			divider()
			if choice == 0:
				cnt = False
				break
			elif 1 <= choice <= amount:
				SELECTED_TRACK_CODE = SONG_SEARCH_RESULTS_CODE [choice-1]
				cnt = True
				break
			else:
				print("[error] Enter a valid number from 1~%s"%amount)
				divider()
				continue
		except:
			print("[error] Enter a valid number from 1~%s"%amount)
			divider()
			continue
		
	if cnt == False:
		exit()
	else:
		parse_track_data(SELECTED_TRACK_CODE, BITRATE)
		print("[info] Downloading %s - %s\n"%(ARTIST_NAME,SONG_NAME))
		filename = OUTPUT_PATH+"%s - %s"%(ARTIST_NAME,SONG_NAME)
		taskname = "%s. %s"%(1,SONG_NAME)
		download_track(DOWNLOAD_URL,filename,taskname)
	
def search_album(keyword,amount):
	
	api_url = "https://app.genie.co.kr/search/category/albums.json?query={}&hl=false&pagesize={}&order=false&of=POPULAR&page=1".format(encode(keyword),amount)
	response = requests.get(api_url).json()
	ALBUM_SEARCH_RESULTS_NAME = {}
	ALBUM_SEARCH_RESULTS_ARTIST = {}
	ALBUM_SEARCH_RESULTS_CODE = {}
	ALBUM_SEARCH_COUNT = int(response['searchResult']['result']['albums']['total'])
	
	if ALBUM_SEARCH_COUNT < amount:
		amount = ALBUM_SEARCH_COUNT

	for i in range (0,amount,1):
		try:
			ALBUM_SEARCH_RESULTS_NAME [i] = decode(response['searchResult']['result']['albums']['items'][i]['album_name']['original'])
			ALBUM_SEARCH_RESULTS_ARTIST [i] = decode(response['searchResult']['result']['albums']['items'][i]['artist_name']['original'])
			ALBUM_SEARCH_RESULTS_CODE [i] = int(response['searchResult']['result']['albums']['items'][i]['album_id'])
		except IndexError:
			print("d")
	print('Here are the album search results for "%s":\n'%keyword)
	for i in range(0,amount,1):
		RESULT_STRING = "%s. %s - %s"%(i+1,ALBUM_SEARCH_RESULTS_ARTIST[i],ALBUM_SEARCH_RESULTS_NAME[i])
		print(RESULT_STRING)
		
	divider()
	while True:
		try:
			choice = int(input("Enter Choice: \n> "))
			divider()
			if choice == 0:
				cnt = False
				break
			elif 1 <= choice <= amount:
				SELECTED_ALBUM_CODE = ALBUM_SEARCH_RESULTS_CODE [choice-1]
				cnt = True
				break
			else:
				print("[error] Enter a valid number from 1~%s"%amount)
				divider()
				continue
		except:
			print("[error] Enter a valid number from 1~%s"%amount)
			divider()
			continue
		
	if cnt == False:
		exit()
	else:
		download_album(SELECTED_ALBUM_CODE)
		

def search_artist(keyword,amount):
	api_url = "https://app.genie.co.kr/search/category/artists.json?query={}&hl=false&pagesize={}&order=false&of=POPULAR&page=1".format(encode(keyword),amount)
	response = requests.get(api_url).json()
	ARTIST_SEARCH_RESULTS_NAME = {}
	ARTIST_SEARCH_RESULTS_ARTIST = {}
	ARTIST_SEARCH_RESULTS_CODE = {}
	ARTIST_SEARCH_COUNT = int(response['searchResult']['result']['artists']['total'])
	
	if ARTIST_SEARCH_COUNT < amount:
		amount = ARTIST_SEARCH_COUNT
		
	for i in range (0,amount,1):
		try:
			ARTIST_SEARCH_RESULTS_NAME [i] = decode(response['searchResult']['result']['artists']['items'][i]['artist_name']['original'])
			ARTIST_SEARCH_RESULTS_CODE [i] = int(response['searchResult']['result']['artists']['items'][i]['artist_id'])
		except IndexError:
			exit()
	print("Here are the search results for %s:\n"%keyword)
	for i in range(0,amount,1):
		RESULT_STRING = "%s. %s"%(i+1,ARTIST_SEARCH_RESULTS_NAME[i])
		print(RESULT_STRING)
		
	divider()
	while True:
		try:
			choice = int(input("Enter Choice: \n> "))
			divider()
			if choice == 0:
				cnt = False
				break
			elif 1 <= choice <= amount:
				SELECTED_ARTIST_CODE = ARTIST_SEARCH_RESULTS_CODE [choice-1]
				cnt = True
				break
			else:
				print("[error] Enter a valid number from 1~%s"%amount)
				divider()
				continue
		except:
			print("[error] Enter a valid number from 1~%s"%amount)
			divider()
			continue
		
	if cnt == False:
		exit()
	else:
		download_artist(SELECTED_ARTIST_CODE)
		

def parse_user_input(url):
	
	global TYPE,CODE
	
	if "plmSeq" in url:
		TYPE = "Playlist"
		CODE = parse_code(url,TYPE)
		download_playlist(CODE)
		
	elif "axnm" in url:
		TYPE = "Album"
		CODE = parse_code(url,TYPE)
		download_album(CODE)
		
	elif "xxnm" in url:
		TYPE = "Artist"
		CODE = parse_code(url,TYPE)
		download_artist(CODE)
		
	elif "xgnm" in url:
		TYPE = "Track"
		CODE = parse_code(url,TYPE)
		parse_track_data(CODE,BITRATE)
		print("[info] Downloading %s - %s\n"%(ARTIST_NAME,SONG_NAME))
		filename = OUTPUT_PATH+"%s - %s"%(ARTIST_NAME,SONG_NAME)
		taskname = "%s. %s"%(1,SONG_NAME)
		download_track(DOWNLOAD_URL,filename,taskname)
		
	else:
		print("[error] Invalid URL: %s"%url)
		divider()
		exit()


def main():
	read_config()
	login(ID,PW)
	divider()

	f = Figlet(font='slant')
	text = f.renderText('GENIE-DL')
	title = text
	options = ['Download Song / Album / Artist / Playlist', 'Download Real-Time Chart', 'View Real-Time Chart', 'Search and Download Song','Search and Download Album','Search and Download Artist','Exit']
	selected = pick(options, title, multiselect=False, min_selection_count=1,indicator="=>")[1]
	if selected == 0:
		CODE = parse_user_input(input("Enter URL: "))
		parse_track_data(CODE,BITRATE)
		print("[info] Downloading %s - %s\n"%(ARTIST_NAME,SONG_NAME))
		filename = OUTPUT_PATH+"%s - %s"%(ARTIST_NAME,SONG_NAME)
		taskname = "%s. %s"%(1,SONG_NAME)
		download_track(DOWNLOAD_URL,filename,taskname)
	elif selected == 0:
		parse_user_input(input("Enter Song / Album / Playlist URL: "))
	elif selected == 1:
		download_realtime_chart(1,200)
	elif selected == 2:
		print_realtime_chart(1,200)
	elif selected == 3:
		search_track(input("Enter Search Keyword: "),SEARCH_AMOUNT)
	elif selected == 4:
		search_album(input("Enter Search Keyword: "),SEARCH_AMOUNT)
	elif selected == 5:
		search_artist(input("Enter Search Keyword: "),SEARCH_AMOUNT)
	elif selected == 6:
		exit()
	
	divider()
	
	
if DOWNLOAD_CHART != True and INPUT_URL == None:
	main()

else:
	read_config()
	login(ID,PW)
	
	if DOWNLOAD_CHART == True:
		download_realtime_chart(1,200)
	
	elif INPUT_URL != None:
		parse_user_input(INPUT_URL)
	
	divider()
	
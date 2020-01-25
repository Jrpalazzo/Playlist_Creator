import pandas as pd
import numpy as np
import random as rn
import os
import sys
import yaml
import spotipy
import spotipy.util as util

from datetime import datetime

from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
from tkinter import messagebox

#read in the album data 
data = pd.read_csv('./nick_data.csv',encoding = "ISO-8859-1")
#scope of the spotify app
scope = 'user-library-read, playlist-modify-private'

#read int the username and playlist data
global user_config
stream = open('config.yaml')
user_config = yaml.load(stream)

#645 http://everynoise.com/everynoise1d.cgi?scope=all
#music_genres = ['psychedelic rock', 'folk album', 'new wave pop', 'indie folk', 'new wave', 'folk', 'baroque pop', 'brazilian rock', 'freak folk', 'progressive rock', 'symphonic rock', 'traditional folk', 'experimental pop', 'classic italian pop', 'post-punk', 'classic swedish pop', 'modern folk rock', 'new age', 'anti-folk', 'experimental rock', 'world', 'canadian folk', 'folk brasileiro', 'uk post-punk', 'japanese city pop', 'post-rock', 'suomi rock']

music_genres = ['psychedelic rock', 'new wave pop', 'new wave', 'baroque pop', 'freak folk', 'progressive rock', 'experimental pop', 'post-punk', 'experimental rock', 'uk post-punk', 'post-rock']

SONG_LIMIT = 12
API_LIMIT = 1000
token = util.prompt_for_user_token(user_config['username'], scope)

rn.seed(datetime.now())

#Creates the button application 
def ListApplication(canvas,window,song_ids):
	newList(canvas,window,song_ids)

def RandomApplication(canvas,window,song_ids):
	row_list = []
	search_results = []
	count = 0
	song_switch = False
	
	#randomSongsArray = ['%25a%25', 'a%25', '%25a','%25e%25', 'e%25', '%25e','%25i%25', 'i%25', '%25i', '%25o%25', 'o%25', '%25o','%25u%25', 'u%25', '%25u']
		
	if token:
		sp = spotipy.Spotify(auth=token)
	
		for i in range(SONG_LIMIT):
			while song_switch is False:
				searchLimit = rn.randint(1, API_LIMIT)
				ranNum = rn.randint(0, len(music_genres)-1)
				#randomSongs = rn.choice(randomSongsArray)
				
				if searchLimit <= 1000 and searchLimit > 0:
					searchLimit = searchLimit - 10
		
				search_results = sp.search(q= 'genre:' + music_genres[ranNum], limit=1, offset=searchLimit, type="track")
			
					
				print(search_results)

				for t in search_results['tracks']['items']:
					if t['name'] is not None:
						song_switch = True
			
			for t in search_results['tracks']['items']:
				song_ids.append(t['id'])
				row_list.append(t['name'])
				T = tk.Label(window, text=row_list[count])
				T.place(x=0,y=0 +(30*count))
				count +=1

			song_switch = False
		try:
			sp.user_playlist_add_tracks(user=user_config['username'], playlist_id=user_config['playlist_id'], tracks=song_ids)
		except:
			print("Invalid IDs")
	
	else:
		print("Can't get token for", username)
	
	return song_ids
				
def DeleteApplication(canvas,window,song_ids):
	canvas.destroy()
	if token:
		sp = spotipy.Spotify(auth=token)
		#if there are songs in the playlist remove them
		try:
			sp.user_playlist_remove_all_occurrences_of_tracks(user=user_config['username'], playlist_id=user_config['playlist_id'], tracks=song_ids)
			#make the list null, actually clears the list
			song_ids[:] = []
		except:
				print("Nothing to Remove.")
	else:
		print("Can't get token for", username)

	win_canvas= createCanvas(window)
	
	createButton(win_canvas, window,song_ids)
	
#Generates a random list of 12 albums
def generateList():
	count = 12
	row_list = []
	
	for index, rows in data.sample(frac=1).iterrows():
		if count < 0:
			break
		else:
			song_list =[rows.Name,rows.Title] 
			row_list.append(song_list)
			count -=1
				
	#Create a row of songs and their titles by 
	#creating a series of labels 
	for i in range(0, len(row_list)):
		T = tk.Label(window, text=', '.join(row_list[i]))
		T.place(x=0,y=0 +(30*i))
		
	return row_list
		
#Creates a canvas to draw the text and button on
def createCanvas(window):
	canvas = tk.Canvas(window, width = 320, height = 420)
	canvas.pack()
	return canvas
	
def createButton(canvas,window,song_ids):
	button1 = tk.Button (window, text='Generate a list',command= lambda: ListApplication(canvas,window,song_ids))
	button2 = tk.Button (window, text='Random list',command= lambda: RandomApplication(canvas,window,song_ids))
	button3 = tk.Button (window, text='Delete list.',command= lambda: DeleteApplication(canvas,window,song_ids))

	canvas.create_window(60, 400, window=button1)
	canvas.create_window(150, 400, window=button2)
	canvas.create_window(230, 400, window=button3)
	
#If the dialog box is clicked a new canvas, button and list is created 
def newList(canvas,window,song_ids):
	canvas.destroy()
	win_canvas= createCanvas(window)
	
	list = generateList()
	#for i in range(0, len(list)):
	#	print(list[i][1])
		
	createButton(win_canvas, window,song_ids)
	
	if token:
		sp = spotipy.Spotify(auth=token)
		#if there are songs in the playlist remove them
		
		for i in range(0, len(list)):
			try:
				album_results = sp.search(q='album:' + list[i][1], type='album', limit=1)
				
				#get the first album uri
				album_id = album_results['albums']['items'][0]['uri']
				
				#get the individual tracks from the album
				tracks = sp.album_tracks(album_id)
				
				#pick a random number 1 to 12 to add to the playlist
				ranNum = rn.randint(1, SONG_LIMIT)

				i = 1
				for track in tracks['items']:
					if ranNum == i:
						song_ids.append(track['id'])
						#print(song_ids)
						i = 1
					i += 1
			except:
				print("Invalid album.")
				
		try:
			sp.user_playlist_add_tracks(user=user_config['username'], playlist_id=user_config['playlist_id'], tracks=song_ids)
		except:
			print("Invalid IDs")
			
	else:
		print("Can't get token for", user_config['username'])
	
	return song_ids

if __name__ == '__main__':  
	#list to story the song ids for each album
	song_ids = []
	
	window = tk.Tk()

	window.title("ListCreator")
	
	win_canvas = createCanvas(window)
	
	createButton(win_canvas,window,song_ids)
	
	window.mainloop()



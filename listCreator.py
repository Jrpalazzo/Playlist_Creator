import pandas as pd
import numpy as np
import random as rn
import os
import sys
import yaml
import spotipy
import spotipy.util as util

from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
from tkinter import messagebox

#read in the album data 
data = pd.read_csv('./song_data.csv',encoding = "ISO-8859-1")
#scope of the spotify app
scope = 'user-library-read, playlist-modify-private'

#read int the username and playlist data
global user_config
stream = open('config.yaml')
user_config = yaml.load(stream)
	
token = util.prompt_for_user_token(user_config['username'], scope)
	
#Creates the button application 
def ListApplication(canvas,window,song_ids):
	MsgBox = tk.messagebox.askquestion ('New List','Are you sure you want to generate another list?',icon = 'warning')
	if MsgBox == 'yes':
		newList(canvas,window,song_ids)
	else:
		tk.messagebox.showinfo('Return','You will now return to the application screen')
def DeleteApplication(canvas,window,song_ids):
	if token:
		sp = spotipy.Spotify(auth=token)
		#if there are songs in the playlist remove them
		try:
			print(song_ids)
			sp.user_playlist_remove_all_occurrences_of_tracks(user=user_config['username'], playlist_id=user_config['playlist_id'], tracks=song_ids)
			#make the list null, actually clears the list
			song_ids[:] = []
		except:
				print("Nothing to Remove.")
	else:
		print("Can't get token for", username)

	
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
	button1 = tk.Button (window, text='Generate another list?',command= lambda: ListApplication(canvas,window,song_ids))
	button2 = tk.Button (window, text='Delete list.',command= lambda: DeleteApplication(canvas,window,song_ids))
	canvas.create_window(80, 400, window=button1)
	canvas.create_window(200, 400, window=button2)
	
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
				#artist_results = sp.search(q='artist:' + list[i][0] + ', album:' + list[i][1], type=type, limit=1)
				album_results = sp.search(q='album:' + list[i][1], type='album', limit=1)
				
				#get the first album uri
				album_id = album_results['albums']['items'][0]['uri']
				
				#get the individual tracks from the album
				tracks = sp.album_tracks(album_id)
				
				#pick a random number 1 to 12 to add to the playlist
				ranNum = rn.randint(1, 12)

				i = 1
				for track in tracks['items']:
					if ranNum == i:
						song_ids.append(track['id'])
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
	
	newList(win_canvas, window, song_ids)
	
	window.mainloop()



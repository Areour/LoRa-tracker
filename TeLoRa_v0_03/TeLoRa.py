#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Programme de teste de porté de trensmission LoRa
Ecrit par Areour mohamed Cherif
Date 	: 10/07/2018 
E-mail  : areour.mohamed@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import time
import serial
import urllib
import base64
import sqlite3
from Tkinter import *
from subprocess import call
from staticmap import StaticMap,Line,IconMarker
from math import radians, cos, sin, asin, sqrt
from tkMessageBox import askokcancel,showinfo,showwarning
import tkSimpleDialog
import paho.mqtt.client as mqtt # importation d un client mqtt

broker=""

#dimention de la carte
largeur = 640
hauteur = 480
zoom = 16

latitude  = 0.0
longitude = 0.0

# instance de l'objet Serial pour la gestion de la liaison série avec la carte
ser=serial.Serial()

#pour le débugage 
print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv[1]),int(sys.argv[2])

#création de la base de données pour le stockages des coordonnées.
coord = sqlite3.connect('BD/coord.db')
cursor = coord.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS coord(
     id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     e_lat REAL,
     e_long REAL,
     s_lat REAL,
     s_long REAL,
     distance REAL,
	 RSSI REAL,
	 SNR REAL
)
""")
# les fonctions callback
def on_log(client, userdata, level, buf):
	print "log: "+buf

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print "connexion OK"
		showinfo("Connexion","Connexion OK")
	else:
		print "Bad connexion code de retour", rc
		showwarning("Erreur","bad connexion")

def on_disconnect(client, userdata, flags, rc=0):
	print "code de resultat de deconnexion ", str(rc)

def on_message(client,userdata,msg):
	global coord
	topic=msg.topic
	m_decode=str(msg.payload.decode("utf-8"))
	print "message recu ", m_decode
	coord = m_decode.split(",")
	
	Latitude.configure(text=coord[0])
	Longitude.configure(text=coord[1])
	Altitude.configure(text=coord[3])
	Speed.configure(text=coord[2])

	show_image()

def get_connexion():
	def connexion():
		broker=ip_server.get()
		print "connexion au broker ",broker

		client.connect(broker) # connection au broker
		client.loop_start()

		#abonnement au broker 
		client.subscribe("Tracker/coord")
		
		conwin.destroy()

	conwin = Toplevel(fenetre)
	conwin.grab_set()

	ip_server = StringVar()
	var_port = IntVar()
		
	txt1 = Label(conwin, text ='Adresse du Server')
	txt2 = Label(conwin, text ='Port')
	entr1 = Entry(conwin,textvariable=ip_server)
	entr2 = Entry(conwin,textvariable=var_port)
	txt1.grid(row =0)
	txt2.grid(row =1)
	entr1.grid(row =0, column=1)
	entr2.grid(row =1, column=1)

	button_con = Button(conwin, text="Connexion",command=connexion)
   	button_con.grid(row=2, column=1)



def about():
	""" display an information window about the Software"""
	showinfo("About FANOS LoRa Mesure","FANOS LoRa Mesure v0.02\nDévloppeur : Areour Mohamed Cherif\nEmail : areour.mohamed@gmail.com")


def connect_hardware():
	"""connect to the arduino using serial"""	

	while 1:	
		try :
			ser.baudrate = int(sys.argv[2])
			ser.port = str(sys.argv[1])
			showinfo("Hardware Connexion","Connexion OK")
			break
		except ValueError:
			showinfo("Hardware Connexion","Port de liaison serie ou vitesse incorecte")
			break
	ser.open()	
	val()

def getDistance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1),float(lon2), float(lat2)])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return "%.6f" % km

def explorDB():
	call(["sqlitebrowser", "BD/coord.db"])

def val():   
	""" fonction who feed the database from the serial port, and display data in the UI"""

	if ser.is_open:
		ser.flush()
		x = ser.readline()
		x.lstrip("\\r\\n")
		print x
		lstData = x.split(",")
		
		if ( len(lstData) == 6):
			dist = getDistance(lstData[0],lstData[1],lstData[2],lstData[3])
			distenceLabel.configure(text=str(dist))

			data = {"e_lat":lstData[0],"e_long":lstData[1],"s_lat":lstData[2],"s_long":lstData[3], "distance" : dist, "RSSI":lstData[4],"SNR":lstData[5]}
			cursor.execute("""INSERT INTO coord(e_lat,e_long,s_lat,s_long,distance,RSSI,SNR) VALUES(:e_lat,:e_long,:s_lat,:s_long,:distance,:RSSI,:SNR)""", data)
			coord.commit()
	
			latLabel.configure(text=lstData[0])
			longLabel.configure(text=lstData[1])	
			rssiLabel.configure(text=lstData[4])
			snrLabel.configure(text=lstData[5])
			fenetre.after(100, val)
		else:
			pass
	else:
		pass
	
def getDistanceMax():
	""" fonction who search in the DB the max distance reached by the the signal"""
	
	m = StaticMap(largeur,hauteur, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')	
	cursor.execute("""SELECT max(distance) FROM coord """)
	dist = cursor.fetchone()
	print dist
	cursor.execute("""SELECT e_lat, e_long, s_lat, s_long, RSSI, SNR FROM coord WHERE distance=?""", dist)
	coord = cursor.fetchone() 
	print coord
	lat_E, long_E,lat_S, long_S =coord[0],coord[1],coord[2],coord[3] 
	
	m.add_line(Line(((long_S, lat_S) , (long_E, lat_E)), 'blue', 3))
	icon_flag_1 = IconMarker((long_E, lat_E), 'icon/icon-flag.png', 12, 32)	
	m.add_marker(icon_flag_1)		
	icon_flag_2 = IconMarker((long_S, lat_S), 'icon/icon-flag.png', 12, 32)	
	m.add_marker(icon_flag_2)	
	
	global image
	image = m.render()
	image.save('map/DistanceMaxMap.png')	
 
	image = PhotoImage(file='map/DistanceMaxMap.png')
	canvas.create_image(0,0,image=image,anchor=NW)
	
	latLabel.configure(text=coord[0])
	longLabel.configure(text=coord[1])	
	distenceLabel.configure(text=dist[0])
	rssiLabel.configure(text=coord[4])
	snrLabel.configure(text=coord[5])

def getRSSIMax():
	""" fonction who search in the DB the best signal reception and despaly it in the map"""

	m = StaticMap(largeur,hauteur, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')	
	cursor.execute("""SELECT max(RSSI) FROM coord """)
	rssi = cursor.fetchone()
	print rssi
	cursor.execute("""SELECT e_lat, e_long, s_lat, s_long, distance, SNR FROM coord WHERE RSSI=?""", rssi)
	coord = cursor.fetchone() #getGPS()
	print coord
	
	lat_E, long_E,lat_S, long_S =coord[0],coord[1],coord[2],coord[3] 
	m.add_line(Line(((long_S, lat_S) , (long_E, lat_E)), 'blue', 3))

	
	icon_flag_1 = IconMarker((long_E, lat_E), 'icon/icon-flag.png', 12, 32)	
	m.add_marker(icon_flag_1)		
	icon_flag_2 = IconMarker((long_S, lat_S), 'icon/icon-flag.png', 12, 32)	
	m.add_marker(icon_flag_2)	

	global image
	image = m.render()
	image.save('map/RSSIMaxMap.png')	
	image = PhotoImage(file='map/RSSIMaxMap.png')
	canvas.create_image(0,0,image=image,anchor=NW)
	
	latLabel.configure(text=coord[0])
	longLabel.configure(text=coord[1])	
	distenceLabel.configure(text=coord[4])

	rssiLabel.configure(text=coord[4])
	snrLabel.configure(text=coord[5])

def global_data():
	""" fonction who search in the DB the distance reached by the the signal"""

	m = StaticMap(largeur,hauteur, url_template='http://b.tile.osm.org/{z}/{x}/{y}.png')	
	cursor.execute("SELECT e_lat, e_long FROM coord")
	rows = cursor.fetchall()

	for row in rows:
		print row
		icon_flag = IconMarker((row[1],row[0]), 'icon/icon-flag.png', 12, 32)	
		m.add_marker(icon_flag)

	global image		
	image = m.render()
	image.save('map/GlobalMap.png')
	image = PhotoImage(file='map/GlobalMap.png')
	canvas.create_image(0,0,image=image,anchor=NW)

def getmap(lat_server, lon_server, lat_client, lon_client, largeur, hauteur, zoom):
	m = StaticMap(largeur,hauteur, url_template='http://b.tile.osm.org/{z}/{x}/{y}.png')
	
	m.add_line(Line(((lon_server, lat_server) , (lon_client, lat_client)), 'blue', 3))

	icon_flag_1 = IconMarker((lon_client, lat_client), 'icon/icon-flag.png', 12, 32)	
	m.add_marker(icon_flag_1)		
	icon_flag_2 = IconMarker((lon_server, lat_server), 'icon/icon-flag.png', 12, 32)	
	m.add_marker(icon_flag_2)	

	image = m.render()
	image.save('map/map.png')

def get_image():
	id = cursor.lastrowid
	print('dernier id: %d' % id)

	cursor.execute("""SELECT e_lat, e_long, s_lat, s_long FROM coord WHERE id=?""", (id,))
	coord = cursor.fetchone() #getGPS()

	lat_E, long_E,lat_S, long_S =coord[0],coord[1],coord[2],coord[3] 
	getmap(lat_S, long_S,lat_E, long_E, largeur, hauteur, zoom)	
	image = PhotoImage(file='map/map.png')
	return image

def show_map():
	global mapimage
	mapimage = get_image()
	canvas.create_image(0,0,image=mapimage,anchor=NW)

def arret():
	ser.close()
	coord.close()
	fenetre.quit()

def deconect():
	ser.close()
	showinfo("Hardware Connexion","Deconnexion OK")

	
def donothing():
	filewin = Toplevel(fenetre)
	button = Button(filewin, text="Do nothing button",command=filewin.destroy)
	button.pack()

client = mqtt.Client("moh_1")

#lien et utilisation des fonction callback
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_log = on_log
client.on_message=on_message

# GUI
fenetre = Tk()
fenetre.iconbitmap(bitmap = "@logo_oha.xbm")
fenetre.resizable(width=False, height=False)
fenetre['bg']='#222735'
fenetre.title("FANOS LoRa Mesure")

menubar = Menu(fenetre)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Connexion", command=connect_hardware)
filemenu.add_command(label="Carte", command=show_map)

filemenu.add_separator()

filemenu.add_command(label="Deconnexion", command=deconect)
filemenu.add_command(label="Exit", command=arret)
menubar.add_cascade(label="File", menu=filemenu)

toolmenu = Menu(menubar, tearoff=0)
toolmenu.add_command(label="Max Distence", command=getDistanceMax)
toolmenu.add_command(label="Best Signal", command=getRSSIMax)
toolmenu.add_command(label="Global Map", command=global_data)

toolmenu.add_separator()

toolmenu.add_command(label="Explore DB", command=explorDB)
toolmenu.add_command(label="Rapport", command=donothing)
menubar.add_cascade(label="Tools", menu=toolmenu)


helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help", command=donothing)
helpmenu.add_command(label="About...", command=about)
menubar.add_cascade(label="Help", menu=helpmenu)

fenetre.config(menu=menubar)

# frame 1
Frame1 = Frame(fenetre, borderwidth=2, relief=GROOVE,bg='#222735')
Frame1.pack(side=LEFT, padx=5, pady=5)

# frame 2
Frame2 = Frame(fenetre, bg="#222735", borderwidth=2, relief=GROOVE)
Frame2.pack(side=TOP, padx=5, pady=5)

latFram = LabelFrame(Frame2,bg="#222735",fg="#00d0c7", text="Latitude ", padx=5,pady=5)
latFram.pack(fill="both", expand="yes",padx=5,pady=5)
latLabel = Label(latFram,bg="#222735",fg="#00d0c7", text="00000000")
latLabel.pack()

longFram = LabelFrame(Frame2,bg="#222735",fg="#00d0c7", text="Longitude ", padx=5,pady=5)
longFram.pack(fill="both", expand="yes",padx=5,pady=5)
longLabel = Label(longFram,bg="#222735",fg="#00d0c7", text="00000000")
longLabel.pack()

distenceFram = LabelFrame(Frame2,bg="#222735",fg="#00d0c7", text="Distance en Km ", padx=5,pady=5)
distenceFram.pack(fill="both", expand="yes",padx=5,pady=5)
distenceLabel = Label(distenceFram,bg="#222735",fg="#00d0c7", text="00000000")
distenceLabel.pack()

rssiFram = LabelFrame(Frame2,bg="#222735",fg="#00d0c7", text="RSSI ", padx=5,pady=5)
rssiFram.pack(fill="both", expand="yes",padx=5,pady=5)
rssiLabel = Label(rssiFram,bg="#222735",fg="#00d0c7", text="00000000")
rssiLabel.pack()

snrFram = LabelFrame(Frame2,bg="#222735",fg="#00d0c7", text="SNR ", padx=5,pady=5)
snrFram.pack(fill="both", expand="yes",padx=5,pady=5)
snrLabel = Label(snrFram,bg="#222735",fg="#00d0c7", text="00000000")
snrLabel.pack()

image_logo= PhotoImage(file="logo_test_anders_final.png")

canvas = Canvas(Frame1, width=largeur, height=hauteur,background='#222735')
canvas.pack(padx=10, pady=10)
carte=canvas.create_image(320,240,image=image_logo,anchor=CENTER)

fenetre.after(100, val)
fenetre.mainloop()

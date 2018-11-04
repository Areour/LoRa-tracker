# -*- coding: utf-8 -*-

"""
Gauge développé pour la librairie Tkinter
Ecrit par Areour mohamed Cherif
Date : 10/01/2016
E-mail : openhardwaredz@gmail.com

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

import Tkinter
import time
from random import randrange

class Mod_gauge(Tkinter.Canvas):
    def __init__(self, parent, titre = "Gauge", background="#222735",foreground="#00d0c7", max = 127, min = 0):
        global valeur, root, arc, text, H, W, coord1, coord2

        self.titre = titre
        self.back  = background
        self.fore  = foreground
        self.max   = max
        self.min   = min
        root = parent
        valeur = 0.
        H = 145
        W = 130
        coord1 = (H-120), (W-107), (H-40), (W-25)
        coord2 = (H-135), (W-120), (H-25), (W-10)

        Tkinter.Canvas.__init__(self, bg=self.back, height=H, width=W)

        # Dessin de la gauge
        self.create_oval(coord1, fill=self.back, outline=self.back)
        #self.create_oval(coord1, outline="#3399FF")

        arc = self.create_arc(coord2, start=-90, extent = valeur, fill=self.fore,outline=self.fore)
        self.create_oval(coord2, outline=self.fore)
        text = self.create_text(65, 65, text=int(valeur), font="Arial 36 italic", fill=self.fore)
        legende = self.create_text(65, 130, text= self.titre, font="Arial 16 ", fill=self.fore)
        
        parent.update()

    def reset(self):
        global root, arc, text
        parent = root
        # Dessin de la gauge
        self.create_oval(coord1, fill=self.back, outline=self.back)
        #self.create_oval(coord1, outline="#3399FF")

        arc = self.create_arc(coord2, start=-90, extent = valeur, fill=self.fore,outline=self.fore)
        self.create_oval(coord2, outline=self.fore)
        text = self.create_text(65, 65, text=int(valeur), font="Arial 36 italic", fill=self.fore)
        legende = self.create_text(65, 130, text= self.titre, font="Arial 16 ", fill=self.fore)
        
    def SetValue(self, entree):
        global valeur, root, arc, text
        parent = root

        consigne =(entree*100)/self.max

        while (int(valeur) != int(consigne*3.6)):

            if (int(valeur) < int(consigne*3.6)):
                valeur = valeur + 1
                txt_consigne = valeur/3.6
                self.delete(arc)
                self.delete(text)
                arc = self.create_arc(coord2, start=-90, extent=-valeur, fill=self.fore)
                self.create_oval(coord2, outline=self.fore)
                self.create_oval(coord1, fill=self.back, outline=self.fore)
                self.create_oval(coord1, outline=self.fore)
                text = self.create_text(65, 65, text=int(txt_consigne), font="Arial 36 italic", fill=self.fore)
                parent.update()
                #time.sleep(0.00002)    #Définie l'inertie de la gauge

            elif( int(valeur) > int(consigne*3.6)):
                valeur = valeur - 1
                txt_consigne = valeur/3.6
                self.delete(arc)
                self.delete(text)
                arc = self.create_arc(coord2, start=-90, extent=-valeur, fill=self.fore)
                self.create_oval(coord2, outline=self.fore)
                self.create_oval(coord1, fill=self.back, outline=self.fore)
                self.create_oval(coord1, outline=self.fore)
                text = self.create_text(65, 65, text=int(txt_consigne), font="Arial 36 italic", fill=self.fore)
                parent.update()
                #time.sleep(0.00002)    #Définie l'inertie de la gauge
                
            else :
                txt_consigne = valeur/3.6
                self.delete(arc)
                self.delete(text)
                arc = self.create_arc(coord2, start=-90, extent=-valeur, fill=self.fore)
                self.create_oval(coord2, outline=self.fore)
                self.create_oval(coord1, fill=self.back, outline=self.fore)
                self.create_oval(coord1, outline=self.fore)
                text = self.create_text(65, 65, text=int(txt_consigne), font="Arial 36 italic", fill=self.fore)
                parent.update()
                #time.sleep(0.00002)    #Définie l'inertie de la gauge

def val():
    for i in range(1,10):
        gauge.SetValue(randrange(100))

if __name__=="__main__":
    app=Tkinter.Tk()
    gauge=Mod_gauge(app)
    gauge.pack()
    val()
    
    app.mainloop()


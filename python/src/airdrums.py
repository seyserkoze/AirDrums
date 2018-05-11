from Tkinter import *
from eventBasedAnimationClass import EventBasedAnimationClass
import random
import copy
import os
import time
import functools
from communication import Communication
from multiprocessing import Process, Pipe
import socket
import thread

class AirDrums(EventBasedAnimationClass):
	def __init__(self):
		self.width = 1000
		self.height = 750
		super(AirDrums,self).__init__(self.width,self.height)

	def initAnimation(self):
		thread.start_new_thread(os.system, ("python connection_stuff.py",))
		time.sleep(1)
		canvas = self.canvas
		self.root.bind("<Motion>", lambda event: self.onMouseMotion(event))

		self.initScreenVals()
		self.initImages()
		self.resetDrumConfig()

		self.posX = "NA"
		self.posY = "NA"
		self.posZ = "NA"

		self.finalDrumList= ["Empty" for i in xrange(6)]
		self.sendDrumList = ["em" for i in xrange(6)]

		self.initButtonActions()

		try:
			self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connection.connect(('localhost', 50000))	
			# print "Made connection"
		except:
			print "no socket found"
		
		# self.connection.sendall('READ')
		# self.connection.sendall("hitoms lotoms crash ride snare hihats")

	#booleans for screen changes
	def initScreenVals(self):
		self.startScreen = True
		self.helpScreen = False
		self.selectSnares = False
		self.selectLoToms = False
		self.selectHiToms = False
		self.selectHiHats = False
		self.selectRide = False
		self.selectCrash = False
		self.testingScreen = False
		self.finalDrumScreen = False
		self.aboutScreen = False

	#initalizing all photo assets
	def initImages(self):
		self.logo = PhotoImage(file="logo.gif")
		self.start = PhotoImage(file="start.gif")
		self.test = PhotoImage(file="test.gif")
		self.about = PhotoImage(file="about.gif")
		self.info = PhotoImage(file="info.gif")
		self.back = PhotoImage(file="back.gif")
		self.done = PhotoImage(file="done.gif")

	#colors for drums etc etc
	def resetDrumConfig(self):
		self.color = ["white" for i in xrange(6)]
		self.currSelected = set()

	def initButtonActions(self):
		self.canvas.tag_bind("circle0", "<Button>", lambda event:  self.printCircle(0))
		self.canvas.tag_bind("circle1", "<Button>", lambda event:  self.printCircle(1))
		self.canvas.tag_bind("circle2", "<Button>", lambda event:  self.printCircle(2))
		self.canvas.tag_bind("circle3", "<Button>", lambda event:  self.printCircle(3))
		self.canvas.tag_bind("circle4", "<Button>", lambda event:  self.printCircle(4))
		self.canvas.tag_bind("circle5", "<Button>", lambda event:  self.printCircle(5))

	def onMousePressed(self, event):
		(self.x, self.y) = (event.x, event.y)

		if (self.startScreen):

			if (self.between(180, 400, 320, 465)): 
				self.startScreen = False
				self.selectSnares = True

			if (self.between(180, 500, 320, 565)): 
				self.startScreen = False
				self.testingScreen = True

			if (self.between(180, 600, 320, 665)): 
				self.startScreen = False
				self.aboutScreen = True

		if (self.aboutScreen):

			if (self.between(143, 122, 188, 173)):
				self.startScreen = True
				self.aboutScreen = False

		if (self.testingScreen):
			if (self.between(143, 122, 188, 173)):
				self.startScreen = True
				self.testingScreen = False
				self.connection.sendall('BACK')


		if (self.selectSnares): 
			if (self.between(891, 664, 938, 710)):
				for s in self.currSelected:
					self.finalDrumList[s] = "snare"
					self.sendDrumList[s] = "sn"

				print self.finalDrumList
				self.resetDrumConfig()
				self.selectSnares = False
				self.selectCrash = True

		if (self.selectCrash):
			if (self.between(891, 604, 938, 650)):
				for s in self.currSelected:
					self.finalDrumList[s] = "crash"
					self.sendDrumList[s] = "cr"

				print self.finalDrumList
				self.selectCrash = False
				self.selectLoToms = True
				self.resetDrumConfig()

		if (self.selectLoToms):
			if (self.between(891, 664, 938, 710)):
				for s in self.currSelected:

					self.finalDrumList[s] = "lotoms"
					self.sendDrumList[s] = "lt"

				print self.finalDrumList
				self.selectLoToms = False
				self.selectHiToms = True
				self.resetDrumConfig()

		if (self.selectHiToms):

			if (self.between(891, 604, 938, 650)):
				for s in self.currSelected:

					self.finalDrumList[s] = "hitoms"
					self.sendDrumList[s] = "ht"

				print self.finalDrumList
				self.selectHiToms = False
				self.selectRide = True
				self.resetDrumConfig()

		if (self.selectRide):
			if (self.between(891, 664, 938, 710)):
				for s in self.currSelected:

					self.finalDrumList[s] = "ride"
					self.sendDrumList[s] = "ri"

				print self.finalDrumList
				self.selectRide = False
				self.selectHiHats = True
				self.resetDrumConfig()

		if (self.selectHiHats):
			if (self.between(891, 604, 938, 650)):
				for s in self.currSelected:

					self.finalDrumList[s] = "hihats"
					self.sendDrumList[s] = "hh"

				print self.finalDrumList
				self.selectHiHats = False
				self.finalDrumScreen = True
				self.connection.sendall('READ')
				self.connection.sendall(' '.join(self.sendDrumList))
				self.resetDrumConfig()

		if (self.finalDrumScreen):
			if (self.between(891, 664, 938, 710)):
				self.connection.sendall("SHUT")
				self.root.destroy()


	def onMouseMotion(self, event):
		pass

	def between(self, x, y, x2, y2):
		return (self.x <= x2 and self.x >= x and self.y >= y and self.y <= y2)

	def onKeyPressed(self, event):
		pass

	def draw_circle(self, xgap, ygap, yoffset, xoffset, i, r, **kwargs):			
			
		self.canvas.create_oval(self.width/6+(i%3)*xgap+xoffset-r, self.height/5+yoffset+(i/3)*(ygap)-r, 
			self.width/6+(i%3)*xgap+xoffset+r, self.height/5+yoffset+(i/3)*(ygap)+r,
			 outline="black", width="3", tags="circle"+str(i), fill=self.color[i])
		return

	def draw_circle_notag(self, xgap, ygap, yoffset, xoffset, i, r, color):			
			
		self.canvas.create_oval(self.width/6+(i%3)*xgap+xoffset-r, self.height/5+yoffset+(i/3)*(ygap)-r, 
			self.width/6+(i%3)*xgap+xoffset+r, self.height/5+yoffset+(i/3)*(ygap)+r,
			 outline="black", width="3", fill=color)

		return

	def draw_start(self):
		image= self.logo
		self.canvas.data["image"]=image
		image = self.canvas.data["image"]
		self.canvas.create_image(3*self.width/4,3*self.height/4, image=image)


		image= self.start
		self.canvas.data["image"]=image
		image = self.canvas.data["image"]
		self.canvas.create_image(self.width/4,250+self.height/4, image=image)

		image= self.test
		self.canvas.data["image"]=image
		image = self.canvas.data["image"]
		self.canvas.create_image(self.width/4,250+self.height/4 + 100, image=image)

		image= self.about
		self.canvas.data["image"]=image
		image = self.canvas.data["image"]
		self.canvas.create_image(self.width/4,250+self.height/4 + 200, image=image)

	def printCircle(self, arg):
		self.color[arg] = "#FFC630"
		self.currSelected.add(arg)
		
	def drawDrumSetup(self):
		yoffset = 75
		xoffset = 120
		xgap = (self.width/4)
		ygap = (self.height/3)

		self.draw_circle(xgap, ygap, xoffset, yoffset, 0, self.width/9)			
		self.draw_circle(xgap, ygap, xoffset, yoffset, 1, self.width/9)
		self.draw_circle(xgap, ygap, xoffset, yoffset, 2, self.width/9)
		self.draw_circle(xgap, ygap, xoffset, yoffset, 3, self.width/9)
		self.draw_circle(xgap, ygap, xoffset, yoffset, 4, self.width/9)
		self.draw_circle(xgap, ygap, xoffset, yoffset, 5, self.width/9)

	def redrawAll(self):
		# print "Redrawing"
		canvas=self.canvas
		canvas.delete(ALL)

		if (self.startScreen): self.draw_start()
			
		if (self.aboutScreen):
			info = "AirDrums is a project with smart drumsticks that allow you to turn air-drumming \ninto percussion music, in real-time with low latency complete with an iOS app\n to allow you to choose and refine your drum kit. The drumsticks will also give \nhaptic feedback to help determine the tempo the user is playing at. \n\nCreated by Avishek Ganguli, Samuel Lee & Shaurya Khazanchi"
			self.canvas.create_text(2*self.width/4,self.height/2, text= info, font="Helvetica 20" )

			image= self.back
			self.canvas.data["image"]=image
			image = self.canvas.data["image"]
			self.canvas.create_image(self.width/6,self.height/5,image=image)
		
		if (self.testingScreen):
			self.connection.sendall("TEST")
			data = self.connection.recv(20)

			if data:
				self.posX, self.posY, self.posZ = data.split(" ")

			self.canvas.create_text(2*self.width/4,self.height/2, text= "PosX:", font="Helvetica 20" )
			self.canvas.create_text(2*self.width/4+100,self.height/2, text= self.posX, font="Helvetica 20 bold")
			self.canvas.create_text(2*self.width/4,self.height/2+20, text= "PosY:", font="Helvetica 20" )
			self.canvas.create_text(2*self.width/4+100,self.height/2+20, text= self.posY, font="Helvetica 20 bold")
			self.canvas.create_text(2*self.width/4,self.height/2+40, text= "PosZ:", font="Helvetica 20" )
			self.canvas.create_text(2*self.width/4+100,self.height/2+40, text= self.posZ, font="Helvetica 20 bold")

			image= self.back
			self.canvas.data["image"]=image
			image = self.canvas.data["image"]
			self.canvas.create_image(self.width/6,self.height/5,image=image)


		if (self.selectSnares):

			self.canvas.create_text(self.width/2,self.height/8,text="Choose Snares", font= "Helvetica 28 bold")

			image= self.done
			self.canvas.data["image"]=image
			image = self.canvas.data["image"]
			self.canvas.create_image(5.5*self.width/6,4.6*self.height/5,image=image)

			self.drawDrumSetup()

		if (self.selectCrash):

			self.canvas.create_text(self.width/2,self.height/8,text="Choose Crash Cymbals", font= "Helvetica 28 bold")

			image= self.done
			self.canvas.data["image"]=image
			image = self.canvas.data["image"]
			self.canvas.create_image(5.5*self.width/6,4.6*self.height/5-60,image=image)

			self.drawDrumSetup()


		if (self.selectLoToms):

			self.canvas.create_text(self.width/2,self.height/8,text="Choose Lo-Toms", font= "Helvetica 28 bold")
		
			image= self.done
			self.canvas.data["image"]=image
			image = self.canvas.data["image"]
			self.canvas.create_image(5.5*self.width/6,4.6*self.height/5,image=image)

			self.drawDrumSetup()


		if (self.selectHiToms):

			self.canvas.create_text(self.width/2,self.height/8,text="Choose Hi-Toms", font= "Helvetica 28 bold")

			image= self.done
			self.canvas.data["image"]=image
			image = self.canvas.data["image"]
			self.canvas.create_image(5.5*self.width/6,4.6*self.height/5-60,image=image)

			self.drawDrumSetup()


		if (self.selectRide):

			self.canvas.create_text(self.width/2,self.height/8,text="Choose Rides", font= "Helvetica 28 bold")
		
			image= self.done
			self.canvas.data["image"]=image
			image = self.canvas.data["image"]
			self.canvas.create_image(5.5*self.width/6,4.6*self.height/5,image=image)

			self.drawDrumSetup()

		if (self.selectHiHats):

			self.canvas.create_text(self.width/2,self.height/8,text="Choose Hi-Hats", font= "Helvetica 28 bold")

			image= self.done
			self.canvas.data["image"]=image
			image = self.canvas.data["image"]
			self.canvas.create_image(5.5*self.width/6,4.6*self.height/5-60,image=image)

			self.drawDrumSetup()

		if (self.finalDrumScreen):
			self.connection.sendall("DRUM")

			self.canvas.create_text(self.width/2,self.height/8,text="Your Custom Drum Set", font= "Helvetica 28 bold")

			yoffset = 75
			xoffset = 120
			xgap = (self.width/4)
			ygap = (self.height/3)


			###############################
			# CODE FOR SECOND DRUM STICK BEGINS HERE
			##############################

			#what's different is that now you need to send two characters
			#so 45 = drum 4 hit by stick 1 and 5 hit by stick 2 
			#in case of nothing played send a 66 or 77 or any integer
			# as a string that has a value about 55, make sure not 
			# to send a -1 for no drum hit

			drumHit = self.connection.recv(2)
			stick1 = drumHit[0]
			stick2 = drumHit[1]

			if (self.finalDrumList[0]): 
				color0 = "white"
				if (stick1 == "0"):
					color0 = "red"
				if (stick2 == "0"):
					color0 = "blue"
				self.draw_circle_notag(xgap, ygap, xoffset, yoffset, 0, self.width/9, color0)	

			if (self.finalDrumList[1]): 
				color1 = "white"
				if (stick1 == "1"):
					color1 = "red"
				if (stick2 == "1"):
					color1 = "blue"
				self.draw_circle_notag(xgap, ygap, xoffset, yoffset, 1, self.width/9, color1)
			if (self.finalDrumList[2]): 
				color2 = "white"
				if (stick1 == "2"):
					color2 = "red"
				if (stick2 == "2"):
					color2 = "blue"
				self.draw_circle_notag(xgap, ygap, xoffset, yoffset, 2, self.width/9, color2)
			if (self.finalDrumList[3]): 
				color3 = "white"
				if (stick1 == "3"):
					color3 = "red"
				if (stick2 == "3"):
					color3 = "blue"
				self.draw_circle_notag(xgap, ygap, xoffset, yoffset, 3, self.width/9, color3)
			if (self.finalDrumList[4]): 
				color4 = "white"
				if (stick1 == "4"):
					color4 = "red"
				if (stick2 == "4"):
					color4 = "blue"
				self.draw_circle_notag(xgap, ygap, xoffset, yoffset, 4, self.width/9, color4)
			if (self.finalDrumList[5]): 
				color5 = "white"
				if (stick1 == "5"):
					color5 = "red"
				if (stick2 == "5"):
					color5 = "blue"
				self.draw_circle_notag(xgap, ygap, xoffset, yoffset, 5, self.width/9, color5)

			self.canvas.create_text(self.width/5+38, self.height/3+25, text= self.finalDrumList[0], font= "Helvetica 24")
			self.canvas.create_text(self.width/5+38+xgap, self.height/3+25, text= self.finalDrumList[1], font= "Helvetica 24")
			self.canvas.create_text(self.width/5+38+2*xgap, self.height/3+25, text= self.finalDrumList[2], font= "Helvetica 24")
			self.canvas.create_text(self.width/5+38, self.height/3+25+ygap, text= self.finalDrumList[3], font= "Helvetica 24")
			self.canvas.create_text(self.width/5+38+xgap, self.height/3+25+ygap, text= self.finalDrumList[4], font= "Helvetica 24")
			self.canvas.create_text(self.width/5+38+2*xgap, self.height/3+25+ygap, text= self.finalDrumList[5], font= "Helvetica 24")

			image= self.done
			self.canvas.data["image"]=image
			image = self.canvas.data["image"]
			self.canvas.create_image(5.5*self.width/6,4.6*self.height/5,image=image)

AirDrums().run()

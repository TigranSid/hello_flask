# ETA Module
#Google API Key: AIzaSyB-eAzkjdfmO0IbI22MYUGSuMFSiImiueA

import json
from transaction import Transaction

class Eta: # Définition de notre classe Eta
	"""
	Un Eta se définit par  :
	- un ID unique
	- une origine (adresse, point GPS à définir)
	- une destination (adresse / point GPS à définir)
	- un mode de déplacement (car, truck, bike, foot etc.)
	- Une liste de distances (une par fournisseur de données)
	- Une liste de temps de déplacement (un par fournisseur de données)
	"""

	def __init__(self, origin, destination, mode): # Notre méthode constructeur
		"""Pour l'instant, on ne va définir qu'un seul attribut"""
		self.id = 1
		self.origin = origin
		self.destination = destination
		self.mode = mode
		self.distance = -1
		self.duration = -1
		self.calculate(self.origin, self.destination, self.mode)

	def calculate(self, origin, destination, mode):
		"""Méthode pour lancer la transaction!!"""
		trans = Transaction(origin, destination, mode, "google")
		self.distance = trans.distance
		self.duration = trans.duration
		

	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, 
			sort_keys=True, indent=4)
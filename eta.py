#ETA Module
import json
from transaction import GoogleTransaction, HereTransaction#, GoogleGeocodeTransaction
from threading import Thread

class Eta: # Définition de notre classe Eta
	"""
	Un Eta se définit par  :
	- un ID unique
	- une adresse d'origine
	- une adresse de destination 
	- un mode de déplacement (car, truck, bike, foot etc.)
	- Une liste de distances (une par fournisseur de données)
	- Une liste de temps de déplacement (un par fournisseur de données)
	"""

postgres://ojikxgsmfauuex:ecd1007073274a10c395eafe4b20ae8ae5662f65db43162452bbe7110d189654@ec2-107-21-201-57.compute-1.amazonaws.com:5432/de8isgs8585crl


	def __init__(self, origin, destination, mode):
		"""
		On définit les attributs de notre objet Eta.
		transactions[] est le tableau qui contiendra les infos de chaque source de données.
		On lance le calcul des ETAs auprès des sources. 
		"""
		self.id = 1
		self.origin = origin
		self.destination = destination
		self.mode = mode
		self.transactions = []

	def calculate(self):
		"""
		Méthode pour lancer les threads de calcul auprès des sources.
		Les appels sont parallélisés grâce à des Threads.
		"""
		threads = []
		t = Thread(target=GoogleTransaction, args=(self.transactions, self.origin, self.destination, self.mode))
		threads.append(t)
		t = Thread(target=HereTransaction, args=(self.transactions, self.origin, self.destination, self.mode))
		threads.append(t)
		
		"""
		Approche GMAPS Geocoding + Matrix éliminée car moins efficace que l'approche String + Matrix
		t = Thread(target=GoogleGeocodeTransaction, args=(self.transactions, origin, destination, mode))
		threads.append(t)
		"""

		[ t.start() for t in threads ]
		[ t.join() for t in threads ]

	def to_JSON(self):
		"""
		Une méthode axée debug pour renvoyer l'objet Eta sous forme de JSON.
		"""
		return json.dumps(self, default=lambda o: o.__dict__, 
			sort_keys=False, indent=4)
# ETA Module
#Google API Key: AIzaSyB-eAzkjdfmO0IbI22MYUGSuMFSiImiueA
# API Google 2 AIzaSyBWa0Sqp6jFlbTL9_LcRqy7tSuBzdaFAos
import requests
import json
from json import JSONDecoder
from threading import Thread

class DictQuery(dict):
    def get(self, path, default = None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [ v.get(key, default) if v else None for v in val]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break;

        return val

class Transaction: # Définition de notre classe Eta
	"""
	Une transaction se définit par  :
	- une cible (google, here etc.)
	- une origine (adresse, point GPS à définir)
	- une destination (adresse / point GPS à définir)
	- un mode de déplacement (car, truck, bike, foot etc.)
	- Une distance renvoyée par la cible
	- Une durée renvoyée par la cible
	"""

	def __init__(self, origin, destination, mode): # Notre méthode constructeur
		"""Pour l'instant, on ne va définir qu'un seul attribut"""
		self.origin = origin
		self.destination = destination
		self.mode = mode
		self.distance = -1
		self.duration = -1
		
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, 
			sort_keys=True, indent=4)

	def get_duration(self):
		return self.duration

	def get_distance(self):
		return self.distance

class GoogleTransaction(Transaction):
	"""Objet de transaction Google. 
	"""
	def __init__(self, origin, destination, mode): # Notre méthode constructeur
		Transaction.__init__(self, origin, destination, mode)
		self.url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric"
		self.key = "AIzaSyB-eAzkjdfmO0IbI22MYUGSuMFSiImiueA"
		r = requests.get(
			self.url
			+"&origins="+self.origin
			+"&destinations="+self.destination
			+"&key="+self.key
			).json()		
		self.distance= str( DictQuery(r['rows'][0]).get('elements/distance/value')[0] )
		self.duration= str( DictQuery(r['rows'][0]).get('elements/duration/value')[0] )
		print("Google:\tDistance:"+self.distance+"\tDuration:"+self.duration)

class HereTransaction(Transaction):
	
	def geocode(self,cible, address):
		r = requests.get(
			"https://geocoder.cit.api.here.com/6.2/geocode.json"
			+"?app_id="+self.app_id
			+"&app_code="+self.app_code
			+"&searchtext="+address
			+"&locationattributes=none&addressattributes=none&responseattributes=none"
			).json()
		lat = DictQuery(DictQuery(r).get('Response/View/Result')[0][0]).get('Location/NavigationPosition/Latitude')[0]
		lng = DictQuery(DictQuery(r).get('Response/View/Result')[0][0]).get('Location/NavigationPosition/Longitude')[0]
		if cible == 'o':
			self.origin = str(lat) + ',' + str(lng)
		elif cible == 'd':
			self.destination = str(lat) + ',' + str(lng)

	"""Objet de transaction HERE. 
	"""
	def __init__(self, origin, destination, mode): # Notre méthode constructeur

		Transaction.__init__(self, origin, destination, mode)
		self.url = "https://matrix.route.cit.api.here.com/routing/7.2/calculatematrix.json"
		self.key = "AIzaSyB-eAzkjdfmO0IbI22MYUGSuMFSiImiueA"
		self.app_id = "IjBDAJJhIEa6eu2t8t2v"
		self.app_code = "cjhvzmqWsSm0vQ859aF_YA"

		# On lance 2 Threads pour geocoder en parallèle
		#self.origin = self.geocode(origin)
		#self.destination = self.geocode(destination)
		threads = []
		t = Thread(target=self.geocode, args=('o', origin))
		threads.append(t)
		t = Thread(target=self.geocode, args=('d', destination))
		threads.append(t)
		[ t.start() for t in threads ]
		[ t.join() for t in threads ]

		#Calcul de la distance et de la durée
		r = requests.get(
			self.url
			+"?app_id="+self.app_id
			+"&app_code="+self.app_code
			+"&start0="+self.origin
			+"&destination0="+self.destination
			+"&mode=fastest;"+self.mode+";traffic:disabled"
			+"&summaryAttributes=tt,di"
			).json()

		self.distance = str( DictQuery(r).get('response/matrixEntry/summary/distance')[0] )
		self.duration = str( DictQuery(r).get('response/matrixEntry/summary/travelTime')[0] )
		print("HERE:\tDistance:"+self.distance+"\tDuration:"+self.duration)
















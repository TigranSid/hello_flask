# ETA Module
#Google API Key: AIzaSyB-eAzkjdfmO0IbI22MYUGSuMFSiImiueA
# API Google 2 AIzaSyBWa0Sqp6jFlbTL9_LcRqy7tSuBzdaFAos
import requests
import json

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

	def __init__(self, origin, destination, mode, source): # Notre méthode constructeur
		"""Pour l'instant, on ne va définir qu'un seul attribut"""
		self.origin = origin
		self.destination = destination
		self.mode = mode
		self.source = source
		self.url = ""
		self.key = ""
		self.set_url_key(self.source)
		if self.url == "" or self.key == "":
			raise Exception({"code": "Undefined Source",
                        "description":
                            "Couldn't load key/url from source."}, 401)
		
		self.distance = -1
		self.duration = -1
		self.set_distance_duration(self.url, self.key, self.origin, self.destination, self.mode)
		if self.distance == -1 or self.duration == -1:
			raise Exception({"code": "Error in Distance/Duration Calculation",
                        "description":
                            "Couldn't calculate distance nor duration"}, 401)
		

	def set_url_key(self, source):
		"""Méthode pour récupérer un ID unique de requête ETA"""
		switcher_url = {
		"google": "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric",
		"here": ""
		}
		self.url = switcher_url.get(source, "")

		switcher_key = {
		#"google": "AIzaSyB-AIzaSyBWa0Sqp6jFlbTL9_LcRqy7tSuBzdaFAos",
		"google": "AIzaSyB-eAzkjdfmO0IbI22MYUGSuMFSiImiueA",
		"here": ""
		}
		self.key = switcher_key.get(source, "")

	def set_distance_duration(self, url, key, origin, destination, mode):
		"""On fait l'appel"""
		r = requests.get(url+"&origins="+origin+"&destinations="+destination+"&key="+key).json()
		for item in r['rows']:
			self.distance= DictQuery(item).get('elements/distance/value')[0]
		for item in r['rows']:
			self.duration= DictQuery(item).get('elements/duration/value')[0]
		
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, 
			sort_keys=True, indent=4)
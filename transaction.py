#Transaction Module
import requests
import json
from json import JSONDecoder
from threading import Thread
from datetime import datetime
import re

# Constantes
GMAP_KEY = "AIzaSyB-eAzkjdfmO0IbI22MYUGSuMFSiImiueA"
GMAP_URL_MATRIX = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric"
GMAP_URL_GEOCODE = "https://maps.googleapis.com/maps/api/geocode/json"
HERE_APP_CODE = "cjhvzmqWsSm0vQ859aF_YA"
HERE_APP_ID = "IjBDAJJhIEa6eu2t8t2v"
HERE_URL_MATRIX = "https://matrix.route.cit.api.here.com/routing/7.2/calculatematrix.json"
HERE_URL_GEOCODE = "https://geocoder.cit.api.here.com/6.2/geocode.json"

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
	- une source (google, here etc.)
	- un delai (temps nécessaire a l'exécution de la requête pour récupérer la distance et la durée)
	- Une distance renvoyée par la cible
	- Une durée renvoyée par la cible
	Une transaction se construit avec:
	- Un tableau dans laquelle elle s'enregistre
	- une origine et une destination en format texte
	- un mode de déplacement 
	"""

	def __init__(self, transactions, origin, destination, mode): 
		"""
		Commune à toutes les requêtes: On définit tous les attributs et on s'enregistre dans la demande d'ETA
		"""
		self.source = "Generic"
		self.delay = -1
		self.distance = -1
		self.duration = -1
		transactions.append(self)
		
	def to_JSON(self):
		"""
		Une méthode axée debug pour renvoyer l'objet Transaction sous forme de JSON.
		"""
		return json.dumps(self, default=lambda o: o.__dict__, 
			sort_keys=False, indent=4)

class GoogleTransaction(Transaction):
	"""
	On définit la sous-classe Google pour faire appel à GMAPS.
	On envoie directement l'origine/destination en mode texte à GMAPS pour en tirer la durée/distance. 
	"""
	def __init__(self, transactions, origin, destination, mode): 
		""" 
		Constructeur:
		On initialise la classe générique avant d'aller remplir les éléments soécifiques et exécuter la requête Google.
		"""
		Transaction.__init__(self, transactions, origin, destination, mode)
		delay_start = datetime.now()
		r = requests.get(
			GMAP_URL_MATRIX
			+"&origins="+origin
			+"&destinations="+destination
			+"&key="+GMAP_KEY
			).json()	
		delay_end = datetime.now()	

		self.source="GMAP_MATRIX"
		self.delay = str(delay_end - delay_start)
		self.distance= str( DictQuery(r['rows'][0]).get('elements/distance/value')[0] )
		self.duration= str( DictQuery(r['rows'][0]).get('elements/duration/value')[0] )

class HereTransaction(Transaction):
	"""
	On définit la sous-classe HERE pour faire appel à HERE.
	On doit d'abord géocoder l'origine/destination en coordonnées GPS avant de faire la requête de distance/durée. 
	"""
	
	def geocode(self,cible, address, trip):
		"""
		Une méthode qui calcule les coordonnées GPS de l'origine ou destination.
		Pour gérer le multi-threading, l'origine se met à jour dans trip[0] et la destination dans trip[1].
		On précise quel élément on traite via la variable cible. 
		"""
		r = requests.get(
			HERE_URL_GEOCODE
			+"?app_id="+HERE_APP_ID
			+"&app_code="+HERE_APP_CODE
			+"&searchtext="+address
			+"&locationattributes=none&addressattributes=none&responseattributes=none"
			).json()
		lat = DictQuery(DictQuery(r).get('Response/View/Result')[0][0]).get('Location/NavigationPosition/Latitude')[0]
		lng = DictQuery(DictQuery(r).get('Response/View/Result')[0][0]).get('Location/NavigationPosition/Longitude')[0]
		if cible == 'o':
			trip[0] = str(lat) + ',' + str(lng)
		elif cible == 'd':
			trip[1] = str(lat) + ',' + str(lng)

	def __init__(self, transactions, origin, destination, mode): 
		""" 
		Constructeur:
		On initialise la classe générique.
		On procède au géocoding d'origine/destination sur HERE.
		On remplit les attributs spécifiques à HERE
		"""

		Transaction.__init__(self, transactions, origin, destination, mode)

		# On lance 2 Threads pour geocoder en parallèle aux geocodes
		trip = [origin,destination]
		delay_start = datetime.now()
		threads = []
		
		#On vérifie si String est de la forme : r"\d+\.    r'[-+]?\d+(\.\d*)?,[-+]?\d+(\.\d*)?'
		pattern = re.compile(r'[-+]?\d+(\.\d*)?,[-+]?\d+(\.\d*)?')
		
		if pattern.fullmatch(origin) == None: #Pas une coordonnées GPS, on Geocode! 	
			t = Thread(target=self.geocode, args=('o', origin, trip))
			threads.append(t)
		if pattern.fullmatch(destination) == None: #Pas une coordonnées GPS, on Geocode! 
			t = Thread(target=self.geocode, args=('d', destination, trip))
			threads.append(t)
		
		if len(threads) > 0: # On a un thread de geocoding a lancer. 
			[ t.start() for t in threads ]
			[ t.join() for t in threads ]

		#Calcul de la distance et de la durée
		r = requests.get(
			HERE_URL_MATRIX
			+"?app_id="+HERE_APP_ID
			+"&app_code="+HERE_APP_CODE
			+"&start0="+str(trip[0])
			+"&destination0="+str(trip[1])
			+"&mode=fastest;"+mode+";traffic:disabled"
			+"&summaryAttributes=tt,di"
			).json()
		delay_end = datetime.now()	

		self.source = "HERE"
		self.delay = str(delay_end - delay_start)
		self.distance = str( DictQuery(r).get('response/matrixEntry/summary/distance')[0] )
		self.duration = str( DictQuery(r).get('response/matrixEntry/summary/travelTime')[0] )

class GoogleGeocodeTransaction(Transaction):
	"""
	DEPRECATED - NE PAS IMPORTER NI UTILISER
	Performance insuffisante. 
	On définit la sous-classe GoogleGeocode qui fait d'abord un geocode avant d'appeler Matrix. 
	On espère atteindre la rapidité de la requête HERE.
	On doit d'abord géocoder l'origine/destination en coordonnées GPS avant de faire la requête de distance/durée. 
	"""
	
	def geocode(self,cible, address, trip):
		"""
		Une méthode qui calcule les coordonnées GPS de l'origine ou destination.
		Pour gérer le multi-threading, l'origine se met à jour dans trip[0] et la destination dans trip[1].
		On précise quel élément on traite via la variable cible. 
		"""
		r = requests.get(
			GMAP_URL_GEOCODE
			+"?key="+GMAP_KEY
			+"&address="+address
			).json()
		place_id = str(DictQuery(r).get('results/place_id')[0])
		if cible == 'o':
			trip[0] = place_id
		elif cible == 'd':
			trip[1] = place_id

	def __init__(self, transactions, origin, destination, mode): 
		""" 
		Constructeur:
		On initialise la classe générique.
		On procède au géocoding d'origine/destination sur GMAPS Geocoding.
		On remplit les attributs spécifiques à GMAPS
		"""

		Transaction.__init__(self, transactions, origin, destination, mode)

		# On lance 2 Threads pour geocoder en parallèle aux geocodes
		trip = ["",""]
		delay_start = datetime.now()
		threads = []
		t = Thread(target=self.geocode, args=('o', origin, trip))
		threads.append(t)
		t = Thread(target=self.geocode, args=('d', destination, trip))
		threads.append(t)
		[ t.start() for t in threads ]
		[ t.join() for t in threads ]

		#Calcul de la distance et de la durée
		r = requests.get(
			GMAP_URL_MATRIX
			+"&origins=place_id:"+str(trip[0])
			+"&destinations=place_id:"+str(trip[1])
			+"&key="+GMAP_KEY
			).json()
		delay_end = datetime.now()	

		self.source = "GMAP_GEOCODE"
		self.delay = str(delay_end - delay_start)
		self.distance= str( DictQuery(r['rows'][0]).get('elements/distance/value')[0] )
		self.duration= str( DictQuery(r['rows'][0]).get('elements/duration/value')[0] )
















from Room import Room
from copy import deepcopy
from random import shuffle
class Hotel():
	"""docstring for Hotel"""
	def __init__(self, id, name, stars, rating, rooms, location, details, owner_id = None):
		self.id = id
		self.__name = name
		self.__stars = stars
		self.__rating = rating
		self.__rooms = rooms
		self.__location = location
		self.__owner_id = owner_id
		self.__details = details
		self.__total_power_in_rooms = len(rooms)
		self.__exposure_counter = 0
		self.__extra_nodes = self.__buildinExtraNodes(rooms=deepcopy(rooms))
		self.__sum_of_percentages = 0


	def getAvailableRooms(self, day):
		return [r for r in self.__rooms if r.isFree(day)]
	def getReservedRooms(self,day):
		return [r for r in self.__rooms if r.isBooked(day)]


	def getNumberOfAvailableRooms(self, day):
		return len([r for r in self.__rooms if r.isFree(day)])
	def getNumberOfReservedRooms(self,day):
		return len([r for r in self.__rooms if r.isBooked(day)])

	def buildRoomsSubGraph(self, day):
		av_rooms = self.getAvailableRooms(day)
		return self.__build_weights(av_rooms)

	def getExposureCounter(self):
		return self.__exposure_counter
	def getSumPercentage(self):
		return self.__sum_of_percentages

	def sumPercentage(self, value):
		self.__sum_of_percentages += value

	def sumPercentageNormalize(self, value):
		self.__sum_of_percentages /= value

	def exposed(self):
		self.__exposure_counter+=1

	# TODO: REVISE WEIGHTS
	# 		---> Add day?
	def __build_weights(self, rooms):
		w = []
		n = self.__total_power_in_rooms
		for i in range(n):
			row = []
			for j in range(n):
				val = (rooms[i].getValue() + rooms[j].getValue() )/(n-1) if i != j else 0
				row += [val]
			w += [row]
		return w

	def buildRoomsSubGraph_dict(self, day):
		av_rooms = self.getAvailableRooms(day)
		return self.__build_weights_dict(av_rooms)
	def __build_weights_dict(self,rooms):
		w = {}
		n = self.__total_power_in_rooms
		for i in range(n):
			row = {}
			for j in range(n):
				val = (rooms[i].getValue() + rooms[j].getValue() )/(n-1) if i != j else 0
				row[rooms[j]] = val
			w[rooms[i]] = row
		return w


	def setOwner(self, id):
		self.__owner_id = id
	def getOwner(self):
		return self.__owner_id
	def getLocation(self):
		return self.__location
	def getName(self):
		return self.__name
	def getRoomList(self):
		return self.__rooms	
	def getTotalNumberOfRooms(self):
		return self.__total_power_in_rooms
	def getStars(self):
		return self.__stars

	def bookRoom(self,day,roomId=None, roomType = None):
		if roomId:
			for r in self.__rooms:
				if r.id==roomId:
					r.book(day)
					return
			print(f'Could not find room with room id {roomId}')
			return

		if roomType:
			for r in self.__rooms:
				if r.isFree(day) and r.getRoomType() == roomType:
					print(f'\t\t\t(Booking room with id {r.id})')
					r.book(day)
					return

			print(f'Could not find avaialbe room of room type {roomType}')
			return

		shuffle(self.__rooms)
		for r in self.__rooms:
			if r.isFree(day):
				r.book(day)
				return
		print(f'Could not find avaialbe room.')
		return

	def cancelRoom(self,day,roomId=None):
		if roomId:
			for r in self.__rooms:
				if r.id==roomId:
					r.cancel(day)
					return
		for r in self.__rooms:
			if r.isBooked(day):
				r.cancel(day)
				return


	def hasAvailableRoom(self,day):
		for r in self.__rooms:
			if r.isFree(day):
				return True
		return False

	def hasReservedRoom(self,day):
		for r in self.__rooms:
			if r.isBooked(day):
				return True
		return False

	def hasRoomTypeAvailable(self,day,room_type):
		for r in self.__rooms:
			if r.isFree(day) and r.getRoomType()==room_type:
				return True
		return False

	def __buildinExtraNodes(self,rooms,dictionary=False):
		types = { i : False for i in ['single','double','triple','suite'] }
		origin_values = { i : 0 for i in ['single','double','triple','suite'] }
		halt = all(types.values())
		while rooms and not halt: 
			r = rooms.pop(0)
			t = r.getRoomType()
			v = r.getValue()
			types[t] = True
			origin_values[t] = v
			if r in rooms:
				rooms.remove(r)
			halt = all(types.values())


		if dictionary:
			extra_nodes = {
				x:Room(id=f'{self.id}_{x}', room_type=x, value = origin_values[x], hotelName = self.__name ) for x in types if types[x] == True
			}
			return extra_nodes

		extra_nodes = [
			Room(id=f'{self.id}_{x}',room_type=x, value = origin_values[x], hotelName = self.__name ) for x in types if types[x] == True
		]
		return extra_nodes

	def getExtraNodes(self, day, dictionary = False):
		return self.__buildinExtraNodes(rooms = self.getAvailableRooms(day),dictionary=dictionary)

	def hasExtraNodeSingle(self, day):
		return f'{self.id}_single' in self.getExtraNodes(day)
	def hasExtraNodeDouble(self, day):
		return f'{self.id}_double' in self.getExtraNodes(day)
	def hasExtraNodeTriple(self, day):
		return f'{self.id}_triple' in self.getExtraNodes(day)
	def hasExtraNodeSuite(self, day):
		return f'{self.id}_suite' in self.getExtraNodes(day)

	def __eq__(self, other):
		# return isinstance(other, Hotel) and self.id == other.id
		return isinstance(other, Hotel) and self.__name.lower() == other.getName().lower()
	def __lt__(self, other):
		# return isinstance(other, Hotel) and self.id < other.id
		return isinstance(other, Hotel) and self.__name.lower() < other.getName().lower
	def __gt__(self, other):
		# return isinstance(other, Hotel) and self.id > other.id
		return isinstance(other, Hotel) and self.__name.lower() > other.getName().lower
	def __le__(self, other):
		# return isinstance(other, Hotel) and self.id <= other.id
		return isinstance(other, Hotel) and self.__name.lower() <= other.getName().lower
	def __ge__(self, other):
		# return isinstance(other, Hotel) and self.id >= other.id
		return isinstance(other, Hotel) and self.__name.lower() >= other.getName().lower
	def __str__(self):
		return str(self.__name)
	def __hash__(self):
		return hash(self.id)
	def __repr__(self):
		return str(self.__name) #f'''Hotel {self.id} in {self.__location} with {self.__total_power_in_rooms} rooms'''


	''' 
		JSON FORMAT:
			{
				hotel_1:{
					location : Athens,
					rooms :{
						room_1:{
							type : single,
							price: 160
						},
						room_2:{
							type : double,
							price: 197
						}	
					}
				},				
				hotel_2:{
					location : Athens,
					rooms :{
						room_3:{
							type : triple,
							price: 170
						},
						room_4:{
							type : double,
							price: 130
						},
						room_5:{
							type : single,
							price: 100
						}	
					}
				},
					
			}
	'''
	@staticmethod
	def loadHotelsJSON(file):
		import json
		with open(file) as f:
			data = json.load(f)
		return Hotel.decodeHotelsFromDictionary(data)

	@staticmethod
	def decodeHotelsFromDictionary(data):
		from Room import Room
		hotels = []
		for entry in data:
			location = data[entry]["location"]
			rooms = Room.decodeRoomsFromDictionary(data[entry]["rooms"])
			hotels += [ Hotel(id = str(entry), location = location, rooms =rooms) ]
		return hotels


	''' 
		CSV FORMAT:
			Hotel id, City, Room id, Room_Type, Price
	'''
	@staticmethod
	def loadHotelsCSV(file):
		import pandas as pd
		df = pd.read_csv(file)
		return Hotel.decodeHotelsFromDataframe(df)

	@staticmethod
	def decodeHotelsFromDataframe(df):
		from Room import Room
		hotels = []
		hotels_ids = df["Hotel id"].unique().tolist()

		for index, row in df.iterrows():
			hotel_id = row["Hotel id"]
			if hotel_id in hotels_ids:
				location = row["City"]
				stars = row["Stars"]
				rating = row["Rating"]
				details = row["Details"]
				rooms = Room.decodeRoomsFromDataframe( df[df["Hotel id"]==hotel_id] )
				hotels += [ Hotel(id = str(hotel_id), name=str(hotel_id),location = location, rooms =rooms, stars=stars, rating=rating, details=details) ]
				hotels_ids.remove(hotel_id)
		return hotels


if __name__ == '__main__':
	file = 'test_file.csv'
	from Constant.room_types import ROOM_TYPES
	hotels = Hotel.loadHotelsCSV(file)
	print(hotels)
	print([h.getTotalNumberOfRooms() for h in hotels])


	'''
		Room:
			-id --> string
			-hotelName --> string
			-value --> float
			-type --> Single/ Double/ Tripple / Suite
			-availability --> [90 items of True / False]
		Hotel:
			-id --> string
			-name --> string
			-location --> string
			-stars --> intenger
			-ratings --> float
			-rooms --> [list of objects Room]

		h1 = Hotel(...)
		h1.__rooms[0].availability[3]

	'''
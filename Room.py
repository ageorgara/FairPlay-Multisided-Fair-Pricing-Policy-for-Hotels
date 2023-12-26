from Constant.room_types import ROOM_TYPES
class Room():
	"""docstring for Room"""
	def __init__(self, id,room_type, value, hotelName, period_of_interest = 90):
		self.id = id
		# if room_type not in [ROOM_TYPES.SINGLE, ROOM_TYPES.DOUBLE, ROOM_TYPES.TRIPLE, ROOM_TYPES.SUITE]:
		# 	self.__room_type = None
		# 	raise ValueError(f'''Room type must be one of the follwoing: {ROOM_TYPES.SINGLE}, {ROOM_TYPES.DOUBLE}, {ROOM_TYPES.TRIPLE}, {ROOM_TYPES.SUITE}''')
		# else:
		# 	self.__room_type = room_type
		self.__room_type = room_type
		self.__value = value
		self.__hotelName = hotelName
		self.__available = [True for i in range(1,period_of_interest+1)]

	def getValue(self): 
		return self.__value
	def getHotelName(self): 
		return self.__hotelName
	def getRoomType(self): 
		return self.__room_type
	def updateValue(self, val):
		self.__value = val


	def isFree(self, day):
		try:
			return self.__available[day]
		except:
			print(f'''Day {day} not within the period of interest''')
		# if day>=0 and day<=len(self.__available):
		# 	return self.__available[day]
		# else:
		# 	return False

	def isBooked(self, day):
		try:
			return not self.isFree(day)
		except:
			print(f'''Day {day} not within the period of interest''')

		# if day>=0 and day<=len(self.__available):
		# 	return not self.__available[day]
		# else:
		# 	return False
		
	def book(self, day):
		try:
			self.__available[day] = False
			return True
		except:
			print(f'''Day {day} not within the period of interest''')		
		return False
		# if day>=0 and day<=len(self.__available):
		# 	self.__available[day] = False
		# 	return True
		# return False


	def cancel(self, day):
		try:
			self.__available[day] = True
			return True
		except:
			print(f'''Day {day} not within the period of interest''')		
		return False

		# if day>=0 and day<=len(self.__available):
		# 	self.__available[day] = True
		# 	return True
		# return False
		
	def sameHotel(self,other):
		return isinstance(other, Room) and self.__hotelName == other.getHotelName()

	def sameType(self,other):
		return isinstance(other, Room) and self.__room_type == other.getRoomType()
		
	def __eq__(self, other):
		return isinstance(other, Room) and self.id == other.id
	def __lt__(self, other):
		return isinstance(other, Room) and self.id < other.id
	def __gt__(self, other):
		return isinstance(other, Room) and self.id > other.id
	def __le__(self, other):
		return isinstance(other, Room) and self.id <= other.id
	def __ge__(self, other):
		return isinstance(other, Room) and self.id >= other.id
	def __str__(self):
		return str(self.id)
	def __hash__(self):
		return hash(self.id)
	def __repr__(self):
		return f'''{self.id}'''

	''' 
		JSON FORMAT:
			{
				room_1:{
					type : single,
					price: 160
				},
				room_2:{
					type : doublee,
					price: 197
				},
				....
			}
	'''
	@staticmethod
	def loadRoomsJSON(file):
		import json
		with open(file) as f:
			input_data = json.load(f)
		return Room.decodeRoomsFromDictionary(input_data)

	@staticmethod
	def decodeRoomsFromDictionary(data):
		rooms= []
		for entry in data:
			room_type = data[entry]["type"].lower()
			value = float(date[entry]["price"])
			rooms += [ Room(id = str(entry), room_type = room_type, value = value) ]
		return rooms


	''' 
		CSV FORMAT:
			Hotel_id, City, Room_id, Room_Type, Price
	'''
	@staticmethod
	def loadRoomsCSV(file):
		import pandas as pd
		df = pd.read_csv(file)
		return Room.decodeRoomsFromDataframe(df)

	@staticmethod
	def decodeRoomsFromDataframe(df):
		rooms = []
		for index, row in df.iterrows():
			room_id = row["Room id"]
			room_type = row["Room Type"].lower()
			hotelName = row["Hotel id"]
			value = float(row["Price"])
			rooms += [ Room(id = room_id, room_type = room_type, value = value, hotelName = hotelName) ]
		return rooms
from Hotel import Hotel
from Room import Room
from Constant.room_types import ROOM_TYPES

isSubset = lambda s,t: sum( [1 for i in s if i in t] )==len(s)

def __preculcTotalNumberOfRooms(hotels):
	return { h.getName():h.getTotalNumberOfRooms() for h in hotels}

def __buildAllEdges(day,hotels):
	all_edges = {}
	CS = [h.getAvailableRooms(day) for h in hotels]
	all_available_rooms = [ room for i in range(len(CS)) for room in CS[i] ]
	# for h in hotels:
	# 	all_edges.update( h.buildRoomsSubGraph_dict(day) )
	# return all_edges,CS

	# Alternatively: build an entry for every possible 
	total_number_of_rooms = __preculcTotalNumberOfRooms(hotels)
	for r1 in all_available_rooms:
		row = {}
		for r2 in all_available_rooms:
			if r1.sameHotel(r2) and r1 != r2:
				n = total_number_of_rooms[r1.getHotelName()]
				edge_weight = (r1.getValue() + r2.getValue() )/ (n-1)
				row[r2] = edge_weight
			else:
				continue
		all_edges[r1] = row
	return all_edges,CS

def __buildAllEdges_with_extra_nodes2(day,hotels):
	'''
		a : availalbe typoy single
		t : total typoy single
		r : reserved typou single
		r + a = t => r/t = 1 - a/t

		sum_{i = 1}^a w_{i,S} = r/t =>
		a * w_{i, S} = 1 - a/t =>
		w_{i, S} = 1/a - 1/t = (t-a)/at



	'''
	CS_tmp = [ h for h in hotels if h.hasAvailableRoom(day) ]
	all_edges = {}
	CS = []
	CS_indexes = []
	for h in CS_tmp:
		extra_nodes = h.getExtraNodes(day)
		available_rooms = h.getAvailableRooms(day)
		total_rooms = h.getRoomList()
		# all_edges.update({r:{} for r in available_rooms})

		for extra_node in extra_nodes:
			t = len( [r for r in total_rooms if r.sameType(extra_node)] )
			a = len( [r for r in available_rooms if r.sameType(extra_node)] )
			
			row = {}
			for r in available_rooms:
				if r.sameType(extra_node):
					row[r] = 1/a - 1/t
					all_edges[r] = { extra_node:1/a-1/t }

			for extra_node2 in extra_nodes:
				if extra_node.sameType(extra_node2):
					continue
				else:
					t2 = len( [r for r in total_rooms if r.sameType(extra_node2)] )
					a2 = len( [r for r in available_rooms if r.sameType(extra_node2)] )
					row[extra_node2] = 1 - (a+a2)/(t+t2)

			for h2 in CS_tmp:
				if h==h2:
					continue
				else:
					extra_nodes2 = h2.getExtraNodes(day)
					available_rooms2 = h2.getAvailableRooms(day)
					total_rooms2 = h2.getRoomList()

					for extra_node2 in extra_nodes2:
						if extra_node.sameType(extra_node2):
							t2 = len( [r for r in total_rooms2 if r.sameType(extra_node2)] )
							a2 = len( [r for r in available_rooms2 if r.sameType(extra_node2)] )
							row[extra_node2] = 1 - (a+a2)/(t+t2)


			all_edges[extra_node] = row
		CS += [available_rooms + extra_nodes]
		CS_indexes += [hotels.index(h)]
	return all_edges,CS,CS_indexes

def __buildAllEdges_with_extra_nodes(day,hotels):
	all_edges = {}
	CS_tmp = [h for h in hotels]
	n = len(CS_tmp)
	CS = []

	hotels_with_room_types = {
		"single" : len([h for h in CS if h.hasExtraNodeSingle(day) ]),
		"double" : len([h for h in CS if h.hasExtraNodeDouble(day) ]),
		"triple" : len([h for h in CS if h.hasExtraNodeTriple(day) ]),
		"suite"  : len([h for h in CS if h.hasExtraNodeSuite(day) ])
	}

	for h in CS_tmp:
		extra_nodes = h.getExtraNodes(day)
		available_rooms = h.getAvailableRooms(day)
		CS += [extra_nodes+available_rooms]
		m = len(extra_nodes)
		for r1 in extra_nodes:
			row = {}
			for r2 in extra_nodes:
				if r1 == r2:
					continue
				else:
					new_edge_weight = (r1.getValue() + r2.getValue())/(len(extra_nodes)-1) #float(h.getStars())
					row[r2] = new_edge_weight
			for r2 in available_rooms:
				if r1.sameType(r2):
					new_edge_weight = r2.getValue()
					row[r2] = new_edge_weight
			for h2 in CS_tmp:
				if h==h2:
					continue
				else:
					exnd = h2.getExtraNodes(day)
					for r2 in exnd:
						if r1.sameType(r2):
							# new_edge_weight = (h.getStars()+h2.getStars())/(n-1)
							new_edge_weight = (r1.getValue() + r2.getValue())/(hotels_with_room_types[ r1.getRoomType() ] -1 )
							row[r2] = new_edge_weight
			all_edges[r1] = row

		for r1 in available_rooms:
			row = {}
			for r2 in extra_nodes:
				if r1.sameType(r2):
					new_edge_weight = r1.getValue()
					row[r2] = new_edge_weight
			all_edges[r1] = row

	return all_edges,CS

def __cleanValues(h,x,day):
	z = {}
	extra_nodes = h.getExtraNodes(day,dictionary=True)
	available_rooms = h.getAvailableRooms(day)
	# rooms = {
	# 	item : [r for r in available_rooms if r.getRoomType()== item] for item in extra_nodes
	# }
	for item in extra_nodes:
		value = x[ extra_nodes[item] ]
		rooms = [r for r in available_rooms if r.getRoomType()== item]
		n = len(rooms)

		z.update( {r : x[r] + value/n for r in rooms} )
		# z.update( {r : x[r] for r in rooms} )

	return z


def computeOwenValues_ISG(day,hotels):
	all_edges,CS, CS_indexes = __buildAllEdges_with_extra_nodes2(day,hotels)
	grand_coalition = sorted([room for i in range(len(CS)) for room in CS[i] ])
	owen_values = computeShapleyValues_ISG(grand_coalition,all_edges)

	owen_values_cleand = {}
	for idx in range(len(CS)):
		owen_values_cleand.update( __cleanValues(hotels[CS_indexes[idx]],owen_values,day) )

	return owen_values_cleand


def computeOwenValues(day, hotels, hotel_power = False):
	# all_edges, CS = __buildAllEdges(day, hotels)
	all_edges, CS =__buildAllEdges_with_extra_nodes(day,hotels)

	owen_values = {}

	if hotel_power:
		coalitional_power = {}	
	for idx in range(len(CS)):
		# x,y = computeOwenValuesPerHotel(CS,idx,all_edges)
		x,y = computeOwenValuesPerHotel2(h,idx,all_edges)
		z = __cleanValues(hotels[idx],x,day)
		owen_values.update( z )
		if hotel_power:
			coalitional_power[idx] = y
	if hotel_power:
		return owen_values, coalitional_power
	return owen_values

def computeOwenValuesPerHotel2(CS,idx,edges):
	N_k 	= sorted( CS[idx] )
	N_all 	= sorted( [room for i in range(len(CS)) for room in CS[i] if i != idx] )

	c = len(CS)

	edges_bar = {}
	for i in N_k:
		row = {}
		for j in N_k:
			if i==j:
				new_edge_weight = sum([ edges[i][k] for k in N_all if k in edges[i] ])/2
				if i in edges[i]:
					new_edge_weight += edges[i][i]
			else:
				new_edge_weight = 0 if j not in edges[i]  else edges[i][j]
			if new_edge_weight != 0:
				row[j] = new_edge_weight
		edges_bar[i] = row

	# x0_self_loop = sum([computeValue_ISG(CS[i],edges) for i in range(c) if i != idx ])
	shapley_values = computeShapleyValues_ISG(N_k,edges_bar)
	# N_k_value = computeValue_ISG(N_k,edges_bar) + x0_self_loop
	# shapley_x0 = N_k_value - sum([shapley_values[i] for i in N_k])
	owen_values = {}
	for room in N_k:
		owen_values[room] = shapley_values[room] 
	return owen_values, 0


def computeOwenValuesPerHotel(CS,idx,edges):
	N_k 	= sorted( CS[idx] )
	N_all 	= sorted( [room for i in range(len(CS)) for room in CS[i] if i != idx] )
	CS_power = computeCSValue_ISG(CS,edges)
	# print(CS_power)
	edges_bar ={}
	for i in N_k:
		row  = {}
		for j in N_k:
			if i==j:
				new_edge_weight = sum([ edges[i][k] for k in N_all if k in edges[i] ])/2 
				if i in edges[i]:
					new_edge_weight += edges[i][i]/(len(CS)-1)
			else:
				new_edge_weight = edges[i][j]/(2*(len(CS)-1)) if j in edges[i] else 0
			if new_edge_weight != 0:
				row[j] = new_edge_weight
		edges_bar[i] = row

	# Void agent x_{\emptyset} with self loop w_{\emptyset,\emptyset} = \sum_{i,j \in N_all} w_{i,j} / 2
	x_0_self_loop = 0
	
	for i in range(len(N_all)):
		ri = N_all[i]
		for j in range(i,len(N_all)):
			rj = N_all[j]
			x_0_self_loop += edges[ri][rj]/(len(CS)-1) if rj in edges[ri] else 0
	x_0_self_loop /= 2

	owen_values = {}
	shapley_values = computeShapleyValues_ISG(N_k,edges_bar)
	N_k_power = computeValue_ISG(N_k,edges_bar)+x_0_self_loop # sum(shapley_values.values()) + x_0_self_loop
	for room in N_k:
		owen_values[room] = shapley_values[room] + x_0_self_loop/len(N_k)#/N_k_power
		# owen_values[room] = round(shapley_values[room] ,2)
	return owen_values, round(x_0_self_loop,2)

def computeShapleyValues_ISG(S,edges):
	shapley_values = {}
	for i in range(len(S)):
		value = 0
		ai = S[i]
		for j in range(len(S)):
			if i==j and ai in edges[ai]:
				value+= edges[ai][ai]
			else:
				aj = S[j]
				value += edges[ai][aj]/2 if aj in edges[ai] else 0
		shapley_values[ai] = value
	return shapley_values

def computeValue_ISG(S,edges):
	value = 0
	for i in range(len(S)):
		ai = S[i]
		for j in range(i,len(S)):
			aj = S[j]
			if aj in edges[ai]:
				value+= edges[ai][aj]
	return value

def computeCSValue_ISG(CS,edges):
	value = 0
	for S in CS:
		value += computeValue_ISG(S,edges)
	return value


if __name__ == '__main__':
	filename = '/home/ageorg/Documents/Hotel Room Pricing/ROOMS_Barcelona_small.csv'
	# filename = '/home/ageorg/Downloads/Dropbox-CSIC/Dropbox/Tractable Game Theoretic Solutions for Fair Hotel Room Pricing Recommendations/test_file.csv'
	from Constant.room_types import ROOM_TYPES
	hotels = Hotel.loadHotelsCSV(filename)
	

	for i in range(0,6):
		print(hotels[i],len(hotels[i].getAvailableRooms(day=0)))
		while hotels[i].hasAvailableRoom(day=0) and i!=4:
			hotels[i].bookRoom(day=0)
		print(hotels[i],len(hotels[i].getAvailableRooms(day=0)))

	# hotels[4].bookRoom(day=0)
	hotels[3].cancelRoom(day=0)
	# hotels[0].bookRoom(0,roomType='double')
	# hotels[2].bookRoom(0,roomType='double')
	# hotels[0].bookRoom(0,roomType='single')
	edges,CS, CS_indexes = __buildAllEdges_with_extra_nodes2(0,hotels)
	# for h in CS:
	owen_values_pre = computeOwenValues_ISG(hotels=hotels,day=0)

	for idx in range(len(hotels)):
		for r in hotels[idx].getAvailableRooms(day=0):
			print(r.id,r.getRoomType(),r.getValue(),'-->',r.getValue()*(1+owen_values_pre[r]))
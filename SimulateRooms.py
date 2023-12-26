from random import randint, random, choice
from Hotel import Hotel
import pandas as pd
from OwenValues import computeOwenValues_ISG
from Constant.room_types import ROOM_TYPES
from math import ceil
from prepareXLSX import createXLSX
__max_rho_index = 1e+10

def findHotels(hotels, reservation_date, type_of_reservation, exposure, items_to_return = 3):
	retval = []
	# shorted_exposure = sorted(exposure.items(), key=lambda x: x[1])
	reverse_expo = {exposure[key]:key for key in exposure}
	xx = sorted(list(exposure.values()))
	yy = [reverse_expo[key] for key in xx]

	hotel_indexs = list(range(len(hotels)))

	while len(retval)<items_to_return and hotel_indexs:
		idx = choice(hotel_indexs)
		h = hotels[ idx ]

		# xxx =  h.hasRoomTypeAvailable(reservation_date,type_of_reservation)

		if h.hasRoomTypeAvailable(reservation_date,type_of_reservation):
			if idx in yy[:items_to_return+1]:
				retval += [h]
				hotel_indexs.remove(idx)
				yy.remove(idx)
			else:
				continue
		else:
			hotel_indexs.remove(idx)
			yy.remove(idx)


	return retval


def findsRoomsToShow(hotels,owen_values,reservation_date, percentage_of_hotels_to_show = 0.3):
	if percentage_of_hotels_to_show>1:percentage_of_hotels_to_show=0.5

	available_hotels = [h for h in hotels if h.hasAvailableRoom(reservation_date)]
	owen_per_hotel = {
		h.id : sum([ owen_values[r] for r in h.getRoomList() if r.isFree(reservation_date) and r in owen_values]) for h in available_hotels
	}
	rho_index = { __max_rho_index if owen_per_hotel[h.id]==0 else h.getExposureCounter()/owen_per_hotel[h.id] : h for h in available_hotels }
	keys2show = sorted(rho_index.keys())
	number_of_hotels_to_show = ceil(percentage_of_hotels_to_show*len(available_hotels))

	hotels2show = [ hotels.index(rho_index[key]) for key in keys2show[:number_of_hotels_to_show] ]
	for idx in hotels2show:
		hotels[idx].exposed()
	return hotels2show


def __findHotelFromList(x,hotels):
	for idx in range(len(hotels)):
		if str(x) in [r.id for r in hotels[idx].getRoomList()]:
			return idx
	return None

def ___post_calc_owen(filename, simulation_period = 90):
	import pandas as pd
	hotels = Hotel.loadHotelsCSV(filename)
	all_room_ids = [r for h in hotels for r in h.getRoomList()]

	
	planfile = filename.split("/")
	planfile = "/".join(planfile[:-1] + ["results XLSX/Simulation for 90 days/"]) + "%s_prices"%(planfile[-1].split(".csv")[0])  + "_%s_days.csv"%simulation_period

	plan = pd.read_csv(planfile)
	plan["Hotel idx"] = plan["Room Id"].apply( __findHotelFromList,args=(hotels,) )


	column_values = plan.columns.to_list()

	owen_values = pd.DataFrame(columns = ["Room Type","Room Id","Init Day"]+["Day " + str(d+1) for d in range(simulation_period)])
	
	ov = computeOwenValues_ISG(hotels = hotels, day = 0)
	column_values = [ov[r] if r in ov else '-' for r in all_room_ids]
	owen_values["Init Day"] = column_values
	owen_values["Room Type"] = plan["Room Type"].to_list()
	owen_values["Room Id"] = plan["Room Id"].to_list()

	for day in range(simulation_period):

		col = "Day "+ str(day+1)
		for index, row in plan.iterrows():
			room_id = row["Room Id"]
			hotel_idx = row["Hotel idx"]

			val = row[col]
			if val == "-":
				hotels[hotel_idx].bookRoom(day = day, roomId = str(room_id))


		ov = computeOwenValues_ISG(hotels = hotels, day = day)
		column_values = [ov[r] if r in ov else '-' for r in all_room_ids]
		# print("Day "+str(day+1))
		owen_values["Day "+str(day+1)] = column_values


	outfile = filename.split("/")
	outfile = "/".join(outfile[:-1] + ["results XLSX/Simulation for 90 days/"]) + "%s_OWEN"%(outfile[-1].split(".csv")[0])  + "_%s_days.csv"%simulation_period
	owen_values.to_csv(outfile,index = False)
	
	# outfile = filename.split("/")
	# outfile = "/".join(outfile[:-1] + ["results XLSX/"]) + "%s_OWEN"%(outfile[-1].split(".csv")[0])  + "_%s_days.xlsx"%simulation_period
	createXLSX(outfile)




def simulate(filename, simulation_period = 90, max_reservations_per_day = 100, cancelation_probability = 0.1, day_target = None):
	hotels = Hotel.loadHotelsCSV(filename)
	all_room_ids = [r for h in hotels for r in h.getRoomList()]


	df_prices = pd.DataFrame(columns = ["Room Type","Room Id","Init Day"]+["Day " + str(d+1) for d in range(simulation_period)])
	# df_counter = pd.DataFrame(columns = ["Hotel Id","Init Day"]+["Day " + str(d+1) for d in range(simulation_period)])
	# df_power = pd.DataFrame(columns = ["Hotel Id","Init Day"]+["Day " + str(d+1) for d in range(simulation_period)])

	if day_target:
		owen_values = computeOwenValues_ISG(hotels = hotels, day = day_target)
	else:
		owen_values = computeOwenValues_ISG(hotels = hotels, day = 0)

	# total_number_of
	column_values = [r.getValue()*(1+owen_values[r]) if r in owen_values else '-' for r in all_room_ids]
	
	df_prices["Room Type"] = [str(r.getRoomType()) for r in all_room_ids]
	df_prices["Room Id"] = [str(r.id) for r in all_room_ids]
	df_prices["Init Day"] = column_values
	

	# column_values = [h.getExposureCounter() for h in hotels]
	# df_counter["Hotel Id"] = [str(h.id) for h in hotels]
	# df_counter["Init Day"] = column_values

	# column_values = [sum([ owen_values[r] if r in owen_values else '-' for r in h.getRoomList()]) for h in hotels]
	# df_power["Hotel Id"] = [str(h.id) for h in hotels]
	# df_power["Init Day"] = column_values

	for day in range(simulation_period):
		print(f'Day {day}')
		reservations_dates = list(
			# range(	day, simulation_period )
			range(	day, min([day+20,simulation_period])	)
		)

		available_rooms_until_end_of_period = sum(
			[
				sum(
					[ len(h.getAvailableRooms(d)) for h in hotels ]
				) for d in reservations_dates
			]
		)

		number_of_reservations = randint(0, min([max_reservations_per_day, available_rooms_until_end_of_period]) )

		while number_of_reservations:
			type_of_reservation = choice([ROOM_TYPES.SINGLE, ROOM_TYPES.DOUBLE, ROOM_TYPES.TRIPLE, ROOM_TYPES.SUITE])
			print(f'\t{number_of_reservations} reservations yet to make...')
			# reservation_date = choice(reservations_dates)
			reservation_date = day

			if sum([h.getNumberOfAvailableRooms(reservation_date) for h in hotels])==0:
				continue


			owen_values = computeOwenValues_ISG(hotels = hotels, day = reservation_date)

			for h in hotels:
				if h.hasAvailableRoom(day):
					h.sumPercentage( sum([ owen_values[r] for r in h.getRoomList() if r.isFree(reservation_date) and r in owen_values]) )

			# Random Hotels
			# hotels_to_show = [h for h in hotels if h.hasRoomTypeAvailable(reservation_date,type_of_reservation) ]

			# # Cheapest hotels
			# # hotels_to_show = findHotels(hotels = hotels, reservation_date = reservation_date, type_of_reservation = type_of_reservation, exposure = power, items_to_return=2)
			# if not hotels_to_show:
			# 	continue
			# chosen_hotel = choice(hotels_to_show)
			# idx = hotels.index(chosen_hotel)
			# print(f'\t\t==>Reserving room of type {type_of_reservation} at {hotels[idx]}<==')
			# hotels[idx].bookRoom(day = reservation_date, roomType = type_of_reservation)

			# Exposure index
			hotels_to_show = findsRoomsToShow(hotels = hotels, owen_values = owen_values, reservation_date = reservation_date, percentage_of_hotels_to_show=0.3)
			

			if not hotels_to_show:
				continue
			idx = choice(hotels_to_show)
			print(f'\t\t==>Reserving room of type {type_of_reservation} at {hotels[idx]}<==')
			hotels[idx].bookRoom(day = reservation_date)

			number_of_reservations -= 1


			# Cancelling
			if random() <= cancelation_probability:
				cancelation_date = choice(reservations_dates)

				hotels_with_reservations = [h for h in hotels if h.hasReservedRoom(cancelation_date) ]

				if hotels_with_reservations:	
					print(f'\t\t==>Cancelling reservation on Day {cancelation_date}<==')
					h = choice(hotels_with_reservations)
					idx = hotels.index(h)
					hotels[idx].cancelRoom(cancelation_date)

	
		if day_target:
			owen_values = computeOwenValues_ISG(hotels = hotels, day = day_target)
		else:
			owen_values = computeOwenValues_ISG(hotels = hotels, day = day)
		
		if day_target and day>day_target:
			continue
		
		column_values = [r.getValue()*(1+owen_values[r]) if r in owen_values else '-' for r in all_room_ids]
	
		df_prices["Day "+ str(day+1)] = column_values


		# column_values = [h.getExposureCounter() for h in hotels]
		# df_counter["Day "+ str(day+1)] = column_values

		# for h in hotels:
		# 	h.sumPercentage( sum([ owen_values[r] for r in h.getRoomList() if r.isFree(reservation_date) and r in owen_values]) )
		# column_values = [h.getSumPercentage() for h in hotels]
		# df_power["Day "+ str(day+1)] = column_values
	
		output_file = filename.split("/")
		# output_file = "/".join(output_file[:-1] + ["results XLSX/"]) 

		# if day_target:
		# 	output_file+= "_for_target_day_%d"%day_target


		# output_file += f'_{simulation_period}_days.csv'

		of = "/".join(output_file[:-1] + ["results XLSX/"]) + "%s_prices"%(output_file[-1].split(".csv")[0])  + "_%s_days.csv"%simulation_period
		df_prices.to_csv(of, index = False)

		# of = "/".join(output_file[:-1] + ["results XLSX/"]) + "%s_counters"%(output_file[-1].split(".csv")[0])+"_%s_days.csv"%simulation_period
		# df_counter.to_csv(of, index = False)

		# of = "/".join(output_file[:-1] + ["results XLSX/"]) + "%s_hotel_power"%(output_file[-1].split(".csv")[0])+"_%s_days.csv"%simulation_period
		# df_power.to_csv(of , index = False)
		# # reservations_per_hotel_day = { h : h.getNumberOfReservedRooms(day=day) for h in hotels }
		# # total_reservations_per_day = sum( reservations_per_hotel_day.values() )
		# # percentage_per_hotel_day = { h: reservations_per_hotel_day[h]/total_reservations_per_day if total_reservations_per_day>0 else 0 for h in hotels }

		# # for h in hotels:
		# # 	if h.hasAvailableRoom(day):
		# # 		h.sumPercentage( sum([ owen_values[r] for r in h.getRoomList() if r.isFree(reservation_date) and r in owen_values]) )

	of = "/".join(output_file[:-1] + ["results XLSX/"]) + "%s_prices"%(output_file[-1].split(".csv")[0])  + "_%s_days.csv"%simulation_period
	createXLSX(of)

	df_counter = pd.DataFrame(columns = ["Hotel Id","Counter","Power"])
	column_values = [str(h.id) for h in hotels]
	df_counter["Hotel Id"] = column_values
	column_values = [h.getExposureCounter() for h in hotels]
	df_counter["Counter"] = column_values
	column_values = [h.getSumPercentage() for h in hotels]
	df_counter["Power"] = column_values

	of = "/".join(output_file[:-1] + ["results XLSX/"]) + "%s_exposure"%(output_file[-1].split(".csv")[0])  + "_%s_days.csv"%simulation_period
	df_counter.to_csv(of, index = False)
	
	# for h in hotels:
	# 	# h.sumPercentageNormalize(simulation_period)
	# 	print(h,'\t',h.getExposureCounter(),'\t',h.getSumPercentage())


if __name__ == '__main__':
	# filename = '/home/ageorg/Documents/Hotel Room Pricing/Athens_large.csv'
	
	filename = 'Datasets/ROOMS_Barcelona_medium.csv'
	# simulate(filename, simulation_period=30, max_reservations_per_day=70 )
	___post_calc_owen(filename, simulation_period=90 )
	# simulation_period = 90
	# output_file = filename.split("/")
	# output_file = "/".join(output_file[:-1] + ["results XLSX/"]) + "%s_prices"%(output_file[-1].split(".csv")[0])
	# output_file += f'_{simulation_period}_days.csv'
	# createXLSX(output_file)
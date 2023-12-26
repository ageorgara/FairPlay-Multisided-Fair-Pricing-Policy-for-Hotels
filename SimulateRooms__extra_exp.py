from random import randint, random, choice
from Hotel import Hotel
import pandas as pd
from OwenValues import computeOwenValues_ISG
from Constant.room_types import ROOM_TYPES
from math import ceil
from prepareXLSX import createXLSX
from prepareXLSX_2 import create_new_XLSX
__max_rho_index = 1e+10
constant_incr = 0.17

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




def simulate(filename, simulation_period = 90, max_reservations_per_day = 100, cancelation_probability = 0.1, day_target = None):
	hotels = Hotel.loadHotelsCSV(filename)
	all_room_ids = [r for h in hotels for r in h.getRoomList()]


	df_prices = pd.DataFrame(columns = ["Room Type","Room Id","Hotel Id","Init Day"]+["Day " + str(d+1) for d in range(simulation_period)])
	df_prices_constant = pd.DataFrame(columns = ["Room Type","Room Id","Hotel Id","Init Day"]+["Day " + str(d+1) for d in range(simulation_period)])
	df_gain = pd.DataFrame(columns = ["Room Type","Room Id","Hotel Id","Init Day"]+["Day " + str(d+1) for d in range(simulation_period)])
	df_gain_constant = pd.DataFrame(columns = ["Room Type","Room Id","Hotel Id","Init Day"]+["Day " + str(d+1) for d in range(simulation_period)])

	if day_target:
		owen_values = computeOwenValues_ISG(hotels = hotels, day = day_target)
	else:
		owen_values = computeOwenValues_ISG(hotels = hotels, day = 0)

	# total_number_of
	column_values = [r.getValue()*(1+owen_values[r]) if r in owen_values else '-' for r in all_room_ids]
	
	df_prices["Room Type"] = [str(r.getRoomType()) for r in all_room_ids]
	df_prices["Room Id"] = [str(r.id) for r in all_room_ids]
	# df_prices["Hotel Id"] = [r.getHotelName() for r in all_room_ids]
	df_prices["Hotel Id"] = [str(r.id[:-4]) for r in all_room_ids]
	df_prices["Init Day"] = column_values


	column_values = [r.getValue()*(1+constant_incr) if r in owen_values else '-' for r in all_room_ids]
	df_prices_constant["Room Type"] = [str(r.getRoomType()) for r in all_room_ids]
	df_prices_constant["Room Id"] = [str(r.id) for r in all_room_ids]
	# df_prices_constant["Hotel Id"] = [r.getHotelName() for r in all_room_ids]
	df_prices_constant["Hotel Id"] = [str(r.id[:-4]) for r in all_room_ids]
	df_prices_constant["Init Day"] = column_values


	column_values = [0 if r in owen_values else '-' for r in all_room_ids]
	df_gain["Room Type"] = [str(r.getRoomType()) for r in all_room_ids]
	df_gain["Room Id"] = [str(r.id) for r in all_room_ids]
	# df_gain["Hotel Id"] = [r.getHotelName() for r in all_room_ids]
	df_gain["Hotel Id"] = [str(r.id[:-4]) for r in all_room_ids]
	df_gain["Init Day"] = column_values
	df_gain_constant["Room Type"] = [str(r.getRoomType()) for r in all_room_ids]
	df_gain_constant["Room Id"] = [str(r.id) for r in all_room_ids]
	# df_gain_constant["Hotel Id"] = [r.getHotelName() for r in all_room_ids]
	df_gain_constant["Hotel Id"] = [str(r.id[:-4]) for r in all_room_ids]
	df_gain_constant["Init Day"] = column_values



	for day in range(simulation_period):
		print(f'Day {day}')
		reservations_dates = list(
			range(	day, min([day+20,simulation_period])	)
		)

		available_rooms_until_end_of_period = sum(
			[
				sum(
					[ len(h.getAvailableRooms(d)) for h in hotels ]
				) for d in reservations_dates
			]
		)

		# number_of_reservations = randint(0, min([max_reservations_per_day, available_rooms_until_end_of_period]) )
		number_of_reservations = min([max_reservations_per_day, available_rooms_until_end_of_period])

		while number_of_reservations:
			type_of_reservation = choice([ROOM_TYPES.SINGLE, ROOM_TYPES.DOUBLE, ROOM_TYPES.TRIPLE, ROOM_TYPES.SUITE])
			print(f'\t{number_of_reservations} reservations yet to make...')
			reservation_date = day

			if sum([h.getNumberOfAvailableRooms(reservation_date) for h in hotels])==0:
				continue


			owen_values = computeOwenValues_ISG(hotels = hotels, day = reservation_date)

			hotels_to_show = []
			for hidx in range(len(hotels)):
				h = hotels[hidx]
				if h.hasAvailableRoom(day):
					h.sumPercentage( sum([ owen_values[r] for r in h.getRoomList() if r.isFree(reservation_date) and r in owen_values]) )
					hotels_to_show.append(hidx)

		

			# Exposure index
			# hotels_to_show = findsRoomsToShow(hotels = hotels, owen_values = owen_values, reservation_date = reservation_date, percentage_of_hotels_to_show=0.3)
			

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

		# s = sum(owen_values.values())
		# column_values = ['-' if r not in owen_values else r.getValue() if s == 0 else r.getValue()*(1+(owen_values[r]/s))for r in all_room_ids]
		column_values = [r.getValue()*(1+owen_values[r]) if r in owen_values else '-' for r in all_room_ids]
		column_values_constant = [r.getValue()*(1+constant_incr) if r in owen_values else '-' for r in all_room_ids]
	
		df_prices["Day "+ str(day+1)] = column_values
		df_prices_constant["Day "+ str(day+1)] = column_values_constant


		column_values = [r.getValue()*(1+owen_values[r]) if r in owen_values else '-' for r in all_room_ids]
		column_values_constant = [r.getValue()*constant_incr if r in owen_values else '-' for r in all_room_ids]

		df_gain["Day "+ str(day+1)] = column_values
		df_gain_constant["Day "+ str(day+1)] = column_values_constant



	
		output_file = filename.split("/")
		
		of = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_prices_Owen"%(output_file[-1].split(".csv")[0])  +  "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
		df_prices.to_csv(of, index = False)
		of = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_prices_Constant"%(output_file[-1].split(".csv")[0])  +  "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
		df_prices_constant.to_csv(of, index = False)
		of = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_gain_Owen"%(output_file[-1].split(".csv")[0])  +  "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
		df_gain.to_csv(of, index = False)
		of = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_gain_Constant"%(output_file[-1].split(".csv")[0])  +  "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
		df_gain_constant.to_csv(of, index = False)

		
	of = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_prices_Owen"%(output_file[-1].split(".csv")[0])  +  "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
	createXLSX(of)	
	of = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_prices_Constant"%(output_file[-1].split(".csv")[0])  +  "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
	createXLSX(of)

	# of = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_gain_Owen"%(output_file[-1].split(".csv")[0])  +  "_%s_days__%d%%.csv"%(simulation_period,int(constant_incr*100))
	# createXLSX(of)
	# of = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_gain_Constant"%(output_file[-1].split(".csv")[0])  +  "_%s_days__%d%%.csv"%(simulation_period,int(constant_incr*100))
	# createXLSX(of)

	of1 = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_prices_Owen"%(output_file[-1].split(".csv")[0])  + "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
	of2 = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_prices_Constant"%(output_file[-1].split(".csv")[0])  + "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
	of3 = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_prices_Owen_vs_Constant"%(output_file[-1].split(".csv")[0])  + "_%s_days__%.2f.xlsx"%(simulation_period,constant_incr)
	create_new_XLSX(input_file_constant=of2,input_file_owen=of1,output_file=of3)

	of1 = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_gain_Owen"%(output_file[-1].split(".csv")[0])  + "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
	of2 = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_gain_Constant"%(output_file[-1].split(".csv")[0]) + "_%s_days__%.2f.csv"%(simulation_period,constant_incr)
	of3 = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_gain_Owen_vs_Constant"%(output_file[-1].split(".csv")[0])  + "_%s_days__%.2f.xlsx"%(simulation_period,constant_incr)
	create_new_XLSX(input_file_constant=of2,input_file_owen=of1,output_file=of3)

	df_counter = pd.DataFrame(columns = ["Hotel Id","Counter","Power"])
	column_values = [str(h.id) for h in hotels]
	df_counter["Hotel Id"] = column_values
	column_values = [h.getExposureCounter() for h in hotels]
	df_counter["Counter"] = column_values
	column_values = [h.getSumPercentage() for h in hotels]
	df_counter["Power"] = column_values

	of = "/".join(output_file[:-1] + ["results XLSX/new series/"]) + "%s_exposure"%(output_file[-1].split(".csv")[0])  + "_%s_days__%d%%.csv"%(simulation_period,int(constant_incr*100))
	df_counter.to_csv(of, index = False)
	



if __name__ == '__main__':
	# filename = '/home/ageorg/Documents/Hotel Room Pricing/Athens_large.csv'

	mrd = {
	"large" : 150,
	"medium" : 300, #100,
	"small" : 115, #50
	# "ultra" : 20
	}
	sz = {
		"Athens" : "large",
		"Barcelona" : "medium",
		"Rome" : "small",
		# "all" : "ultra"
	}
	# folder = "/home/ageorg/Downloads/Dropbox-CSIC/Dropbox/Tractable Game Theoretic Solutions for Fair Hotel Room Pricing Recommendations/"

	folder = "/home/ageorg/Documents/Hotel Room Pricing/"
	for city in ["Barcelona"]:
		# for size in ["small", "medium", "large"]:
		size = sz[city]
		# city = "Barcelona"
		print(f'{city} {size}')

		filename = f'{folder}6-Nov-23/ROOMS_{city}_{size}.csv'
		simulate(filename, simulation_period=90, max_reservations_per_day=mrd[size],cancelation_probability=0.1 )
		# ___post_calc_owen(filename, simulation_period=90 )
		# simulation_period = 20
		# output_file = filename.split("/")
		# output_file = "/".join(output_file[:-1] + ["results XLSX/"]) + "%s_prices"%(output_file[-1].split(".csv")[0])
		# output_file += f'_{simulation_period}_days.csv'
		# createXLSX(output_file)

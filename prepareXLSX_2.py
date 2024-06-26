import xlsxwriter
import pandas as pd
import sys

__letters = {i : chr(ord('`')+(i+1)) for i in range(26)}
for i in range(26):
	for j in range(26):
		v = chr(ord('`')+(i+1))+chr(ord('`')+(j+1))
		idx = (i+1)*26+j
		__letters.update( {idx:v} )


def create_new_XLSX(input_file_constant,input_file_owen,output_file = None):
	if output_file == None:
		output_file = input_file_constant.split("Constant")
		output_file = output_file[0][:-1] + output_file[1].split('.csv')[0] + '.xlsx'

	constant_data = pd.read_csv(input_file_constant)
	owen_data = pd.read_csv(input_file_owen)
	owen_data2 = owen_data

	owen_data2 = owen_data2.drop("Room Type", axis='columns')
	owen_data2 = owen_data2.drop("Hotel Id", axis='columns')
	column_names = constant_data.columns.tolist()
	days = column_names[3:]
	number_of_days = len(days)
	owen_data2.columns = ["Room Id"]+[col+' Owen' for col in days]
	joined = pd.concat([constant_data.set_index('Room Id'),owen_data2.set_index('Room Id')], axis=1, join='inner').reset_index()

	unique_hotels = joined['Hotel Id'].unique().tolist()
	#
	joined =__swaps(joined,unique_hotels,days)
	# print("Swaps done...")
	# print(joined[["Hotel Id","Room Id", "Day 3"]].head(5))
	# print(joined2[["Hotel Id","Room Id", "Day 3"]].head(5))
	reservation_percentage_per_hotel = pd.DataFrame(columns = ["Hotel Id"] + column_names[3:] )
	#
	for hotel in unique_hotels:
		row = {}
		row["Hotel Id"] = hotel
		for col in column_names[3:]:
			x = joined[ (joined["Hotel Id"]==hotel) & (joined[col]=="-")][col].count()
			y = joined[ (joined[col]=="-")][col].count()
			row[col] = 0 if y==0 else x/y
		row = pd.DataFrame({'name':row.keys(), 'value':row.values()})
		# reservation_percentage_per_hotel = reservation_percentage_per_hotel.append(row, ignore_index=True)
		reservation_percentage_per_hotel = pd.concat([reservation_percentage_per_hotel,row], ignore_index=True)
	#
	ranking = pd.DataFrame(columns = ["Hotel Id"] + column_names[3:] )
	xx = reservation_percentage_per_hotel["Hotel Id"].tolist()
	ranking["Hotel Id"] = xx
	for col in column_names[3:]:
		yy = reservation_percentage_per_hotel[col].tolist()
		zz = {xx[i] : yy[i] for i in range(len(xx))}
		zz = sorted(zz.items(), key=lambda x:x[1])
		rank = {zz[i][0]:len(zz)-i for i in range(len(zz))}
		ranking[col] = [rank[hotel] for hotel in xx]
	#
	workbook = xlsxwriter.Workbook(output_file)
	worksheet = workbook.add_worksheet('All Data')
	createWorksheet(worksheet, column_names, number_of_days, unique_hotels, joined, None)
	#
	for hotel in unique_hotels:
		worksheet = workbook.add_worksheet(hotel)
		createWorksheet(worksheet,column_names,number_of_days,[hotel],joined[joined["Hotel Id"] == hotel], workbook, ranking[ranking["Hotel Id"]==hotel], chart = True)

	workbook.close()



def createWorksheet(worksheet, column_names, number_of_days, unique_hotels, df, workbook, ranking = None, chart = False):
	room_type = column_names[0]
	room_id = column_names[1]
	hotel_id = column_names[2]

	worksheet.write(1,0,room_type)
	worksheet.write(1,1,room_id)
	worksheet.write(1,2,hotel_id)
	day_columns = column_names[3:]
	number_of_entries = df.shape[0]

	worksheet.write(0,3,"Constant")
	worksheet.write(0,3+number_of_days,"Owen")
	col_offset = 3
	for day in range(number_of_days):
		col_index = day + col_offset
		col_name = column_names[col_index]
		worksheet.write(1,col_index, col_name)
		col_index = day + col_offset + number_of_days
		worksheet.write(1,col_index, col_name)
	room_types = {item: {item2.strip(): [] for item2 in df["Room Type"].unique()} for item in unique_hotels}

	row_idx = 2
	for index, row in df.iterrows():
		room_type = row["Room Type"].strip()
		room_id = row["Room Id"]
		hotel_id = row["Hotel Id"]
		room_types[hotel_id][room_type].append(row_idx)
		worksheet.write(row_idx,0,room_type)
		worksheet.write(row_idx,1,room_id)
		worksheet.write(row_idx,2,hotel_id)

		for day in range(number_of_days):
			col_index = day + col_offset
			value = row[ column_names[col_index] ]
			if value != "-":
				value = float(value)
			worksheet.write(row_idx, col_index, value)
			value = row[ column_names[col_index] + " Owen" ]
			if value != "-":
				value = float(value)
			col_index = day + col_offset + number_of_days
			worksheet.write(row_idx, col_index, value)

		row_idx += 1

	row_idx_map = {}
	row_idx += 2
	worksheet.write(row_idx, 2, "Total Reservations")
	worksheet.write(row_idx+1, 2, "Total Reservations Prc")
	row_idx_map["Total Reservations"] = row_idx
	row_idx_map["Total Reservations Prc"] = row_idx + 1
	index_offset = 3
	for idx in range(number_of_days):
		l = __letters[idx+index_offset]
		################################################
		# Total
		################################################
		cell_value = '{'+f'=countif({l}3:{l}{number_of_entries+2},"=-")'+'}'
		worksheet.write_formula(row_idx,idx+index_offset,cell_value)
		cell_value = '{'+f'={l}{row_idx+1}/{number_of_entries}'+'}'
		worksheet.write_formula(row_idx+1,idx+index_offset,cell_value)
		################################################
		# Total Per Room Type
		################################################
		row_offset = 2
		for room_type in ["single","double","triple", "suites"]:
			if room_type in df["Room Type"].unique():
				worksheet.write(row_idx+row_offset, 2, f'{room_type.capitalize()} Reservations')
				row_idx_map[f'{room_type.capitalize()} Reservations'] = row_idx+row_offset
				ranges = [f'countif({l}{min(room_types[hotel_id][room_type])+1}:{l}{max(room_types[hotel_id][room_type])+1},"=-")' for hotel_id in unique_hotels if room_types[hotel_id][room_type]]
				cell_value = '{'+"+".join(ranges)+'}'
				worksheet.write_formula(row_idx+row_offset,idx+index_offset,cell_value)
				worksheet.write(row_idx+row_offset+1, 2, f'{room_type.capitalize()} Reservations Prc')
				row_idx_map[f'{room_type.capitalize()} Reservations Prc'] = row_idx+row_offset+1
				cell_value = '{'+f'={l}{row_idx+row_offset+1}/{number_of_entries}'+'}'
				worksheet.write_formula(row_idx+row_offset+1,idx+index_offset,cell_value)
				row_offset += 2
	if chart:
		################################################4
		# Ranking
		################################################
		worksheet.write(row_idx+row_offset,2,'Reservation Ranking')
		col_idx = 3
		for day in day_columns:
			value = ranking[day].tolist()[0]
			worksheet.write(row_idx+row_offset,col_idx,value)
			col_idx += 1
		################################################4
		# Add Charts....
		################################################
		anchor = df.shape[0] + 20

		chart = workbook.add_chart({'type': 'line'})
		row = row_idx_map["Total Reservations Prc"]
		values = f'{hotel_id}!$D{row}:{__letters[3+number_of_days]}{row}'
		chart.add_series({
					'values': values,
					'marker': {'type': 'automatic'},
					'name' : f'={hotel_id}!$C${row+1}'
				})
		for room_type in ["Single","Double","Triple", "Suites"]:
		# for room_type in ["single", "double", "triple", "suite"]:
			room_type += " Reservations Prc"
			if room_type in row_idx_map:
				row = row_idx_map[room_type]
				values = f'{hotel_id}!$D{row}:{__letters[3+number_of_days]}{row}'
				categories = f'={hotel_id}!$D$2:{__letters[3+number_of_days]}$2'
				chart.add_series({
							'values': values,
							'marker': {'type': 'automatic'},
							'name' : f'={hotel_id}!$C${row+1}',
							'categories': categories
						})
		worksheet.insert_chart(f'A{anchor}',chart,{'x_scale': 6, 'y_scale': 2})

		anchor += 40

		ll = __letters[number_of_days+2].upper()
		for rt in ["single", "double", "triple", "suite"]:
			if rt in room_types[hotel_id]:
				chart = workbook.add_chart({'type':'column'})
				row = room_types[hotel_id][rt][0]
				values = f'={hotel_id}!$D${row+1}:{ll}${row+1}'
				chart.add_series({
					'values': values,
					'marker': {'type': 'automatic'},
					'categories':f'={hotel_id}!$D$2:{ll}$2',
					'name' : [hotel_id, 0,3]
				})
				ll1 = __letters[number_of_days+3].upper()
				ll2 = __letters[2*number_of_days+2].upper()
				values = f'={hotel_id}!${ll1}${row+1}:{ll2}${row+1}'
				chart.add_series({
					'values': values,
					'marker': {'type': 'automatic'},
					'categories':f'={hotel_id}!$D$2:{ll}$2',
					'name' : [hotel_id, 0,3+number_of_days]
				})

				chart.set_title ({'name': f'{hotel_id} {rt}'})
				chart.set_x_axis({'name': 'Day'})
				chart.set_y_axis({'name': 'Price (€)'})

				worksheet.insert_chart(f'A{anchor}',chart,{'x_scale': 6, 'y_scale': 2})
				anchor += 40


def __swaps(df,unique_ids, days):
	df = df.replace('-',-1000)

	for hid in unique_ids:
		tmp = df[ df["Hotel Id"]==hid]
		for room_type in tmp["Room Type"].unique():
			tmp2 = df[ (df["Hotel Id"]==hid) & (df["Room Type"] == room_type)]
			room_id = min(tmp2["Room Id"].tolist())
			head_idx = df.index[df["Room Id"]==room_id].tolist()[0]
			for day in days:
				current_value = df.loc[head_idx][day]
				if current_value==-1000:
					non_booked = tmp2[ tmp2[day]!=-1000]
					if non_booked.size > 0:
						owen_day = day + " Owen"
						swap_idx = df.index[(df["Hotel Id"]==hid) & (df["Room Type"]==room_type) & (df[day]!=-1000)].tolist()[0]
						value = df.loc[swap_idx][day]
						df.at[head_idx,day] = value
						df.at[swap_idx,day] = '-'
						value = df.loc[swap_idx][day + " Owen"]
						df.at[head_idx,day + " Owen"] = value
						df.at[swap_idx,day + "Owen"] = '-'
	df = df.replace(-1000,'-')
	return df
			



if __name__ == "__main__":
	folder = "/home/ageorg/Downloads/Dropbox-CSIC/Dropbox/Tractable Game Theoretic Solutions for Fair Hotel Room Pricing Recommendations/Datasets/results XLSX/new series"

	size = "large"
	city = "Athens"
	incr = 0.17
	number_of_days = 90


	input_file_constant = folder + "/" + f"ROOMS_{city}_{size}_prices_Constant_{number_of_days}_days__{incr}.csv"
	input_owen_file = folder + "/" + f"ROOMS_{city}_{size}_prices_Owen_{number_of_days}_days__{incr}.csv"
	output_file = folder + "/" + f"ROOMS_{city}_{size}_prices_Owen_vs_Constant_{number_of_days}_days__{incr}.xlsx"

	create_new_XLSX(input_file_constant,input_owen_file)

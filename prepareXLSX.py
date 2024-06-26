import xlsxwriter
import pandas as pd
from copy import deepcopy

__letters = {i : chr(ord('`')+(i+1)) for i in range(26)}
for i in range(26):
	for j in range(26):
		v = chr(ord('`')+(i+1))+chr(ord('`')+(j+1))
		idx = (i+1)*26+j
		__letters.update( {idx:v} )

def createWorksheet(workbook,worksheet,df,unique_hotels,ttypes_per_hotel,ttypes_all,ttypes_idx,number_of_columns, chart = False, all_number_of_row=-1):
	df_columns =  list(df.columns)
	number_of_rows = df.shape[0]
	for i in range(number_of_columns):
		value = df_columns[i]
		idx = i
		worksheet.write(0,idx,value)

	maximum_price_range = {'single':-1, 'double':-1, 'triple':-1, 'suite':-1}
	maximum_price_range_idx = {'single':-1, 'double':-1, 'triple':-1, 'suite':-1}
	maximum_price_range_rid = {'single':-1, 'double':-1, 'triple':-1, 'suite':-1}

	row_index = 1
	for index, row in df.iterrows():
		hotel_name = row['Room Id'][:-4]
		room_type  = row['Room Type'].strip()
		ttypes_per_hotel[hotel_name][room_type] += [row_index+2]
		ttypes_all[room_type] += 1

		n = sum( [1 for i in range(2,number_of_columns) if row[df_columns[i]]!='-'] )
		if n>maximum_price_range[room_type]:
			maximum_price_range[room_type] = n
			maximum_price_range_idx[room_type] = row_index + 1
			maximum_price_range_rid[room_type] = row['Room Id']



		for i in range(number_of_columns):
			name = df_columns[i]
			idx = i
			value = row[name] if i<2 or row[name]=='-' else float(row[name])
			worksheet.write(row_index,idx,value)

		row_index += 1


	for i in range(2,number_of_columns):
		if len(unique_hotels)==1:
			worksheet.write(number_of_rows+1,1,f'All Reservations ({unique_hotels[0]})')
		else:
			worksheet.write(number_of_rows+1,1,'All Reservations (Total)')

		l = __letters[i]
		cell_idx = f'{l.upper()}{number_of_rows+2}'
		cell_value = '{'+f'=countif({l}2:{l}{number_of_rows+1},"=-")'+'}'

		worksheet.write_formula(cell_idx,cell_value)

		for t in ttypes_all:
			if len(unique_hotels)==1:
				worksheet.write(number_of_rows+1+ttypes_idx[t],1,f'{t.capitalize()} Reservations ({unique_hotels[0]})')
			else:
				worksheet.write(number_of_rows+1+ttypes_idx[t],1,f'{t.capitalize()} Reservations (Total)')

			if ttypes_all[t]>0:
				cell_idx = f'{l.upper()}{number_of_rows+2+ttypes_idx[t]}'
				cell_value = []

				for hotel in unique_hotels:
					if len(ttypes_per_hotel[hotel][t])>0:
						min_val = min(ttypes_per_hotel[hotel][t])-1
						max_val = max(ttypes_per_hotel[hotel][t])-1

						cell_range = f'{l}{min_val}:{l}{max_val}'

						cell_value += [f'countif({cell_range},"=-")']
				cell_value = '{ ='+ '+'.join(cell_value) + ' }'

				worksheet.write_formula(cell_idx,cell_value)


	ttypes_ll = {'single':'A', 'double':'F', 'triple':'K', 'suite':'P'}
	if chart:
		anchor = number_of_rows + 10
		for t in ttypes_all:

			if ttypes_all[t]>0:

				chart = workbook.add_chart({'type': 'line'})
				ll = __letters[number_of_columns-1].upper()



				values = f'=Data!$C${all_number_of_row+2+ttypes_idx[t]}:{ll}${all_number_of_row+2+ttypes_idx[t]}'
				chart.add_series({
					'values': values,
					'marker': {'type': 'automatic'},
					'name' : f'=Data!$B${all_number_of_row+2+ttypes_idx[t]}'
				})

				values = f'={hotel_name}!$C${number_of_rows+2}:{ll}${number_of_rows+2}'
				chart.add_series({
					'values': values,
					'marker': {'type': 'automatic'},
					'name' : f'={hotel_name}!$B${number_of_rows+2}'
				})

				values = f'={hotel_name}!$C${number_of_rows+2+ttypes_idx[t]}:{ll}${number_of_rows+2+ttypes_idx[t]}'
				chart.add_series({
					'values': values,
					'marker': {'type': 'automatic'},
					'categories':f'={hotel_name}!$C$1:{ll}$1',
					'name' : f'={hotel_name}!$B${number_of_rows+2+ttypes_idx[t]}'
				})
				chart.set_title ({'name': f'Total vs Hotel Reservations\n{hotel_name}'})
				chart.set_x_axis({'name': 'Day'})
				chart.set_y_axis({'name': 'Number of Reservations'})

				worksheet.insert_chart(f'A{anchor}',chart,{'x_scale': 6, 'y_scale': 2})
				anchor += 40
				# 
				chart = workbook.add_chart({'type':'column'})
				ll = __letters[number_of_columns-1].upper()

				values = f'={hotel_name}!$C${maximum_price_range_idx[t]}:{ll}${maximum_price_range_idx[t]}'
				# print(values)
				chart.add_series({
					'values': values,
					'marker': {'type': 'automatic'},
					'categories':f'={hotel_name}!$C$1:{ll}$1',
					'name' : [hotel_name, maximum_price_range_idx[t]-1,1]
				})
				chart.set_title ({'name': f'Room Price'})
				chart.set_x_axis({'name': 'Day'})
				chart.set_y_axis({'name': 'Price (€)'})

				worksheet.insert_chart(f'A{anchor}',chart,{'x_scale': 6, 'y_scale': 2})
				anchor += 40


def createXLSX(input_file):
	df = pd.read_csv(input_file)


	unique_hotels = df["Hotel Id"].unique().tolist()
	df.drop("Hotel Id", inplace = True, axis=1)

	output_file = input_file.split('.csv')[0] + '.xlsx'
	workbook = xlsxwriter.Workbook(output_file)

	worksheet = workbook.add_worksheet('Data')


	df_columns =  list(df.columns)
	number_of_columns = len(df_columns)
	ll = __letters[number_of_columns-1]


	ttypes_per_hotel = {
		hotel:{	'single':[], 'double':[], 'triple':[], 'suite':[] } for hotel in unique_hotels
		}
	ttypes_all = {'single':0, 'double':0, 'triple':0, 'suite':0}
	ttypes_idx = {'single':1, 'double':2, 'triple':3, 'suite':4}
	
	createWorksheet(workbook,worksheet,df,unique_hotels,deepcopy(ttypes_per_hotel),ttypes_all,ttypes_idx,number_of_columns)		

	for hotel in unique_hotels:
		worksheet = workbook.add_worksheet(hotel)

		ttypes_hotel = {
			'single':len(ttypes_per_hotel[hotel]['single']), 
			'double':len(ttypes_per_hotel[hotel]['double']),
			'triple':len(ttypes_per_hotel[hotel]['triple']),
			'suite':len(ttypes_per_hotel[hotel]['suite'])}
		createWorksheet(workbook,worksheet,df[df['Room Id'].str.startswith(hotel)],[hotel],deepcopy(ttypes_per_hotel),ttypes_hotel,ttypes_idx,number_of_columns,True,df.shape[0])
	workbook.close()

if __name__ == '__main__':
	
	input_file = '/home/ageorg/Documents/Hotel Room Pricing/results/ROOMS_Barcelona_small_prices.csv'
	createXLSX(input_file)

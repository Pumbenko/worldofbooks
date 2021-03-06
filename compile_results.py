import os

import pandas as pd
import glob

def compile_results():
	dirs=[x[0] for x in os.walk(f'{os.getcwd()}/temp/')][1:]
	for dir in dirs:
		name=dir.split('/')[-1:][0]
		path = f'{dir}/*.csv'
		all_files = glob.glob(path)
		li = []
		for filename in all_files:
			df = pd.read_csv(filename, sep=';', index_col=None, header=0, error_bad_lines=False)
			li.append(df)

		frame = pd.concat(li, axis=0, ignore_index=True)
		frame.to_csv('frame.csv', sep=';', index=None)
		with pd.ExcelWriter( f'{os.getcwd()}/{name}_result.xlsx', engine='openpyxl') as writer:
			frame.to_excel(writer, sheet_name='Result_combined', startrow=0, startcol=0, index=False)
			writer.save()

compile_results()
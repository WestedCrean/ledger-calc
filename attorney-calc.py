import numpy as np
import pandas as pd
import xlrd
import xlsxwriter 
import datetime

def opening_balance_structure(input_df,opening_balance):

    cols=['CLIENT MATTER', 'SETTLEMENTS','DISBURSED','DIFFERENTIAL','OPENING BALANCE']
    to_show=['CLIENT MATTER', 'OPENING BALANCE']

    attny = pd.DataFrame(columns=cols)
    output_df = pd.DataFrame(columns=cols)


    output_df['CLIENT MATTER'] = input_df['CLIENT MATTER']
    
    output_df['DISBURSED'] = input_df['Outgoing']
    output_df['SETTLEMENTS'] = input_df['Incoming']
    atny = output_df[(output_df['CLIENT MATTER'] == 'Attorney Fees')|(output_df['CLIENT MATTER'] == 'ATTORNEY FEES')|(output_df['CLIENT MATTER'] == 'attorney fees')]
    output_df = output_df.sort_values('CLIENT MATTER')
    output_df = output_df.groupby('CLIENT MATTER').sum()

    output_df = output_df.reset_index()
    
    output_df['DIFFERENTIAL'] = output_df['SETTLEMENTS'] + output_df['DISBURSED']

    atny = output_df[(output_df['CLIENT MATTER'] == 'Attorney Fees')|(output_df['CLIENT MATTER'] == 'Attorney fees')|(output_df['CLIENT MATTER'] == 'attorney fees')]
    idx = atny.index[0]
    output_df = output_df.drop(output_df.index[idx])
    atny = atny.reset_index(drop=True)

    output_df = pd.concat([atny, output_df])
    output_df = output_df.reset_index(drop=True)

    # opening balance 
    output_df['OPENING BALANCE'] = 0
    output_df['OPENING BALANCE'] = output_df[ (output_df['DIFFERENTIAL'] < 0)]['DIFFERENTIAL'] * -1
    output_df.iloc[0,4] = 0 
    output_df.iloc[0,4] = (opening_balance - output_df['OPENING BALANCE'].sum())
    output_df = output_df[['CLIENT MATTER','OPENING BALANCE']]

    return output_df
   
def calculateLedger(input_file, start_date, end_date):
    inputdataframe = pd.read_excel(input_file, sheet_name='Ledger', header=[0], converters={'Client Matter': str})
    input_ledger = inputdataframe[ ( start_date <= inputdataframe['DATE'] ) & ( inputdataframe['DATE']  <= end_date ) ]
    return input_ledger


input_file = 'inputFile.xlsx'
output_file = 'outputFile.xlsx'

opening_balance= 396145.16
start_date = '1/12/2015'
end_date = '10/12/2015'

ledger = calculateLedger(input_file, start_date, end_date)

df = opening_balance_structure(ledger, opening_balance)

# save df
writer = pd.ExcelWriter(output_file,engine='xlsxwriter',
                date_format = 'yyyy/mm/dd', 
                datetime_format='yyyy/mm/dd'
                )
df.to_excel(writer, index=False, sheet_name='Output data')

workbook = writer.book
worksheet = writer.sheets['Output data']

money_fmt = workbook.add_format({'num_format': '$#,##0'})

worksheet.set_column('B:B', 20, money_fmt)
worksheet.set_column('A:A',35)
writer.save()

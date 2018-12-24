import json
import boto3
import os
import numpy as np
import pandas as pd

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

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key'] 
        file = key.rsplit('/', 1)[-1]
        
        download_path = 'inputFiles/{}'.format(key)
        upload_path = 'outputFiles/{}'.format(file)




    
    try:
        localFilename = '/tmp/{}'.format(os.path.basename(key))
        s3.download_file(Bucket=bucket, Key=key, Filename=localFilename)

        input_file = localFilename
        output_file = localFilename

        with open(localFilename, "r") as data:
            # file opened
            
            opening_balance= 396145.16
            start_date = '1/12/2015'
            end_date = '10/12/2015'






            s3.upload_file(localFilename,bucket,upload_path)
            return {
                'statusCode': 200,
                'body': json.dumps('' + str(df.to_json(orient='split')) + ' was saved.')
            }
    except Exception as e: 
       print('exception')
       return {
           'statusCode': 404,
           'body': json.dumps(str(e))
       }
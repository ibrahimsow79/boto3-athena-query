#!/usr/bin/env python3.11

"""" 
This program is build to run the athena query that builds the aws backup report 
"""

import boto3
import time

# Create a Boto3 client for Athena
session = boto3.Session (
  region_name='eu-west-1'
)

athena_client = session.client('athena')
print(athena_client)


region = 'eu-west-1',
catalog = 'AwsDataCatalog'
database = 'awsbackup-reporting'
query_string = 'select * from "AwsDataCatalog"."awsbackup-reporting"."awsbackup-resource-reportingcrossaccount"'
output_location = 's3://s3-awsbackup-reports-claranet/queryresults/'
maxresults = 10000000000



def execute_athena_query(query_string, database, catalog, output_location):
    response = athena_client.start_query_execution(
        QueryString=query_string,
        QueryExecutionContext={
            'Database': database,
            'Catalog': catalog 
        }, 
        ResultConfiguration={
            'OutputLocation': output_location  
        }
    )
    return response['QueryExecutionId'] 

def get_query_status(query_execution_id):
    response = athena_client.get_query_execution(
        QueryExecutionId=query_execution_id)
    print(f"{response['QueryExecution']['Status']['State']}")
    
    return response['QueryExecution']['Status']['State'] 

def get_query_results(query_execution_id, maxresults):
    response = athena_client.get_query_results(
        QueryExecutionId=query_execution_id,
        MaxResults=maxresults
    )
   # Process and print/ query results
    for row in response['ResultSet']['Rows']:
        print([field['VarCharValue'] for field in row['Data'] ] ) 

    
if __name__ == '__main__':
    query_execution_id = execute_athena_query(query_string, database, catalog, output_location)
    print(f"query_execution_id is equal to {query_execution_id}")

    while get_query_status(query_execution_id) == 'RUNNING':
        print("Query is still running ....")
        time.sleep(5)
        
    if get_query_status(query_execution_id) == 'SUCCEEDED':
        print("Query Succeeded!!!!!")
        get_query_results(query_execution_id)
    else:
        print("Query failed or was cancelled")
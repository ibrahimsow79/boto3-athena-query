#!/usr/bin/env python3.11

"""" 
This program is build to run the athena query that builds the aws backup report 
"""

import boto3
import time
import re

# Create a Boto3 client for Athena
session = boto3.Session (
  region_name='eu-west-1'
)

athena_client = session.client('athena')

region = 'eu-west-1',
catalog = 'AwsDataCatalog'
database = 'awsbackup-reporting'
query_string = 'select "account id", "region", "job status", "status message", "resource arn", "resource type", "creation date" from "AwsDataCatalog"."awsbackup-reporting"."awsbackup-backupjobs-reportingcrossaccount" where (concat_ws('-',"partition_1", "partition_2", "partition_3") = to_iso8601(current_date)) and (("status message" is not null and "status message" <> '') or  "job status" = "FAILED")'
output_location = 's3://s3-awsbackup-reports-claranet/queryresults/report-isow-results'
maxresults = 100



def execute_athena_query(query_string, database, catalog, output_location):
    """"
    This function will execute the athena query
    Inputs are the : QueryString, QueryExecutionContext (Database, Catalog and OutputLocation)
    Ouptut is QueryExectionId
    """
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
        QueryExecutionId=query_execution_id
    )
   
    return response['QueryExecution']['Status']['State'] 

def get_query_results(query_execution_id, maxresults):
    response = athena_client.get_query_results(
        QueryExecutionId=query_execution_id,
        MaxResults=maxresults
    )
   # Process and print/ query results
   #  for row in response['ResultSet']['Rows']:
   #     print([field['VarCharValue'] for field in row['Data'] ] ) 

    
if __name__ == '__main__':
    query_execution_id = execute_athena_query(query_string, database, catalog, output_location)
    print(f"query_execution_id is equal to {query_execution_id}")

    while get_query_status(query_execution_id) in ['QUEUED', 'RUNNING']:
        print("Query is being queued or running  ....")
        time.sleep(2)
   
    if get_query_status(query_execution_id) == 'SUCCEEDED':
        print("Query Succeeded!!!!!")
       
        get_query_results(query_execution_id, maxresults)
        filename = f"s3://s3-awsbackup-reports-claranet/queryresults/report-isow-results/{query_execution_id}.csv/"
        print(f"the filename containing the results is: {filename}")
    else:
        print("Query failed or was cancelled")
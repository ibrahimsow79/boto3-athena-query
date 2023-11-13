"""" 
This program is build to run the athena query that builds the aws backup report 
"""
import boto3

# Create a Boto3 client for Athena
session = boto3.Session (
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region='eu-west-1'
)
athena_client = boto3.client('athena', region_name = 'eu-west-1')

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
        QueryExecutionId=query_execution_id
    )
    return response['QueryExecution']['Status']['State'] 

def get_query_results(query_execution_id, maxresults):
    response = athena_client.get_query_results(
        QueryExecutionId=query_execution_id
        MaxResults=maxresults
    )
   # Process and print/ query results
   for row in response['ResultSet']['Rows']:
    print([field['VarCharValue'] for field in row['Data'] ] ) 

    
    if __name__ == "__main__":
        while get_query_status(query_execution_id) == 'RUNNING':
            print("Query is still running ....")
            time.sleep(5)
        
        if get_query_status(query_execution_id) == 'SUCCEDEED':
            print("Query Succeded!!!!!")
            get_query_results(query_execution_id)
        else:
            print("Query failed or was cancelled")


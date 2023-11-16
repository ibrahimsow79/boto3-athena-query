from pyathena import connect

# Connect to Athena
conn = connect(s3_staging_dir='s3://s3-awsbackup-reports-claranet/queryresults/report-isow-results', region_name='eu-west-1')

# Execute the query
cursor = conn.cursor()
query = 'select * from "AwsDataCatalog"."awsbackup-reporting"."awsbackup-resource-reportingcrossaccount"'
cursor.execute(query)
 
# Get the query result location

query_execution_id = cursor._query_execution_id
query_result_location = f"s3://s3-awsbackup-reports-claranet/queryresults/report-isow-results/{query_execution_id}.csv/"


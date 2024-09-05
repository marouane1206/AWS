from bedrock import test_bedrock,generate_budget_report
from db import get_customer_transations,prettyprint

def lambda_handler(event,context):

    # This code tests access to the database printing the users transaction statement
    
    # prettyprint(get_customer_transations())
    
    # This code tests access to bedrock api 
    
    print(test_bedrock())
    
    # This code generates the customer transaction report using the db and the bedrock model
    
    # transactions = get_customer_transations()
    # print(generate_budget_report(transactions))

import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
class Connector:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name=os.environ['AWS_REGION']
        )

    def scan(self, table_name):
        table = self.dynamodb.Table(table_name)
        res = table.scan()['Items']
        return res
    
    def get_item(self, table_name, key):
        table = self.dynamodb.Table(table_name)
        res = table.get_item(Key= key)
        if res.get('Item') is None:
            raise KeyError(key)
        return res.get('Item')
    
    def scan_w_filter(self, table_name, filter_expression):
        table = self.dynamodb.Table(table_name)
        res = table.scan(
            FilterExpression=filter_expression
        )
        return res['Items']
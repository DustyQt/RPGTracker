from src.data.connector import Connector

def __init__(self):
    self.connector = Connector()

def call_query(self):
    query='select * from stats'
    response = self.connector.query(query)
    print(response)

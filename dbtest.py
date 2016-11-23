from neo4jrestclient import client

class Connection:
    def __init__(self, conn_file):
        data = None
        with open(conn_file, 'r') as f:
            data = f.read().split()
        self.url = data[0]
        self.username = data[1]
        self.password = data[2]
        self.connect(data[0], data[1], data[2])

    def connect(self, url, uname, pwd):
        self.gdb = client.GraphDatabase(url, username=uname, password=pwd)
        return self.gdb

    # item name -> find location name
    # return: (code, message to read)
    def find_location(self, item_name='Pencil'):
        # query returns 0!!
        # TODO: make a query / test data
        query = """match (n:Item {name:"%s"})-[r:LOCATED_AT {active:1}]->(l:Location) return l.name""" % item_name
        results = self.gdb.query(query, returns=(str))
        location_name =''
        if len(results) > 0:
            print(results)
            location_name = '' # TODO: from the results!
        else:
            # cannot find the item
            print('No item named %s' % item_name)
            return (-1, 'No item named %s' % item_name)
        return (1, location_name)

    def set_location(self, item_name, location_name):
        # TODO: make a query / test data
        query = """match ..."""
        results = self.gdb.query(query, returns=(str))
        if len(results) > 0:
            print(results)
        else:
            print('error - multiple cases')
        return None

if __name__ == "__main__":
    conn = Connection('connection.txt')
    conn.find_location()

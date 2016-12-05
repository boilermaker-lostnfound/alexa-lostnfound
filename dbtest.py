from neo4jrestclient import client
import time
import boto3
import os

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

    def iotconfig(self):
        os.environ['AWS_CONFIG_FILE'] = '~/.aws/config'
        self.iotclient = boto3.client('iot-data')

    # not planning to use
    def literal_test(self, literal):
        return "input voice is " + literal

    # item name -> find location name
    # return: (code, message to read)
    def find_location(self, item_name='Backpack'):
        item_name = item_name.capitalize()
        # TODO: location with reader -> active==1 & timestamp-now < 5mins?
        # if nfctag is connected:
        #    if timestamp - now < 5mins: call beep(), return l.name
        #    else: return msg('the item was l.name t-now seconds ago. not now')
        # else:
        #    return l.name
        query = """match (n:Item {name:"%s"})-[r:LOCATED_AT {active:"1"}]->(l:Location) return l.name""" % item_name
        results = self.gdb.query(query, returns=(str))
        #print(results.elements) #[['Office Table']]
        location_name =''
        if len(results) > 0:
            print(results[0])
            location_name = str(results[0][0])
        else:
            # cannot find the item
            print('No item named %s' % item_name)
            return (-1, 'No item named %s' % item_name)
        return (1, location_name)

    def find_location_beep(self, nfcid):
        #TODO:beeep! AWS IOT -> policy check
        #TODO: payload -> should contain nfcid
        #           -> every raspberry receive data, but this specific one
        #              with the id should beep
        iodata = self.iotclient.publish(
                topic='ios',
                qos=0,
                payload='start'
        )


    def set_location(self, item_name, location_name):
        """add item to an existing or new location
        """
        # TODO: redundant data.. Keeps generating relation
        timestamp = str(int(time.time()))
        location_name = location_name.capitalize()
        item_name = item_name.capitalize()
        query = """MATCH (:Item{name:"%s"}) - [rel:LOCATED_AT] -> (:Location) SET rel.active=0
        MERGE (item:Item{name:"%s"}) MERGE (location:Location{name:"%s"}) MERGE (item) - [r:LOCATED_AT { active:1, timestamp:%s}] -> (location)"""\
                %(item_name, item_name, location_name, timestamp)
        results = self.gdb.query(query) # this query returns[]
        print(results.elements)

    def add_new_location(self, location_name):
        query = """MERGE (location:Location{name:"%s"})""" % location_name
        results = self.gdb.query(query)

    def add_new_item(self, item_name):
        query = """MERGE (item:Item{name:"%s"})""" % item_name
        results = self.gdb.query(query)

#    #under developing
#    def recommend_by_item:
#        query = """  """
#        results = self.gdb.query(query)
#
#    def recommend_by_item_timestamp:
#        query = """  """
#        results = self.gdb.query(query)
#
#    def recommend_by_item_category:
#        query = """  """
#        results = self.gdb.query(query)
#
#    def recommend_by_item_category_weight:
#        query = """  """
#        results = self.gdb.query(query)

if __name__ == "__main__":
    conn = Connection('connection.txt')
    conn.iotconfig()
    res = conn.find_location('pencil')
    #res = conn.find_location_beep()
    #conn.find_location_beep()

    #conn.set_location('Headphone', 'Bedroom Table')
    

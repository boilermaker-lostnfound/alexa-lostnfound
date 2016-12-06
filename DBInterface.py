from neo4jrestclient import client
import time
import boto3
import os

class DBInterface:
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
        os.environ['AWS_CONFIG_FILE'] = './.aws/config'
        self.iotclient = boto3.client('iot-data')

    # not planning to use
    def literal_test(self, literal):
        return "input voice is " + literal

    # return: (code, message to read)
    def find_location(self, item_name='Backpack'):
        item_name = item_name.capitalize()
        # TODO:
        # if nfctag is connected:
        #    if timestamp - now < 5mins: call beep(), return l.name
        #    else: return msg('the item was l.name t-now seconds ago. not now')
        # else:
        #    return l.name
        query = """match (n:Item {name:"%s"})-[r:LOCATED_AT ]->(l:Location) return l.name""" % item_name
#        query = """
#        match (item:Item{name:"%s"})-[r1:LOCATED_AT{active:1}]->(location:Location) 
#        optional match (tag:NFCTag)-[r2:CONNECTED_TO]->(item) 
#        optional match (:RaspberryPi)-[:PLACED_AT]->(location) 
#        return location.name as location, (1480975071 - toInt(r1.timestamp)) as timecap, (case when tag is null then false else true end) as nfc_connected
#        """
        results = self.gdb.query(query, returns=(str))
        print(results.elements) #[['Office Table']]

        location_name =''
        if len(results) > 0:
            print(results[0])
            location_name = str(results[0][0])
            print(location_name)
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
        query ="""MERGE (item:Item{name:"%s"}) 
        MERGE (location:Location{name:"%s"}) with item, location
        optional MATCH (:Item{name:"%s"}) - [rel:LOCATED_AT] -> (:Location) 
            SET rel.active=0 with item, location
        MERGE (item) - [r:LOCATED_AT { active:1, timestamp:"%s"}] -> (location)
        """ % (item_name, location_name, item_name, timestamp)
        results = self.gdb.query(query) # this query returns[]

    def add_new_location(self, location_name):
        location_name = location_name.capitalize()
        query = """MATCH (l:Location {name:"%s"}) return l.name""" % location_name
        results = self.gdb.query(query)
        if len(results) > 0:
            return (-1, 'Already exists.')
        else:
            query = """MERGE (location:Location {name:"%s"})""" % location_name
            results = self.gdb.query(query)
            return (1, 'Succeeded. ')

    def add_new_item(self, item_name):
        item_name = item_name.capitalize()
        query = """MATCH (item:Item {name:"%s"}) return item.name""" % item_name
        results = self.gdb.query(query)
        if len(results) > 1: # Must TODO: should be 0
            return (-1, 'Already exists.')
        else:
            query = """MERGE (item:Item {name:"%s"})""" % item_name
            results = self.gdb.query(query)
            return (1, 'Succeeded. ')

    def get_recommendation(self, item_name):
        item_name = item_name.capitalize()
        query = """
        MATCH (i:Item{name:"%s"})-[r:LOCATED_AT]->(l:Location) 
        WITH count(r) AS TOTAL_COUNT
        MATCH (i:Item{name:"%s"})-[r:LOCATED_AT]->(l:Location) 
        RETURN l.name AS Location, (count(r)*1.0/ TOTAL_COUNT*1.0) AS Weight
        ORDER BY Weight DESC
        """%(item_name, item_name)
        results = self.gdb.query(query)
        return results[0][0]

    def get_categories(self):
        query = """MATCH (c:Category) return c.name"""
        results = self.gdb.query(query,returns=(str))
        lst = [results[i][0] for i in range(len(results.elements))]
        return lst

    def set_category(self, item_name, category_name):
        #TODO: DB constraints....!
        category_name = category_name.capitalize()
        item_name = item_name.capitalize()
        query = """MATCH (i:Item {name: "%s"}) MERGE (c:Category {name: "%s"})
            MERGE (i)-[h:HAS_CATEGORY]->(c)""" %(item_name, category_name)
        results = self.gdb.query(query,returns=(str))
        #TODO: check needed? how to check? have return code?

if __name__ == "__main__":
    conn = DBInterface('connection.txt')
    conn.iotconfig()
    res = conn.find_location('phone')
    res = conn.find_location_beep()
    conn.find_location_beep()
    conn.set_location('Headphone', 'Bedroom Table')
    conn.get_recommendation('Headphone')

# Queries needed in this project

## Scenario 1: Find location
* Using the item name as input, return location name
> match (n:Item {name:"%s"})-[r:LOCATED_AT {active:"1"}]->(l:Location) return l.name

## Scenario 2: Set location of an item
* Add a item to a new location
1. set all remaining relation between the item and all location to inactive ("active=0")
2. create new active relation, even item and location doesnt exists in the database

> MATCH (:Item{name:"Headphone"}) - [rel:LOCATED_AT] -> (:Location) SET rel.active=0

> MERGE (item:Item{name:"Headphone"}) MERGE (location:Location{name:"Bedroom Table"}) MERGE (item) - [r:LOCATED_AT { active:1, timestamp:1480380695}] -> (location)

* Add new location
> MERGE (location:Location{name:"Bedroom Table"})
* Add new item
> MERGE (item:Item{name:"Headphone"})

## Scenario 3: Get location recommendation
* Get location recommondation by item
> MATCH (i:Item{name:"Headphone"})-[r:LOCATED_AT]->(l:Location) 
WITH count(r) AS TOTAL_COUNT
MATCH (i:Item{name:"Headphone"})-[r:LOCATED_AT]->(l:Location) 
RETURN l.name AS Location, (count(r)*1.0/ TOTAL_COUNT*1.0) AS Weight
ORDER BY Weight DESC

* Get location recommondation by item consider timestamp
> MATCH (i:Item{name:"Headphone"})-[r:LOCATED_AT]->(l:Location) 
WITH count(r) AS TOTAL_COUNT
MATCH (i:Item{name:"Headphone"})-[r:LOCATED_AT]->(l:Location) 
WITH (count(r)*1.0/ TOTAL_COUNT*1.0) AS Weight,l,(1480459596-toInt(r.timestamp)) as timecap
WITH collect({location: l.name, weight: Weight*(100.0/timecap*1.0)}) AS results
UNWIND results AS row
RETURN row.location AS Location, sum(row.weight) AS Weight
ORDER BY Weight DESC

* Get location recommondation by category item
> MATCH (i:Item{name:"Headphone"})-[r:HAS_CATEGORY]->(c:Category) 
WITH c
MATCH (c)<-[]-()-[r:LOCATED_AT]->(:Location) 
WITH count(r) AS TOTAL_COUNT
MATCH (i:Item{name:"Headphone"})-[r:HAS_CATEGORY]->(c:Category) 
WITH c, TOTAL_COUNT
MATCH (c)<-[]-()-[r:LOCATED_AT]->(l:Location) 
RETURN l.name AS Location, count(r)*1.0/TOTAL_COUNT*1.0 AS Weight
ORDER BY Weight DESC

* Get location recommondation item and category combined, with weights item recommondation = 1 and category recommondation = 1.2
> MATCH (i:Item{name:"Headphone"})-[r:LOCATED_AT]->(l:Location) 
WITH count(r) AS TOTAL_COUNT
MATCH (i:Item{name:"Headphone"})-[r:LOCATED_AT]->(l:Location) 
WITH (count(r)*1.0/ TOTAL_COUNT*1.0) AS Weight,l
WITH collect({location: l.name, weight: Weight*1 }) AS itemResult

> MATCH (i:Item{name:"Headphone"})-[r:HAS_CATEGORY]->(c:Category) 
WITH c,itemResult
MATCH (c)<-[]-()-[r:LOCATED_AT]->(:Location) 
WITH count(r) AS TOTAL_COUNT,itemResult
MATCH (i:Item{name:"Headphone"})-[r:HAS_CATEGORY]->(c:Category) 
WITH c, TOTAL_COUNT,itemResult
MATCH (c)<-[]-()-[r:LOCATED_AT]->(l:Location) 
WITH (count(r)*1.0/ TOTAL_COUNT*1.0) AS Weight,l,itemResult
WITH itemResult + collect({location: l.name, weight: Weight*1.2 }) AS results
UNWIND results AS row
RETURN row.location AS Location, sum(row.weight) AS Weight
ORDER BY Weight DESC

# Queries needed in this project

## Scenario 1: Find location
* Using the item name as input, return location name
> match (n:Item {name:"%s"})-[r:LOCATED_AT {active:"1"}]->(l:Location) return l.name

## Scenario 2: Set location of an item

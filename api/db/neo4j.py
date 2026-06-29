import os
from neo4j import GraphDatabase


class Neo4jDB:
    def __init__(self):
        self.driver = None

    def connect(self):
        if self.driver is None:
            self.driver = GraphDatabase.driver(
                f"bolt://{os.getenv('NEO4J_HOST')}:{os.getenv('NEO4J_BOLT_PORT')}",
                auth=(
                    os.getenv("NEO4J_USER"),
                    os.getenv("NEO4J_PASSWORD"),
                ),
            )
            print("✓ Connected to Neo4j")

    async def disconnect(self):
        if self.driver is not None:
            self.driver.close()
            self.driver = None
            print("✓ Neo4j connection closed")


db_neo4j = Neo4jDB()
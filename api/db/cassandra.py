# api/db/cassandra.py
import os
from cassandra.cluster import Cluster
from typing import Optional

class CassandraManager:
    def __init__(self):
        self.cluster: Optional[Cluster] = None
        self.session = None

    def connect(self):
        if not self.cluster:
            host = os.getenv("CASSANDRA_HOST", "timeseries-db")
            port = int(os.getenv("CASSANDRA_PORT", "9042"))
            
            self.cluster = Cluster([host], port=port)
            self.session = self.cluster.connect()
            
            self.session.execute("""
                CREATE KEYSPACE IF NOT EXISTS gridsense
                WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
            """)
            self.session.set_keyspace("gridsense")

    def disconnect(self):
        if self.cluster:
            self.cluster.shutdown()
            self.cluster = None
            self.session = None

    def get_session(self):
        if not self.session:
            raise RuntimeError("Cassandra session is not initialized.")
        return self.session

# Ensure it is exported cleanly as db_cassandra
db_cassandra = CassandraManager()
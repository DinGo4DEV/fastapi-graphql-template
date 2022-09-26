from functools import reduce
from arango import ArangoClient
from arango.database import StandardDatabase
from arango.result import Result
from arango.graph import Graph
from typing import List, Optional
from arango import exceptions
class ArangoManager:
    
    class TransactionDB:
        def __init__(self,db:StandardDatabase,collection:str):
            self.db = db
            self.col = ArangoManager.get_or_create_vertex_collection(db,collection)
    
        def __enter__(self):        
            self.session = self.db.begin_transaction(read=self.col.name, write=self.col.name)
            
            # print(self.session.transaction_id)
            return self.session
        
        def __exit__(self,type,value,traceback):
            if type or value:
                self.session.abort_transaction()
                # print(type,value)
                return 
            return self.session.commit_transaction()
    
    @staticmethod
    def get_or_create_vertex_collection(db:StandardDatabase,collection:str,auto_increase=False):
        
        if not db.has_collection(collection):
            return db.create_collection(collection) if not auto_increase else db.create_collection(collection,key_generator="autoincrement",key_increment=1)
        else:
            return db.collection(collection)
        
    @staticmethod
    def get_or_create_edge_collection(graph:Result[Graph],collection:str,from_vertex_collection=List[str],to_vertex_collections=List[str]):
        if not graph.has_edge_collection(collection):
            return graph.create_edge_definition(
                    edge_collection=collection,
                    from_vertex_collections=from_vertex_collection,
                    to_vertex_collections=to_vertex_collections
                )
        else:
            return graph.edge_collection(collection)
        
    @staticmethod
    def get_or_create_view(db:StandardDatabase,view_name,collections:List[str],link:Optional[dict]):
        try:
            return db.view(view_name)
        except exceptions.ViewGetError:
            if not collections:
                raise IndexError("Empty collections, please specific one")
            
            def _create_basic_link(collection:str):
                return {collection: {
                    "analyzers": [
                        "zh",
                        "en",
                        "identity"
                    ],
                    "includeAllFields": True,
                    "storeValues": "none",
                    "trackListPositions": False
                    }
                }
                
            ##https://www.arangodb.com/docs/stable/http/views-arangosearch.html
            view_property = {
                "links": reduce(
                    lambda x,y: x|y
                    , map(_create_basic_link,collections)) if not link else link
            }
            db.create_view(view_name,"arangosearch",view_property)
    
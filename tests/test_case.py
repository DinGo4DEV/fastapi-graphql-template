from concurrent.futures import ThreadPoolExecutor
from typing import List
from urllib import response
from app.managers.account_manager import ACCOUNT_COLLECTION, AccountManager
from app.models.branch import Branch
from app.models.user import AgentUser, AgentUserInDB, MasterUserInDB, MasterAgentUserInput, PlusUser, PlusUserIn, PlusUserInDB
from faker import Faker
import logging
from functools import reduce
import json
import operator
import pytest
from app.models.config import config
from app.managers.arango_manager import ArangoManager
from arango.database import StandardDatabase
from arango import ArangoClient
from app.models.http_client import HTTPClient
from fastapi.testclient import TestClient
from app.main import app
from pydantic import parse_obj_as
from uuid import UUID, uuid4
from fastapi.encoders import jsonable_encoder
from app.utils.encoder import custom_encoder

ARANGO_CONFIG = config['datasource']['ARANGO']
TEST_DB = "epc-test"
logger = logging.getLogger()
BATCH_SIZE= 5000

fake = Faker(['zh_TW'])

TEST_PLUS_ID = "test_ac"
TEST_MASTER_ID = "test_master_ac"

@pytest.fixture
def db(scope='session', autouse=True):
    client = ArangoClient(hosts=ARANGO_CONFIG["url"],http_client=HTTPClient())
    db = client.db(TEST_DB, username=ARANGO_CONFIG['username'],password=ARANGO_CONFIG['password'],verify=False)
    yield db
    col = db.collection(ACCOUNT_COLLECTION)
    col.delete_match({"plusId":TEST_PLUS_ID},sync=True)

@pytest.fixture
def client():
    client = TestClient(app)
    return client
    
def test01_01_account_manager_create_plus_user(client:TestClient,db: StandardDatabase):
    user:PlusUserInDB = PlusUserInDB(plus_id=TEST_PLUS_ID)
    AccountManager.create_or_update_user(db,user)
        

# def test01_02_account_manager_create_master_user(db: StandardDatabase):
#     user: MasterUserInput = 

# def test01_03_account_manager_update_plus_to_agent(client: TestClient,db: StandardDatabase):
#     user:AgentUserInDB = AgentUser(plus_id=TEST_PLUS_ID,email=fake.email(),company_id=)
    

@pytest.mark.skip(reason="Skip now")
def test02_add_history(client: TestClient,db: StandardDatabase):
    with ArangoManager.TransactionDB(db,"listing") as txn_db:
        col = txn_db.collection("listing")
        listings = list(col.all())
        
    with ArangoManager.TransactionDB(db,ACCOUNT_COLLECTION) as txn_db:
        col = txn_db.collection(ACCOUNT_COLLECTION)        
        for i in range(BATCH_SIZE):        
            users = list(col.all(skip=i*BATCH_SIZE,limit=BATCH_SIZE))
            logger.info(len(users))
            if not users:
                break
            users_db = parse_obj_as(List[PlusUserInDB],users)
            def _add_listing_history(user):
                nonlocal listings,client
                for listing in fake.random_elements(elements=listings, length=fake.random_int(min=5,max=200), unique=True):
                    response = client.post(f"/history/listing/add",json={
                        "user": jsonable_encoder(user,by_alias=True,custom_encoder=custom_encoder()),
                        "listingId": listing['listingId']
                    })
                    logger.info(f"user {user.plus_id} add history")
            for result in ThreadPoolExecutor(max_workers=5).map( _add_listing_history,users_db):
                print(result)
            # for user in users_db:
            #     for listing in fake.random_choices(elements=listings, length=fake.random_int(max=50)):
            #         response = client.post(f"/history/listing/add",json={
            #             "user": jsonable_encoder(user,by_alias=True,custom_encoder=custom_encoder()),
            #             "listingId": listing['listingId']
            #         })
            #         assert response.status_code == 200
    
    
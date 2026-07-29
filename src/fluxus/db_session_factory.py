from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session
from fluxus.settings import PIPELINE_STORE_ADDRESS



def create_pipeline_store_session() -> Session:
    engine = create_engine(PIPELINE_STORE_ADDRESS)
    return Session(bind=engine)
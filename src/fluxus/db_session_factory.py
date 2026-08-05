from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session
from fluxus.settings import RUNTIME_STORE


def create_pipeline_store_session() -> Session:
    engine = create_engine(RUNTIME_STORE)
    return Session(bind=engine)

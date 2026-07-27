from sqlalchemy import create_engine
from fluxus.settings import PIPELINE_STORE_ADDRESS
from fluxus.models.orm import FluxusORM

engine = create_engine(PIPELINE_STORE_ADDRESS)

if __name__ == "__main__":
    FluxusORM.metadata.create_all(engine)
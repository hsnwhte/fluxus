from sqlalchemy import create_engine, text

from pluggle.strategies.fetch.db_fetch_strategy import DBFetchStrategy

POSTGRES_URL = "postgresql://postgres:testpass@localhost:5432/postgres"


def check():
    engine = create_engine(POSTGRES_URL)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS dialect_check"))
        conn.execute(
            text("CREATE TABLE dialect_check (id INTEGER PRIMARY KEY, test_data TEXT)")
        )
        conn.execute(
            text(
                "INSERT INTO dialect_check (id, test_data) VALUES (1, 'postgres works')"
            )
        )
        conn.commit()

    result = DBFetchStrategy.fetch(address=POSTGRES_URL, table_name="dialect_check")
    print(result.content)
    print(result.source_format)


if __name__ == "__main__":
    check()

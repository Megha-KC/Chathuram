from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from collections import defaultdict


# Init database
# engine = create_engine("mysql+pymysql://admin:password@127.0.0.1:3306/test")
engine = None
session = None
insp = None


# Return list of all tables in the db
def get_tables_in_db():
    return insp.get_table_names()


def get_columns(self, table_name, schema=None, **kw):
    with self._operation_context() as conn:
        col_defs = self.dialect.get_columns(
            conn, table_name, schema, info_cache=self.info_cache, **kw
        )
    # remove single quotes within double quotes
    for col_def in col_defs:
        if col_def["default"] is not None:
            col_def["default"] = "".join(col_def["default"].split("'"))
    return col_defs


def get_foreignkey(ins):
    tables = get_tables_in_db()
    fk_list = defaultdict(list)
    for table in tables:
        for fk in ins.get_foreign_keys(table):
            fk_list[fk["referred_table"]].append(fk)
    return fk_list


# Return column metadata associated with a table
def get_metadata(table):
    metadata = get_columns(insp, table)
    # Making the column objects json serializable
    for col in metadata:
        col["type"] = str(col["type"])
        col["value"] = "" if col["default"] is None else col["default"]
    # f_key = get_foreignkey(insp)[table]
    # metadata.append(f_key)
    return metadata


# Choose the correct driver
def pick_db_driver(db_type):
    if db_type == "mysql":
        return "mysql+pymysql"
    elif db_type == "postgres":
        return "postgresql+psycopg2"


# Handle special cases in incoming data before insertion/updation
def clean_data(row, table):
    meta = get_metadata(table)
    row_keys = list(row.keys())
    for idx, col in enumerate(meta):
        # BIT type in MySQL cannot take a string as input, so convert to int instead
        if col["type"] == "BIT":
            row[row_keys[idx]] = int(row[row_keys[idx]])
    return row


# Establish connection:
def establish_connection(username, password, url, port, db_name, db_type):
    global session, insp, engine
    db_driver = pick_db_driver(db_type)
    engine = create_engine(
        "{0}://{1}:{2}@{3}:{4}/{5}".format(
            db_driver, username, password, url, port, db_name
        )
    )
    session = Session(engine)
    insp = inspect(engine)
    return True

    # Create classes that map to the tables
    # This only works for tables that have a primary key
    # Base.prepare(engine, reflect=True)
    # Test
    # Sample is the name of a table in the db with columns "name" and "age"
    # smp = Base.classes.sample
    # Print all rows in sample
    # temp = session.query(smp).all()
    # for t in temp:
    # print(t.name, t.age)

import typing
import datetime as dt
from sqlalchemy import (Engine, Connection, MetaData, Table, Column, BigInteger, TIMESTAMP, TEXT)
from sqlalchemy import (create_engine, bindparam)


class Record(typing.TypedDict):
    id: int
    time_stamp: dt.datetime
    content: str


class Chronicle:
    """
    Permanent memory of raw knowledge.

    Usage:

        chronicle = Chronicle("mysql+mysqldb://scott:tiger@localhost/test")
        with chronicle.begin() as con:
            chronicle.insert(con, content="Bridgekeeper: What... is the air-speed velocity of an unladen swallow?")
            chronicle.insert(con, content="King: What do you mean? An African or a European swallow?")
        with chronicle.connect() as con:
            with con.begin():
                chronicle.insert(con, content="Dennis: Help! Help! I'm being repressed!")
    """
    _engine: Engine
    _created: bool
    table: Table
    meta_data: MetaData

    def __init__(
            self,
            url: str,
            pool_size: int = 1,
            max_overflow: int = 2,
    ) -> None:
        """
        Configure engine and prep queries.

        :param url: DB connection URL
        :param pool_size: connection pool size
        :param max_overflow: connection pool size
        """
        self._created = False
        self.meta_data = MetaData()
        self.table = Table(
            "chronicle",
            self.meta_data,
            Column("id", BigInteger, primary_key=True, autoincrement=True),
            Column("time_stamp", TIMESTAMP, nullable=False, index=True, comment="time fo creation"),
            Column("content", TEXT, nullable=False),
            comment="each row is one record of knowledge produced or gained",
        )
        self._engine = create_engine(url, pool_size=pool_size, max_overflow=max_overflow)

        # queries
        self._range_scan = self.table.select(
        ).where(
            self.table.c.time_stamp.between(bindparam("lower"), bindparam("upper"))
        ).order_by(
            self.table.c.time_stamp.asc()
        )
        self._get_one = self.table.select().where(self.table.c.id == bindparam("key"))
        self._get_many = self.table.select().where(self.table.c.id.in_(bindparam("keys", expanding=True))).order_by(
            self.table.c.time_stamp.asc()
        )

    @property
    def engine(self) -> Engine:
        """Get sqlalchemy engine. Getter handles lazy init."""
        if not self._created:
            self.meta_data.create_all(self.engine, checkfirst=True)
            self._created = True
        return self._engine

    def connect(self):
        """check out pooled connection"""
        return self.engine.connect()

    def begin(self):
        """transaction with checked out pooled connection"""
        return self.engine.begin()

    def insert(
            self,
            con: Connection,
            content: str,
            time_stamp: typing.Optional[dt.datetime] = None,
    ) -> Record:
        """
        Create new row.
        :param con: database connection
        :param content: knowledge to insert
        :param time_stamp: creation stamp
        :return: inserted row
        """
        time_stamp_: dt.datetime = time_stamp or dt.datetime.utcnow()
        cur = con.execute(self.table.insert(), {"time_stamp": time_stamp_, "content": content})
        id_ = cur.inserted_primary_key
        return {"id": id_, "time_stamp": time_stamp_, "content": content}

    def find_one_or_none(
            self,
            con: Connection,
            id_: int,
    ) -> typing.Union[Record | None]:
        """
        Select one rows by id, if record does not exist return None instead
        :param con: database connection
        :param id_: row primary key
        """
        record = None
        cur = con.execute(self._get_one, {"key": id_})
        for row in cur:
            record = {"id": row.id, "time_stamp": row.time_stamp, "content": row.content}
        if cur and not cur.closed:
            cur.close()
        return record

    def find_many(
            self,
            con: Connection,
            ids: list[int],
    ) -> list[Record]:
        """
        Select many rows by id. len(returned) <= len(ids). Ordered by `created`.
        :param con: database connection
        :param ids: rows primary keys
        """
        cur = con.execute(self._get_many, {"keys": ids})
        records = [{"id": row.id, "time_stamp": row.time_stamp, "content": row.content} for row in cur]
        if cur and not cur.closed:
            cur.close()
        return records

    def range(
            self,
            con: Connection,
            lower: dt.datetime,
            upper: dt.datetime,
    ) -> list[Record]:
        """
        Time scan of knowledge. Ordered by `created`.
        :param con: database connection
        :param lower: time range lower boundary of creation time_stamp
        :param upper: time range upper boundary of creation time_stamp
        """
        cur = con.execute(self._range_scan, {"lower": lower, "upper": upper})
        records = [{"id": row.id, "time_stamp": row.time_stamp, "content": row.content} for row in cur]
        if cur and not cur.closed:
            cur.close()
        return records

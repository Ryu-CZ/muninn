import typing
import datetime as dt
from sqlalchemy import (Engine, Connection, MetaData, Table, Column, BigInteger, TIMESTAMP, TEXT,
                        create_engine, bindparam)


class Record(typing.TypedDict):
    id: int
    time_stamp: dt.datetime
    content: str


class Chronicle:
    """Permanent memory of raw knowledge"""
    _engine: Engine
    created: bool
    table: Table
    meta_data: MetaData

    def __init__(self, url: str) -> None:
        self.created = False
        self.meta_data = MetaData()
        self.table = Table(
            "chronicle",
            self.meta_data,
            Column("id", BigInteger, primary_key=True, autoincrement=True),
            Column("time_stamp", TIMESTAMP, nullable=False, index=True, comment="time fo creation"),
            Column("content", TEXT, nullable=False),
            comment="each row is one record of knowledge produced or gained",
        )
        self._engine = create_engine(url, pool_size=1, max_overflow=2)
        self._range_scan = self.table.select(
        ).where(
            self.table.c.time_stamp.between(bindparam("lower"), bindparam("upper"))
        ).order_by(
            self.table.c.time_stamp.asc()
        )
        self._get_one = self.table.select().where(self.table.c.id==bindparam("key"))
        self._get_many = self.table.select().where(self.table.c.id.in_(bindparam("keys", expanding=True))).order_by(
            self.table.c.time_stamp.asc()
        )

    @property
    def engine(self) -> Engine:
        if not self.created:
            self.meta_data.create_all(self.engine, checkfirst=True)
            self.created = True
        return self._engine

    def insert(
            self,
            content: str,
            time_stamp: typing.Optional[dt.datetime] = None,
    ) -> Record:
        """
        Create new row
        :param content: knowledge to insert
        :param time_stamp: creation stamp
        :return: inserted row
        """
        time_stamp_: dt.datetime = time_stamp or dt.datetime.utcnow()
        with self.engine.begin() as con:
            cur = con.execute(self.table.insert(), {"time_stamp": time_stamp_, "content": content})
            id_ = cur.inserted_primary_key
        return {"id": id_, "time_stamp": time_stamp_, "content": content}

    def get_one(self, id_: int) -> typing.Optional[Record]:
        """Select one rows by id, if does not exist return None"""
        con: Connection
        record = None
        with self.engine.begin() as con:
            cur = con.execute(self._get_one, {"key": id_})
            for row in cur:
                record = {"id": row.id, "time_stamp": row.time_stamp, "content": row.content}
        return record

    def get_many(self, ids: list[int]) -> list[Record]:
        """Select many rows by id. len(returned) <= len(ids)"""
        with self.engine.begin() as con:
            cur = con.execute(self._get_many, {"keys": ids})
            return [{"id": row.id, "time_stamp": row.time_stamp, "content": row.content} for row in cur]

    def range(self, lower: dt.datetime, upper: dt.datetime) -> list[Record]:
        """Time scan of knowledge"""
        with self.engine.begin() as con:
            cur = con.execute(self._range_scan, {"lower": lower, "upper": upper})
            return [{"id": row.id, "time_stamp": row.time_stamp, "content": row.content} for row in cur]

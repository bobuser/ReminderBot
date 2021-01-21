from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, Dict, Any

from sqlalchemy import create_engine, Column, Integer, PickleType
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from telegram.ext import DictPersistence

base = declarative_base()

class Storage(base):
    __tablename__ = "storage"
    id = Column(Integer, primary_key=True)
    bot_data = Column(PickleType)
    chat_data = Column(PickleType)
    user_data = Column(PickleType)
    conversations = Column(PickleType)
    bot_data_json = Column(JSON)
    chat_data_json = Column(JSON)
    user_data_json = Column(JSON)


class PsqlPersistence(DictPersistence):
    # postgresql+psycopg2://USER:PASS@address:5432/db
    db = create_engine(str(open("connection.txt", "r").readline()).strip(), echo=True)
    base.metadata.create_all(db)
    Session = sessionmaker(db)
    session = Session()

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)

    def get_user_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        query = self.session.query(Storage).first()
        if query:
            print("user existing: ", query.user_data)
            self._user_data = query.user_data
        else:
            print("user not existing")
            self._user_data = defaultdict(dict)
        return deepcopy(self.user_data)

    def get_chat_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        query = self.session.query(Storage).first()
        if query:
            self._chat_data = query.chat_data
        else:
            self._chat_data = defaultdict(dict)
        return deepcopy(self.chat_data)

    def get_bot_data(self) -> Dict[Any, Any]:
        query = self.session.query(Storage).first()
        if query:
            self._bot_data = query.bot_data
        else:
            self._bot_data = {}
        return deepcopy(self.bot_data)  # type: ignore[arg-type]

    def flush(self) -> None:
        query = self.session.query(Storage).first()
        if not query:
            storage = Storage(bot_data=self._bot_data, chat_data=self._chat_data, user_data=self._user_data,
                          bot_data_json=self.bot_data_json, user_data_json=self.user_data_json,
                          chat_data_json=self.chat_data_json)
            self.session.add(storage)
        else:
            storage = query
            storage.bot_data = self.bot_data
            storage.chat_data = self.chat_data
            storage.user_data = self.user_data
            storage.bot_data_json = self.bot_data_json
            storage.chat_data_json = self.chat_data_json
            storage.user_data_json = self.user_data_json
        # self.session.flush()
        self.session.commit()
        print("Data saved successfully")

    def __init__(self):
        super().__init__()

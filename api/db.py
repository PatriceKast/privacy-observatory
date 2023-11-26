import os
import logging

from datetime import datetime
from typing import Optional, Iterator, Any, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    select,
    ForeignKey,
    Boolean,
    Interval,
    create_engine,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import asc, desc
from sqlalchemy import or_, and_, func, cast, extract

from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from flask import current_app as APP


SessionLocal = sessionmaker()

def init_db(app) -> None:
    app.logger.info("Initializing database")

    engine = create_engine('postgresql://' + os.environ['DB_USER'] + ':' + os.environ['DB_PASSWORD'] + '@' + os.environ['DB_HOST'] + ':5432/' + os.environ['DB_DATABASE'])
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(engine)

    app.logger.info("Success")

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key = True)
    name: Mapped[str] = Column(String(32), index = True)
    email: Mapped[str] = Column(String(32), index = True)
    password_hash: Mapped[str] = Column(String(128))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 600):
        s = Serializer(APP.config['SECRET_KEY'])
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(session, token):
        s = Serializer(APP.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token

        user = session.query(Users).get(data['id'])
        return user

class Workers(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    token: Mapped[str] = mapped_column(String)
    heartbeat_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Domains(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Domainsets(Base):
    __tablename__ = "domainsets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    generator: Mapped[str] = mapped_column(String) # must be maybe a blob instead of a string
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Measurements(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String)
    value: Mapped[str] = mapped_column(String) # must be maybe a blob instead of a string
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    domain_id: Mapped[Optional[int]] = mapped_column(ForeignKey("domains.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Studys(Base):
    __tablename__ = "studys"

    id: Mapped[int] = mapped_column(primary_key=True)
    domainset_id: Mapped[int] = mapped_column(ForeignKey("domainsets.id"))
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), nullable=True) # not yet implemented, but can be used in the future to specify specific workers for execution of the study
    name: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    composefile: Mapped[str] = mapped_column(String) # must be maybe a blob instead of a string
    output_format: Mapped[str] = mapped_column(String) # must be maybe a blob instead of a string
    cron_schedule: Mapped[str] = mapped_column(String)
    next_scan_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    scan_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    complete_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    heartbeat_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Runs(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("studys.id"))
    output: Mapped[str] = mapped_column(String)
    duration: Mapped[datetime] = mapped_column(Interval)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
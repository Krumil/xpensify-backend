from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import create_engine, Column, BigInteger, String, Float, DateTime, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import CreateSchema
from utils import AlchemyEncoder
import json
import os

# Database connection setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Settlement(Base):
    __tablename__ = 'Settlements'
    __table_args__ = {'schema': 'expense_schema'}
    id = Column(BigInteger, primary_key=True)
    payerId = Column(String, ForeignKey('expense_schema.Users.tgId'))
    receiverId = Column(String, ForeignKey('expense_schema.Users.tgId'))
    amount = Column(Float)
    status = Column(String)  # e.g., 'pending', 'completed', 'cancelled'
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    payer = relationship("User", foreign_keys=[payerId], back_populates="settlementsPaid")
    receiver = relationship("User", foreign_keys=[receiverId], back_populates="settlementsReceived")


# Define models
class User(Base):
    __tablename__ = 'Users'
    __table_args__ = {'schema': 'expense_schema'}
    id = Column(BigInteger, primary_key=True)
    tgId = Column(String, unique=True, nullable=False)
    username = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    groupMemberships = relationship("GroupMember", back_populates="user")
    settlementsPaid = relationship("Settlement", foreign_keys=[Settlement.payerId], back_populates="payer")
    settlementsReceived = relationship("Settlement", foreign_keys=[Settlement.receiverId], back_populates="receiver")
    

class Wallet(Base):
    __tablename__ = 'Wallets'
    __table_args__ = {'schema': 'expense_schema'}
    id = Column(String, primary_key=True)
    userId = Column(BigInteger, ForeignKey('expense_schema.Users.id'), unique=True)
    walletId = Column(String, unique=True)
    seed = Column(String)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="wallet")

class Group(Base):
    __tablename__ = 'Groups'
    __table_args__ = {'schema': 'expense_schema'}
    id = Column(BigInteger, primary_key=True)
    tgId = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    currency = Column(String, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    members = relationship("GroupMember", back_populates="group")

class GroupMember(Base):
    __tablename__ = 'GroupMembers'
    __table_args__ = {'schema': 'expense_schema'}
    id = Column(BigInteger, primary_key=True)
    userId = Column(BigInteger, ForeignKey('expense_schema.Users.id'))
    groupId = Column(BigInteger, ForeignKey('expense_schema.Groups.id'))
    joinedAt = Column(DateTime, default=datetime.utcnow)
    isAdmin = Column(Boolean, default=False)
    balance = Column(Float, default=0)
    user = relationship("User", back_populates="groupMemberships")
    group = relationship("Group", back_populates="members")
    transactions = relationship("Transaction", back_populates="groupMember")

class Transaction(Base):
    __tablename__ = 'Transactions'
    __table_args__ = {'schema': 'expense_schema'}
    id = Column(BigInteger, primary_key=True)
    groupMemberId = Column(BigInteger, ForeignKey('expense_schema.GroupMembers.id'))
    description = Column(String)
    amount = Column(Float)
    date = Column(DateTime)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    groupMember = relationship("GroupMember", back_populates="transactions")

# Database initialization and session management
def init_db():
    with engine.connect() as connection:
        schema_exists = connection.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'expense_schema'")).fetchone()
        if not schema_exists:
            connection.execute(CreateSchema('expense_schema'))
            connection.commit()
    
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Helper functions for database operations
def create_user(tgId: str, username: str, firstName: str, lastName: str, session=None):
    def _create_user(session):
        user = User(tgId=tgId, username=username, firstName=firstName, lastName=lastName)
        session.add(user)
        session.flush()
        return user

    if session:
        return _create_user(session)
    else:
        with session_scope() as session:
            return _create_user(session)

def get_or_create_user(tgId: str, username: str, firstName: str, lastName: str, session=None):
    def _get_or_create_user(session):
        user = session.query(User).filter_by(tgId=tgId).first()
        if not user:
            user = create_user(tgId, username, firstName, lastName, session)
        return user

    if session:
        return _get_or_create_user(session)
    else:
        with session_scope() as session:
            return _get_or_create_user(session)

def create_group(name: str, description: str, currency: str, tgId: str, session=None):
    def _create_group(session):
        group = Group(name=name, description=description, currency=currency, tgId=tgId)
        session.add(group)
        session.flush()
        return group

    if session:
        return _create_group(session)
    else:
        with session_scope() as session:
            return _create_group(session)
        
def update_group(tgId: str, name: str, description: str, currency: str, session=None):
    def _update_group(session):
        group = session.query(Group).filter_by(tgId=tgId).first()
        if group:
            group.name = name
            group.description = description
            group.currency = currency
            group.updatedAt = datetime.utcnow()
            session.flush()
        return group

    if session:
        return _update_group(session)
    else:
        with session_scope() as session:
            return _update_group(session)		

def add_user_to_group(userId: int, groupId: int, isAdmin: bool = False, session=None):
    def _add_user_to_group(session):
        groupMember = GroupMember(userId=userId, groupId=groupId, isAdmin=isAdmin)
        session.add(groupMember)
        session.flush()
        return groupMember

    if session:
        return _add_user_to_group(session)
    else:
        with session_scope() as session:
            return _add_user_to_group(session)

def create_transaction(groupMemberId: int, description: str, amount: float, date: datetime, session=None):
    def _create_transaction(session):
        transaction = Transaction(groupMemberId=groupMemberId, description=description, amount=amount, date=date)
        session.add(transaction)
        
        groupMember = session.query(GroupMember).get(groupMemberId)
        groupMember.balance += amount
        
        session.flush()
        return transaction

    if session:
        return _create_transaction(session)
    else:
        with session_scope() as session:
            return _create_transaction(session)

def create_settlement(payerTgId: str, receiverTgId: str, amount: float, session=None):
    def _create_settlement(session):
        settlement = Settlement(payerId=payerTgId, receiverId=receiverTgId, amount=amount, status='pending')
        session.add(settlement)
        session.flush()
        return settlement

    if session:
        return _create_settlement(session)
    else:
        with session_scope() as session:
            return _create_settlement(session)

def get_group_balance(groupId: int, session=None):
    def _get_group_balance(session):
        groupMembers = session.query(GroupMember).filter_by(groupId=groupId).all()
        return {member.user.tgId: member.balance for member in groupMembers}

    if session:
        return _get_group_balance(session)
    else:
        with session_scope() as session:
            return _get_group_balance(session)
        

def get_user_from_tgId(tgId: str, session=None):
    def _get_user_from_tgId(session):
        user = session.query(User).filter_by(tgId=tgId).first()
        return json.loads(json.dumps(user, cls=AlchemyEncoder))

    if session:
        return _get_user_from_tgId(session)
    else:
        with session_scope() as session:
            return _get_user_from_tgId(session)
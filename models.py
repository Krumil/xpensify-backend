from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

Base = declarative_base()

class ChatMessage(BaseModel):
    role: str
    content: dict

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    totalExpenses = Column(Float)
    averagePerPerson = Column(Float)
    currency = Column(String)
    lastUpdated = Column(DateTime)
    members = relationship("Member", back_populates="group")
    transactions = relationship("Transaction", back_populates="group")
    settlements = relationship("Settlement", back_populates="group")

class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    userId = Column(String)
    paid = Column(Float)
    receives = Column(Float, nullable=True)
    groupId = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group", back_populates="members")
    transactions = relationship("Transaction", back_populates="member")

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    description = Column(String)
    amount = Column(Float)
    date = Column(DateTime)
    memberId = Column(Integer, ForeignKey('members.id'))
    member = relationship("Member", back_populates="transactions")
    groupId = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group", back_populates="transactions")

class Settlement(Base):
    __tablename__ = 'settlements'

    id = Column(Integer, primary_key=True)
    fromUserId = Column(String)
    toUserId = Column(String)
    amount = Column(Float)
    groupId = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group", back_populates="settlements")
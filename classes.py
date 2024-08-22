from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: dict

class Transaction(BaseModel):
    description: str
    amount: float
    date: str

class GroupMember(BaseModel):
    userId: int
    tgId: str
    username: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    paid: float
    transactions: List[Transaction]

class Group(BaseModel):
    id: int
    tgId: str
    name: str
    description: Optional[str]
    currency: str
    members: List[GroupMember]
    
class User(BaseModel):
    id: int
    tgId: str
    username: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    balance: float
    createdAt: str
    updatedAt: str

class ExpenseTrackingOutput(BaseModel):
    group: Group
    totalExpenses: float
    averagePerPerson: float
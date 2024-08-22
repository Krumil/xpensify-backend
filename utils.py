from typing import Dict, List, Any
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.ext.declarative import DeclarativeMeta
import json

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # Convert SQLAlchemy model to dictionary
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)

def calculate_settlement(expenseData: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Calculate the settlement transactions based on the expense data.
    
    :param expenseData: Dictionary containing the expense tracking data
    :return: List of settlement transactions
    """
    # Convert relevant values to Decimal for precise calculations
    totalExpenses = Decimal(str(expenseData['totalExpenses']))
    averagePerPerson = Decimal(str(expenseData['averagePerPerson']))
    
    # Calculate how much each person owes or is owed
    balances = {}
    for member in expenseData['group']['members']:
        userId = member['tgId']
        paid = Decimal(str(member['paid']))
        balance = paid - averagePerPerson
        balances[userId] = balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Separate into those who owe money and those who are owed
    debtors = [(userId, -amount) for userId, amount in balances.items() if amount < 0]
    creditors = [(userId, amount) for userId, amount in balances.items() if amount > 0]
    
    # Sort both lists by amount (largest first)
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)
    
    # Calculate settlements
    settlements = []
    while debtors and creditors:
        debtor, debt = debtors.pop(0)
        creditor, credit = creditors.pop(0)
        
        if debt > credit:
            settlements.append({
                "fromUserId": debtor,
                "toUserId": creditor,
                "amount": float(credit)
            })
            debtors.insert(0, (debtor, debt - credit))
        elif credit > debt:
            settlements.append({
                "fromUserId": debtor,
                "toUserId": creditor,
                "amount": float(debt)
            })
            creditors.insert(0, (creditor, credit - debt))
        else:
            settlements.append({
                "fromUserId": debtor,
                "toUserId": creditor,
                "amount": float(debt)
            })
    
    return settlements
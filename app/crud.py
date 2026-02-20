from sqlalchemy.orm import Session
from . import models, schemas, auth

# 1. Создание пользователя
def create_user(db: Session, user: schemas.UserCreate):
    safe_password = user.password[:50] 
    hashed_pwd = auth.get_password_hash(safe_password)
    db_user = models.User(username=user.username, hashed_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 2. Создание транзакции (ТОЛЬКО ОДНА ФУНКЦИЯ, С USER_ID)
def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(
        amount=transaction.amount,
        category=transaction.category,
        type=transaction.type,
        description=transaction.description,
        owner_id=user_id  # Привязываем к конкретному пользователю
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# 3. Получение списка транзакций пользователя
def get_transactions(db: Session, user_id: int):
    return db.query(models.Transaction).filter(models.Transaction.owner_id == user_id).all()

# 4. Получение баланса пользователя
def get_balance(db: Session, user_id: int):
    user_txs = db.query(models.Transaction).filter(models.Transaction.owner_id == user_id)
    
    incomes = user_txs.filter(models.Transaction.type == "income").all()
    expenses = user_txs.filter(models.Transaction.type == "expense").all()
    
    total_income = sum(t.amount for t in incomes)
    total_expense = sum(t.amount for t in expenses)
    
    return {"balance": total_income - total_expense}
    
# 5. Удаление транзакции
def delete_transaction(db: Session, transaction_id: int):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return True
    return False
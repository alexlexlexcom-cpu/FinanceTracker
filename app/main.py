from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database 
from .database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from . import auth
from .auth import get_current_user
from fastapi.middleware.cors import CORSMiddleware

# 1. Создаем таблицы
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# 2. Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# 3. Создание транзакции (POST)
@app.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # ИСПРАВЛЕНО: вызываем crud.create_transaction и передаем user_id
    return crud.create_transaction(db=db, transaction=transaction, user_id=current_user.id)

# 4. Просмотр транзакций (GET)
@app.get("/transactions/", response_model=list[schemas.Transaction])
def read_transactions(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_transactions(db, user_id=current_user.id)

# 5. Баланс (GET)
@app.get("/balance/") 
def get_balance(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_balance(db, user_id=current_user.id)

# 6. Удаление (DELETE)
@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    success = crud.delete_transaction(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Successfully deleted"}

# 7. Регистрация (POST)
@app.post("/users/", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# 8. Логин (POST)
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
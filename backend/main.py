from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List

import models, schemas, auth, ai_service, seed
from database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bashkiria Discovery API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@app.on_event("startup")
def on_startup():
    db = next(get_db())
    seed.init_db(db)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except auth.JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update streak
    now = datetime.utcnow()
    if user.last_active_date:
        days_diff = (now.date() - user.last_active_date.date()).days
        if days_diff == 1:
            user.streak_days += 1
        elif days_diff > 1:
            user.streak_days = 0 # Streak broken
    else:
        user.streak_days = 1 # First login today

    user.last_active_date = now
    db.commit()

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/levels", response_model=List[schemas.LevelResponse])
def get_levels(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    levels = db.query(models.Level).order_by(models.Level.order_index).all()
    # Add tasks to each level
    for level in levels:
        level.tasks = db.query(models.Task).filter(models.Task.level_id == level.id).all()
    return levels

@app.get("/levels/{level_id}/tasks", response_model=List[schemas.TaskResponse])
def get_tasks_for_level(level_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.level_id == level_id).all()
    return tasks

@app.post("/tasks/{task_id}/submit", response_model=schemas.AnswerResult)
def submit_answer(task_id: int, answer_submit: schemas.AnswerSubmit, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user_answer = answer_submit.answer
    is_correct = False
    feedback = None
    stars = None
    xp_earned = 0

    if task.type == "choice" or task.type == "translate":
        # Check standard answer directly
        if user_answer.strip().lower() == task.correct_answer.strip().lower():
            is_correct = True
            xp_earned = 10
            feedback = "Правильно!"
        else:
            is_correct = False
            if task.type == "translate":
                # Smart Fail
                ai_feedback = ai_service.analyze_translation_error(task.question, task.correct_answer, user_answer)
                feedback = ai_feedback if ai_feedback else "Ответ неверный." # Graceful Degradation fallback
            else:
                feedback = "Ответ неверный."

    elif task.type == "scenario":
        # Check scenario
        ai_result = ai_service.evaluate_scenario(task.question, user_answer)
        stars = ai_result.get("stars", 2)
        feedback = ai_result.get("feedback", "Ответ принят.")
        is_correct = True # Scenario is generally accepted
        xp_earned = stars * 10

    # Track Progress
    progress = db.query(models.UserTasksProgress).filter(
        models.UserTasksProgress.user_id == current_user.id,
        models.UserTasksProgress.task_id == task_id
    ).first()

    if not progress:
        progress = models.UserTasksProgress(
            user_id=current_user.id,
            task_id=task_id,
            is_completed=is_correct,
            attempts_count=1,
            stars_earned=stars if stars else 0,
            last_attempt_date=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.attempts_count += 1
        progress.last_attempt_date = datetime.utcnow()
        if is_correct and not progress.is_completed:
            progress.is_completed = True
        if stars and stars > progress.stars_earned:
            progress.stars_earned = stars # Keep best stars

    if is_correct:
        current_user.total_xp += xp_earned

    db.commit()

    # Check if level is completed to increment current_level
    level_tasks = db.query(models.Task).filter(models.Task.level_id == task.level_id).all()
    level_task_ids = [t.id for t in level_tasks]

    completed_progresses = db.query(models.UserTasksProgress).filter(
        models.UserTasksProgress.user_id == current_user.id,
        models.UserTasksProgress.task_id.in_(level_task_ids),
        models.UserTasksProgress.is_completed == True
    ).all()

    if len(completed_progresses) == len(level_tasks):
        # All tasks in this level are completed
        level = db.query(models.Level).filter(models.Level.id == task.level_id).first()
        if current_user.current_level <= level.order_index:
            current_user.current_level = level.order_index + 1
            db.commit()

    return schemas.AnswerResult(
        is_correct=is_correct,
        feedback=feedback,
        stars=stars,
        xp_earned=xp_earned
    )

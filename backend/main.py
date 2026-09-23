from fastapi import FastAPI, Request, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

from backend.database import engine, Base, get_db
from backend import models, auth
from backend.gemini_service import ask_gemini
from backend.quiz import generate_quiz
from backend.summary import summarize_text
from backend.roadmap import generate_roadmap
from backend.pdf_reader import extract_text_from_pdf

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EduGenie AI",
    description="AI Powered Educational Assistant",
    version="4.0"
)

# Add Session Middleware for secure session cookies
app.add_middleware(
    SessionMiddleware, secret_key="edugenie_super_secret_session_key_2026"
)

# ==========================================
# Static Files & Templates
# ==========================================

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def render_template(template_name: str, request: Request, db: Session, context: dict = None):
    if context is None:
        context = {}
    current_user = auth.get_current_user(request, db)
    context.update({"request": request, "current_user": current_user})
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context
    )


# ==========================================
# Request Models
# ==========================================

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Question(BaseModel):
    question: str


class QuizRequest(BaseModel):
    topic: str
    difficulty: str
    num_questions: int


class SummaryRequest(BaseModel):
    text: str


class RoadmapRequest(BaseModel):
    topic: str


# ==========================================
# Authentication Routes
# ==========================================

@app.get("/login-page")
def login_page(request: Request, db: Session = Depends(get_db)):
    if auth.get_current_user(request, db):
        return RedirectResponse(url="/dashboard", status_code=303)
    return render_template("login.html", request, db)


@app.get("/signup-page")
def signup_page(request: Request, db: Session = Depends(get_db)):
    if auth.get_current_user(request, db):
        return RedirectResponse(url="/dashboard", status_code=303)
    return render_template("signup.html", request, db)


@app.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        (models.User.username == user_data.username) | (models.User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already registered."
        )

    hashed_pwd = auth.hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"success": True, "message": "Account registered successfully."}


@app.post("/login")
def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        (models.User.username == login_data.username) | (models.User.email == login_data.username)
    ).first()

    if not user or not auth.verify_password(user.password_hash, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    request.session["user_id"] = user.id
    return {"success": True, "username": user.username}


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


# ==========================================
# Page Routes
# ==========================================

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    return render_template("index.html", request, db)


@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    return render_template("dashboard.html", request, db)


@app.get("/ask-page")
def ask_page(request: Request, db: Session = Depends(get_db)):
    return render_template("ask.html", request, db)


@app.get("/quiz-page")
def quiz_page(request: Request, db: Session = Depends(get_db)):
    return render_template("quiz.html", request, db)


@app.get("/summary-page")
def summary_page(request: Request, db: Session = Depends(get_db)):
    return render_template("summary.html", request, db)


@app.get("/roadmap-page")
def roadmap_page(request: Request, db: Session = Depends(get_db)):
    return render_template("roadmap.html", request, db)


@app.get("/history")
def history(request: Request, db: Session = Depends(get_db)):
    return render_template("history.html", request, db)


# ==========================================
# Feature APIs with Database Persistence
# ==========================================

@app.post("/ask")
def ask(question: Question, request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user(request, db)
    answer = ask_gemini(question.question)

    if user:
        chat_entry = models.ChatHistory(
            user_id=user.id,
            question=question.question,
            answer=answer
        )
        db.add(chat_entry)
        db.commit()

    return {"answer": answer}


@app.post("/quiz")
def quiz(quiz_req: QuizRequest, request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user(request, db)
    quiz_data = generate_quiz(
        quiz_req.topic,
        quiz_req.difficulty,
        quiz_req.num_questions
    )

    if user:
        quiz_entry = models.QuizResult(
            user_id=user.id,
            topic=quiz_req.topic,
            difficulty=quiz_req.difficulty,
            score=0,
            total_questions=quiz_req.num_questions
        )
        db.add(quiz_entry)
        db.commit()

    return {"quiz": quiz_data}


@app.post("/summary")
def summary(summary_req: SummaryRequest, request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user(request, db)
    summary_result = summarize_text(summary_req.text)

    if user:
        summary_entry = models.SummaryLog(
            user_id=user.id,
            source_type="text",
            summary_text=summary_result
        )
        db.add(summary_entry)
        db.commit()

    return {"summary": summary_result}


@app.post("/roadmap")
def roadmap(roadmap_req: RoadmapRequest, request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user(request, db)
    roadmap_result = generate_roadmap(roadmap_req.topic)

    if user:
        roadmap_entry = models.RoadmapLog(
            user_id=user.id,
            topic=roadmap_req.topic,
            roadmap_content=roadmap_result
        )
        db.add(roadmap_entry)
        db.commit()

    return {"roadmap": roadmap_result}


@app.post("/upload-pdf")
async def upload_pdf(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = auth.get_current_user(request, db)
    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    extracted_text = extract_text_from_pdf(file_path)
    if not extracted_text.strip():
        return {"summary": "No readable text found in the PDF."}

    summary_result = summarize_text(extracted_text)

    if user:
        summary_entry = models.SummaryLog(
            user_id=user.id,
            source_type="pdf",
            summary_text=summary_result
        )
        db.add(summary_entry)
        db.commit()

    return {"summary": summary_result}


# ==========================================
# Database Statistics & History APIs
# ==========================================

@app.get("/stats")
def get_stats(request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user(request, db)

    if user:
        questions_count = db.query(models.ChatHistory).filter(models.ChatHistory.user_id == user.id).count()
        quiz_count = db.query(models.QuizResult).filter(models.QuizResult.user_id == user.id).count()
        summary_count = db.query(models.SummaryLog).filter(models.SummaryLog.user_id == user.id).count()
        roadmap_count = db.query(models.RoadmapLog).filter(models.RoadmapLog.user_id == user.id).count()
        pdf_count = db.query(models.SummaryLog).filter(
            models.SummaryLog.user_id == user.id, models.SummaryLog.source_type == "pdf"
        ).count()
    else:
        questions_count = db.query(models.ChatHistory).count()
        quiz_count = db.query(models.QuizResult).count()
        summary_count = db.query(models.SummaryLog).count()
        roadmap_count = db.query(models.RoadmapLog).count()
        pdf_count = db.query(models.SummaryLog).filter(models.SummaryLog.source_type == "pdf").count()

    return {
        "questions": questions_count,
        "quiz": quiz_count,
        "summary": summary_count,
        "roadmap": roadmap_count,
        "pdf": pdf_count
    }


@app.get("/chat-history")
def get_chat_history(request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user(request, db)
    
    if user:
        history_records = db.query(models.ChatHistory).filter(
            models.ChatHistory.user_id == user.id
        ).order_by(models.ChatHistory.timestamp.desc()).all()
    else:
        history_records = db.query(models.ChatHistory).order_by(models.ChatHistory.timestamp.desc()).all()

    formatted_history = [
        {
            "question": item.question,
            "answer": item.answer,
            "time": item.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for item in history_records
    ]

    return {"history": formatted_history}


@app.post("/clear-chat-history")
def clear_chat_history(request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user(request, db)
    if user:
        db.query(models.ChatHistory).filter(models.ChatHistory.user_id == user.id).delete()
        db.commit()
    return {"success": True}
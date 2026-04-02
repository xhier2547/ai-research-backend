import os
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from tavily import TavilyClient

# Import database settings
from database import Report, get_db
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI(title="Professional Multi-Agent AI System")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-research-frontend-plum.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ---------------------------------------------------------
# 1. Define LLMs based on 2026 Quota Table
# ---------------------------------------------------------
# Primary: High daily quota (500/day) & Fast
primary_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

# Ultimate Backup: Immortal daily quota (14,400/day)
backup_llm = LLM(
    model="google/gemma-3-27b",
    api_key=os.getenv("GEMINI_API_KEY")
)

# ---------------------------------------------------------
# 2. Define Tools
# ---------------------------------------------------------
@tool
def search_internet(query: str) -> str:
    """ใช้ค้นหาข้อมูลที่เป็นปัจจุบันจากอินเทอร์เน็ต"""
    response = tavily.search(query=query, search_depth="basic")
    results = [f"Title: {res['title']}\nContent: {res['content']}" for res in response['results']]
    return "\n\n".join(results)

# ---------------------------------------------------------
# 3. Create API Schema
# ---------------------------------------------------------
class TopicRequest(BaseModel):
    topic: str

# ---------------------------------------------------------
# 4. Main API Endpoint with Automatic Fallback
# ---------------------------------------------------------
@app.post("/api/generate-report/")
async def generate_report(request: TopicRequest, db: Session = Depends(get_db)):
    search_topic = request.topic.strip().lower()
    
    if not search_topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    # LOGIC 1: Cache Check (PostgreSQL)
    existing_report = db.query(Report).filter(Report.topic == search_topic).first()
    if existing_report:
        print(f"✅ Cache Hit: {search_topic}")
        return {
            "status": "success (from cache)",
            "topic": existing_report.topic,
            "report": existing_report.result
        }

    print(f"⚠️ Cache Miss: Initiating Multi-Agent Workflow for '{search_topic}'...")

    # LOGIC 2: Define Agent & Task Structure
    # We define them inside the function to easily swap LLMs if needed
    researcher = Agent(
        role='Senior Web Researcher',
        goal=f'ค้นหาข้อมูลที่ลึกและถูกต้องที่สุดเกี่ยวกับ {search_topic}',
        backstory='คุณคือนักวิจัยระดับเหรียญทองที่หาข้อมูลเก่งที่สุดในโลก',
        tools=[search_internet],
        llm=primary_llm
    )
    
    analyst = Agent(
        role='Data Insight Analyst',
        goal='วิเคราะห์ข้อมูลดิบหาแนวโน้มและข้อเท็จจริง',
        backstory='คุณเชี่ยวชาญการมองหาจุดแข็งจุดอ่อนและการเปรียบเทียบข้อมูล',
        llm=primary_llm
    )
    
    writer = Agent(
        role='Professional Content Architect',
        goal='เขียนรายงานที่สมบูรณ์แบบในรูปแบบ Markdown พร้อมตารางเปรียบเทียบ',
        backstory='คุณคือบรรณาธิการนิตยสารเทคโนโลยีระดับโลกที่เน้นความชัดเจนและฟันธง',
        llm=primary_llm
    )

    task1 = Task(description=f'ค้นหาข้อมูลล่าสุดและข้อเท็จจริงเกี่ยวกับ {search_topic}', expected_output='ข้อมูลดิบ 3-5 แหล่งที่น่าเชื่อถือ', agent=researcher)
    task2 = Task(description='วิเคราะห์ข้อมูลเปรียบเทียบหาจุดเด่นจุดด้อย', expected_output='Insights สำคัญสำหรับการตัดสินใจ', agent=analyst)
    task3 = Task(
        description=(
            f'สรุปข้อมูลเรื่อง {search_topic} เป็นรายงาน Markdown '
            'ต้องมี: 1.หัวข้อ H2/H3 2.ตารางเปรียบเทียบชัดเจน 3.ข้อดี/ข้อเสีย 4.บทสรุปฟันธง'
        ),
        expected_output='Professional Markdown Report with tables',
        agent=writer
    )

    my_crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=[task1, task2, task3],
        process=Process.sequential,
        verbose=False
    )

    # LOGIC 3: Execute with Intelligent Error Recovery
    try:
        print("🚀 Executing with Primary LLM (Gemini 3.1 Flash Lite)...")
        result = my_crew.kickoff()
    except Exception as e:
        error_msg = str(e)
        # Check for Quota Limit (429) or Resource Exhausted
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            print("🛑 Quota Exceeded! Activating Backup LLM (Gemma 3)...")
            # Swap LLM for all agents and retry
            for agent in my_crew.agents:
                agent.llm = backup_llm
            
            # Second Attempt with Immortal Backup
            result = my_crew.kickoff()
        else:
            print(f"❌ Critical Error: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

    # LOGIC 4: Persistence (Save to Database)
    final_text = str(result.raw)
    try:
        new_report = Report(
            topic=search_topic,
            result=final_text,
            status="completed"
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
    except Exception as db_err:
        db.rollback()
        print(f"💾 DB Save Error: {str(db_err)}")

    return {
        "status": "success (generated newly)",
        "topic": search_topic,
        "report": final_text
    }
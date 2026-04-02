import os
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from tavily import TavilyClient

# Import ไฟล์ database ที่เราเพิ่งสร้าง (ต้องมีไฟล์ database.py อยู่โฟลเดอร์เดียวกัน)
from database import Report, get_db

# เพิ่ม import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI(title="Multi-Agent AI API")

# เพิ่มส่วนนี้ลงไปใต้ app = FastAPI(...)
# เพิ่ม CORS Middleware ตรงนี้ (สำคัญมาก ต้องตั้งค่าให้ครบ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-research-frontend-plum.vercel.app" # เพิ่ม URL นี้เข้าไป
    ],
    allow_credentials=True,
    allow_methods=["*"],  # <--- บรรทัดนี้แหละครับที่จะเปิดทางให้คำสั่ง OPTIONS ผ่าน
    allow_headers=["*"],
)

# 1. โหลดการตั้งค่า
load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ถอด Local LLM (Ollama) ออกเพื่อไม่ให้เป็นภาระการ์ดจอ GTX 1060
# ใช้ Mixtral 8x7B แทน เพราะเสถียรเรื่องการใช้ Tool มากกว่า
# ใช้ Gemini 1.5 Flash (มีความเร็วสูงมาก และเก่งภาษาไทย เหมาะกับการให้ Agent ค้นหาข้อมูล)
cloud_llm = LLM(
    model="gemini/gemini-2.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY")
)

# หมายเหตุ: หากต้องการความฉลาดขั้นสุดระดับเทพ ให้เปลี่ยนชื่อ model เป็น "gemini/gemini-1.5-pro"
# 2. สร้าง Tool
@tool
def search_internet(query: str) -> str:
    """ใช้ค้นหาข้อมูลที่เป็นปัจจุบันจากอินเทอร์เน็ต"""
    response = tavily.search(query=query, search_depth="basic")
    results = [f"Title: {res['title']}\nContent: {res['content']}" for res in response['results']]
    return "\n\n".join(results)

# 3. กำหนด Agent (เปลี่ยนมาใช้ cloud_llm ทั้งหมด)
researcher = Agent(
    role='Senior Web Researcher', 
    goal='ค้นหาข้อมูลที่ถูกต้องเกี่ยวกับเรื่องที่ได้รับมอบหมาย', 
    backstory='คุณคือนักวิจัยมืออาชีพ', 
    tools=[search_internet], 
    llm=cloud_llm
)
analyst = Agent(
    role='Data Analyst', 
    goal='วิเคราะห์ข้อมูลดิบ', 
    backstory='คุณคือผู้เชี่ยวชาญการวิเคราะห์ข้อมูล', 
    llm=cloud_llm
)
# 3. อัปเกรด Agent นักเขียน (The Professional Content Architect)
writer = Agent(
    role='Professional Technical Reviewer', 
    goal='เขียนรายงานเปรียบเทียบเชิงลึกที่อ่านง่ายและมีโครงสร้างชัดเจน', 
    backstory=(
        'คุณคือบรรณาธิการบริหารของนิตยสารเทคโนโลยีระดับโลก '
        'คุณเชี่ยวชาญการย่อยข้อมูลยากๆ ให้กลายเป็นบทความที่ทรงพลัง '
        'กฎเหล็กของคุณคือ: ต้องมีหัวข้อชัดเจน, มีตารางเปรียบเทียบ, '
        'และมีการสรุปฟันธงที่เป็นประโยชน์ต่อผู้อ่าน'
    ), 
    llm=cloud_llm
)


# กำหนดโครงสร้างข้อมูล (JSON) ที่ API ต้องรับเข้ามา
class TopicRequest(BaseModel):
    topic: str

# สร้าง Endpoint สำหรับรับยิง API แบบ POST (รับ Session DB เข้ามาด้วย)
@app.post("/api/generate-report/")
async def generate_report(request: TopicRequest, db: Session = Depends(get_db)):
    try:
        # ตัดช่องว่างหัวท้ายและบังคับให้เป็นตัวพิมพ์เล็ก เพื่อให้ค้นหาใน Database แม่นยำ
        search_topic = request.topic.strip().lower()
        
        if not search_topic:
            raise HTTPException(status_code=400, detail="Topic cannot be empty (ห้ามส่งค่าว่าง)")

        # ---------------------------------------------------------
        # Logic 1: เช็คระบบ Caching ใน PostgreSQL
        # ---------------------------------------------------------
        existing_report = db.query(Report).filter(Report.topic == search_topic).first()
        
        # ถ้ามีข้อมูลแล้ว ดึงส่งกลับทันที (ใช้เวลาแค่เสี้ยววินาที)
        if existing_report:
            print(f"✅ Cache Hit! ดึงข้อมูล '{search_topic}' จาก Database")
            return {
                "status": "success (from cache)",
                "topic": existing_report.topic,
                "report": existing_report.result
            }

        # ---------------------------------------------------------
        # Logic 2: ถ้าไม่มีใน Cache ค่อยสั่ง AI ทำงาน
        # ---------------------------------------------------------
        print(f"⚠️ Cache Miss! กำลังสั่ง AI รันข้อมูลเรื่อง: {search_topic} ...")

        task1 = Task(description=f'ค้นหาข้อมูลล่าสุดเกี่ยวกับ: {search_topic}', expected_output='ข้อมูลดิบ 3-5 แหล่ง', agent=researcher)
        task2 = Task(description='วิเคราะห์ข้อมูลดิบหาแนวโน้มสำคัญ', expected_output='สรุป Insight 5 ข้อ', agent=analyst)
        task3 = Task(
    description=(
        f'นำข้อมูลวิเคราะห์ที่ได้รับ มาเขียนสรุปเปรียบเทียบเรื่อง {search_topic} '
        'โดยใช้โครงสร้างดังนี้:\n'
        '1. ใช้หัวข้อใหญ่ (H2) และหัวข้อย่อย (H3) ให้ชัดเจน\n'
        '2. สร้าง "ตารางเปรียบเทียบ" (Markdown Table) เพื่อแสดงความแตกต่างในหัวข้อหลักๆ\n'
        '3. ใช้ Bullet points สำหรับข้อดี-ข้อเสีย\n'
        '4. จบด้วยส่วน "ฟันธง (Verdict)" ว่าตัวเลือกไหนเหมาะกับใคร'
    ),
    expected_output='บทความสรุปในรูปแบบ Markdown ที่มีโครงสร้างครบถ้วนและมีตารางเปรียบเทียบ',
    agent=writer
)

        my_crew = Crew(
            agents=[researcher, analyst, writer],
            tasks=[task1, task2, task3],
            process=Process.sequential,
            verbose=False # ปิด Log รายละเอียดเพื่อไม่ให้รกหน้าจอเซิร์ฟเวอร์
        )

        # สั่งรัน AI
        result = my_crew.kickoff()
        final_text = str(result.raw)
        
        # ---------------------------------------------------------
        # Logic 3: บันทึกผลลัพธ์ลง PostgreSQL
        # ---------------------------------------------------------
        new_report = Report(
            topic=search_topic,
            result=final_text,
            status="completed"
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        # ส่งผลลัพธ์กลับไปในรูปแบบ JSON
        return {
            "status": "success (generated newly)",
            "topic": search_topic,
            "report": final_text
        }

    except Exception as e:
        db.rollback() # หากรันแล้วเกิด Error ให้ยกเลิกการแก้ไข Database ป้องกันข้อมูลพัง
        print(f"Error occur: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
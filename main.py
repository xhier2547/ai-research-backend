import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from tavily import TavilyClient

# ---------------------------------------------------------
# ส่วนที่ 1: โหลดการตั้งค่าและเครื่องมือ
# ---------------------------------------------------------
# ดึง API Key จากไฟล์ .env
load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ใส่ตัวนี้เข้าไปแทน
cloud_llm = LLM(
    model="groq/llama-3.1-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)
# สร้าง Custom Tool ให้ AI ใช้ค้นหาอินเทอร์เน็ตได้
@tool("Search Internet")
def search_internet(query: str) -> str:
    """ใช้ค้นหาข้อมูลที่เป็นปัจจุบันจากอินเทอร์เน็ต"""
    response = tavily.search(query=query, search_depth="basic")
    results = [f"Title: {res['title']}\nContent: {res['content']}" for res in response['results']]
    return "\n\n".join(results)

# ---------------------------------------------------------
# ส่วนที่ 2: กำหนดบทบาทให้ Agent ทั้ง 3 ตัว
# ---------------------------------------------------------
researcher = Agent(
    role='Senior Web Researcher',
    goal='ค้นหาข้อมูลที่ถูกต้องเกี่ยวกับ {topic}',
    backstory='คุณคือนักวิจัยที่เก่งที่สุดในการหาข้อมูลเชิงลึกจากอินเทอร์เน็ต',
    tools=[search_internet],
    llm=cloud_llm,
    verbose=True
)

analyst = Agent(
    role='Data Analyst',
    goal='วิเคราะห์ข้อมูลที่ได้จากนักวิจัยและสรุปประเด็นสำคัญ',
    backstory='คุณคือผู้เชี่ยวชาญในการเปลี่ยนข้อมูลดิบให้เป็นบทวิเคราะห์ที่เฉียบคม',
    llm=cloud_llm,
    verbose=True
)

writer = Agent(
    role='Content Writer',
    goal='เขียนรายงานสรุปจากข้อมูลที่วิเคราะห์แล้ว',
    backstory='คุณคือนักสื่อสารที่สามารถอธิบายเรื่องยากให้เข้าใจง่ายและน่าอ่าน',
    llm=cloud_llm,
    verbose=True
)

# ---------------------------------------------------------
# ส่วนที่ 3: ออกแบบงาน (Tasks) และกำหนดให้ทำงานต่อกัน (Sequential)
# ---------------------------------------------------------
task1 = Task(description='ค้นหาข้อมูลล่าสุดเกี่ยวกับ {topic}', expected_output='ข้อมูลดิบ 3-5 แหล่ง', agent=researcher)
task2 = Task(description='วิเคราะห์ข้อมูลดิบหาแนวโน้มสำคัญ', expected_output='สรุป Insight 5 ข้อ', agent=analyst)
task3 = Task(description='เขียนบทความสรุปจาก Insight', expected_output='บทความสรุป 3 ย่อหน้า', agent=writer)

my_crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[task1, task2, task3],
    process=Process.sequential,
    verbose=True
)

# ---------------------------------------------------------
# ส่วนที่ 4: สั่งรันระบบ
# ---------------------------------------------------------
if __name__ == "__main__":
    # คุณสามารถเปลี่ยนหัวข้อในบรรทัดนี้ได้ตามต้องการ
    topic_to_search = 'แนวโน้มเทคโนโลยี AI ในไทยปี 2026'
    
    print(f"เริ่มการทำงาน... หัวข้อ: {topic_to_search}")
    result = my_crew.kickoff(inputs={'topic': topic_to_search})
    
    print("\n\n" + "="*40)
    print("ผลลัพธ์สุดท้าย (FINAL RESULT):")
    print("="*40)
    print(result)
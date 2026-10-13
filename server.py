"""
肺康守护 (LungCare Platform) 轻量后端服务
技术栈：Python 3 + FastAPI + SQLite
特点：单文件零配置、自带嵌入式数据库、自带静态网页托管、自带医生管理API与CSV导出
"""

import os
import csv
import io
import json
import time
import sqlite3
from collections import defaultdict
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ==================== 配置区 ====================
DB_FILE = "lungcare_records.db"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "doctor2025")  # 医生端后台密码，可随时在此修改

app = FastAPI(title="LungCare Platform API", version="2.0")

# 轻量内存防刷限流器：防暴力爬取与恶意连续提交 (同IP每分钟限15次)
ip_submit_records = defaultdict(list)

def check_rate_limit(client_ip: str):
    now = time.time()
    ip_submit_records[client_ip] = [t for t in ip_submit_records[client_ip] if now - t < 60]
    if len(ip_submit_records[client_ip]) >= 15:
        raise HTTPException(status_code=429, detail="提交频率过高，请稍候 1 分钟再试")
    ip_submit_records[client_ip].append(now)

@app.get("/api/health")
def health_check():
    """云端探针健康检查接口"""
    return {"status": "ok", "service": "LungCare Platform API", "timestamp": datetime.now().isoformat()}

# 允许跨域（方便本地测试或前后端分离部署）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据库初始化 ====================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        patient_uid TEXT,
        patient_name TEXT,
        hospital_record_no TEXT,
        contact_phone TEXT,
        surgery_date TEXT,
        score INTEGER,
        tier TEXT,
        tier_title TEXT,
        rfs3 INTEGER,
        rfs5 INTEGER,
        stage TEXT,
        histology TEXT,
        node TEXT,
        gene TEXT,
        invasion TEXT,
        diff TEXT,
        margin TEXT,
        adjuvant TEXT,
        smoke TEXT,
        age TEXT,
        recov TEXT,
        mmrc INTEGER,
        vas INTEGER,
        doctor_note TEXT,
        visit_count INTEGER DEFAULT 1,
        status TEXT DEFAULT 'pending'
    )
    """)
    # 自动无缝升级已有旧表字段
    cursor.execute("PRAGMA table_info(patient_records)")
    columns = [col[1] for col in cursor.fetchall()]
    if "patient_uid" not in columns:
        cursor.execute("ALTER TABLE patient_records ADD COLUMN patient_uid TEXT")
    if "hospital_record_no" not in columns:
        cursor.execute("ALTER TABLE patient_records ADD COLUMN hospital_record_no TEXT")
    if "visit_count" not in columns:
        cursor.execute("ALTER TABLE patient_records ADD COLUMN visit_count INTEGER DEFAULT 1")
    conn.commit()
    conn.close()

init_db()

# ==================== 数据模型 ====================
class PatientSubmitModel(BaseModel):
    patient_uid: Optional[str] = ""
    patient_name: Optional[str] = "匿名患者"
    hospital_record_no: Optional[str] = ""
    contact_phone: Optional[str] = ""
    surgery_date: Optional[str] = ""
    score: int
    tier: str
    tier_title: str
    rfs3: int
    rfs5: int
    stage: Optional[str] = ""
    histology: Optional[str] = ""
    node: Optional[str] = ""
    gene: Optional[str] = ""
    invasion: Optional[str] = ""
    diff: Optional[str] = ""
    margin: Optional[str] = ""
    adjuvant: Optional[str] = ""
    smoke: Optional[str] = ""
    age: Optional[str] = ""
    recov: Optional[str] = ""
    mmrc: Optional[int] = 1
    vas: Optional[int] = 2
    doctor_note: Optional[str] = ""

class AdminLoginModel(BaseModel):
    password: str

# ==================== 患者端 API ====================
@app.post("/api/patient/submit")
def submit_patient_record(data: PatientSubmitModel, request: Request):
    """接收患者手机端填写的全部病理、分层结果与写给医生的留言"""
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 计算该患者（按 hospital_record_no、phone 或 uid）历史上第几次填报
    prev_count = 0
    if data.hospital_record_no or data.contact_phone or data.patient_uid:
        cursor.execute("""
            SELECT COUNT(*) FROM patient_records 
            WHERE (hospital_record_no != '' AND hospital_record_no = ?)
               OR (contact_phone != '' AND contact_phone = ?)
               OR (patient_uid != '' AND patient_uid = ?)
        """, (data.hospital_record_no, data.contact_phone, data.patient_uid))
        prev_count = cursor.fetchone()[0]
    visit_count = prev_count + 1

    cursor.execute("""
        INSERT INTO patient_records (
            created_at, patient_uid, patient_name, hospital_record_no, contact_phone, surgery_date,
            score, tier, tier_title, rfs3, rfs5,
            stage, histology, node, gene, invasion, diff, margin, adjuvant,
            smoke, age, recov, mmrc, vas, doctor_note, visit_count, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        created_at, data.patient_uid, data.patient_name, data.hospital_record_no, data.contact_phone, data.surgery_date,
        data.score, data.tier, data.tier_title, data.rfs3, data.rfs5,
        data.stage, data.histology, data.node, data.gene, data.invasion, data.diff, data.margin, data.adjuvant,
        data.smoke, data.age, data.recov, data.mmrc, data.vas, data.doctor_note, visit_count, 'pending'
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {
        "success": True,
        "message": f"档案及留言已成功同步至医生团队！(这是您的第 {visit_count} 次随访记录)",
        "record_id": record_id,
        "visit_count": visit_count
    }

# ==================== 医生管理端 API ====================
@app.post("/api/admin/login")
def admin_login(payload: AdminLoginModel):
    """管理员/医生密码校验"""
    if payload.password == ADMIN_PASSWORD:
        return {"success": True, "token": "token_verified_admin"}
    raise HTTPException(status_code=401, detail="管理密码错误，请核对后重试")

@app.get("/api/admin/records")
def get_patient_records(token: str = Query(...), tier: Optional[str] = None, keyword: Optional[str] = None):
    """医生端获取所有患者填报记录"""
    if token != "token_verified_admin":
        raise HTTPException(status_code=403, detail="未授权访问")
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = "SELECT * FROM patient_records WHERE 1=1"
    params = []
    
    if tier and tier != "all":
        sql += " AND tier = ?"
        params.append(tier)
    
    if keyword:
        sql += """ AND (
            patient_name LIKE ? OR 
            contact_phone LIKE ? OR 
            hospital_record_no LIKE ? OR 
            patient_uid LIKE ? OR 
            doctor_note LIKE ?
        )"""
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw, kw, kw])
        
    sql += " ORDER BY id DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    # 统计数据
    cursor.execute("SELECT COUNT(*) FROM patient_records")
    total_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM patient_records WHERE tier = 'high'")
    high_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM patient_records WHERE doctor_note != '' AND doctor_note IS NOT NULL")
    note_count = cursor.fetchone()[0]
    
    conn.close()
    
    records = [dict(r) for r in rows]
    return {
        "success": True,
        "stats": {
            "total": total_count,
            "high_risk": high_count,
            "with_notes": note_count
        },
        "records": records
    }

@app.post("/api/admin/mark-status")
def mark_record_status(payload: dict):
    """标记患者留言状态为已处理"""
    record_id = payload.get("id")
    status = payload.get("status", "reviewed")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE patient_records SET status = ? WHERE id = ?", (status, record_id))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/admin/export-csv")
def export_csv(token: str = Query(...)):
    """一键导出为 Excel/CSV 表格供科研统计（含患者精准识别号）"""
    if token != "token_verified_admin":
        raise HTTPException(status_code=403, detail="未授权访问")
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_records ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    # 写入 UTF-8 BOM，防止 Excel 打开中文乱码
    output.write('\ufeff')
    writer = csv.writer(output)
    
    headers = [
        "序号", "填报时间", "患者随访码(PID)", "患者姓名", "住院号/病案号", "联系电话", "随访轮次",
        "手术日期", "风险评分", "风险等级", "3年无复发率%", "5年无复发率%", 
        "分期", "病理类型", "淋巴结", "驱动基因", "浸润侵犯", "分化程度", "切缘", "辅助治疗", 
        "吸烟史", "年龄", "体能状态", "气短mMRC", "疼痛VAS", "写给医生的留言", "处理状态"
    ]
    writer.writerow(headers)
    
    for r in rows:
        writer.writerow([
            r["id"], r["created_at"], r["patient_uid"] or "", r["patient_name"], r["hospital_record_no"] or "",
            r["contact_phone"] or "", f"第{r['visit_count'] or 1}次", r["surgery_date"],
            r["score"], r["tier_title"], r["rfs3"], r["rfs5"], r["stage"], r["histology"],
            r["node"], r["gene"], r["invasion"], r["diff"], r["margin"], r["adjuvant"],
            r["smoke"], r["age"], r["recov"], r["mmrc"], r["vas"], r["doctor_note"], r["status"]
        ])
        
    output.seek(0)
    filename = f"lungcare_patients_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# 静态资源挂载：将当前目录下的 index.html 作为前端提供服务
if os.path.exists("index.html"):
    @app.get("/")
    def read_root():
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
            
if __name__ == "__main__":
    import uvicorn
    # 启动在 8000 端口，腾讯云服务器上可以通过 80 或 8000 访问
    print("==================================================")
    print("肺康守护系统已启动！")
    print("本地访问网址：http://127.0.0.1:8000")
    print(f"医生管理后台默认密码：{ADMIN_PASSWORD}")
    print("==================================================")
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 肺康守护 (LungCare Platform · Recovery Atlas)
## 肺癌全病程居家康复与临床随访决策管理系统

一个极简轻量、零外部繁重依赖、开箱即用的肺癌患者居家康复与临床决策支持平台。同时支持**纯前端无服务器运行（GitHub Pages / 微信直接打开）**与**云端前后端一体化联动部署（FastAPI + SQLite）**。

---

### 🌟 系统核心功能板块

1. **🏡 居家生活日常指南 (12 条高频痛点实操)**：
   - 饮食营养与“发物”辟谣（优质蛋白量化、破除油汤大补迷思）
   - 伤口洗澡防水贴、侧卧翻身防积液与胸腔引流恢复
   - 做饭油烟禁忌、手指爬墙防“凝肩”肩周炎、术侧限重 3kg
   - 乘机气压防气胸、复查扫描焦虑（Scanxiety）心态调试
   - 靶向药/慢病药 12 小时漏服补服法则、抑酸胃药错开 2~4h、增强 CT 停二甲双胍
   - 声音嘶哑（喉返神经牵拉自愈）、双手抱枕爆发性排痰抵消 90% 震动剧痛
   - 严禁闭气死命大便（瓦氏动作防残端瘘与气胸）、温和乳果糖通便
   - 前开襟全棉衣物防神经摩擦刺痛、女性术后半年远离钢圈文胸
   - **科学运动锻炼**：八段锦/太极首选、谈话测试控强度、血氧 <90% 悬崖红线
   - **居家空气安全**：雾霾 AQI>100 坚决不晨练、彻底清除二手与三手烟、严禁室内燃香/熏艾/明火蚊香、空气净化器选 HEPA 坚决避开副产臭氧机型

2. **🏛️ 国际临床权威指南与医学依据 (6 条循证专区)**：
   - NCCN 2025、CSCO 2025、ESMO 2024、中华胸心外科围术期康复专家共识
   - 肺癌局部复发与远处转移“红旗预警信号”
   - 靶向/化疗不良反应居家自查与避坑

3. **📊 根治术后复发风险评估工具（Clinical Nomogram 列线图测算器）**：
   - 输入病理分期、病理亚型、淋巴结清扫状态、驱动基因、脉管侵犯、分化程度、吸烟史等基线指标
   - 实时量化测算预后风险得分（0~100 分）、分层等级与预估 **3 年 / 5 年无复发生存率（RFS）**

4. **📅 智能随访排期生成器 & 手机日历导出 (.ics)**：
   - 根据手术日期与风险级别，自动推算 1个月、3个月、6个月、1年、2年 随访节点与推荐检查项目
   - 支持**一键导出 `.ics` 日历文件**，可直接导入苹果 iPhone、华为、小米等手机自带日历，自动设置提前 1 天响铃提醒

5. **📝 门诊就诊问诊便签本 & 手机端一键向医生建档**：
   - 点击常见高频问题气泡一键加入清单，支持复制与本地自动保存
   - 弹窗提交档案：生成患者专属随访码（PID），自动同步到医生工作台

6. **🩺 随访医生工作台 (Doctor Workspace)**：
   - 口令认证安全登录、患者全病程复查轨迹时间线展示
   - 自动按手机号/姓名/UID合并档案、一键呼叫患者电话、一键导出科研 CSV 报表

---

### 📂 本地文件目录说明

```text
lung_cancer_care_app/
├── index.html              # 核心单文件前端应用 (离线/在线均可直接打开)
├── server.py               # 轻量 Python 后端 (FastAPI + SQLite，含防刷限流与接口)
├── lungcare_records.db     # SQLite 数据库文件 (预置脱敏测试病历)
├── requirements.txt        # Python 运行依赖 (仅需 fastapi uvicorn)
├── start.bat               # Windows 本地一键启动脚本
├── start.sh                # Linux / 云服务器一键启动脚本
├── DEPLOY_GUIDE.md         # 腾讯云/服务器上线部署指南
├── .gitignore              # Git 忽略文件
└── README.md               # 项目说明文档
```

---

### 🚀 如何上传到 GitHub 并免费开启公网访问

> ⚠️ **重要提示**：只上传当前 `lung_cancer_care_app/` 目录，**切勿上传根目录的论文稿件文件**。

#### 步骤 1：在 GitHub 创建新仓库
1. 打开 [GitHub](https://github.com/) 并登录，点击右上角 **New repository**。
2. 填写仓库名称（例如 `lung-cancer-care-app`），勾选 **Public**（公开），其他选项留空，点击 **Create repository**。

#### 步骤 2：在本地提交并推送代码
在终端（PowerShell 或 CMD）中进入当前目录并执行以下命令：

```bash
cd "e:\MY DATA\Environmental Health\lung_cancer_care_app"

# 初始化本地 Git 仓库
git init

# 添加全部应用文件并提交
git add .
git commit -m "feat: initial commit of Lung Cancer Care & Recovery Atlas"

# 设置主分支并关联 GitHub 仓库 (请将下面的 YOUR_USERNAME 替换为您的 GitHub 用户名)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/lung-cancer-care-app.git

# 推送代码至 GitHub
git push -u origin main
```

#### 步骤 3：免费开启 GitHub Pages（获得永久免费公网网址）
1. 打开刚刚创建的 GitHub 仓库页面，点击顶部的 **Settings**（设置）。
2. 在左侧菜单中找到 **Pages**。
3. 在 **Build and deployment** 下方的 **Branch**：
   - 分支选择 `main`
   - 文件夹选择 `/ (root)`
   - 点击 **Save**（保存）。
4. 等待 1~2 分钟，页面顶部会显示您的专属公网网址：
   `https://YOUR_USERNAME.github.io/lung-cancer-care-app/`
5. **现在您可以直接将这个网址发给任何人，或者做成二维码贴在患者指南手册上，任何人拿出手机扫码即可立即全屏体验！**

---

### 💻 本地离线运行方法

- **方式一（纯双击打开）**：直接双击 `index.html`，无需任何配置，浏览器即可完整运行全部前端与 Mock 演示功能。
- **方式二（前后端联动）**：双击 `start.bat`，脚本会自动检测依赖、启动本地后端并打开网页。

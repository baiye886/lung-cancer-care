# 肺康守护平台 · 腾讯云极简部署与运维使用手册

本文档指导你如何将本平台完整部署到已购买的**腾讯云服务器**（轻量应用服务器 Lighthouse 或云服务器 CVM），实现：
1. 患者手机端微信扫码或点击网址直接访问、评估并提交档案；
2. 医生团队随时凭密码登录后台，实时查看患者的临床指标、**重点查阅患者写给医生的留言**，并支持**一键导出 Excel (CSV)**。

---

### 一、 核心文件清单

项目目录下已包含完整的轻量化生产套件：
* `index.html`：前端单页（患者端界面 + 医生工作台合一，支持手机全屏自适应、大字模式、语音朗读、防误触）
* `server.py`：后端服务（Python FastAPI + 自动创建嵌入式 SQLite 数据库 `lungcare_records.db` + 内存级防刷限流）
* `requirements.txt`：Python 运行环境依赖清单
* `start.sh`：Linux / 腾讯云服务器后台一键启动与重启脚本
* `start.bat`：Windows 本地双击启动脚本

---

### 二、 腾讯云服务器极简部署步骤（约 3~5 分钟）

#### 第一步：登录腾讯云服务器并安装环境
在腾讯云控制台点击“登录”（通过 SSH 或网页版 WebShell 登录终端）：
```bash
# 1. 检查 Python 版本（建议 Python 3.8 及以上，系统通常自带）
python3 --version

# 2. 一键安装全部依赖包
pip3 install -r requirements.txt
```

#### 第二步：上传代码文件
在服务器上新建一个目录（如 `/data/lungcare`），并将项目文件夹内容传上去：
```bash
mkdir -p /data/lungcare
cd /data/lungcare
# 将文件上传至此目录，并赋予启动脚本执行权限：
chmod +x start.sh
```

#### 第三步：修改医生后台密码（可选）
打开 `server.py`，第 22 行可修改专属医生后台密码（默认初始密码为 `doctor2025`）：
```python
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "doctor2025")
```

#### 第四步：启动服务
```bash
# 执行一键后台启动脚本（即使关闭终端窗口，服务也会持续在后台运行）：
./start.sh

# 查看实时运行日志：
tail -f server.log
```
*启动后，系统默认监听 `8000` 端口（若想改为常规 80 端口，可修改 `server.py` 最末行的 `port=80`）。*

#### 第五步：在腾讯云控制台开放防火墙端口
1. 进入腾讯云控制台 ➔ 找到你的服务器实例 ➔ 点击**【防火墙】**或**【安全组】**；
2. 点击**【添加规则】**：
   * 协议：`TCP`
   * 端口：`8000`（或你修改的 80 端口）
   * 策略：`允许`
3. 保存后，即可通过公网 IP 访问：
   `http://你的腾讯云服务器公网IP:8000`

---

### 三、 微信生态传播与上线进阶建议（重要）

#### 1. 微信防拦截与 HTTPS 证书配置
- **痛点**：微信内置浏览器若直接访问纯 HTTP 裸 IP 网页，常会弹出“非微信官方网页，请确认是否继续访问”或“已停止访问该网页”的拦截提示。
- **解决方案**：
  1. 在腾讯云购买或绑定一个域名（国内云服务器绑域名需完成 ICP 备案，通常 1~2 周；内测阶段可直接使用公网 IP 测试）；
  2. 在腾讯云 SSL 证书控制台申请**免费一年期 TrustAsia 证书**（或使用 `certbot` 申请 Let's Encrypt 免费证书）；
  3. 使用 Nginx 反向代理将 443 (HTTPS) 流量转至本地 8000 端口，即可在微信中丝滑打开并生成漂亮的分享卡片！

#### 2. 开机自启服务配置 (systemd)
若希望腾讯云服务器重启后自动恢复服务，可创建系统守护进程：
```bash
# 创建服务配置文件
sudo nano /etc/systemd/system/lungcare.service
```
粘贴以下内容（将路径替换为实际路径）：
```ini
[Unit]
Description=LungCare Platform Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/data/lungcare
ExecStart=/usr/bin/python3 /data/lungcare/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```
生效并启动：
```bash
sudo systemctl daemon-reload
sudo systemctl enable lungcare
sudo systemctl start lungcare
```

#### 3. 数据安全与定时自动备份
数据库文件为单一文件 `lungcare_records.db`，极为轻量且不会出现连接池冲突。建议配置 Linux crontab 每天夜间自动备份一份至本地或云对象存储：
```bash
crontab -e
# 添加每天凌晨 3:00 自动备份数据库副本：
0 3 * * * cp /data/lungcare/lungcare_records.db /data/lungcare/backup_$(date +\%Y\%m\%d).db
```

---

### 四、 医生如何查看患者数据与留言？

1. **医生端登录**：
   在手机或电脑打开网页，点击顶部状态栏的 **【👨‍⚕️ 医生工作台】** 或页脚 **【医生管理工作台入口】**，输入密码即可进入。
2. **患者档案归纳视图**：
   按手机号/PID 将同一患者的初评与复查自动归入同一份档案，直观查看时间轴恢复走势。
3. **重点查阅患者留言**：
   每条记录清晰展示 **`💬 患者写给医生的留言 / 咨询问题`**。
4. **一键导出 Excel (CSV)**：
   点击右上角 **【一键导出 Excel (CSV)】**，即可下载格式工整、带 UTF-8 BOM（保证 Excel 打开绝不乱码）的科研汇总表。

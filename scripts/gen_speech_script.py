"""
Presentation_Script.docx v2 — 配套 11 张幻灯片的 15 分钟讲稿
精简版：去掉 UML / 时序图 / 类图等过度技术内容，保留产品故事 + 真实部署数据
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
section = doc.sections[0]
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1.25)
section.right_margin = Inches(1.25)

def heading1(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.size = Pt(16); r.font.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    p.paragraph_format.space_before = Pt(18); p.paragraph_format.space_after = Pt(6)
    return p

def heading2(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.size = Pt(13); r.font.bold = True
    r.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(3)
    return p

def heading3(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text); r.font.size = Pt(12); r.font.bold = True
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
    return p

def body(doc, text):
    p = doc.add_paragraph(text)
    if p.runs: p.runs[0].font.size = Pt(11)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = Pt(15)
    return p

def script(doc, text):
    p = doc.add_paragraph(text)
    if p.runs: p.runs[0].font.size = Pt(11)
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = Pt(16)
    return p

def bullet(doc, text):
    p = doc.add_paragraph(style='List Bullet')
    r = p.add_run(text); r.font.size = Pt(11)
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_after = Pt(3)
    return p

def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1+len(rows), cols=len(headers))
    table.style = 'Table Grid'
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        c = hdr.cells[i]; c.text = h
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(10)
        tc = c._tc; tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), '1F497D'); shd.set(qn('w:val'), 'clear')
        tcPr.append(shd)
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
    for ri, row_data in enumerate(rows):
        row = table.rows[ri+1]
        for ci, val in enumerate(row_data):
            c = row.cells[ci]; c.text = str(val)
            c.paragraphs[0].runs[0].font.size = Pt(10)
            if ri % 2 == 1:
                tc = c._tc; tcPr = tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), 'D6E4F0'); shd.set(qn('w:val'), 'clear')
                tcPr.append(shd)
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Inches(w)
    return table

# === Cover ===
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(60)
r = p.add_run("PRESENTATION SCRIPT (v2)")
r.font.size = Pt(22); r.font.bold = True; r.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
doc.add_paragraph()
p2 = doc.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p2.add_run("校园学术资源共享平台")
r.font.size = Pt(16); r.font.bold = True
doc.add_paragraph()
p3 = doc.add_paragraph(); p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p3.add_run("配套 Final_Presentation.pptx 的逐页讲稿（15 分钟精简版）")
r.font.size = Pt(13); r.font.color.rgb = RGBColor(0x65, 0x75, 0x8B)
doc.add_paragraph()
info = [
    ("Slides:", "11 张  ·  时长约 15 分钟（含 Q&A）"),
    ("Speakers:", "连宇翔（主持/总结）/ 郁凯杰（架构）/ 陈瀚中（演示）"),
    ("Course:", "System Analysis and Design"),
    ("Lecturer:", "Dr. CHE Pak Hou (Howard)"),
    ("URL:", "https://signing-isle-printed-shapes.trycloudflare.com"),
    ("Demo Account:", "学号 1230020693  ·  密码 demo123"),
]
for label, value in info:
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"{label}  "); r.font.size = Pt(11); r.font.bold = True
    r2 = p.add_run(value); r2.font.size = Pt(11)
doc.add_page_break()

# === 时间轴 ===
heading1(doc, "演讲时间轴 (15 分钟)")
schedule_headers = ["#", "时段", "主题", "主讲", "时长"]
schedule_rows = [
    ["1", "0:00 – 0:30", "Title 开场", "连宇翔", "0:30"],
    ["2", "0:30 – 1:00", "Agenda 路线", "连宇翔", "0:30"],
    ["3", "1:00 – 2:30", "校园学术资源痛点", "连宇翔", "1:30"],
    ["4", "2:30 – 4:00", "我们的解决方案", "连宇翔", "1:30"],
    ["5", "4:00 – 5:00", "系统怎么搭起来的", "郁凯杰", "1:00"],
    ["6", "5:00 – 11:00", "🎬 LIVE DEMO", "陈瀚中", "6:00"],
    ["7", "11:00 – 12:30", "压测结果", "连宇翔", "1:30"],
    ["8", "12:30 – 13:00", "Charter 目标完成", "连宇翔", "0:30"],
    ["9", "13:00 – 13:30", "反思", "连宇翔", "0:30"],
    ["10-11", "13:30 – 15:00", "Q&A + Thank You", "全员", "1:30"],
]
add_table(doc, schedule_headers, schedule_rows, [0.5, 1.4, 2.7, 1.0, 0.8])

doc.add_page_break()

# === Slide-by-slide ===
heading1(doc, "逐页讲稿")

# --- Slide 1 ---
heading2(doc, "▼ Slide 1：Title  (0:00 – 0:30  ·  连宇翔)")
script(doc, "「各位老师、各位同学，大家好。我是连宇翔，跟我一起的是郁凯杰和陈瀚中。」")
script(doc, "「接下来 15 分钟，我们带大家看一个我们做的网站——校园学术资源共享平台。」")
script(doc, "「简单说，就是解决我们自己平时找资源很累的问题。」")

# --- Slide 2 ---
heading2(doc, "▼ Slide 2：Agenda  (0:30 – 1:00  ·  连宇翔)")
script(doc, "「今天的路线很简洁：先讲 1 分半钟我们看到的问题，然后 1 分半钟讲我们做了什么。」")
script(doc, "「最大头是中间的 6 分钟实时演示——是真在线的网站，老师可以现场注册账号。」")
script(doc, "「最后 4 分钟讲压测数据、Charter 目标、反思和问答。」")

# --- Slide 3 ---
heading2(doc, "▼ Slide 3：痛点  (1:00 – 2:30  ·  连宇翔)")
script(doc, "「先问大家一个问题：上一次你为了找一份历年试卷，花了多久？」")
script(doc, "「我们调研了 47 个同学。平均答案是 38 分钟。」（停顿 2 秒）")
script(doc, "「为什么这么久？因为资源散在好几个地方——课程群、网盘、付费平台、学姐学长私聊。每个地方搜索都很粗，下错年份的真题是常事。」")
script(doc, "「右边这 5 行是同学告诉我们的痛点。最关键的是最后一行——76% 的同学说，如果有奖励机制，他们愿意主动分享自己的笔记和资料。」")
script(doc, "「这就是机会：能不能做一个统一的、能精准筛选的、还能用积分激励同学分享的平台？」")

# --- Slide 4 ---
heading2(doc, "▼ Slide 4：解决方案  (2:30 – 4:00  ·  连宇翔)")
script(doc, "「我们做了一个网站，让学生能 1 分钟找到资源、3 步上传分享并获得奖励。」")
script(doc, "「核心是两个功能。」")
script(doc, "「左边蓝色卡片是功能改进——优化精准检索。可以按课程代码、学年、类型、最低评分四个维度同时筛选。结果排序用一个综合公式：匹配度 40% + 热度 30% + 评分 30%。实测搜索响应不到 100 毫秒。」")
script(doc, "「右边黄色卡片是新功能——积分激励体系。逻辑很简单：新用户注册送 100 分，上传被审核通过 +10 分，资源被下载 +2 分，被好评 +1 分。下载消耗 1 分，每天还有 3 次免费下载兜底。攒够 50 分能换 100 次下载，100 分可以让自己上传的资源置顶 7 天。」")
script(doc, "「这两个功能不是独立的——它们形成飞轮：你上传越多，分越多，搜索时找到优质资源越快，整个社区就活起来了。」")

# --- Slide 5 ---
heading2(doc, "▼ Slide 5：技术架构  (4:00 – 5:00  ·  郁凯杰)")
script(doc, "「谢谢宇翔，我是郁凯杰。我用 1 分钟讲讲系统是怎么搭起来的。」")
script(doc, "「左边这张图是经典的三层架构。最上面是前端网页，中间是 Python 写的 API 服务，最下面是 MariaDB 数据库——MariaDB 是 MySQL 的开源分叉版本，所有 SQL 都是通用的。」")
script(doc, "「右边重点：这个系统不是只在我们电脑上跑的 demo。它真实部署在一台 1GB 内存的云服务器上，用 Docker 容器隔离数据库和 API，避免互相挤占内存。」")
script(doc, "「Cloudflare 提供 HTTPS 证书和 CDN 加速，所以你看到的这个绿色锁，是真的合法证书，不是自签的。」")
script(doc, "「下面这条 URL 就是真实在线的地址，老师可以现在就用手机扫码或者打开试试。下一秒交给瀚中做现场演示。」")

# --- Slide 6 ---
heading2(doc, "▼ Slide 6：LIVE DEMO  (5:00 – 11:00  ·  陈瀚中)")
script(doc, "「谢谢凯杰。各位老师、同学，接下来 6 分钟我带大家做一次完整的现场演示。」")
script(doc, "「请看屏幕——网站现在打开。注意右下角有个绿色的『后端在线』标志，说明系统真在跑。」")
script(doc, "")

heading3(doc, "▶ Step 1: 老师当场注册账号 (5:00 – 6:30)")
script(doc, "「演示之前先做个最关键的事——我想请老师当场注册一个账号，证明这个系统真的能用。」")
script(doc, "「老师，请输一个学号，比如 12345678 这种 8 位的随便数字，再输一个密码。」")
script(doc, "「点注册——看右上角，老师立刻拥有了 100 积分（注册奖励）。」")
script(doc, "「这数据这一秒就进了 MariaDB 数据库。如果有同学想看证据，演示完我可以远程登入服务器，给大家看 users 表里多了老师这一行。」")

heading3(doc, "▶ Step 2: 搜索演示 (6:30 – 7:30)")
script(doc, "「现在用老师刚注册的账号试一下搜索功能。」")
script(doc, "「我搜『Forecasting』，左边筛选课程代码 BBAZ16605。」")
script(doc, "「点搜索——0.1 秒不到结果就出来了。每条结果右上角显示『相关性分数』，就是刚才说的综合排序的得分。」")

heading3(doc, "▶ Step 3: 真下载 + 积分扣减 (7:30 – 9:00)")
script(doc, "「点开第一份资源——这是商务预测的第一讲讲义，真实文件，1MB 左右。」")
script(doc, "「关键来了：点下载，会弹出一个确认框，告诉老师『要扣 1 分』。这是 UX 里的重要原则——花积分前必须明确告知。」")
script(doc, "「老师确认——文件真的下载到老师电脑了，并且老师的余额从 100 变成 99。」")
script(doc, "「这一笔扣分是数据库里的原子事务，不会因为同时有人在抢而扣错。我们等下会说压测数据。」")

heading3(doc, "▶ Step 4: 评分 (9:00 – 9:45)")
script(doc, "「老师可以给这份资源打分。点 5 颗星，提交。」")
script(doc, "「这个评分立刻生效——上传者会因为收到 4 星以上好评，再奖励 1 分。这就是激励循环。」")

heading3(doc, "▶ Step 5: 积分中心 (9:45 – 10:30)")
script(doc, "「切到『积分中心』——这是项目的核心新功能展示。」")
script(doc, "「上面三个数字一目了然：当前余额、本月排名、剩余免费下载次数。」")
script(doc, "「下面是完整流水。每一笔积分变动都被记录——什么时候、为什么、剩多少。这种透明性是积分系统能让人信任的基础。」")
script(doc, "「老师如果想兑换 50 分换 100 次下载次数，点一下就行——但老师只有 99 分，够。我们演示一下兑换……」")

heading3(doc, "▶ Step 6: Admin 功能 + 收尾 (10:30 – 11:00)")
script(doc, "「最后秀一下管理员功能。我们的演示账号是 admin，可以看待审核队列。」")
script(doc, "「如果老师刚才上传了什么资源，会出现在这里等审批。点通过——上传者立得 +10 分。」")
script(doc, "「OK，演示到此结束。把话筒交回给宇翔讲压测结果。」")

# --- Slide 7 ---
heading2(doc, "▼ Slide 7：压测结果  (11:00 – 12:30  ·  连宇翔)")
script(doc, "「谢谢瀚中演示。一个真问题：这系统能扛多少人一起用？我们做了真实压测。」")
script(doc, "「四张大字号卡片就是答案。」")
script(doc, "「左 1：100 个并发请求全部成功——这是 2 倍极限测试。」")
script(doc, "「左 2：搜索 95 百分位响应时间 87 毫秒，比 2 秒目标快了 22 倍。」")
script(doc, "「左 3：1000 笔并发扣分操作零冲突——意思是哪怕 1000 个同学同时点同一个用户的下载，余额绝对不会扣成负数，也不会少扣。这是数据库原子事务的保证。」")
script(doc, "「右 1：服务器资源占用 166MB，限额 340MB，还有近一半余量。lana 上有别的服务也在跑，没受影响。」")
script(doc, "「下面 6 行是具体场景。最关键的是倒数第二行：1000 笔同时扣积分，余额绝不为负、零冲突。这是我们 SDD 设计文档第 10 节里设计的原子事务真正运行的证据。」")
script(doc, "「最后一行是给老师的承诺：班里 40 个同学一起用，绰绰有余。」")

# --- Slide 8 ---
heading2(doc, "▼ Slide 8：Charter 目标  (12:30 – 13:00  ·  连宇翔)")
script(doc, "「30 秒过一下我们立项时定的 7 个目标。」")
script(doc, "「需求覆盖 100%、用户测试完成率 100%、检索效率 87 毫秒、资源时间从 38 分降到不到 1 分、分享意愿通过积分激励解决、综合满意度通过实测稳定，最后是按时交付——比 6 月 30 号截止提前完成，而且 24 小时在线。」")
script(doc, "「全部 ✅。最后这一行画在右上角是因为它是最值得说的——这不是一份文档项目，是一个真在线运行的系统。」")

# --- Slide 9 ---
heading2(doc, "▼ Slide 9：反思  (13:00 – 13:30  ·  连宇翔)")
script(doc, "「30 秒诚实复盘。」")
script(doc, "「做对的事：先做用户调研再设计，避免拍脑袋；用单文件 HTML，演示零依赖；部署到云上让系统真在线。」")
script(doc, "「做得不够好的：积分公式调了 3 次才稳定；移动端响应式做得偏晚；缺少自动化测试。」")
script(doc, "「之后想做：推荐算法升级、做移动 App、扩展到全校。」")

# --- Slide 10 ---
heading2(doc, "▼ Slide 10：Q&A  (13:30 – 14:30  ·  全员)")
script(doc, "「OK，到 Q&A 环节。我们 3 个人都在台上。技术问题凯杰熟，演示问题瀚中熟，整体规划我接。请问大家有什么问题？」")
script(doc, "")
script(doc, "[预演 Q&A 时长约 60 秒，准备 3 个常见问题：见后文]")

# --- Slide 11 ---
heading2(doc, "▼ Slide 11：Thank You  (14:30 – 15:00  ·  连宇翔)")
script(doc, "「再次感谢老师和同学的聆听。」")
script(doc, "「网站 24 小时在线，欢迎演讲后扫码或者用 PPT 上的链接体验。」")
script(doc, "「Thank You！」")

# === Q&A Prep ===
doc.add_page_break()
heading1(doc, "Q&A 准备 — 3 个高概率问题 + 标准答案")

heading2(doc, "Q1：你们的相关性分数公式是怎么定的？为什么是 40/30/30？")
body(doc, "回答：这是经过迭代调整的。我们最初版本是 50/30/20——把文本匹配度权重设最高。但发现这样会让冷门资源因为标题完全匹配而排前面。调整为 40/30/30 后，把质量信号（下载量+评分）总权重提到 60%，让真正受欢迎的优质资源浮上来。")
body(doc, "未来如果上线，可以根据用户行为做 A/B 测试持续优化这三个权重。")

heading2(doc, "Q2：积分系统会不会被刷？比如自己注册多个账号互相下载？")
body(doc, "回答：好问题。我们设计了三层防御：")
bullet(doc, "数据库层 UNIQUE 约束：一个用户对一个资源只能评 1 次")
bullet(doc, "API 层频率限制：每用户每天最多上传/下载次数有上限")
bullet(doc, "Admin 审核：所有上传必须经过管理员审核才能进入流通")
body(doc, "更深层的反作弊（多人共谋）我们目前没做，因为校园场景账号需要学号实名，违规成本很高。如果上线发现问题，可以再加风控规则。")

heading2(doc, "Q3：你们没有真实的后端运行环境，能保证以后真用起来吗？")
body(doc, "回答：实际上我们 **真的有**——这就是为什么演讲一开始我们让老师注册了账号。")
bullet(doc, "数据库：MariaDB 真在云服务器上跑，老师注册的账号已经写入 users 表")
bullet(doc, "API：FastAPI 真在响应请求，瀚中的所有演示动作都打到了真实后端")
bullet(doc, "前端：Prototype.html 是真用户能访问的网站，不是 PPT 截图")
bullet(doc, "压测：100 并发请求 0 错误，1000 笔积分操作 0 race condition，都是真测出来的")
body(doc, "演讲结束后，平台还会继续在线。任何老师同学随时都可以访问体验。")

# === Tips ===
doc.add_page_break()
heading1(doc, "舞台呈现 Tips")

heading2(doc, "时间控制（最重要）")
bullet(doc, "Demo 6 分钟是核心——切忌时间不够时跳过 Demo，宁可砍 reflection 那一页")
bullet(doc, "如果 Demo 顺利只用了 4 分钟，多出 2 分钟给老师互动注册、提问")
bullet(doc, "用手表 / 手机定时，每张 slide 大概多少时间心里有数")

heading2(doc, "演示路径绝对不能错")
bullet(doc, "演讲开始前 5 分钟，浏览器里测一遍：登录 → 搜索 → 下载 → 流水")
bullet(doc, "URL 提前发到自己手机备忘 + 老师电脑（万一笔记本挂了能切换）")
bullet(doc, "Demo 时**字号调到 1.3x**，让后排能看清")

heading2(doc, "应急预案")
bullet(doc, "Cloudflare URL 失效（quick tunnel 偶尔会变）→ 备用 IP：http://178.157.59.239/")
bullet(doc, "Demo 完全卡死 → 用 PPT 上的截图过一遍流程，说明真实行为")
bullet(doc, "投影仪故障 → PPT 转成 PDF 提前存 USB + iCloud + 老师邮箱三处")
bullet(doc, "时间不够 → 跳过 Slide 9 反思，直接从 Slide 8 跳到 Slide 10 Q&A")

heading2(doc, "讲话节奏")
bullet(doc, "数字要慢念两遍：『87 毫秒，比目标快 22 倍』")
bullet(doc, "切换讲者时明确说『把话筒交给 X』+ 微笑握手 1 秒")
bullet(doc, "如果忘词，停 1 秒看 PPT 再继续，比说『嗯额啊』强一万倍")

doc.add_paragraph()
footer = doc.add_paragraph("End of Presentation Script v2  |  15-min lean version  |  May 2026")
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.runs[0].font.size = Pt(9)
footer.runs[0].font.color.rgb = RGBColor(0x80, 0x80, 0x80)

doc.save('/Users/yuxianglian/Documents/系统分析与设计/SAD_Project/Presentation_Script.docx')
print("Done: Presentation_Script.docx (15-min version)")

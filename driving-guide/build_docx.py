"""
Builds a comprehensive Arabic (Egyptian) driving lesson Word document (.docx)
without external libraries. A .docx file is a ZIP archive containing XML files.
"""
import os
import zipfile
from xml.sax.saxutils import escape

OUT = "/projects/sandbox/Hossam/driving-guide/دليل_السواقة_الشامل.docx"

# ---------- XML helpers ----------
NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)

def p_heading(text, level=1, color="1F4E79"):
    """Arabic heading paragraph (RTL)."""
    sizes = {1: 40, 2: 32, 3: 28}  # half-points
    sz = sizes.get(level, 28)
    text = escape(text)
    return f'''
<w:p>
  <w:pPr>
    <w:bidi/>
    <w:spacing w:before="240" w:after="120"/>
    <w:jc w:val="right"/>
    <w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="{color}"/></w:pBdr>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/>
      <w:b/>
      <w:color w:val="{color}"/>
      <w:sz w:val="{sz}"/>
      <w:szCs w:val="{sz}"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">{text}</w:t>
  </w:r>
</w:p>'''

def p_text(text, bold=False, color="000000", size=24, align="right", highlight=None, indent=0):
    text = escape(text)
    bold_xml = "<w:b/><w:bCs/>" if bold else ""
    hl_xml = f'<w:highlight w:val="{highlight}"/>' if highlight else ""
    indent_xml = f'<w:ind w:right="{indent}"/>' if indent else ""
    return f'''
<w:p>
  <w:pPr>
    <w:bidi/>
    <w:jc w:val="{align}"/>
    <w:spacing w:after="100"/>
    {indent_xml}
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/>
      {bold_xml}
      <w:color w:val="{color}"/>
      <w:sz w:val="{size}"/>
      <w:szCs w:val="{size}"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
      {hl_xml}
    </w:rPr>
    <w:t xml:space="preserve">{text}</w:t>
  </w:r>
</w:p>'''

def p_bullet(text, level=0):
    text = escape(text)
    return f'''
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="1"/></w:numPr>
    <w:bidi/>
    <w:jc w:val="right"/>
    <w:spacing w:after="60"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">{text}</w:t>
  </w:r>
</w:p>'''

def p_numbered(text, num_id=2):
    text = escape(text)
    return f'''
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num_id}"/></w:numPr>
    <w:bidi/>
    <w:jc w:val="right"/>
    <w:spacing w:after="80"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">{text}</w:t>
  </w:r>
</w:p>'''

def p_box(text, color="FFF2CC", border="BF8F00"):
    """Highlighted box (single paragraph) for tips/warnings."""
    text = escape(text)
    return f'''
<w:p>
  <w:pPr>
    <w:bidi/>
    <w:jc w:val="right"/>
    <w:spacing w:before="120" w:after="120"/>
    <w:pBdr>
      <w:top w:val="single" w:sz="8" w:space="4" w:color="{border}"/>
      <w:left w:val="single" w:sz="8" w:space="4" w:color="{border}"/>
      <w:bottom w:val="single" w:sz="8" w:space="4" w:color="{border}"/>
      <w:right w:val="single" w:sz="8" w:space="4" w:color="{border}"/>
    </w:pBdr>
    <w:shd w:val="clear" w:color="auto" w:fill="{color}"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/>
      <w:b/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">{text}</w:t>
  </w:r>
</w:p>'''

def p_blank():
    return '<w:p><w:pPr><w:bidi/></w:pPr></w:p>'

def page_break():
    return '''
<w:p>
  <w:r><w:br w:type="page"/></w:r>
</w:p>'''

def table(rows, widths=None, header_color="1F4E79"):
    """rows: list of list of strings. First row is header."""
    if widths is None:
        widths = [3000] * len(rows[0])
    cols = len(rows[0])

    def cell(text, is_header=False, width=3000):
        text = escape(text)
        bold = "<w:b/><w:bCs/>" if is_header else ""
        color = "FFFFFF" if is_header else "000000"
        shade = f'<w:shd w:val="clear" w:color="auto" w:fill="{header_color}"/>' if is_header else ""
        return f'''
<w:tc>
  <w:tcPr>
    <w:tcW w:w="{width}" w:type="dxa"/>
    {shade}
    <w:tcBorders>
      <w:top w:val="single" w:sz="6" w:color="999999"/>
      <w:left w:val="single" w:sz="6" w:color="999999"/>
      <w:bottom w:val="single" w:sz="6" w:color="999999"/>
      <w:right w:val="single" w:sz="6" w:color="999999"/>
    </w:tcBorders>
  </w:tcPr>
  <w:p>
    <w:pPr><w:bidi/><w:jc w:val="right"/></w:pPr>
    <w:r>
      <w:rPr>
        <w:rtl/>
        {bold}
        <w:color w:val="{color}"/>
        <w:sz w:val="22"/>
        <w:szCs w:val="22"/>
        <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
      </w:rPr>
      <w:t xml:space="preserve">{text}</w:t>
    </w:r>
  </w:p>
</w:tc>'''

    out = ['<w:tbl>',
           '<w:tblPr>',
           '<w:tblW w:w="9000" w:type="dxa"/>',
           '<w:bidiVisual/>',
           '<w:jc w:val="center"/>',
           '<w:tblBorders>',
           '<w:top w:val="single" w:sz="6" w:color="999999"/>',
           '<w:left w:val="single" w:sz="6" w:color="999999"/>',
           '<w:bottom w:val="single" w:sz="6" w:color="999999"/>',
           '<w:right w:val="single" w:sz="6" w:color="999999"/>',
           '<w:insideH w:val="single" w:sz="6" w:color="999999"/>',
           '<w:insideV w:val="single" w:sz="6" w:color="999999"/>',
           '</w:tblBorders>',
           '</w:tblPr>',
           '<w:tblGrid>']
    for w in widths:
        out.append(f'<w:gridCol w:w="{w}"/>')
    out.append('</w:tblGrid>')

    for i, row in enumerate(rows):
        out.append('<w:tr>')
        for j, c in enumerate(row):
            out.append(cell(c, is_header=(i == 0), width=widths[j]))
        out.append('</w:tr>')
    out.append('</w:tbl>')
    out.append(p_blank())
    return '\n'.join(out)

# ---------- Build document body ----------
body_parts = []

# COVER
body_parts.append('''
<w:p>
  <w:pPr>
    <w:bidi/>
    <w:jc w:val="center"/>
    <w:spacing w:before="3000" w:after="240"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/>
      <w:b/>
      <w:color w:val="1F4E79"/>
      <w:sz w:val="72"/>
      <w:szCs w:val="72"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">دليل السواقة الشامل</w:t>
  </w:r>
</w:p>
<w:p>
  <w:pPr>
    <w:bidi/>
    <w:jc w:val="center"/>
    <w:spacing w:after="240"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/>
      <w:b/>
      <w:color w:val="2E75B6"/>
      <w:sz w:val="40"/>
      <w:szCs w:val="40"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">للمبتدئين - باللهجة المصرية</w:t>
  </w:r>
</w:p>
<w:p>
  <w:pPr>
    <w:bidi/>
    <w:jc w:val="center"/>
    <w:spacing w:after="240"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/>
      <w:i/>
      <w:color w:val="595959"/>
      <w:sz w:val="32"/>
      <w:szCs w:val="32"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">نقل اللاينات • التحرك من الإشارة • اليمين واليسار واليو-تيرن</w:t>
  </w:r>
</w:p>
''')
body_parts.append(page_break())

# ============== مقدمة ==============
body_parts.append(p_heading("مقدمة قبل ما نبدأ", level=1))
body_parts.append(p_text(
    "يا حسام، الكلام اللي هتقراه ده مش كتاب نظري ممل. ده دليل عملي مكتوب باللهجة المصرية "
    "علشان تفهمه من أول مرة، وتقدر ترجعله قبل كل حصة سواقة. هنركز على اللي اتكلمت عنه: "
    "نقل اللاينات، والتحرك من الإشارة (يمين/يسار/أمام/يو-تيرن)، وكل خطوة بالترتيب الصح."
))
body_parts.append(p_text(
    "أهم حاجة تفتكرها: السواقة مش قوة عضلات ولا سرعة بديهة، السواقة \"عادة\". "
    "لما تكرر نفس الخطوات في نفس الترتيب 20-30 مرة، إيدك ورجلك ودماغك بيشتغلوا لوحدهم. "
    "أنت لسه أول مرة، فالأخطاء طبيعية جدًا. المدرّب موجود علشان كده."
))
body_parts.append(p_box(
    "💡 القاعدة الذهبية اللي لو حفظتها هتسوق كويس: مرايا → إشارة → نظرة عمياء → حركة. "
    "(Mirror → Signal → Blind Spot → Move)",
    color="FFF2CC", border="BF8F00"
))

body_parts.append(page_break())

# ============== فهرس ==============
body_parts.append(p_heading("فهرس الدليل", level=1))
toc = [
    "1) قبل ما تشغل العربية - الـ Checklist",
    "2) المرايا والـ Blind Spot - أهم حاجة في السواقة",
    "3) الإشارة (الإندكيتور) - متى تشغّلها ومتى تطفّيها",
    "4) نقل اللاين (Lane Change) - الخطوات بالترتيب",
    "5) التحرك من إشارة المرور (الكوبري الأحمر)",
    "    - لو هتكمل أمام",
    "    - لو هتلف يمين",
    "    - لو هتلف يسار",
    "    - لو هتعمل يو-تيرن",
    "6) الأخطاء اللي بيقع فيها كل المبتدئين (وأنت مش لوحدك)",
    "7) تمارين عملية تعملها في كل حصة",
    "8) الـ Cheat Sheet - ورقة سريعة قبل كل حصة",
]
for line in toc:
    body_parts.append(p_text(line, size=24))

body_parts.append(page_break())

# ============== 1) Checklist قبل التشغيل ==============
body_parts.append(p_heading("1) قبل ما تشغل العربية - Checklist", level=1))
body_parts.append(p_text(
    "قبل ما تلف المفتاح أصلاً، فيه 6 حاجات لازم تعملهم. ده روتين \"اقعد على الكرسي\" "
    "وهو اختصار سهل تحفظه:"
))
checklist = [
    "اقعد - اظبط الكرسي بحيث رجلك توصل للبدالات وركبتك متعفّلش لما تدوس فرامل لآخرها.",
    "ظهر - اظبط ظهر الكرسي عدل، يدك تقدر تمسك أعلى الدركسيون والكتف لسه على الكرسي.",
    "حزام - لبس حزام الأمان (السيفتي بلت). أنت والركاب.",
    "مرايا - اظبط الـ 3 مرايا (وسط + يمين + شمال). الكلام عليها بالتفصيل في الفصل اللي جاي.",
    "جير - اتأكد إن العربية في وضع P (لو أوتوماتيك) أو N (لو مانوال) قبل ما تشغل.",
    "لمبات - شوف اللمبات قدامك في التابلوه. لو في لمبة حمراء صفراء غريبة، اسأل المدرّب.",
]
for i, item in enumerate(checklist, 1):
    body_parts.append(p_text(f"{i}. {item}", size=24))

body_parts.append(p_box(
    "⚠️ تنبيه: مرايتك مش مظبوطة = أنت بتسوق وأنت أعمى. خد دقيقة قبل كل حصة وظبطهم.",
    color="FCE4D6", border="C00000"
))

body_parts.append(page_break())

# ============== 2) المرايا والـ Blind Spot ==============
body_parts.append(p_heading("2) المرايا والـ Blind Spot", level=1))

body_parts.append(p_heading("إيه هي الـ 3 مرايا؟", level=2))
body_parts.append(p_text("في كل عربية فيه 3 مرايا أساسية لازم تستخدمهم:", size=24))
body_parts.append(p_bullet("مرايا الوسط (الـ Rear-view): اللي قدامك فوق الزجاج. بتوريك اللي ورا العربية مباشرة."))
body_parts.append(p_bullet("مرايا اليمين (الجانبية اليمنى): على باب الراكب. بتوريك اللاين اللي على يمينك."))
body_parts.append(p_bullet("مرايا الشمال (الجانبية اليسرى): على بابك. بتوريك اللاين اللي على شمالك."))

body_parts.append(p_heading("ضبط المرايا الصحيح", level=2))
body_parts.append(p_text(
    "المرايا الجانبية ميصحش تشوف فيها العربية بتاعتك. لازم تشوف الطريق برّه. "
    "اظبطها بحيث تشوف شوية بسيطة من بدن العربية على طرف المرايا الداخلي، "
    "والباقي طريق. كده هتقلل الـ Blind Spot.",
    size=24
))

body_parts.append(p_heading("إيه هو الـ Blind Spot (النقطة العمياء)؟", level=2))
body_parts.append(p_text(
    "الـ Blind Spot هي المنطقة اللي على جنب العربية مباشرة، اللي مش بتبان في أي مرايا. "
    "ممكن تكون عربية كاملة جنبك ومش شايفها في المرايا. علشان كده قبل أي نقل لاين أو حركة جانبية، "
    "لازم تلف وشّك بسرعة على الجنب اللي رايح ليه (نظرة سريعة، مش تحريك راس كامل).",
    size=24
))

body_parts.append(p_box(
    "🎯 تمرين: في كل حصة، كل ما تقف عند إشارة، استخدم الفرصة دي وبصّ في كل مرايا واحدة واحدة. "
    "كده دماغك بتعتاد إن المرايا جزء من السواقة، مش حاجة تتعمل لما حد يفكّرك.",
    color="E2EFDA", border="548235"
))

body_parts.append(page_break())

# ============== 3) الإشارة ==============
body_parts.append(p_heading("3) الإشارة (الإندكيتور)", level=1))
body_parts.append(p_text(
    "الإشارة هي طريقة كلامك مع باقي السواقين. لما تشغل إشارة، أنت بتقول للناس \"أنا هتحرك ناحية كذا\". "
    "السواقة من غير إشارة = أنت بتفاجئ كل اللي حواليك، وده أكبر سبب للحوادث."
))

body_parts.append(p_heading("القاعدة الأساسية للإشارة", level=2))
rules = [
    "شغّل الإشارة قبل الحركة بـ 3 إلى 5 ثواني (مش وأنت بتنقل، وقبل كده بشوية).",
    "اليمين = ذراع الإشارة لتحت (في معظم العربيات). الشمال = لفوق. (في عربيات يابانية الموضوع معكوس - اسأل المدرّب).",
    "بعد ما تخلص الحركة، اتأكد إن الإشارة طفت لوحدها. لو لسه شغالة، طفّيها بإيدك.",
    "في الدوران الكامل (يمين/يسار في الإشارة): الإشارة بتطفي لوحدها بعد ما تكمل الدوران.",
    "في نقل اللاين البسيط: غالبًا الإشارة مش بتطفي لوحدها، لازم ترجّعها بإيدك.",
]
for r in rules:
    body_parts.append(p_numbered(r))

body_parts.append(p_box(
    "❌ خطأ شائع: الناس بتنقل اللاين الأول وتشغّل الإشارة بعدين. ده غلط. "
    "الإشارة بتيجي الأول علشان تقول للناس نيّتك، بعدين تتحرك.",
    color="FCE4D6", border="C00000"
))

body_parts.append(page_break())

# ============== 4) نقل اللاين ==============
body_parts.append(p_heading("4) نقل اللاين (Lane Change) خطوة بخطوة", level=1))

body_parts.append(p_text(
    "ده الجزء اللي قلت إنك بتغلط فيه. خد نفس عميق وذاكر الترتيب ده زي ما هو، "
    "لأنه نفس الترتيب اللي هتعمله طول حياتك في السواقة:",
    bold=True, size=26
))

body_parts.append(p_heading("الخطوات الـ 6 لنقل اللاين", level=2))

steps = [
    ("1- بصّ في مرايا الوسط",
     "أول حاجة تشوف اللي ورا العربية - فيه عربية قريبة قوي؟ فيه عربية جاية بسرعة؟"),
    ("2- بصّ في مرايا الجنب اللي رايح ليه",
     "لو هتنقل يمين، بصّ في المرايا اليمين. لو هتنقل شمال، بصّ في المرايا الشمال. "
     "اللاين اللي جنبك فاضي؟ فيه عربية جنبك على طول؟"),
    ("3- شغّل الإشارة",
     "إشارة الجنب اللي رايح ليه. سيبها شغالة 2-3 ثواني علشان الناس تشوفها قبل ما تتحرك."),
    ("4- نظرة عمياء (Blind Spot)",
     "لف وشّك بسرعة على الكتف اللي رايح ناحيته (يمين أو شمال) علشان تشوف اللي مش ظاهر في المرايا. "
     "نظرة سريعة بس، مش تشيل عينك من قدامك لفترة طويلة."),
    ("5- انقل بالتدريج",
     "لف الدركسيون شوية بس (مش كتير)، والعربية تتحرك ناحية اللاين الجديد بهدوء. "
     "متعمليش حركة فجائية. ابقى ثابت على نفس السرعة."),
    ("6- طفّي الإشارة وبصّ في المرايا",
     "بعد ما تستقر في اللاين الجديد، طفّي الإشارة (لو ما طفتش لوحدها)، "
     "وبصّ في مرايا الوسط علشان تتأكد إن في مسافة كويسة بينك وبين اللي ورا."),
]
for title, desc in steps:
    body_parts.append(p_text(title, bold=True, size=26, color="1F4E79"))
    body_parts.append(p_text(desc, size=24, indent=400))

body_parts.append(p_box(
    "🧠 طريقة سهلة تحفظها: \"شوف ورا، شوف جنب، إشارة، نظرة عمياء، انقل، طفّي\". "
    "كرّرها بصوت عالي في كل مرة هتنقل لاين، لحد ما تبقى تلقائية.",
    color="FFF2CC", border="BF8F00"
))

body_parts.append(p_heading("متى متنقلش لاين؟", level=2))
dont = [
    "لو فيه عربية في الـ Blind Spot بتاعك (مش هتعرف إلا بالنظرة العمياء).",
    "لو فيه خط متصل (مش متقطع) في النص. الخط المتصل = ممنوع التغيير.",
    "في النفق أو على الكوبري لو فيه علامة بتمنع.",
    "في آخر 30 متر قبل تقاطع أو إشارة.",
    "لو السرعة بتاعتك أقل بكتير من سرعة اللاين اللي رايح ليه (هتعطلهم).",
]
for d in dont:
    body_parts.append(p_bullet(d))

body_parts.append(page_break())

# ============== 5) التحرك من الإشارة ==============
body_parts.append(p_heading("5) التحرك من إشارة المرور", level=1))
body_parts.append(p_text(
    "أنت واقف عند إشارة حمراء. الإشارة هتفتح. السؤال: تعمل إيه؟ ده بيختلف على حسب أنت رايح فين."
))

body_parts.append(p_heading("القواعد المشتركة (في كل الحالات)", level=2))
common = [
    "وأنت لسه واقف، حدّد نيّتك: هكمل أمام؟ هلف يمين؟ هلف شمال؟ يو-تيرن؟",
    "لو هتلف، شغّل الإشارة وأنت لسه واقف (مش بعد ما الإشارة تفتح).",
    "اظبط نفسك في اللاين الصح: اللاين اليمين للف يمين، اللاين الشمال للف شمال، الأوسط للأمام.",
    "لما الإشارة تخضّر، استنى ثانية واحدة قبل ما تتحرك (في حد ممكن يكون لسه بيعدّي من الجنب).",
    "بصّ يمين، بصّ شمال، بصّ يمين تاني. بعدين اتحرك.",
]
for c in common:
    body_parts.append(p_numbered(c))

# ----- لو هتكمل أمام -----
body_parts.append(p_heading("الحالة الأولى: لو هتكمل أمام (مش هتلف)", level=2))
body_parts.append(p_text("أبسط حالة. الترتيب:", size=24))
fwd = [
    "خلي الجير على D (لو أوتوماتيك) أو الأولى (لو مانوال) وأنت لسه واقف.",
    "لما تخضّر الإشارة، شيل رجلك من الفرامل ببطء.",
    "في المانوال: ارفع الكلتش بهدوء وأنت بتدوس بنزين خفيف.",
    "بصّ قدامك ويمين وشمال علشان تتأكد محدش بيقطع أمامك.",
    "اتحرك بسرعة معقولة (متبطّأش جامد ومتسرعش جامد).",
]
for f in fwd:
    body_parts.append(p_numbered(f, num_id=3))

# ----- لو هتلف يمين -----
body_parts.append(p_heading("الحالة الثانية: لو هتلف يمين", level=2))
body_parts.append(p_text(
    "اللف يمين عمومًا أسهل من اليسار، لأنك مش بتقطع طريق العربيات اللي قدامك. بس فيه حاجات لازم تنتبه ليها.",
    size=24
))
right = [
    "وأنت لسه واقف: شغّل إشارة اليمين.",
    "اتأكد إنك في اللاين اليمين (اللاين الأخير على اليمين).",
    "لما الإشارة تخضّر: بصّ يمين على المشاة (في ناس بتقطع الشارع).",
    "بصّ في المرايا اليمين علشان متلاش حد جنبك على الموتوسيكل أو دراجة.",
    "ابدأ تلف بهدوء. لف الدركسيون لليمين بس مش لآخره.",
    "لما تكمل اللفة، رجّع الدركسيون عدل بنفس السرعة اللي لففتها بيها.",
    "اتأكد إنك دخلت في اللاين الصح (في الشارع الجديد، اللاين اليمين).",
]
for r in right:
    body_parts.append(p_numbered(r, num_id=4))

body_parts.append(p_box(
    "⚠️ خد بالك من المشاة! اللي بيقطع الشارع من اليمين بياخد وقت يلاحظك. "
    "لو فيه ماشي، استنى لحد ما يخلّص قبل ما تلف.",
    color="FCE4D6", border="C00000"
))

# ----- لو هتلف يسار -----
body_parts.append(p_heading("الحالة الثالثة: لو هتلف يسار (شمال)", level=2))
body_parts.append(p_text(
    "اللف يسار أصعب لأنك بتقطع طريق العربيات اللي جاية من المواجهة. ركّز كويس.",
    size=24, bold=True
))
left = [
    "وأنت لسه واقف: شغّل إشارة الشمال.",
    "اتأكد إنك في اللاين الشمال (اللاين الأول على اليسار).",
    "لما الإشارة تخضّر: متتحركش على طول. ادخل بسيارتك شوية للأمام في النص.",
    "استنى لحد ما العربيات اللي جاية من المواجهة تعدّي أو الإشارة تبقى صفراء.",
    "لما الطريق يبقى آمن: لف الدركسيون لليسار وادخل بهدوء.",
    "بصّ في الـ Blind Spot الشمال قبل اللف (في حد ممكن يكون ورا الكتف).",
    "بعد اللف، اتأكد إنك دخلت في اللاين الصح (اللاين اليمين أو الأوسط، حسب اتجاه طريقك).",
    "رجّع الدركسيون عدل وكمّل سواقتك.",
]
for l in left:
    body_parts.append(p_numbered(l, num_id=5))

body_parts.append(p_box(
    "🚨 أهم حاجة في اللف يسار: متستعجلش. لو شفت إن العربيات جاية بسرعة، استنى. "
    "أحسن تستنى دورة إشارة كاملة من إنك تتعرض لخطر.",
    color="FCE4D6", border="C00000"
))

# ----- يو تيرن -----
body_parts.append(p_heading("الحالة الرابعة: لو هتعمل يو-تيرن (U-Turn)", level=2))
body_parts.append(p_text(
    "اليو-تيرن هو لما تلف 180 درجة وترجع في عكس اتجاهك. مش كل تقاطع مسموح فيه يو-تيرن!",
    size=24
))
uturn = [
    "أول حاجة: شوف العلامات. لو فيه علامة \"ممنوع اليو-تيرن\" متعملوش.",
    "اظبط نفسك في اللاين الشمال (الأخير على اليسار) وأنت لسه على بعد من التقاطع.",
    "شغّل إشارة الشمال.",
    "وأنت في التقاطع، خفّف السرعة جدًا.",
    "بصّ يمين، شمال، يمين تاني. اتأكد محدش جاي.",
    "لف الدركسيون كله للشمال (آخره) وادخل في الدوران.",
    "وأنت بتلف، بصّ على المكان اللي رايح ليه (مش على الدركسيون).",
    "لما تكمل اللفة، رجّع الدركسيون عدل بسرعة معقولة.",
    "ادخل في اللاين اليمين (لأنك في طريق جديد، تبدأ من اليمين وتتدرّج).",
]
for u in uturn:
    body_parts.append(p_numbered(u, num_id=6))

body_parts.append(p_box(
    "💡 تيب: لو الشارع ضيّق، ممكن تحتاج ترجع شوية ورا في النص اللفة (3-point turn). "
    "ده طبيعي، متترددش. الأهم تكمل اللفة من غير ما تخبط الرصيف أو تعطّل العربيات.",
    color="FFF2CC", border="BF8F00"
))

body_parts.append(page_break())

# ============== 6) الأخطاء الشائعة - جدول ==============
body_parts.append(p_heading("6) الأخطاء الشائعة وحلولها", level=1))
body_parts.append(p_text(
    "أنت مش لوحدك. كل سواق دلوقتي كان مبتدئ زيك وغلط نفس الغلطات. "
    "الجدول ده هيوفّر عليك وقت كتير:"
))

errors_table = [
    ["الغلطة", "ليه بتحصل", "الحل الصح"],
    ["نسيان الإشارة", "ركّزت في الحركة ونسيت", "اعمل عادة: إيدك تتحرك للإشارة قبل ما الدركسيون يلف"],
    ["نقل لاين بسرعة فجأة", "خوف من إن العربية اللي ورا تلحقك", "انقل بالتدريج، الدركسيون لفّة خفيفة بس"],
    ["نسيان النظرة العمياء", "بتعتمد على المرايا بس", "اعمل النظرة جزء من الـ checklist، دايمًا قبل النقل"],
    ["السرعة الزيادة في اللف", "مش متعوّد على إحساس الدوران", "خفّف للنص قبل اللف. لو حسّيت إنها بتاخد لازم تخفّف أكتر"],
    ["نسيان طفي الإشارة", "العربية مكمّلتش الدوران علشان تطفيها لوحدها", "بعد كل حركة، اتأكد إن الإشارة طفت"],
    ["الوقوف بعيد عن الإشارة", "خوف من إنك تخش في التقاطع", "اوقف ورا الخط الأبيض مباشرة، مش بعيد عنه"],
    ["التحرك بطيء قوي بعد ما الإشارة تفتح", "تردد", "ثانية واحدة بعد الخضرا، بعدين اتحرك بسرعة معقولة"],
    ["التركيز على الدركسيون", "خوف من إن إيدك تزيغ", "بصّ بعيد على الطريق، الدركسيون هيتظبط لوحده"],
    ["دوس فرامل قوي عند الإشارة", "الإحساس مش متظبط لسه", "ابدأ تخفّف من بعيد، استخدم الفرامل بالتدريج"],
    ["نسيان الجير في المانوال", "كثرة الحاجات اللي بتفكر فيها", "اعمل عادة: قبل ما توقف، انزل الجير الأقل قبل ما تطفئ"],
]
body_parts.append(table(errors_table, widths=[2400, 3200, 3400]))

body_parts.append(page_break())

# ============== 7) تمارين عملية ==============
body_parts.append(p_heading("7) تمارين عملية لكل حصة", level=1))
body_parts.append(p_text(
    "كل حصة سواقة، حاول تركز على تمرين واحد بس. متحاولش تعمل كل حاجة في يوم واحد:"
))

body_parts.append(p_heading("الحصة الجاية: تمرين المرايا", level=2))
ex1 = [
    "كل 8-10 ثواني وأنت بتسوق، بصّ في مرايا الوسط نظرة سريعة.",
    "كل ما توقف عند إشارة، بصّ في الـ 3 مرايا واحدة واحدة.",
    "قبل أي حركة (نقل لاين، لف، توقف)، إجباري تبص في مرايا الوسط الأول.",
]
for e in ex1:
    body_parts.append(p_bullet(e))

body_parts.append(p_heading("الحصة اللي بعدها: تمرين الإشارة", level=2))
ex2 = [
    "حتى لو الشارع فاضي، شغّل الإشارة في كل لف ونقل لاين.",
    "اتعوّد إن إيدك تروح للإشارة أوتوماتيكي قبل ما تلف الدركسيون.",
    "لو نسيت إشارة، قل لنفسك بصوت عالي \"نسيت إشارة\" - كده هتفتكر المرة الجاية.",
]
for e in ex2:
    body_parts.append(p_bullet(e))

body_parts.append(p_heading("الحصة اللي بعدها: تمرين النقل", level=2))
ex3 = [
    "في طريق فاضي، اطلب من المدرب تعمل نقل لاين 5 مرات يمين و5 شمال.",
    "كل مرة قول الخطوات بصوت عالي: \"مرايا، إشارة، نظرة عمياء، نقل، طفّي\".",
    "ركّز على إن النقل يكون ناعم (smooth) مش فجأة.",
]
for e in ex3:
    body_parts.append(p_bullet(e))

body_parts.append(p_heading("الحصة اللي بعدها: تمرين الإشارات والتقاطعات", level=2))
ex4 = [
    "اطلب من المدرب يخدك في طريق فيه إشارات كتير.",
    "في كل إشارة، قبل ما توصلها، حدّد إيه نيّتك (أمام/يمين/شمال/يو-تيرن).",
    "اظبط لاينك من بعيد، وشغّل الإشارة من بدري.",
]
for e in ex4:
    body_parts.append(p_bullet(e))

body_parts.append(p_box(
    "📈 قاعدة التحسّن: لو في كل حصة بتغلط أقل من اللي قبلها، أنت ماشي صح. "
    "السواقة بتاخد 20-30 ساعة عملية لحد ما تبقى مرتاح فيها. متستعجلش على نفسك.",
    color="E2EFDA", border="548235"
))

body_parts.append(page_break())

# ============== 8) Cheat Sheet ==============
body_parts.append(p_heading("8) الـ Cheat Sheet - اقرأها قبل كل حصة", level=1))

body_parts.append(p_heading("قبل ما أركب العربية:", level=2))
cs1 = [
    "كرسي ✓  ظهر ✓  حزام ✓  مرايا ✓  جير ✓  لمبات ✓",
]
for c in cs1:
    body_parts.append(p_text(c, bold=True, size=26, align="center"))

body_parts.append(p_heading("قبل أي نقل لاين:", level=2))
cs2 = [
    "1. مرايا الوسط",
    "2. مرايا الجنب",
    "3. إشارة",
    "4. نظرة عمياء",
    "5. انقل بالتدريج",
    "6. طفّي الإشارة",
]
for c in cs2:
    body_parts.append(p_text(c, bold=True, size=26, color="1F4E79"))

body_parts.append(p_heading("عند الإشارة - حسب الاتجاه:", level=2))

dir_table = [
    ["الاتجاه", "اللاين الصح", "الإشارة", "أهم نقطة"],
    ["أمام", "أوسط", "مفيش", "بصّ يمين وشمال قبل ما تتحرك"],
    ["يمين", "اليمين الأخير", "يمين", "احذر المشاة على الجنب"],
    ["شمال", "الشمال الأول", "شمال", "استنى العربيات اللي جاية مواجهك"],
    ["يو-تيرن", "الشمال الأقصى", "شمال", "اتأكد إن مفيش علامة \"ممنوع\""],
]
body_parts.append(table(dir_table, widths=[1800, 2400, 1800, 3000]))

body_parts.append(p_heading("القاعدة الذهبية اللي ميصحش تنساها:", level=2))
body_parts.append(p_box(
    "مرايا → إشارة → نظرة عمياء → حركة\n(Mirror → Signal → Blind Spot → Move)",
    color="DEEBF7", border="2E75B6"
))

body_parts.append(p_blank())
body_parts.append(p_text(
    "كلمة أخيرة: السواقة هي مهارة بتتعلم بالتكرار، مش بالموهبة. "
    "اللي بيسوق دلوقتي 20 سنة كان زيك أول حصة بيغلط في كل حاجة. "
    "اللي بيفرّق هو إنك تركّز، تكرر، وتتعلم من كل غلطة. "
    "كل حصة هتبقى أحسن من اللي قبلها. ربنا معاك يا حسام. 🚗💨",
    bold=True, size=26, align="center", color="1F4E79"
))

# ---------- Build full document.xml ----------
document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document {NS}>
  <w:body>
    {''.join(body_parts)}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
      <w:bidi/>
    </w:sectPr>
  </w:body>
</w:document>
'''

# ---------- Other docx parts ----------
content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
</Types>
'''

rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
'''

document_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>
'''

styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
        <w:sz w:val="24"/>
        <w:szCs w:val="24"/>
        <w:lang w:val="ar-EG" w:bidi="ar-EG"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:bidi/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:styleId="ListParagraph" w:default="0">
    <w:name w:val="List Paragraph"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:bidi/>
      <w:ind w:right="720"/>
    </w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Normal" w:default="1">
    <w:name w:val="Normal"/>
    <w:pPr><w:bidi/></w:pPr>
  </w:style>
</w:styles>
'''

numbering_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0">
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="bullet"/>
      <w:lvlText w:val="•"/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:bidi/><w:ind w:right="720" w:hanging="360"/></w:pPr>
    </w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="1">
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="decimal"/>
      <w:lvlText w:val="%1."/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:bidi/><w:ind w:right="720" w:hanging="360"/></w:pPr>
    </w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="2">
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="decimal"/>
      <w:lvlText w:val="%1."/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:bidi/><w:ind w:right="720" w:hanging="360"/></w:pPr>
    </w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="3">
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="decimal"/>
      <w:lvlText w:val="%1."/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:bidi/><w:ind w:right="720" w:hanging="360"/></w:pPr>
    </w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="4">
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="decimal"/>
      <w:lvlText w:val="%1."/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:bidi/><w:ind w:right="720" w:hanging="360"/></w:pPr>
    </w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="5">
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="decimal"/>
      <w:lvlText w:val="%1."/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:bidi/><w:ind w:right="720" w:hanging="360"/></w:pPr>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
  <w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
  <w:num w:numId="3"><w:abstractNumId w:val="2"/></w:num>
  <w:num w:numId="4"><w:abstractNumId w:val="3"/></w:num>
  <w:num w:numId="5"><w:abstractNumId w:val="4"/></w:num>
  <w:num w:numId="6"><w:abstractNumId w:val="5"/></w:num>
</w:numbering>
'''

settings_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:zoom w:percent="100"/>
  <w:defaultTabStop w:val="720"/>
  <w:characterSpacingControl w:val="doNotCompress"/>
  <w:themeFontLang w:val="en-US" w:eastAsia="en-US" w:bidi="ar-EG"/>
</w:settings>
'''

# ---------- Write the .docx (zip) ----------
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', content_types)
    z.writestr('_rels/.rels', rels)
    z.writestr('word/_rels/document.xml.rels', document_rels)
    z.writestr('word/document.xml', document_xml)
    z.writestr('word/styles.xml', styles_xml)
    z.writestr('word/numbering.xml', numbering_xml)
    z.writestr('word/settings.xml', settings_xml)

size = os.path.getsize(OUT)
print(f"Created: {OUT}")
print(f"Size: {size:,} bytes")

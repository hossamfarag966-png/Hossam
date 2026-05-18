"""
Builds a comprehensive Arabic (Egyptian) guide for Dubai RTA Road Assessment
exam (focused on Emirates Driving Institute first road assessment + final road test).
Pure stdlib - no external libraries. A .docx is just a ZIP with XML inside.
"""
import os
import zipfile
from xml.sax.saxutils import escape

OUT = "/projects/sandbox/Hossam/driving-guide/دليل_امتحان_دبي_RTA.docx"

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)

# ---------- helpers ----------
def p_heading(text, level=1, color="1F4E79"):
    sizes = {1: 44, 2: 34, 3: 28}
    sz = sizes.get(level, 28)
    text = escape(text)
    return f'''
<w:p>
  <w:pPr>
    <w:bidi/>
    <w:spacing w:before="280" w:after="140"/>
    <w:jc w:val="right"/>
    <w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="{color}"/></w:pBdr>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/><w:b/><w:color w:val="{color}"/>
      <w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">{text}</w:t>
  </w:r>
</w:p>'''

def p_text(text, bold=False, color="000000", size=24, align="right", indent=0, italic=False):
    text = escape(text)
    bold_xml = "<w:b/><w:bCs/>" if bold else ""
    italic_xml = "<w:i/><w:iCs/>" if italic else ""
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
      <w:rtl/>{bold_xml}{italic_xml}
      <w:color w:val="{color}"/>
      <w:sz w:val="{size}"/><w:szCs w:val="{size}"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">{text}</w:t>
  </w:r>
</w:p>'''

def p_bullet(text):
    text = escape(text)
    return f'''
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>
    <w:bidi/><w:jc w:val="right"/><w:spacing w:after="60"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/><w:sz w:val="24"/><w:szCs w:val="24"/>
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
    <w:bidi/><w:jc w:val="right"/><w:spacing w:after="80"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rtl/><w:sz w:val="24"/><w:szCs w:val="24"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">{text}</w:t>
  </w:r>
</w:p>'''

def p_box(text, color="FFF2CC", border="BF8F00", text_color="000000"):
    text = escape(text)
    return f'''
<w:p>
  <w:pPr>
    <w:bidi/><w:jc w:val="right"/>
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
      <w:rtl/><w:b/>
      <w:color w:val="{text_color}"/>
      <w:sz w:val="24"/><w:szCs w:val="24"/>
      <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    </w:rPr>
    <w:t xml:space="preserve">{text}</w:t>
  </w:r>
</w:p>'''

def p_blank():
    return '<w:p><w:pPr><w:bidi/></w:pPr></w:p>'

def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

def table(rows, widths=None, header_color="1F4E79"):
    if widths is None:
        widths = [3000] * len(rows[0])

    def cell(text, is_header=False, width=3000):
        text = escape(text)
        bold = "<w:b/><w:bCs/>" if is_header else ""
        color = "FFFFFF" if is_header else "000000"
        shade = f'<w:shd w:val="clear" w:color="auto" w:fill="{header_color}"/>' if is_header else ""
        return f'''
<w:tc>
  <w:tcPr>
    <w:tcW w:w="{width}" w:type="dxa"/>{shade}
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
        <w:rtl/>{bold}<w:color w:val="{color}"/>
        <w:sz w:val="22"/><w:szCs w:val="22"/>
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

# ---------- BODY ----------
B = []

# COVER
B.append('''
<w:p><w:pPr><w:bidi/><w:jc w:val="center"/><w:spacing w:before="2400" w:after="240"/></w:pPr>
  <w:r><w:rPr><w:rtl/><w:b/><w:color w:val="1F4E79"/><w:sz w:val="80"/><w:szCs w:val="80"/>
  <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/></w:rPr>
  <w:t xml:space="preserve">دليل امتحان السواقة في دبي</w:t></w:r></w:p>
<w:p><w:pPr><w:bidi/><w:jc w:val="center"/><w:spacing w:after="240"/></w:pPr>
  <w:r><w:rPr><w:rtl/><w:b/><w:color w:val="2E75B6"/><w:sz w:val="44"/><w:szCs w:val="44"/>
  <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/></w:rPr>
  <w:t xml:space="preserve">RTA Road Assessment</w:t></w:r></w:p>
<w:p><w:pPr><w:bidi/><w:jc w:val="center"/><w:spacing w:after="240"/></w:pPr>
  <w:r><w:rPr><w:rtl/><w:b/><w:color w:val="2E75B6"/><w:sz w:val="36"/><w:szCs w:val="36"/>
  <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/></w:rPr>
  <w:t xml:space="preserve">دليل النجاح من أول مرة - Emirates Driving Institute</w:t></w:r></w:p>
<w:p><w:pPr><w:bidi/><w:jc w:val="center"/><w:spacing w:after="240"/></w:pPr>
  <w:r><w:rPr><w:rtl/><w:i/><w:color w:val="595959"/><w:sz w:val="32"/><w:szCs w:val="32"/>
  <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/></w:rPr>
  <w:t xml:space="preserve">باللهجة المصرية - مكتوب خصيصًا لحسام</w:t></w:r></w:p>
''')
B.append(page_break())

# ============ INTRO ============
B.append(p_heading("مقدمة - اقرأها قبل أي حاجة", level=1))
B.append(p_text(
    "يا حسام، الكلام اللي قدامك ده مش من النت ولا كتاب نظري. ده دليل عملي مكتوب علشانك أنت، "
    "بناءً على إنك بتدرس في Emirates Driving Institute (EDI) في دبي، وقدامك امتحان "
    "Road Assessment الأسبوعين الجايين."
))
B.append(p_text(
    "أهم حقيقة لازم تعرفها: نسبة النجاح في امتحانات RTA من أول مرة حوالي 50%، "
    "والمتوسط في الإمارات إن السواق بيحتاج 3 محاولات. ده مش علشان الناس فاشلة، "
    "ده علشان الفاحص بيركز على تفاصيل صغيرة جدًا الناس بتنساها تحت الضغط."
))
B.append(p_text(
    "الدليل ده هيخليك تعدّي من أول مرة لو ذاكرته كويس وطبقته في كل حصة. الاتنين أسبوع الجايين "
    "كفاية جدًا لو شغلت دماغك صح."
))

B.append(p_box(
    "🎯 الفكرة الأساسية: الفاحص مش بيدوّر على سواق محترف. هو بيدوّر على سواق آمن. "
    "السرعة الزيادة = رسوب. اللخبطة = رسوب. عدم النظر في المرايا = رسوب. "
    "الهدوء + المرايا + الإشارة + السرعة المعتدلة = نجاح.",
    color="DEEBF7", border="2E75B6"
))

B.append(page_break())

# ============ FIHRES ============
B.append(p_heading("فهرس الدليل", level=1))
toc = [
    "1) إيه هو امتحان Road Assessment وإيه الفرق بينه وبين الامتحان النهائي؟",
    "2) رحلة استخراج الرخصة الكاملة في دبي",
    "3) شكل الامتحان من ساعة ما تدخل لحد ما تخرج",
    "4) الـ 12 نقطة اللي بيقيمك عليها الفاحص",
    "5) أكتر 15 سبب بيخلي الناس ترسب (وإزاي تتجنبها)",
    "6) الأخطاء الفورية (Immediate Failures) - متعملهاش أبدًا",
    "7) خطة التحضير لمدة أسبوعين - يوم بيوم",
    "8) قواعد المرور المهمة في دبي (السرعات، الإشارات، اللاينات)",
    "9) Yard Test - امتحان الباركنج الـ 5 مهارات",
    "10) في يوم الامتحان - من الصبح للحظة دخول العربية",
    "11) جمل وكلمات إنجليزية ممكن الفاحص يقولها",
    "12) الـ Cheat Sheet النهائية",
]
for line in toc:
    B.append(p_text(line, size=24))

B.append(page_break())

# ============ 1) WHAT IS ROAD ASSESSMENT ============
B.append(p_heading("1) إيه هو الـ Road Assessment؟", level=1))
B.append(p_text(
    "الـ Road Assessment (اسمه كمان Initial Assessment أو Internal Road Test) "
    "هو أول امتحان عملي بتعمله في المدرسة قبل ما تنزل الشارع رسمي. هدفه إن المدرسة تتأكد إنك "
    "وصلت لمستوى آمن قبل ما تخسر فلوس أو تشتكي من المدرسة الفاحص الرسمي."
))

B.append(p_heading("الفرق بين Road Assessment والامتحان النهائي:", level=2))
diff_table = [
    ["النقطة", "Road Assessment (المدرسة)", "RTA Final Test (النهائي)"],
    ["مين بيمتحنك", "مدرّب من نفس المدرسة (EDI)", "فاحص من RTA رسمي"],
    ["مكانه", "ساحة + شوارع المدرسة", "شوارع دبي الفعلية + هايواي"],
    ["مدته", "10-15 دقيقة", "15-20 دقيقة"],
    ["لو رسبت", "تاخد حصص زيادة وتعيد", "تاخد حصص زيادة + تدفع تاني + تعيد"],
    ["أهميته", "بدونه مش هتعمل النهائي", "ده اللي بياخدك الرخصة"],
    ["مستوى الصعوبة", "أسهل شوية", "أصعب وأدق في الملاحظة"],
]
B.append(table(diff_table, widths=[1800, 3500, 3700]))

B.append(p_box(
    "📌 خد بالك: الـ Road Assessment ده تجربة تدريبية - الفاحص فيه عادةً بيكون أقل صرامة من "
    "فاحص RTA. لو نجحت فيه بسهولة، يبقى أنت جاهز للنهائي. لو رسبت فيه، اعتبره فرصة تعرف "
    "مواطن ضعفك قبل ما تخسر فلوس أكتر.",
    color="E2EFDA", border="548235"
))

B.append(page_break())

# ============ 2) JOURNEY ============
B.append(p_heading("2) رحلة استخراج الرخصة الكاملة في دبي", level=1))
B.append(p_text("علشان تبقى عارف أنت في أنهي مرحلة:", size=24))
journey = [
    "فتح ملف في المدرسة (EDI) وأخذ Eye Test",
    "حضور المحاضرات النظرية (Theory Classes)",
    "الـ RTA Knowledge Test (امتحان نظري كمبيوتر)",
    "حصص السواقة العملية في الساحة (Yard) والشوارع الداخلية",
    "Initial Assessment / Road Assessment ← أنت هنا 🎯",
    "حصص الـ Highway (هايواي) والمدينة",
    "Internal Parking Test (الباركنج بـ 5 مناورات)",
    "Internal Road Test (آخر بروفة قبل النهائي)",
    "RTA Final Road Test (الامتحان الرسمي)",
    "استلام الرخصة في خلال يومين",
]
for i, step in enumerate(journey, 1):
    if "أنت هنا" in step:
        B.append(p_text(f"{i}. {step}", bold=True, color="C00000", size=26))
    else:
        B.append(p_text(f"{i}. {step}", size=24))

B.append(page_break())

# ============ 3) EXAM STRUCTURE ============
B.append(p_heading("3) شكل الامتحان - من الدخول للخروج", level=1))

B.append(p_heading("قبل ما تركب العربية:", level=2))
pre = [
    "بتروح المدرسة ومعاك الإمارات ID والـ File Number والـ Learning Permit.",
    "بيقولوا لك في أنهي عربية تستنى. بتروح وتدخل من جنب الراكب وتقعد ورا الفاحص في الكرسي الخلفي (لو مش دورك).",
    "لما يجي دورك، بتاخد كرسي السواق. الفاحص بيقعد جنبك في كرسي الراكب.",
    "بيسلم عليك ويقول لك \"تفضل اظبط نفسك\" أو \"Adjust yourself\". أنت ليك حق تاخد الوقت ده.",
]
for p in pre:
    B.append(p_bullet(p))

B.append(p_heading("الخطوات الـ 6 الأولى - أهم 60 ثانية في الامتحان:", level=2))
B.append(p_text(
    "الفاحص بيراقبك في الـ60 ثانية الأولى وبيحط في باله انطباع أولي. لو عملت الخطوات دي صح، "
    "هو هيدخل وعنده ثقة فيك. لو لخبطت، هيبقى أكتر صرامة معاك بقية الامتحان.",
    size=24
))
first60 = [
    "اظبط الكرسي - يقدم لقدام لحد ما رجلك توصل البدالات وركبتك مش متعفّلة.",
    "اظبط ظهر الكرسي - تكون مش راقد ومش جالس مستقيم 90 درجة.",
    "اظبط مرايا الوسط - بحيث تشوف الزجاج الخلفي كله وسط المرايا.",
    "اظبط مرايا الجنبين - تشوف 80% طريق و20% بدن العربية.",
    "لبس حزام الأمان - وتأكد إن الفاحص لابس حزامه (هتسأله Sir, please your seatbelt).",
    "اضغط الفرامل وحط الجير على D، شغل الإشارة الشمال (لأنك هتدخل في الطريق من الباركنج).",
]
for i, s in enumerate(first60, 1):
    B.append(p_text(f"{i}. {s}", size=24))

B.append(p_box(
    "⚠️ أكتر غلطة بدري: الناس بتركز على إن العربية تتحرك وتنسى تظبط الكرسي والمرايا. "
    "لو الفاحص شافك مش ظابط نفسك، يحس إنك مش جدي. خد وقتك في الإعداد.",
    color="FCE4D6", border="C00000"
))

B.append(p_heading("بعد ما تتحرك:", level=2))
during = [
    "الفاحص هيقول لك \"Take the next right\" أو \"Go straight\". اسمعه كويس ولو مش فاهم اقول له \"Sorry, can you repeat?\"",
    "هيوديك في طريق فيه: نقل لاينات + إشارات مرور + لفات يمين وشمال + roundabout + ممكن هايواي قصير + باركنج في الآخر.",
    "كل ما تنقل لاين أو تلف، الفاحص بيكتب في ورقة جنبه. متبصش على الورقة - ركز في الطريق.",
    "في النص بتاع الامتحان ممكن يقول \"Pull over to the right\" يعني وقف على اليمين. ده بيتعمل علشان يشوف إزاي بتوقف وبتتحرك.",
    "في الآخر بيرجعك للمدرسة ويقول لك \"Park in any available spot\" أو يحدد لك باركنج معين.",
]
for d in during:
    B.append(p_bullet(d))

B.append(page_break())

# ============ 4) 12 EVALUATION POINTS ============
B.append(p_heading("4) الـ 12 نقطة اللي بيقيمك عليها الفاحص", level=1))
B.append(p_text(
    "ده هو الـ Score Sheet اللي الفاحص شايله جنبه. عارف النقط دي يعني عارف هتنجح إزاي:",
    bold=True
))

points = [
    ("1- استخدام المرايا (Mirror Usage)",
     "بيراقبك كل ما بتلف عينيك في المرايا. الفاحص بيشوف حركة عينيك. كل 5-8 ثواني يفترض تبص في مرايا الوسط."),
    ("2- النظرة العمياء (Blind Spot Check)",
     "قبل أي نقل لاين أو تحرك من باركنج أو يو-تيرن، لازم تلف وشّك بسرعة على الكتف. الفاحص لازم يشوف رأسك بتلف."),
    ("3- استخدام الإشارة (Signaling)",
     "كل تغيير اتجاه، حتى لو الشارع فاضي. شغل الإشارة قبل الحركة بـ 3 ثواني على الأقل."),
    ("4- الالتزام بالسرعة (Speed Control)",
     "في دبي، السرعة لازم تكون مناسبة للمكان: 40 في الشوارع الداخلية، 60-80 في الشوارع الرئيسية، 100-120 في الهايواي. أبطأ من اللزوم = رسوب. أسرع من اللزوم = رسوب."),
    ("5- المسافة الآمنة (Safe Distance)",
     "خلي 2-3 ثواني بينك وبين العربية اللي قدامك. لو دوست فرامل والعربية اللي قدامك دوست برضو، يبقى بعدت كفاية."),
    ("6- الالتزام باللاين (Lane Discipline)",
     "متمشيش بين خطين، ومتلمسش الخطوط بعجلاتك. كن في نص اللاين."),
    ("7- اللف الصحيح (Proper Turning)",
     "اليمين من اللاين اليمين، الشمال من اللاين الشمال. بعد اللف، تدخل في اللاين الصحيح."),
    ("8- التوقف عند العلامات (Stop Signs / Red Lights)",
     "العلامة اللي مكتوب عليها STOP لازم توقف وقفة كاملة (3 ثواني)، حتى لو الشارع فاضي. عدم الوقوف الكامل = رسوب."),
    ("9- التعامل مع المشاة (Pedestrian Awareness)",
     "أي ماشي في خط المشاة (zebra) عنده الأولوية. وقف له وخليه يكمل."),
    ("10- التحكم في العربية (Vehicle Control)",
     "الدركسيون بهدوء، الفرامل بالتدريج، البنزين ناعم. مفيش حركة فجائية."),
    ("11- التعامل مع Roundabouts",
     "الأولوية للي داخل الـ roundabout. شغل إشارة الشمال لو هتلف يسار، اليمين لو هتلف يمين، مفيش إشارة لو هتكمل أمام."),
    ("12- الباركنج في الآخر (Final Parking)",
     "في الآخر بترجع تركن. لازم تكون بين الخطوط. لو طلعت من الباركنج هترجع تركن تاني = نقطة سلبية."),
]
for title, desc in points:
    B.append(p_text(title, bold=True, color="1F4E79", size=26))
    B.append(p_text(desc, size=24, indent=300))

B.append(page_break())

# ============ 5) WHY PEOPLE FAIL ============
B.append(p_heading("5) أكتر 15 سبب بيخلي الناس ترسب", level=1))
B.append(p_text(
    "كل سبب من دول حصل لمئات الناس قبلك. اعرفهم وافهمهم الأول، علشان متعملهومش:",
    size=24
))

fail_table = [
    ["السبب", "إزاي تتجنبه"],
    ["نسيان النظرة العمياء قبل نقل اللاين", "اعمل عادة: كل ما تشغل إشارة، رأسك تلف على الكتف"],
    ["السرعة قليلة جدًا", "لو الـ limit 60 سوق 55-60، مش 40. البطء يعطّل الناس"],
    ["السرعة عالية", "اعرف اللوحات. خفّف قبل ما توصل المنطقة الأبطأ"],
    ["نسيان الإشارة في roundabout", "أي تغيير اتجاه = إشارة، حتى لو ثانية واحدة"],
    ["عدم الوقوف الكامل عند STOP sign", "عد \"1001، 1002، 1003\" وأنت واقف"],
    ["التوقف في النص أو على الخط", "اوقف ورا الخط الأبيض، مش عليه ولا قدامه"],
    ["نقل لاين فجأة وقت الإشارة", "ممنوع تنقل لاين قبل تقاطع بـ 30 متر"],
    ["دوس فرامل بعنف", "ابدأ تخفّف من بعيد، الفاحص بيكره الفرامل المفاجأة"],
    ["دركسيون بإيد واحدة", "الإيدين على 9 و3 دايمًا، إلا لما تغيّر جير"],
    ["متابعة الفاحص بعينيك", "ركز على الطريق، الفاحص هيقولك التعليمات"],
    ["عدم التزام اللاين في roundabout", "اللاين الخارجي للخروج بدري، الداخلي لو هتدور"],
    ["السواقة في اللاين الشمال (الأقصى) من غير سبب", "ده لاين السرعة العالية، استخدمه للتجاوز فقط"],
    ["نسيان حزام الأمان", "أول حاجة بعد ما تقعد، الحزام"],
    ["الباركنج النهائي اعوج", "خد وقتك، استخدم المرايا، تأكد إنك بين الخطوط"],
    ["عدم التحرك لما الإشارة تفتح", "ثانية واحدة بعد الخضرا، ثم تحرك"],
]
B.append(table(fail_table, widths=[3500, 5500]))

B.append(page_break())

# ============ 6) IMMEDIATE FAILURES ============
B.append(p_heading("6) الأخطاء الفورية - متعملهاش أبدًا", level=1))
B.append(p_box(
    "🚨 الأخطاء دي = رسوب فوري حتى لو مكنش باقي الامتحان فيه أي غلطة. الفاحص بيوقف الامتحان "
    "في نصه ويرجعك للمدرسة. احفظهم زي ما اسمك.",
    color="FCE4D6", border="C00000"
))

immediate = [
    ("الخروج من الإشارة الحمرا", "حتى لو متراجع بثانية. الإشارة الحمرا = وقفة كاملة."),
    ("تجاوز السرعة بـ 20 كم/س", "لو الـ limit 60 وأنت 80، رسوب فوري."),
    ("تخبيط أي حاجة", "رصيف، عمود، عربية، مخالفة. حتى لو خبطة خفيفة."),
    ("التدخل في الطريق على عربية تانية", "تخلي عربية تدوس فرامل علشانك = رسوب."),
    ("عدم الوقوف عند Stop Sign", "حتى لو الشارع فاضي، Stop = وقفة كاملة 3 ثواني."),
    ("الدخول في لاين معاكس", "في اليو-تيرن أو اللف الشمال، لو دخلت في الاتجاه المضاد."),
    ("استخدام الموبايل", "حتى لو نظرة سريعة. الموبايل في جيبك أو الشنطة."),
    ("عدم استخدام الإشارة في تغيير اتجاه كامل", "نسيان إشارة في يو-تيرن أو لف كامل = رسوب."),
    ("التدخل في حق المشاة", "عدّيت من على ماشي حتى لو من بعيد = رسوب."),
    ("القيادة بدون حزام", "حتى لو 5 ثواني، الفاحص هينهي الامتحان."),
]
for title, desc in immediate:
    B.append(p_text(f"❌ {title}", bold=True, color="C00000", size=26))
    B.append(p_text(desc, size=24, indent=300))

B.append(page_break())

# ============ 7) 2-WEEK PLAN ============
B.append(p_heading("7) خطة الأسبوعين - يوم بيوم", level=1))
B.append(p_text(
    "الخطة دي مفيش فيها كلام نظري - كلها خطوات عملية. اطبعها وعلق عليها كل ما تخلص يوم.",
    bold=True
))

B.append(p_heading("الأسبوع الأول: التركيز على الأساسيات", level=2))

week1 = [
    ("اليوم 1 (السبت)", "اقرا الدليل ده كله مرة واحدة بهدوء. هتلاقي حاجات تركز عليها أكتر من غيرها."),
    ("اليوم 2 (الأحد)", "حصة سواقة: ركّز فقط على المرايا والـ blind spot. كل دقيقة، قول بصوت عالي \"مرايا وسط، يمين، شمال\"."),
    ("اليوم 3 (الاتنين)", "ذاكر القسم 5 و6 (الأخطاء) كويس. شوف فيديوهات يوتيوب \"RTA Dubai road test\" - 5-6 فيديوهات."),
    ("اليوم 4 (التلات)", "حصة سواقة: ركّز على نقل اللاينات والإشارة. اطلب من المدرّب طريق فيه نقل لاين كتير."),
    ("اليوم 5 (الأربع)", "ذاكر إشارات المرور وقواعدها. حدد سرعات دبي (40 / 60 / 80 / 100 / 120)."),
    ("اليوم 6 (الخميس)", "حصة سواقة: ركز على الـ roundabouts والإشارات. مارس وقفة كاملة عند Stop signs."),
    ("اليوم 7 (الجمعة)", "راحة. اقرا الدليل تاني. ذاكر الـ Cheat Sheet."),
]
for day, desc in week1:
    B.append(p_text(day, bold=True, color="1F4E79", size=26))
    B.append(p_text(desc, size=24, indent=300))

B.append(p_heading("الأسبوع الثاني: المحاكاة والتمرين النهائي", level=2))

week2 = [
    ("اليوم 8 (السبت)", "حصة سواقة: اطلب من المدرب عمل \"Mock Test\" - يقعد كأنه فاحص، ميتكلمش، يديك تعليمات بس."),
    ("اليوم 9 (الأحد)", "اشتغل على الباركنج النهائي. مارس 10-15 مرة باركنج صحيح."),
    ("اليوم 10 (الاتنين)", "حصة سواقة: Mock Test تاني. سجل كل غلطة ومراجعتها."),
    ("اليوم 11 (التلات)", "ركّز على الحاجات اللي بتغلط فيها. لو لسه بتنسى الإشارة، اعمل تمرين خاص."),
    ("اليوم 12 (الأربع)", "حصة سواقة أخيرة قبل الامتحان. حصة هادية، مفيش ضغط."),
    ("اليوم 13 (الخميس)", "راحة. متسوقش! اقرا الدليل تاني، نام بدري."),
    ("اليوم 14 (يوم الامتحان)", "اتبع الـ checklist في القسم 10."),
]
for day, desc in week2:
    B.append(p_text(day, bold=True, color="1F4E79", size=26))
    B.append(p_text(desc, size=24, indent=300))

B.append(page_break())

# ============ 8) DUBAI TRAFFIC RULES ============
B.append(p_heading("8) قواعد المرور المهمة في دبي", level=1))

B.append(p_heading("السرعات (احفظهم):", level=2))
speed_table = [
    ["نوع الطريق", "السرعة الافتراضية", "ملاحظات"],
    ["الشوارع السكنية", "25-40 كم/س", "بالقرب من المدارس 25 كم/س"],
    ["الشوارع الداخلية في الأحياء", "40 كم/س", "حتى لو الشارع فاضي"],
    ["الشوارع الرئيسية في المدينة", "60-80 كم/س", "حسب اللوحة"],
    ["Sheikh Zayed Road و Emirates Road", "100-120 كم/س", "في دبي 120 كم/س"],
    ["داخل النفق", "60-80 كم/س", "حسب اللوحة"],
    ["داخل الباركنج (مولات)", "10-20 كم/س", "حذر شديد"],
]
B.append(table(speed_table, widths=[3000, 2400, 3600]))

B.append(p_box(
    "📌 في دبي فيه Salik (تول) والكاميرات في كل حتة. الكاميرا بتمسك سرعة زيادة من 1 كم/س بس "
    "في بعض المناطق. سوق على نفس السرعة المكتوبة، مش زيها ولا أقل بكتير.",
    color="DEEBF7", border="2E75B6"
))

B.append(p_heading("الإشارات اللي لازم تحفظها:", level=2))
signs_table = [
    ["الإشارة", "معناها", "اللي تعمله"],
    ["STOP (مثمنة حمرا)", "وقفة كاملة", "وقف 3 ثواني، بصّ يمين وشمال، ثم اتحرك"],
    ["GIVE WAY (مثلث مقلوب)", "أعطِ الأولوية", "خفّف، لو فيه عربية جاية استناها"],
    ["No Entry (دايرة حمرا)", "ممنوع الدخول", "متدخلش الشارع ده"],
    ["No U-Turn", "ممنوع اليو-تيرن", "كمل أو لف يمين أو شمال بس"],
    ["School Zone", "منطقة مدرسة", "خفّف لـ 25 كم/س"],
    ["Pedestrian Crossing", "خط مشاة", "خفّف وكن جاهز للوقوف"],
    ["Yield (على Roundabout)", "أعطِ الأولوية", "للي داخل الـ roundabout"],
]
B.append(table(signs_table, widths=[2400, 2400, 4200]))

B.append(p_heading("قواعد اللاينات في دبي:", level=2))
lanes = [
    "اللاين الشمال (الأقصى) في الهايواي = للسرعات العالية والتجاوز فقط، مش للسواقة العادية.",
    "اللاين اليمين (الأقصى) في الهايواي = للخروج وللدخول وللسرعات الأبطأ.",
    "في الشوارع: اللاين الشمال للف الشمال، الأوسط للأمام، اليمين للف اليمين.",
    "الخط المتقطع = ممكن النقل. الخط المتصل = ممنوع النقل.",
    "الخط الأصفر المتصل = ممنوع تتجاوز ولا تنقل (نادر في دبي بس موجود).",
]
for l in lanes:
    B.append(p_bullet(l))

B.append(page_break())

# ============ 9) YARD TEST PARKING ============
B.append(p_heading("9) Yard Test - امتحان الباركنج", level=1))
B.append(p_text(
    "الـ Yard Test هو امتحان منفصل عن Road Assessment لكن مهم تعرفه. فيه 5 مهارات:",
    size=24
))

yard = [
    ("1- Parallel Parking (الركن الموازي)",
     "بين عربيتين. الخطوات: 1) قف موازي للعربية اللي قدامك. 2) ارجع، لف الدركسيون يمين كل لما تشوف الزاوية الخلفية للعربية اللي قدامك. 3) لما العربية تدخل بزاوية 45، رجّع الدركسيون شمال. 4) عدّل العربية بين الخطين."),
    ("2- Garage Parking (الركن في جراج)",
     "بترجع تدخل في مكان مغلق من 3 جوانب. لف الدركسيون كله، ارجع ببطء، استخدم المرايا الجانبية. لو حسيت إنك مش في النص، اطلع وارجع تاني."),
    ("3- Angle Parking 60° (الركن المائل)",
     "بترجع بزاوية 60 درجة. ركّز على المسافة بين العربية والخطوط الجانبية."),
    ("4- Slope / Hill Start (الركن على المنحدر)",
     "بتوقف على رمبة (طلوع). بتشغل الـ Hand brake. لما تتحرك، ترفع الـ hand brake وتدوس بنزين شوية. العربية ميصحش ترجع لورا."),
    ("5- Emergency Brake (الفرامل الفجائية)",
     "السيارة بتمشي بسرعة 40 كم/س، الفاحص يقول لك \"BRAKE!\" - تدوس فرامل بكل قوتك. لازم العربية تقف في 3-4 متر."),
]
for title, desc in yard:
    B.append(p_text(title, bold=True, color="1F4E79", size=26))
    B.append(p_text(desc, size=24, indent=300))

B.append(p_box(
    "💡 تيب: في كل مهارة باركنج، استخدم المرايا أكتر من بصرك المباشر. لف وشّك للخلف لما تكون "
    "بترجع، بس استخدم المرايا للتحكم.",
    color="FFF2CC", border="BF8F00"
))

B.append(page_break())

# ============ 10) EXAM DAY ============
B.append(p_heading("10) في يوم الامتحان", level=1))

B.append(p_heading("الليلة اللي قبل:", level=2))
night_before = [
    "نام بدري - 7-8 ساعات نوم على الأقل.",
    "متسوقش الليلة دي. خد راحة.",
    "حضّر هدومك ومستنداتك (Emirates ID + File Number + Learning Permit).",
    "اقرا الـ Cheat Sheet مرة واحدة قبل النوم. مش الكتاب كله، الـ Cheat Sheet بس.",
    "متشربش قهوة كتير - هتزود التوتر.",
]
for n in night_before:
    B.append(p_bullet(n))

B.append(p_heading("الصبح:", level=2))
morning = [
    "افطر، بس مش وجبة تقيلة. أكل خفيف.",
    "روح المدرسة قبل الميعاد بـ 30 دقيقة. التأخير = مشاكل.",
    "خد ميه معاك علشان لو حسيت بتوتر.",
    "متفتحش الموبايل لقراءة \"تيبس آخر لحظة\". هتلخبط نفسك.",
    "اعمل breathing exercise: شهيق 4 ثواني، مسك 4، زفير 6. كرّرها 5 مرات.",
]
for m in morning:
    B.append(p_bullet(m))

B.append(p_heading("لما يجي دورك:", level=2))
turn = [
    "متستعجلش. ادخل العربية وخد نَفَس.",
    "اظبط نفسك بهدوء (الـ 6 خطوات الأولى). ميهمكش لو الفاحص بيستنى.",
    "لو الفاحص قال لك حاجة مش فاهمها، اقول له \"Sorry, can you repeat?\"",
    "متتكلمش زيادة. الفاحص مش صديقك في الامتحان. ركز.",
    "لو غلطت في حاجة، متفكرش فيها. كمل عادي. الفاحص بيخصم نقاط، مش بيرسبك على غلطة واحدة.",
]
for t in turn:
    B.append(p_numbered(t))

B.append(p_box(
    "🧘 لو حسيت بتوتر شديد قبل الامتحان: حط إيدك على الدركسيون، اقفل عينيك 10 ثواني، "
    "نَفَس عميق، وقول لنفسك \"أنا قدامي 15 دقيقة بس - مذاكرت كويس - أنا قادر\". "
    "الإيمان بنفسك ½ النجاح.",
    color="E2EFDA", border="548235"
))

B.append(page_break())

# ============ 11) ENGLISH PHRASES ============
B.append(p_heading("11) جمل إنجليزية ممكن الفاحص يقولها", level=1))
B.append(p_text(
    "الامتحان كله بالإنجليزي. حتى لو إنجليزيتك حلوة، التوتر بيخلي الواحد يستوعب كلمات بصعوبة. "
    "احفظ الجمل دي:"
))

phrases_table = [
    ["الإنجليزي", "اللي قصده الفاحص", "اللي تعمله"],
    ["Adjust yourself / Get ready", "اظبط نفسك", "كرسي + مرايا + حزام"],
    ["Move off when ready", "اتحرك لما تجهز", "تأكد، إشارة، مرايا، اتحرك"],
    ["Take the next right / left", "خد التالي يمين/شمال", "اظبط لاينك من بدري"],
    ["Go straight", "كمّل أمام", "متلفش"],
    ["Pull over to the right", "وقف على اليمين", "إشارة يمين، ابحث عن مكان آمن، اوقف"],
    ["Move off when safe", "اتحرك لما يبقى آمن", "إشارة، مرايا، blind spot، تحرك"],
    ["Park on the right / left", "اركن على اليمين/شمال", "إشارة، اوقف موازي للرصيف"],
    ["Take the next exit", "خد المخرج التالي", "في الـ roundabout أو الهايواي"],
    ["U-turn at the next opportunity", "اعمل يو-تيرن", "اظبط لاين الشمال، إشارة"],
    ["Follow the road ahead", "اتبع الطريق", "كمّل عادي بنفس الاتجاه"],
    ["Sorry, can you repeat?", "(تقولها أنت)", "لو مش فاهم تعليمات"],
    ["BRAKE!", "(صراخ مفاجئ)", "Emergency brake - دوس بكل قوتك"],
    ["End of test, return to school", "خلصت، ارجع المدرسة", "كمل بنفس التركيز للآخر"],
]
B.append(table(phrases_table, widths=[3000, 3200, 2800]))

B.append(p_box(
    "🗣️ نصيحة مهمة: لو الفاحص قال لك \"Take the next right\" وأنت لسه في اللاين الشمال "
    "ومفيش وقت تنقل، اقول له \"Sir, I can't change lanes safely now\" وكمل أمام. "
    "ده دليل على إنك سواق مسؤول - مش هيخصم منك. لكن لو نقلت بشكل خطر، هيرسبك.",
    color="DEEBF7", border="2E75B6"
))

B.append(page_break())

# ============ 12) CHEAT SHEET ============
B.append(p_heading("12) الـ Cheat Sheet النهائية - اطبعها", level=1))

B.append(p_heading("قبل ما العربية تتحرك:", level=2))
B.append(p_text("كرسي ✓  ظهر ✓  مرايا ×3 ✓  حزام ✓  جير D ✓  إشارة ✓",
                bold=True, size=28, align="center", color="1F4E79"))

B.append(p_heading("قبل أي نقل لاين:", level=2))
B.append(p_text("1. مرايا الوسط", bold=True, size=26))
B.append(p_text("2. مرايا الجنب اللي رايح ليه", bold=True, size=26))
B.append(p_text("3. إشارة (3 ثواني)", bold=True, size=26))
B.append(p_text("4. نظرة عمياء (لف الراس)", bold=True, size=26))
B.append(p_text("5. انقل بالتدريج", bold=True, size=26))
B.append(p_text("6. طفّي الإشارة", bold=True, size=26))

B.append(p_heading("عند Stop Sign:", level=2))
B.append(p_text("وقفة كاملة 3 ثواني → بصّ يمين → بصّ شمال → بصّ يمين → اتحرك",
                bold=True, size=26, color="C00000", align="center"))

B.append(p_heading("في الـ Roundabout:", level=2))
B.append(p_text("• هتكمل أمام = مفيش إشارة لحد ما تقرّب من المخرج، وقتها يمين", size=24))
B.append(p_text("• هتلف يمين (المخرج الأول) = إشارة يمين قبل ما تدخل", size=24))
B.append(p_text("• هتلف شمال (مخرج الـ 3 أو 4) = إشارة شمال قبل، يمين قبل المخرج", size=24))
B.append(p_text("• هتعمل يو-تيرن = إشارة شمال طول الوقت + يمين قبل المخرج النهائي", size=24))

B.append(p_heading("الأخطاء الفورية - متعملهاش:", level=2))
B.append(p_text("✗ الخروج من إشارة حمرا", color="C00000", bold=True, size=26))
B.append(p_text("✗ تجاوز السرعة بـ 20+ كم/س", color="C00000", bold=True, size=26))
B.append(p_text("✗ تخبيط أي حاجة (حتى رصيف)", color="C00000", bold=True, size=26))
B.append(p_text("✗ عدم الوقوف عند Stop Sign", color="C00000", bold=True, size=26))
B.append(p_text("✗ الموبايل في إيدك", color="C00000", bold=True, size=26))
B.append(p_text("✗ عدم لبس حزام الأمان", color="C00000", bold=True, size=26))

B.append(p_heading("القاعدة الذهبية:", level=2))
B.append(p_box(
    "Mirror → Signal → Blind Spot → Move\nمرايا → إشارة → نظرة عمياء → حركة\n\n"
    "في كل حركة، في كل مرة، طول الامتحان.",
    color="DEEBF7", border="2E75B6"
))

B.append(p_blank())
B.append(p_text(
    "كلمة أخيرة يا حسام:",
    bold=True, size=28, color="1F4E79", align="center"
))
B.append(p_text(
    "أنت قدامك 14 يوم. لو ذاكرت الدليل ده 3 مرات، طبّقت كل تيب في حصصك، "
    "ونمت كويس قبل الامتحان - هتعدّي من أول مرة بإذن الله. التوتر طبيعي، "
    "بس الاستعداد بيقلّله. أنت قادر. ربنا معاك. 🚗💪",
    bold=True, size=26, align="center", color="1F4E79"
))

# ---------- DOCUMENT XML ----------
document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document {NS}>
  <w:body>
    {''.join(B)}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
      <w:bidi/>
    </w:sectPr>
  </w:body>
</w:document>
'''

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
        <w:sz w:val="24"/><w:szCs w:val="24"/>
        <w:lang w:val="ar-EG" w:bidi="ar-EG"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault><w:pPr><w:bidi/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:styleId="ListParagraph" w:default="0">
    <w:name w:val="List Paragraph"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:bidi/><w:ind w:right="720"/></w:pPr>
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
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/>
    <w:lvlText w:val="•"/><w:lvlJc w:val="left"/>
    <w:pPr><w:bidi/><w:ind w:right="720" w:hanging="360"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="1">
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>
    <w:lvlText w:val="%1."/><w:lvlJc w:val="left"/>
    <w:pPr><w:bidi/><w:ind w:right="720" w:hanging="360"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
  <w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
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

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', content_types)
    z.writestr('_rels/.rels', rels)
    z.writestr('word/_rels/document.xml.rels', document_rels)
    z.writestr('word/document.xml', document_xml)
    z.writestr('word/styles.xml', styles_xml)
    z.writestr('word/numbering.xml', numbering_xml)
    z.writestr('word/settings.xml', settings_xml)

print(f"Created: {OUT}")
print(f"Size: {os.path.getsize(OUT):,} bytes")

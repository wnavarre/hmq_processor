import load_data
import string_stuff
from string_stuff import *
import common_print

def body(office, fp):
    fp.write("    <img src=\"./hml.jpg\" class=\"logo_top\" />\n")
    fp.write("    <h1>2024 Housing Medford Questionnaire: Candidates for {}, arranged by question</h1>\n".format(office))
    common_print.print_discussion(fp)
    fp.write("    <h2>Index</h2>\n")
    qs, rs = load_data.load()
    rs.sort(key=lambda r: last_name(r["NAME"]))
    rs = [ v for v in rs if v["OFFICE"] == office ]
    for q in qs:
        if q.applies_all() or (not q.applies_to_office(office)): continue
        string_stuff.format_paragraphs_as_html(q.text(), fp)
        fp.write("<ul>\n")
        all_short = all(("\n" not in r[q.code()]) and (len(r[q.code()]) < 80) for r in rs)
        for r in rs:
            a = r[q.code()]
            empty = (not a) or a.isspace()
            if all_short:
                a_pview = " ({})".format(a)
            else:
                a_pview = ""
            if empty and q.is_aux():
                fp.write("  <li>{} (NO ANSWER)</li>".format(r["NAME"]))
            else:
                if empty: a_pview = "(NO ANSWER)"
                fp.write("  <li><a href=\"#{}\">{}</a> {}</li>".format(html_name(r, q), r["NAME"], a_pview))
        fp.write("</ul>\n")
    open_question_div = False
    q_index = -1
    for q in qs:
        if q.applies_all() or (not q.applies_to_office(office)): continue
        if not q.is_aux():
            q_index += 1
            if open_question_div: fp.write("</div>\n")
            fp.write("<hr />\n")
            fp.write("<div class=\"QRESPONSEBLOCK{}\">\n".format(1 - (q_index % 2)))
            open_question_div = True
        fp.write("    <a name=\"QQ{}\" />".format(q.code()))
        if q.is_aux():
            fp.write("    <h2>Follow-up question</h2>\n")
        else:
            fp.write("    <h2>Question</h2>\n")
        string_stuff.format_paragraphs_as_html(q.text(), fp)
        for r in rs:
            a = r[q.code()]
            if q.is_aux() and ((not a) or a.isspace()):
                if q.is_aux():
                    continue
            fp.write("    <a name=\"{}\" />\n".format(html_name(r, q)))
            fp.write("    <h3>{} [<a href=\"#QQ{}\">QUESTION</a>]</h3>\n".format(r["NAME"], q.code()))
            if q.is_aux():
                main_q = q.aux_of()
                fp.write("    <p>[ Answer to <a href=\"#QQ{}\">main question</a>: {} ]</p>".format(
                    main_q.code(),
                    r[main_q.code()]
                ))
            common_print.print_question_response(fp, q, r)
    if open_question_div: fp.write("</div>\n")
    fp.write("    <img src=\"./hml.jpg\" class=\"logo_bottom\" />\n")

def go(fp, office):
    fp.write("<html>\n")
    fp.write("  <head>\n")
    fp.write("    <link rel=\"stylesheet\" href=\"./survey_response_style.css\" />\n")
    fp.write("    <title>2024 Housing Medford Questionnaire</title>\n")
    fp.write("  </head>\n")
    fp.write("<body>\n")
    body(office, fp)
    fp.write("</body></html>")
    
if __name__ == "__main__":
    with open("sc_by_question.html", 'w+') as fp: go(fp, "School Committee")
    with open("cc_by_question.html", 'w+') as fp: go(fp, "City Council")
    with open("mayor_by_question.html", 'w+') as fp: go(fp, "Mayor")

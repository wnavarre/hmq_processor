import load_data
import string_stuff
from string_stuff import *
import common_print
import offices

def body(fp):
    qs, rs = load_data.load()
    rs.sort(key=lambda r: (offices.rank[r["OFFICE"]], last_name(r["NAME"])))
    fp.write("    <img src=\"./hml.jpg\" class=\"logo_top\" />\n")
    fp.write("    <h1>2024 Housing Medford Questionnaire: All candidates, arranged by candidate</h1>\n")
    common_print.print_discussion(fp)
    fp.write("    <h2>Index</h2>\n")
    fp.write("    <ul>\n")
    for r in rs:
        name = r["NAME"]
        name_code = name.replace(" ", "_")
        fp.write("      <li>{} candidate <a href=\"#{}\">{}</a></li>\n".format(
            offices.adjective[r["OFFICE"]],
            name_code,
            name
        ))
    fp.write("    </ul>\n")
    for r in rs:
        fp.write("   <hr />\n")
        name = r["NAME"]
        name_code = name.replace(" ", "_")
        office = r["OFFICE"]
        fp.write("    <a name=\"{}\" />\n".format(name_code))
        fp.write("    <h2>{}, candidate for {}</h2>\n".format(
            name, office
        ))
        for q in qs:
            if q.applies_all() or (not q.applies_to_office(office)): continue
            fp.write("    <h3>Question</h3>\n")
            string_stuff.format_paragraphs_as_html(q.text(), fp)
            fp.write("    <h3>{}'s answer{}</h3>\n".format(
                name,
                "" if (not q.is_selection())
                else
                " (candidates were given several options to choose from)"
            ))
            common_print.print_question_response(fp, q, r)
    fp.write("    <img src=\"./hml.jpg\" class=\"logo_bottom\" />\n")

if __name__ == "__main__":
    with open("by_candidate.html", "w+") as fp:
        fp.write("<html>\n")
        fp.write("  <head>\n")
        fp.write("    <link rel=\"stylesheet\" href=\"./survey_response_style.css\" />\n")
        fp.write("    <title>2024 Housing Medford Questionnaire</title>\n")
        fp.write("  </head>\n")
        fp.write("<body>\n")
        body(fp)
        fp.write("</body></html>")

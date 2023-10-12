import string_stuff

def print_question_response(fp, q, r):
    if q.is_selection():
        options_and_flags, others = q.selection_flags_in_response(r)
        assert len(others) < 2
        for opt, flag in options_and_flags:
            flag_emoji = "&#9745;" if flag else "&#9744;"
            if not flag:
                expl = " (N.B.: Candidate {} did <em>not</em> select this option)".format(r["NAME"])
            else:
                expl = ""
            fp.write("<p><big><big>{}</big></big> {}{}</p>\n".format(flag_emoji, opt, expl))
        for e in others:
            fp.write("<p><big><big>&#9745</big></big><strong> OTHER:</strong> {}</p>\n".format(e))
    else:
        string_stuff.format_paragraphs_as_html(r[q.code()] or "(NO ANSWER)", fp)

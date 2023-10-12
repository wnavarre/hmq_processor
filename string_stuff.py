import io

class ListFormatter:
    def __init__(self, output_pointer):
        self._fp = output_pointer
        self._bullet_points = []
    def add_line(self, line):
        if not line: return
        if line[0] in "*-":
            self._bullet_points.append(line[1:])
        else:
            self.finish()
            self._fp.write("<p>{}</p>\n".format(line))
    def finish(self):
        if not self._bullet_points: return
        self._fp.write("<ul>\n")
        for e in self._bullet_points:
            self._fp.write("  <li>{}</li>\n".format(e))
        self._fp.write("</ul>\n")
        self._bullet_points = []

def format_paragraphs_as_html(st, fp):
    st = st.replace("\r", "\n")
    old_length = -1
    while len(st) != old_length:
        old_length = len(st)
        st = st.replace("  "  ,  " ")
        st = st.replace("\n\n", "\n")
        st = st.replace(" \n" , "\n")
        st = st.replace("\n " , "\n")
    formatter = ListFormatter(fp)
    for e in st.split("\n"): formatter.add_line(e)
    formatter.finish()

def last_name(name):
    return name.split()[-1]
    
def html_name(response, question):
    return question.code() + response["NAME"].replace(" ", "_")

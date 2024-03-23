import csv
import consistent_sort

class Question:
    __slots__ = [
        "_applies_to",
        # _applies_to is a list; empty one if NONE; None if ALL.
        "_raw_text",
        "_text",
        "_code",
        "_rank",
        "_aux_count",
        "_aux_of",
        "_selection_options",
        "_selection_options_set"
    ]
    def __init__(self, question_set, qdata, text, rank):
        if not qdata:
            raise ValueError("No qdata for question: {}".format(text))
        assert qdata
        assert text
        self._selection_options = None
        self._aux_count = 0
        self._raw_text = text
        self._rank = rank
        self._aux_of = None
        text, _ = text
        is_aux = text.startswith("AUX")
        if is_aux:
            self._aux_of = question_set.main_for_aux()
            self._aux_of._aux_count += 1
            self._text = text[3:]
        else:
            self._text = text
        if qdata[0] == "_":
            self._applies_to = None
            self._code = qdata[1:]
            if self._code == "DEL": self._applies_to = ()
        else:
            self._applies_to = (qdata,)
            dot = self._text.find(".")
            assert dot > 0
            self._code = self._text[0:dot] + "+" + self.applies_to_code()
        if self._aux_of is not None:
            main_applies_to = self._aux_of._applies_to
            if main_applies_to != self._applies_to:
                raise AssertionError("Aux with mismatch: {} != {}\nMain code: {}; Aux code: {}".format(
                    main_applies_to,
                    self._applies_to,
                    self._aux_of.code(),
                    self.code()
                ))
    def applies_any(self): return self.applies_all() or self._applies_to
    def applies_all(self): return self._applies_to is None
    def applies_to(self, candidate): return self.applies_to_office(candidate["OFFICE"])
    def applies_to_office(self, office):
        debug = False
        if debug: print(self.code(), end=' ')
        if self.applies_all():
            if debug: print("applies to {} because applies to all.".format(office))
            return True
        if office in self._applies_to:
            if debug: print("applies to {} because applies to {}.".format(office, self._applies_to))
            return True
        if debug: print("doesn't apply to {} because applies to {}.".format(office, self._applies_to))
        return False
    def applies_to_code(self):
        out = "-".join(a.replace(" ", "_") for a in self._applies_to)
        assert not any((c.isspace() or c in "/\"'\\") for c in out)
        return out
    def has_aux(self):  return self._aux_count
    def is_aux(self):   return self._aux_of is not None
    def aux_of(self):   return self._aux_of
    def text(self):     return self._text
    def raw_text(self): return self._raw_text
    def is_selection(self): return self._selection_options is not None
    def set_selection(self, selection_string):
        if not selection_string: return
        self._selection_options = self.selections_in_answer(selection_string)
        self._selection_options_set = set(self._selection_options)
    def selection_flags_in_response(self, r):
        sel_set = set(self.selections_in_response(r))
        return [ (e, e in sel_set) for e in self._selection_options ], list(sel_set - self._selection_options_set)
    def selections_in_response(self, r): return self.selections_in_answer(r[self.code()])
    def selections_in_answer(self, a): return [v.strip() for v in a.split(";")]
    def code(self): return self._code
    def __repr__(self):
        return "{} -> {} ({})".format(self._code, self._text, self._applies_to)

class QuestionSet:
    __slots__ = [
        "_code_to_q",
        "_text_to_q",
        "_current_aux_main"
    ]
    def __init__(self):
        self._code_to_q, self._text_to_q = {}, {}
        self._current_aux_main = None
    def read_selection(self, d):
        for qtext, v in d.items():
            if v:
                q = self.from_text(qtext, failure_ok=True)
                if q is not None: q.set_selection(v)
    def from_code(self, code): return self._code_to_q[code]
    def from_text(self, raw_text, *, failure_ok=False):
        if failure_ok:
            return self._text_to_q.get(raw_text)
        else:
            return self._text_to_q[raw_text]
    def __getitem__(self, code): return self.from_code(code)
    def process_response(self, response_dict):
        processed = {}
        old_count = len(processed)
        # First processed the "applies to all" cases.
        for q in iter(self):
            if not q.applies_all(): continue
            processed[q.code()] = response_dict[q.raw_text()].strip()
        for k, v in response_dict.items():
            q = self.from_text(k)
            if q.code() in processed: continue
            if q.applies_to(processed): processed[q.code()] = v.strip()
        return processed
    def __iter__(self): return iter(self._code_to_q.values())
    def insert(self, q):
        text, code = q.raw_text(), q.code()
        if text in self._text_to_q: raise ValueError("Duplicate 'text' key: " + text)
        self._text_to_q[text] = q
        if code != "DEL":
            if code in self._code_to_q: raise ValueError("Duplicate 'code' key: " + code)
            self._code_to_q[code] = q
        if not q.is_aux(): self._current_aux_main = q
    def main_for_aux(self): return self._current_aux_main

def build_question_set(dqdata):
    qs = QuestionSet()
    rank = 0
    for text, qdata in dqdata.items():
        qs.insert(Question(qs, qdata, text, rank))
        rank += 1
    return qs

QDATA_FIELD = ("Timestamp", "_QDATA")
QDATA_VALUE = "_QDATA"

def without_field(d, field):
    del d[field]
    return d

class DictMaker:
    __slots__ = ("_keys",)
    def __init__(self, keys): self._keys = keys
    def __call__(self, values):
        assert len(self._keys) == len(values)
        return { k : v for k, v in zip(self._keys, values) }
    def it_to_it(self, it):
        for e in it: yield self(e)

def load(fname="./cleaned_up.csv"):
    with open(fname, 'r') as fp:
        reader = csv.reader(fp)
        heading_row = next(reader)
        column_count = len(heading_row)
        first_row = next(reader)
        assert len(first_row) == column_count
        assert first_row[0] == QDATA_VALUE
        as_dict = DictMaker(tuple(zip(heading_row, first_row)))
        q_out = build_question_set(without_field(as_dict(first_row), QDATA_FIELD))
        reader = as_dict.it_to_it(reader)
        second_row = next(reader)
        assert second_row[QDATA_FIELD] == "_QDATA_SELECT"
        q_out.read_selection(second_row)
        r_out = [ q_out.process_response(without_field(row, QDATA_FIELD)) for row in reader ]
        return q_out, r_out

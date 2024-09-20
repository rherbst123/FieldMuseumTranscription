import re

def is_abbreviated_name(s):
    return re.match("[A-Z]{1}.\s([A-Z]{1}.\s)?([A-Z]{1}.\s)?(von\s|van\s|der\s)?[A-Z]{1}[a-z]+", s)

for s in ["A.B.C. Touw", "A. B. Touw", "D. der Mensch"]:
    print(is_abbreviated_name(s))

# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re

regex = r"([^a-zA-Z]'.*?'[^a-zA-Z])"

with open('tests/example_novel_chapter.txt', 'r') as f:
    test_str = f.read()

matches = re.finditer(regex, test_str, re.MULTILINE)

for matchNum, match in enumerate(matches, start=1):
    
    print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    
    for groupNum in range(0, len(match.groups())):
        groupNum = groupNum + 1
        
        print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

print()
print()
for m in re.finditer(regex, test_str, re.MULTILINE):
    print(m.group(1))
# Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.

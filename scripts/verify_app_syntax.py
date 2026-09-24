import re

with open('frontend/app.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# We can also check if there are any obvious unclosed tags or syntax issues
stack = []
pairs = {')': '(', '}': '{', ']': '['}

in_multiline_comment = False
in_template = False

for line_idx, line in enumerate(lines):
    line_no = line_idx + 1
    i = 0
    while i < len(line):
        if in_multiline_comment:
            if line[i:i+2] == '*/':
                in_multiline_comment = False
                i += 2
                continue
            i += 1
            continue
        
        if line[i:i+2] == '/*':
            in_multiline_comment = True
            i += 2
            continue
            
        if line[i:i+2] == '//':
            break # rest of line is single-line comment
            
        ch = line[i]
        
        if ch == '`':
            in_template = not in_template
            i += 1
            continue
            
        if not in_template:
            if ch in '({[':
                stack.append((ch, line_no))
            elif ch in ')}]':
                if not stack:
                    print(f"ERROR: Extra closing {ch} at line {line_no}")
                else:
                    top, top_line = stack.pop()
                    if top != pairs[ch]:
                        print(f"ERROR: Mismatched {ch} at line {line_no}, expected {top} from line {top_line}")
        i += 1

if stack:
    print(f"ERROR: Unclosed items: {len(stack)}")
    for s, l in stack[-10:]:
        print(f"  Unclosed '{s}' from line {l}")
else:
    print("SUCCESS: All brackets, braces, and parentheses perfectly balanced!")

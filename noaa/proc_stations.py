import re

def alter(line):
    l = re.compile(r'(?<![A-Z])\s+').split(line)
    if len(l) > 5:
        l = l[:5]
    return '\t'.join([c.strip() for c in l])

with open('ghcnd-stations.txt', 'r') as f:
    lines = (line.strip() for line in f)
    new_lines = [alter(l) for l in lines]

with open('stations.txt', 'w') as f:
    f.write('\n'.join(new_lines) + '\n')
        

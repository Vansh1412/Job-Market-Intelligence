import os
import re

PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret[_-]?key|password|auth[_-]?token)\s*[:=]\s*["\'][^"\']+["\']'),
    re.compile(r'ghp_[a-zA-Z0-9]{36}'),
    re.compile(r'xox[baprs]-[0-9a-zA-Z]{10,48}'),
    re.compile(r'AIza[0-9A-Za-z-_]{35}'),
    re.compile(r'(?i)eval\s*\('),
    re.compile(r'(?i)exec\s*\('),
]

findings = []
for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['node_modules', '.git', '.pytest_cache', 'jobs-tier1-L', 'data']):
        continue
    for f in files:
        if f.endswith(('.py', '.ts', '.tsx', '.json', '.yaml', '.yml', '.md', '.sh')):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as handle:
                    for idx, line in enumerate(handle, 1):
                        for pat in PATTERNS:
                            if pat.search(line):
                                findings.append((filepath, idx, pat.pattern, line.strip()[:100]))
            except Exception:
                pass

print(f'Total findings: {len(findings)}')
for file, line, pat, content in findings:
    print(f'{file}:{line} [{pat}] -> {content}')

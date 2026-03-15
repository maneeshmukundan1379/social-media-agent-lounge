#!/usr/bin/env python3
"""
Fix script to remove researcher agent references.
Run this with: python3 fix_researcher.py
"""
import os
import re

# Fix crew.py - remove researcher agent method
crew_file = 'src/man_debate/crew.py'
if os.path.exists(crew_file):
    with open(crew_file, 'r') as f:
        content = f.read()
    
    # Remove the researcher agent method
    # Pattern: @agent\n    def researcher(self) -> Agent: ... (until next @agent or @task)
    pattern = r'@agent\s+def researcher\(self\) -> Agent:.*?(?=\n    @(?:agent|task|crew)|\Z)'
    new_content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    if new_content != content:
        with open(crew_file, 'w') as f:
            f.write(new_content)
        print(f"✅ Fixed {crew_file}: Removed researcher agent method")
    else:
        print(f"✅ {crew_file}: No researcher agent found (already clean)")
else:
    print(f"❌ {crew_file} not found")

# Fix tasks.yaml - replace researcher with debater
tasks_file = 'src/man_debate/config/tasks.yaml'
if os.path.exists(tasks_file):
    with open(tasks_file, 'r') as f:
        content = f.read()
    
    if 'agent: researcher' in content:
        content = content.replace('agent: researcher', 'agent: debater')
        with open(tasks_file, 'w') as f:
            f.write(content)
        print(f"✅ Fixed {tasks_file}: Replaced 'agent: researcher' with 'agent: debater'")
    else:
        print(f"✅ {tasks_file}: No researcher reference found (already clean)")
else:
    print(f"❌ {tasks_file} not found")

# Verify
print("\n📋 Verification:")
for file in [crew_file, tasks_file]:
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read()
            researcher_count = content.count('researcher')
            status = "✅" if researcher_count == 0 else "❌"
            print(f"  {status} {os.path.basename(file)}: 'researcher' count = {researcher_count}")

print("\n✅ Fix complete! The crew should now work without researcher references.")


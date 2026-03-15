#!/usr/bin/env python3
"""
Fix script to replace {topic} with {motion} in config files.
Run this with: python3 fix_topic_variable.py
"""
import os
import sys

config_dir = 'src/man_debate/config'

# Read and fix tasks.yaml
tasks_file = os.path.join(config_dir, 'tasks.yaml')
if os.path.exists(tasks_file):
    with open(tasks_file, 'r') as f:
        content = f.read()
    
    if '{topic}' in content:
        content = content.replace('{topic}', '{motion}')
        with open(tasks_file, 'w') as f:
            f.write(content)
        print(f"✅ Fixed {tasks_file}: Replaced {{topic}} with {{motion}}")
    else:
        print(f"✅ {tasks_file}: Already uses {{motion}}")
else:
    print(f"❌ {tasks_file} not found")

# Read and fix agents.yaml
agents_file = os.path.join(config_dir, 'agents.yaml')
if os.path.exists(agents_file):
    with open(agents_file, 'r') as f:
        content = f.read()
    
    if '{topic}' in content:
        content = content.replace('{topic}', '{motion}')
        with open(agents_file, 'w') as f:
            f.write(content)
        print(f"✅ Fixed {agents_file}: Replaced {{topic}} with {{motion}}")
    else:
        print(f"✅ {agents_file}: Already uses {{motion}}")
else:
    print(f"❌ {agents_file} not found")

# Verify
print("\n📋 Verification:")
for file in [tasks_file, agents_file]:
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read()
            topic_count = content.count('{topic}')
            motion_count = content.count('{motion}')
            status = "✅" if topic_count == 0 else "❌"
            print(f"  {status} {os.path.basename(file)}: {{topic}}={topic_count}, {{motion}}={motion_count}")

if topic_count == 0:
    print("\n✅ All template variables fixed! You can now run the crew.")
    sys.exit(0)
else:
    print("\n❌ Some {topic} variables still remain. Please check the files.")
    sys.exit(1)


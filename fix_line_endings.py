#!/usr/bin/env python3
"""Convert vCard file to Unix line endings for iCloud compatibility"""

import config

# Read the file
with open(config.PROCESSED_VCARD_FILE, 'rb') as f:
    content = f.read()

# Convert CRLF to LF
content = content.replace(b'\r\n', b'\n')

# Write new file
output_file = config.PROCESSED_VCARD_FILE.replace('.vcf', '_unix.vcf')
with open(output_file, 'wb') as f:
    f.write(content)

print(f"Created: {output_file}")
print("This file has Unix line endings (LF) which should be compatible with iCloud import.")
#!/usr/bin/python3
'''Converts a markdown table, the output of the LLM from one_prompt_per_bullet_for_trial.py,
to CSV format.
'''

import csv
import sys


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: create_csv_from_md_response.py <markdown_table.md>')
        sys.exit(1)

    with open(sys.argv[1]) as f:
        lines = f.read().split('\n')
        lines = lines[2:]  # Remove header rows

    csv_filename = sys.argv[1].replace('.md', '.csv')
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        for line in lines:
            line = line.strip()
            if line:
                fields = [field.strip() for field in line.split('|')]
                fields = fields[1:-1]
                if len(fields) == 6:
                    fields.insert(0, '01')
                    writer.writerow(fields)
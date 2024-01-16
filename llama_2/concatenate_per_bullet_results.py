#!/usr/bin/python3
'''Creates a final markdown table based on the LLM outputs produces by
one_prompt_per_bullet_for_trial.py.
'''

import sys
import subprocess


def line_not_categorized(line):
    fields = [field.strip() for field in line.split('|')[1:-1]]
    if len(fields) != 6:
        return True

    def field_not_categorized(field):
        return (not field) or field == 'None' or field == '-'

    return (field_not_categorized(fields[0]) or (field_not_categorized(fields[2])
            and field_not_categorized(fields[3]) and field_not_categorized(fields[4])))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: concatenate_per_bullet_results.py <trial_directory>')
        sys.exit(1)

    # List all the outputs.
    files = subprocess.run('ls %s/response_bullet_*.txt' % sys.argv[1], check=True, shell=True, capture_output=True).stdout
    result = []
    for filename in files.split():
        print('Reading %s...' % filename, file=sys.stderr)
        with open(filename) as f:
            s = f.read().strip()
        if not s:
            print('WARNING: empty file %s, skipping...' % filename)
        else:
            lines = s.split('\n')

            # Look for lines that look like markdown tables; skip everything else.
            for line in lines:
                line = line.strip()
                if line.startswith('|'):

                    # Exclude header.
                    if (line != '| Criterion Text | Inclusion/Exclusion | Disease | Biomarker | Prior Therapy | Criterion Rule |'
                            and not line.startswith('| --- |') and not line_not_categorized(line)):
                        result.append(line)

    print('| Criterion Text | Inclusion/Exclusion | Disease | Biomarker | Prior Therapy | Criterion Rule |')
    print('| --- | --- | --- | --- | --- | --- |')
    print('\n'.join(result))

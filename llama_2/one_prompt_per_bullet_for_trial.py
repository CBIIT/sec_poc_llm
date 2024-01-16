'''Script to call Llama 2 once for each top-level bullet point in an EC section.

TODO: use command-line arguments instead of constants.
TODO: there are some cases where this splits bullet points too aggressively,
      losing context.
'''

import boto3
import json
import sys


PROMPT_TEMPLATE = '/Users/callawayjl/Dev/CTRP/LLM/new_zeroshot_approach/single_bullet_prompt.txt'

# Most trials use various types of bullet characters to distinguish criteria,
# but Trial 8 uses numbers.
BULLET_CHARS = {str(i) for i in range(1, 10)}
BULLET_CHARS.add('•')
BULLET_CHARS.add('')

# Fill in the following two with the actual values when you jumpstart llama2.

ENDPOINT = 'jumpstart-dft-meta-textgeneration-l-20240111-175221'

MODEL = 'jumpstart-dft-meta-textgeneration-l-20240111-1-20240111-1752270'

# When using a chat model
PROMPT = '[INST] <<SYS>> You are assisting in scientific research on cancer treatments in human patients.  Clear, concise, technically accurate language is more important than eloquence.  Above all, be correct and do not output any false or misleading material. <<SYS>> %s [/INST] '

# LLM Hyperparameters

MAX_NEW_TOKENS = 350

TEMPERATURE = 0.6  # Default 1.0

TOP_P = 0.5

TOP_K = 35  # Default 40

REPETITION_PENALTY = 1.0  # 1.0 means no penalty


def call_sagemaker_llama(prompt, sequence_num):
    formatted_prompt = PROMPT % prompt
    request = {
            'inputs': formatted_prompt,
#            'inputs': prompt,
            'parameters': {
                    'max_new_tokens': MAX_NEW_TOKENS,
                    'return_full_text': False,
                    'temperature': TEMPERATURE,
                    'top_p': TOP_P,
                    'top_k': TOP_K,
                    'repetition_penalty': REPETITION_PENALTY,
                    'seed': 0,  # Keep deterministic; same response each time
                    }
            }
    client = boto3.client('sagemaker-runtime', region_name='us-east-1')
    response = client.invoke_endpoint(EndpointName=ENDPOINT, InferenceComponentName=MODEL,
            ContentType='application/json', Body=json.dumps(request))
    return json.loads(response['Body'].read().decode('utf-8'))[0]['generated_text']


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: one_prompt_per_bullet_for_trial.py <ec_section.txt>')
        sys.exit(1)

    with open(PROMPT_TEMPLATE) as f:
        prompt_template = f.read()

    with open(sys.argv[1]) as f:
        lines = f.read().split('\n')

    prompts = []

    last_bullet = ''
    for line in lines:
        if line.lower().startswith('inclusion criteria') or line.lower().startswith('exclusion criteria'):
            mode = line
            continue

        line = line.strip()
        if line:
            if line[0] in BULLET_CHARS:
                if last_bullet:
                    prompts.append(prompt_template.replace('__EC_CRITERIA_SNIPPET__', last_bullet))
                last_bullet = '%s\n\n%s' % (mode, line)
            else:
                if last_bullet:
                    last_bullet = '%s\n%s' % (last_bullet, line)
    prompts.append(prompt_template.replace('__EC_CRITERIA_SNIPPET__', last_bullet))

    print('Starting endpoint calls for %d chunks...' % len(prompts))
    for i, prompt in enumerate(prompts):
        num = i + 1
        print('Calling endpoint for chunk %d...' % num)
        response = call_sagemaker_llama(prompt, num)
        with open('response_bullet_%03d.txt' % num, 'w') as f:
            f.write(response)
        with open('prompt_bullet_%03d.txt' % num, 'w') as f:
            f.write(prompt)

    print('Finished.  Made %d calls to endpoint.' % num)

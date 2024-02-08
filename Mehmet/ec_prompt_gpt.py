'''Constructs a prompt for summarizing/extracting information about eligibility
criteria for a clinical trial, and sends it to a GPT instance in Azure.

The prompt consists of several parts which are assembled from text files:

- a "preamble" giving common instructions; this is the same for all the prompts
- the eligibility criteria section from the trial; specific to an individual trial
- a specific question (with an optional example) that is added after the prior two
'''
import argparse
import os
import os.path
import openai
import sys


def parse_args():
    parser = argparse.ArgumentParser(description='TODO')
    parser.add_argument('--endpoint', type=str, required=True, help='Azure OpenAI Endpoint')
    parser.add_argument('--version', type=str, default='2023-07-01-preview', help='Azuer OpenAI model version')
    parser.add_argument('--model', type=str, required=True, help='Azure OpenAI model aka engine')
    parser.add_argument('--system_prompt', type=str, default='system_prompt.txt', help='System prompt')
    parser.add_argument('--prompt_template', type=str, default='prompt_template.txt',
            help='Prompt template (same across all questions; EC section will be substituted in here)')
    parser.add_argument('--ec_section', type=str, required=True, help='Trial Eligibility Criteria text')
    parser.add_argument('--question_prompt', type=str, required=True,
            help='Question (with optional example); will be prefixed with prompt_template to form user prompt')
    parser.add_argument('--save_dir',
            help='If present, prompt and output will be saved to this directory; otherwise only response will be printed')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print('OPENAI_API_KEY must be provided as an environment variable', file=sys.stderr)
        sys.exit(1)

    with open(args.system_prompt) as f:
        system_prompt = f.read()
    with open(args.prompt_template) as f:
        prompt = f.read()
    with open(args.ec_section) as f:
        prompt = prompt.replace('__EC_SECTION__', f.read())
    with open(args.question_prompt) as f:
        prompt += f.read()

    openai.api_type = 'azure'
    openai.api_base = args.endpoint
    openai.api_version = args.version
    openai.api_key = api_key

    message_text = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
            ]

    response = openai.ChatCompletion.create(
            engine=args.model,
            messages = message_text,
            temperature=0.1,
            max_tokens=800,
            top_p=0.5,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
            )
    response_text = response['choices'][0]['message']['content']

    if args.save_dir:
        with open(os.path.join(args.save_dir, 'prompt.txt'), 'w') as f:
            f.write(prompt)
        with open(os.path.join(args.save_dir, 'response.txt'), 'w') as f:
            f.write(response_text)

    print(response_text)

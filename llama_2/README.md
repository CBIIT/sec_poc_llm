# Notes on Llama 2 zero-shot approach:

- The general approach I settled on was to send a separate prompt to the LLM for each bullet point in the eligibility criteria section.  I used this approach largely because I was bumping up against the context window limit when trying to have Llama 2 summarize/categorize an entire EC section.

- This approach required scripting of sending the response, and post-processing the LLM output into the final table.  While the scripts make certain decisions about what output to keep and what to discard (described below), the same scripts were used for every trial; in other words, no trial was treated specially or differently from the others.

- one_prompt_per_bullet_for_trial.py was called for each trial.  This script cuts the EC section into separate bullet points (while preserving the "Inclusion:" or "Exclusion:" header), and sends a prompt to the LLM for each bullet.

- For convenience, the prompt template that one_prompt_per_bullet_for_trial.py uses is saved as single_bullet_prompt.txt at the top level.

- The resulting prompts and raw LLM outputs are saved in subdirectories of test_results_final for each trial.  The naming should be self-explanatory: for instance, prompt_bullet_003.txt was the prompt for the third bullet point in the EC section, and the LLM replied with response_bullet_003.txt.

- concatenate_per_bullet_results.py was then called for each trial.  This script does several things:
  1. Discard any output that does not appear to be a markdown table row (which is what the LLM was instructed to return).  This removes things like footnotes and chatty asides the LLM would generate.
  2. Discard any table rows where the first column (Criterion Text) is blank.  I had a lot of problems with the LLM returning blank columns, even when instructed never to do so.
  3. Discard any table rows where the third, fourth, and fifth (Disease, Biomarker, and Prior Therapies) were ALL blank.  Again, the LLM was instructed to always populate at least one of these columns, but didn't always do so.

- Markdown tables were converted to the CSV included in the final results spreadsheet with the script create_csv_from_md_response.py.

- Hyperparameters (temperature, top_p, etc) are documented in the file settings.txt, and were the same for all prompts and trials.   The specific model used for all outputs was llama-2-70b-chat.

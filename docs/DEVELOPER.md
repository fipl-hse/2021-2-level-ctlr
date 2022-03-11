## CI pipeline

1. Triggers on commit to fork with opened PR to main repository
1. Validates PR name - [skip-ci]
1. Runs Stage 1 script - check `requirements.txt` or add to requirements of the lab
1. **1A** Validates Stage CLI (Milestone 1)
    1. Wrong URL - exit code? message?
    1. Too big N
    1. Incorrect N
    1. Is `tmp/articles` populated?
    1. `stages.txt` -> 1
1. **1B** Validates raw data with proper messaging
    1. Can I open this URL?
    1. Is a date in given format?
    1. Does texts quantity match requested volume?
    1. Are IDs from 1 to the N without errors in ordering?
1. Runs Stage 2 script
1. **2A** Validates Stage 1 CLI
1. **2B** Validates processed data with proper messaging
    1. Does the `-1_raw.txt` result in `-1_processed.txt`?
    1. Does `-1_processed.txt` contain only lemmas and tags without punctuation signs?
    1. Does `-1_processed.txt` contains tags of proper format?
1. (Always) Publishes build artifacts (a.k.a. dataset) on AWS S3
1. (Optional) Puts a link to artifact to the PR

### Milestones

1. `scrapper.py` with CLI and fake files creation passing CI 1A
1. `scrapper.py` passing 1B (11 February)
1. public repository with tests for 1A/1B (11 February) - stages?
1. `pipeline.py` with CLI and fake files creation passing CI 2A
1. `pipeline.py` passing CI 2B (18 February)
1. artifacts on S3 (18 February)

## Configuring Python for course development

Instructions below are validated on macOS. For Windows setup replace `python3` with `py`.
**TBD** how to provide python path on Windows.

```
python3 -m pip install --user virtualenv
python3 -m virtualenv -p `which python3` venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Spell checking

1. Install dependencies 
   [spell checker](https://facelessuser.github.io/pyspelling/#usage-in-linux). 
   For example, for macOS:

   ```bash
   brew install aspell
   ```

1. Install Python dependencies:

   ```bash
   python -m pip install -r requirements_qa.txt
   ```

1. Run checks:

   ```bash
   python -m pyspelling -c config/spellcheck/.spellcheck.yaml
   ```

## Running tests

1. Install dependencies (assuming you have activated the environment from the previous step)
   ```bash
   python -m pip install -r requirements_qa.txt
   ```
   
1. Run the tests for the given mark. You can select any level: `mark4`, `mark6`, `mark8`, `mark10`:
   
   ```bash
   python -m pytest -m mark8
   ```

## CI stages

1. Stage 1. Style
   1. Stage 1.1. PR Name
   1. Stage 1.2. Code style (`pylint`, `flake8`)
   
1. Stage 2. Crawler
   1. Stage 2.1. Crawler config validation (we ensure that crawler has certain sanity checks)
   1. Stage 2.2. `Crawler` instantiation validation
   1. Stage 2.3. `Parser` instantiation validation
   1. Stage 2.4. Articles downloading
   1. Stage 2.5. Dataset volume validation
   1. Stage 2.6. Dataset structure validation
   
1. Stage 3. Text Processing Pipeline
   1. Stage 3.1. Dataset sanity checks (we ensure that pipeline has certain sanity checks)
   1. Stage 3.2. `CorpusManager` sanity checks (we ensure that pipeline identifies all articles correctly)
   1. Stage 3.3. `MorphologicalToken` sanity checks (we ensure that pipeline displays all tokens appropriately)
   1. Stage 3.4. Admin data processing
   1. Stage 3.5. Student dataset processing
   1. Stage 3.6. Student dataset validation
   
1. Stage 4. Additional tasks
   1. Stage 4.1. Frequency visualization
   

## Synchronizing between admin and public repository

1. Run the following command (macOS specific):
 
   ```bash
   cd ..
   diff -rq 2021-2-level-ctlr 2021-2-level-ctlr-admin/ \
          -x .git -x .idea -x .pytest_cache -x __pycache__ \
          -x venv -x tmp \
          -x dictionary.dic -x target_score.txt \
          -x scrapper_config.json -x scrapper.py \
          -x pipeline.py -x pos_frequency_pipeline.py \
          -x crawler_pdf.yml -x html_with_pdf_parser_launcher.py \
          -x get_mark.sh -x requirements.txt \
          -x scrapper_config_test.json > hse.diff
   ```
   

set -ex

echo "CorpusManager validation"
echo "Starting tests for CorpusManager"

TARGET_SCORE=$(bash config/get_mark.sh pipeline)

if [[ ${TARGET_SCORE} == 4 ]]; then
  echo "Running score four checks"
  python -m pytest -m "mark4 and stage_3_2_corpus_manager_checks"
elif [[ ${TARGET_SCORE} == 6 ]]; then
  echo "Running score six checks"
  python -m pytest -m "mark6 and stage_3_2_corpus_manager_checks"
elif [[ ${TARGET_SCORE} == 8 ]]; then
  echo "Running score eight checks"
  python -m pytest -m "mark8 and stage_3_2_corpus_manager_checks"
  echo "TBD: later"
else
  echo "Running score ten checks"
  python -m pytest -m "mark10 and stage_3_2_corpus_manager_checks"
  echo "TODO: check for PosFrequencyPipeline"
  echo "TBD: later"
fi

echo "CorpusManager is checked. Done"

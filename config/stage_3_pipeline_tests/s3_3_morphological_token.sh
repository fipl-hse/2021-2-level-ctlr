set -ex

echo "MorphologicalToken validation"
echo "Starting tests for MorphologicalToken"

TARGET_SCORE=$(bash config/get_mark.sh pipeline)

source venv/bin/activate

if [[ ${TARGET_SCORE} == 4 ]]; then
  echo "Running score four checks"
  python -m pytest -m "mark4 and stage_3_3_morphological_token_checks"
elif [[ ${TARGET_SCORE} == 6 ]]; then
  echo "Running score six checks"
  python -m pytest -m "mark6 and stage_3_3_morphological_token_checks"
elif [[ ${TARGET_SCORE} == 8 ]]; then
  echo "Running score eight checks"
  python -m pytest -m "mark8 and stage_3_3_morphological_token_checks"
fi

echo "MorphologicalToken is checked. Done"

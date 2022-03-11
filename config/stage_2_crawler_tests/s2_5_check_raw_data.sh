set -ex

echo "Stage 1B: Validating metadata"
echo "Starting tests for received metadata"

TARGET_SCORE=$(bash config/get_mark.sh crawler)

if [[ ${TARGET_SCORE} == 4 ]]; then
  echo "Running score four checks"
  python -m pytest -m "mark4 and stage_2_5_dataset_validation"
elif [[ ${TARGET_SCORE} == 6 ]]; then
  echo "Running score six checks"
  python -m pytest -m "mark6 and stage_2_5_dataset_validation"
elif [[ ${TARGET_SCORE} == 8 ]]; then
  echo "Running score eight checks"
  python -m pytest -m "mark8 and stage_2_5_dataset_validation"
else
  echo "Running score ten checks"
  python -m pytest -m "mark10 and stage_2_5_dataset_validation"
fi

echo "Raw data is checked. Done"

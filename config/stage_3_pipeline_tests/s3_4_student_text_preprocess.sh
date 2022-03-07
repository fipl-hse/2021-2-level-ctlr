set -ex

echo "Stage 2B: Student text preprocessing"
echo "Starting tests for student dataset"

TARGET_SCORE=$(bash config/get_mark.sh pipeline)

if [[ ${TARGET_SCORE} == 4 ]]; then
  echo "Running score four checks"
  python -m pytest -m "mark4 and stage_3_4_student_dataset_validation"
elif [[ ${TARGET_SCORE} == 6 ]]; then
  echo "Running score six checks"
  python -m pytest -m "mark6 and stage_3_4_student_dataset_validation"
elif [[ ${TARGET_SCORE} == 8 ]]; then
  echo "Running score eight checks"
  python -m pytest -m "mark8 and stage_3_4_student_dataset_validation"
  echo "TBD: later"
else
  echo "Running score ten checks"
  python -m pytest -m "mark10 and stage_3_4_student_dataset_validation"
  echo "TODO: check for PosFrequencyPipeline"
  echo "TBD: later"
fi

echo "Raw data is checked. Done"

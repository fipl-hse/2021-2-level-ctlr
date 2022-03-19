set -ex

echo "POSFrequencyPipeline validation"
echo "Starting tests for POSFrequencyPipeline"

TARGET_SCORE=$(bash config/get_mark.sh pipeline)

source venv/bin/activate

if [[ ${TARGET_SCORE} == 10 ]]; then
  echo "Running score ten checks"
  python -m pytest -m "mark10 and stage_4_pos_frequency_pipeline_checks"
fi

echo "POSFrequencyPipeline is checked. Done"

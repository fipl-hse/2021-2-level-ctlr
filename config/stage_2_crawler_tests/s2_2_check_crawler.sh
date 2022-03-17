set -ex

echo "Crawler validation"
echo "Starting tests for Crawler"

TARGET_SCORE=$(bash config/get_mark.sh crawler)

source venv/bin/activate

if [[ ${TARGET_SCORE} == 4 ]]; then
  echo "Running score four checks"
  python -m pytest -m "mark4 and stage_2_2_crawler_check"
elif [[ ${TARGET_SCORE} == 6 ]]; then
  echo "Running score six checks"
  python -m pytest -m "mark6 and stage_2_2_crawler_check"
elif [[ ${TARGET_SCORE} == 8 ]]; then
  echo "Running score eight checks"
  python -m pytest -m "mark8 and stage_2_2_crawler_check"
fi

echo "Crawler is checked. Done"
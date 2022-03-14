set -ex

echo -e '\n'
echo "Crawler checks"

TARGET_SCORE=$(bash config/get_mark.sh crawler)

if [[ ${TARGET_SCORE} != 0 ]]; then
  bash config/stage_2_crawler_tests/s2_2_check_crawler.sh
else
  echo "Skipping stage"
fi

set -ex

echo -e '\n'
echo "Check files processing on student dataset"

TARGET_SCORE=$(bash config/get_mark.sh pipeline)

if [[ ${TARGET_SCORE} != 0 ]]; then
  mkdir -p tmp/articles
  mv *_cleaned.txt tmp/articles
  if [[ ${TARGET_SCORE} != 4 ]]; then
    mv *_meta.json tmp/articles
    mv *_single_tagged.txt tmp/articles
    if [[ ${TARGET_SCORE} != 6 ]]; then
      mv *_multiple_tagged.txt tmp/articles
    fi
  fi
  mv *_raw.txt tmp/articles
  bash config/stage_4_pos_frequency_pipeline_tests/run_pos_frequency_pipeline.sh
  bash config/stage_4_pos_frequency_pipeline_tests/s4_pos_frequency_pipeline.sh
  echo "Your solution is accepted! Proceed to further tasks from your lecturer."
else
  echo "Skip stage"
fi

set -ex

echo -e '\n'
echo "Check morphological token is implemented correctly"

TARGET_SCORE=$(bash config/get_mark.sh pipeline)

if [[ ${TARGET_SCORE} != 0 ]]; then
  bash config/stage_3_pipeline_tests/s3_3_morphological_token.sh
else
  echo "Skip stage"
fi

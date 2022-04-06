set -ex

echo -e '\n'
echo "Check processing on student dataset"

TARGET_SCORE=$(bash config/get_mark.sh pipeline)

source venv/bin/activate

if [[ ${TARGET_SCORE} != 0 ]]; then
  mkdir -p tmp/articles
  if [[ ${TARGET_SCORE} != 4 ]]; then
    mv *_meta.json tmp/articles
  fi
  mv *_raw.txt tmp/articles
  python pipeline.py
  ls -la tmp/articles
else
  echo "Skip stage"
fi

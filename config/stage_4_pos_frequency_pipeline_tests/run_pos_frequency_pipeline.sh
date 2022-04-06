set -ex

TARGET_SCORE=$(bash config/get_mark.sh pipeline)

source venv/bin/activate

if [[ ${TARGET_SCORE} == 10 ]]; then
  python pos_frequency_pipeline.py
fi

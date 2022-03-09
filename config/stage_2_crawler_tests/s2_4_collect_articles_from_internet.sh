set -ex

echo "Stage: Downloading articles"

python config/config_param_changer.py --config_path="scrapper_config.json"

echo "Changed config params"

python scrapper.py

echo "Collected dataset"

echo "Checking volume of files"

TARGET_SCORE=$(bash config/get_mark.sh crawler)

if [[ ${TARGET_SCORE} == 4 ]]; then
  echo "Running score four checks"
  python -m pytest -m "mark4 and stage_2_4_dataset_volume_check"
else
  python -m pytest -m "mark10 and stage_2_4_dataset_volume_check"
fi

echo "Volume is correct"

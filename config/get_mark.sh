set -ex

if [[ $1 == "crawler" ]]; then
  export TARGET_SCORE=$(head -5 config/target_score.txt | tail -1)
elif [[ $1 == "pipeline" ]]; then
  export TARGET_SCORE=$(head -2 config/target_score.txt | tail -1)
else
  echo "Can not find TARGET_SCORE for $1"
  exit 1
fi

echo ${TARGET_SCORE}

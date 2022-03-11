set -ex

echo -e '\n'

echo "Spellchek running ..."
python -m pyspelling -c config/spellcheck/.spellcheck.yaml

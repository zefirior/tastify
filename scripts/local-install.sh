SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

pip install -r $SCRIPT_DIR/../back/requirements.txt
pip install -r $SCRIPT_DIR/../back/requirements-test.txt

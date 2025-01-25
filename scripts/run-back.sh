# Run fastapi server contains in back directory

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Run the application
pushd $SCRIPT_DIR/../back || exit
fastapi dev main.py
popd || exit

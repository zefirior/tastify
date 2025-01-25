# Run litestar server contains in back directory

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Run the application
pushd $SCRIPT_DIR/../back || exit
PYTHONPATH=.. litestar run
popd || exit

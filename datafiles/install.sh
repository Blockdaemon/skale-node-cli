#!/usr/bin/env bash
set -e

CONFIG_DIR="$SKALE_DIR"/config
CONTRACTS_DIR="$SKALE_DIR"/contracts_info
NODE_DATA_DIR=$SKALE_DIR/node_data

source "$DATAFILES_FOLDER"/helper.sh

if [[ -z $CONTAINER_CONFIGS_DIR ]]; then
    cd $CONFIG_DIR
    if [[ ! -d .git ]]; then
        echo "Cloning container configs ..."
        git clone "https://github.com/skalenetwork/skale-node.git" "$CONFIG_DIR"
    fi
    echo "Fetching new branches and tags..."
    git fetch
    echo "Checkouting to container configs branch $CONTAINER_CONFIGS_STREAM ..."
    git checkout $CONTAINER_CONFIGS_STREAM
    is_branch="$(git show-ref --verify refs/heads/$CONTAINER_CONFIGS_STREAM >/dev/null 2>&1; echo $?)"
    if [[ $is_branch -eq 0 ]] ; then
      echo "Pulling recent changes from $CONTAINER_CONFIGS_STREAM ..."
      git pull
    fi
else
    echo "Syncing container configs ..."
    rsync -r $CONTAINER_CONFIGS_DIR/* $CONFIG_DIR
    rsync -r $CONTAINER_CONFIGS_DIR/.git $CONFIG_DIR
fi

echo "Creating .env symlink to $CONFIG_DIR/.env ..."
if [[ -f $CONFIG_DIR/.env ]]; then
    rm "$CONFIG_DIR/.env"
fi
ln -s $SKALE_DIR/.env $CONFIG_DIR/.env

cd $SKALE_DIR

download_contracts
download_filestorage_artifacts
configure_filebeat
configure_flask
iptables_configure

if [[ -z $DRY_RUN ]]; then
    docker_lvmpy_install
    cd $CONFIG_DIR
    if [[ ! -z $CONTAINER_CONFIGS_DIR ]]; then
        echo "Building containers ..."
        SKALE_DIR=$SKALE_DIR docker-compose -f docker-compose.yml build
    fi
    up_compose
fi

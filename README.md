# This is a fork of https://github.com/skalenetwork/skale-node-cli

The goal of this fork is to make the cli executable by a non-root user (although that user does need `sudo` rights).

Note that the upstream repo uses `develop` as main branch! If you send a PR from this repo, do not include this `README.md` file, I just wrote it to explain the fork, it doesn't belong upstream.

# Building it

On a Ubuntu 18.04 machine run:

```
sudo apt update -y
sudo apt install python3.7-dev
sudo apt install libusb-1.0.0-dev
git clone git@github.com:Blockdaemon/skale-node-cli.git
cd skale-node-cli
virtualenv --python=python3.7 venv
. venv/bin/activate
pip install -e .[dev]
./scripts/build.sh 1.0.0 1.0.0 # or whatever version number/branch you want
```

The resulting binary is in the `./dist` folder.


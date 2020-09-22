# This is a fork of https://github.com/skalenetwork/skale-node-cli

The goal of this fork is to make the cli executable by a non-root user (although that user does need `sudo` rights).

Note that the upstream repo uses `develop` as main branch! In this fork we use `develop` as a melting pot for all the PRs. If you send a PR from this repo, do not include this `README.md` file, I just wrote it to explain the fork, it doesn't belong upstream.

# Binary

The latest binary (manually) build is in the `binary` branch. This is just temprorary until the changes land in upstream. It's typically not a good idea to store binary artifacts in github!

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


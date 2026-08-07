https://docs.astral.sh/uv/getting-started/installation/

Installation methods

Install uv with our standalone installers or your package manager of choice.
Standalone installer

uv provides a standalone installer to download and install uv:
macOS and Linux
Windows

Use curl to download the script and execute it with sh:

curl
 -LsSf https://astral.sh/uv/install.sh | sh

If your system doesn't have curl, you can use wget:

wget
 -qO- https://astral.sh/uv/install.sh | sh

Request a specific version by including it in the URL:

curl
 -LsSf https://astral.sh/uv/0.12.2/install.sh | sh

PyPI

For convenience, uv is published to PyPI.

If installing from PyPI, we recommend installing uv into an isolated environment, e.g., with pipx:

pipx
 install uv

However, pip can also be used:

pip
 install uv
Docker

uv provides a Docker image at ghcr.io/astral-sh/uv.

See our guide on using uv in Docker for more details.
GitHub Releases

uv release artifacts can be downloaded directly from GitHub Releases.

Each release page includes binaries for all supported platforms as well as instructions for using the standalone installer via github.com instead of astral.sh.
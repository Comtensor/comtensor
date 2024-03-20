<div align="center">

# **Comtensor** <!-- omit in toc -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 



### Bridging Commune and Bittensor <!-- omit in toc -->

[Bittensor](https://discord.gg/bittensor) • [Commune-ai](https://www.communeai.org/)

![Comtensor Image](docs/images/comtensor-2.png)


</div>


----------
## How to install

1. Clone the repository.

    ```bash
    git clone https://github.com/Comtensor/comtensor.git
    cd comtensor
    ```

2. Install venv

    ```bash
    apt install python3.10-venv
    python3 -m venv my-env
    . my-env/bin/activate
    ```

3. Install dependancies

    ```bash
    python3 -m pip install -e .
    python3 -m pip install -r requirements.txt
    ```

## How to contribute

- Make sub-directory in `crossvals` directory and name it with subnet name.

    ex. `crossvals/healthcare`

    Add all your files in this directory.
- Declare the class inheriting from `CommitBasedCrossval` class or `SynapseBasedCrossval` class.

    ex. 

    ```python
    import bittensor as bt
    from constants import BASE_DIR
    from base.commit_based_crossval import CommitBasedCrossval

    class HealthcareCrosscal(CommitBasedCrossval):
        ...
- Then customize this class with your own functions and implementing abstruct functions.


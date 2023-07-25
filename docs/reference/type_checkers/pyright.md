# Pyright

[Pyright](https://github.com/microsoft/pyright) is a static type checker for python created by Microsoft and designed for speed and configurability.

## Installing

### PyPi

!!! note
    I am the maintainer of the [pyright PyPI package](https://pypi.org/project/pyright/) which is a wrapper over the [official version](https://github.com/microsoft/pyright).

You can install pyright using [pip](https://pip.pypa.io/en/stable/).

```sh
pip install pyright
```

### npm

The official version of pyright can be installed from npm, to install globally run the command:

```sh
npm install -g pyright
```

## Configuration

Pyright can be configured from either a `pyproject.toml` file or a `pyrightconfig.json` file, see the [official documentation](https://github.com/microsoft/pyright/blob/main/docs/configuration.md) for more options.

`pyproject.toml`
```toml
[tool.pyright]
typeCheckingMode = "strict"
```

`pyrightconfig.json`
```json
{
    "typeCheckingMode": "strict"
}
```

## Running

After using any of the installation methods listed above, pyright should now be in your PATH and you can execute as shown:

```sh
pyright
```

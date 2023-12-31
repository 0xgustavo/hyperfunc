import pathlib


def get_pyproject_toml():
    current_path = pathlib.Path.cwd()

    for parent in [current_path, *current_path.parents]:
        pyproject_path = parent / "pyproject.toml"
        if pyproject_path.exists():
            return pyproject_path

    return None


pyproject_toml = get_pyproject_toml()

if not pyproject_toml:
    raise RuntimeError('pyproject.toml not found.')

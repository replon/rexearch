# Python Template

Python Project Template

- CI: Github Action
- Code Coverage: codecov

## Template Replace Check-List

- [ ] Make your own package name 👋
- [ ] Replace `package/` to new package name 🎉
- [ ] Replace command in `.github/workflows/main.yml` with new package name 🔨
- [ ] Replace command in `Makefile` with new package name
- [ ] Replace name, description, author etc in `setup.py` with new package setting 🏄‍♂️
- [ ] Replace version in `package/__init__.py` to new package name
- [ ] Make REAL runnable code 👨‍💻
- [ ] Make REAL test code 👩🏻‍💻
- [ ] Remove this README and make your own story! 👍

## Commit Rule

Following the [Conventional Commits/Angular convention](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type)

```bash
git config commit.template .gitmessage
```

## Run Linting

This project use three Linter: `black`, `isort`, `flake8`

Before run linting, you should install the **exact version** of linting libraries.

```bash
pip3 install -r requirements-dev.txt
```

```
# use linter to fix code format
make style

# check lint error
make quality
```

## Run Test

All runnable test codes should be located in `tests/` folder

```shell
pytest
```

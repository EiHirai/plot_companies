# plot office location

## environment

python version: 3.6.8

## initial setup

```zsh
$ virtualenv venv
```

## activate & deactivate

```zh
$ source venv/bin/activate

(venv)$ which python
(venv)$ pip install -r requirements.txt
(venv)$ pip install -U git+ssh://git@github.com/estie-inc/tools__calc_location_info.git
(venv)$ pip install RW_S3

(venv)$ deactivate
```

## check kernel
```zh
jupyter kernelspec list
```

## remove environment

```zh
rm -r venv
```
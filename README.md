# Overview

This small project shows some specifics of practical development with
balancing SQL-queries through [Pgpool-II](https://www.pgpool.net)

Practical examples to look into are available in [./scripts/opt/tests/](./scripts/opt/tests) 
directory.

A current setup of Pgpool-II is:

- 1 primary write replica
- 2 different read replicas
- pgpool node
- all non-write queries go to read-replicas only


## Environments

- Pgpool listens on `<docker-host>:5555`
- Username: `postgres`
- Password: `pass`
- Database: `target_db`

### Requirements

1. Python 3.9+
2. Docker
3. Docker-compose
4. `psql` cli must be installed and available via `PATH`

### Docker

This environment runs on a single machine. So latency should be very short.

I use docker-compose v2 because v3 doesn't provide ways to limit resources. 
Discussion is available on [this issue](https://github.com/docker/compose/issues/4513)

### How to run

1. Start all docker containers and wait for DBs being replicated:

```shell
docker-compose up
```
2. In other terminal set environment:

```shell
python -m pip install pipenv
pipenv install
pipenv shell
export PYTHONPATH=$(pwd):$(pwd)/scripts:${PYTHONPATH}

```

3. Load sample data:

```shell

./scripts/bin/load_data.py

# You can check all options with
./scripts/bin/load_data.py --help
```

4. Run tests

```shell
pytest ./scripts/opt/tests
```

## Links

- [Pagila](https://github.com/devrimgunduz/pagila) - sample database for Postgres 12+
- https://www.refurbed.org/posts/load-balancing-sql-queries-using-pgpool/
- https://www.pgpool.net/docs/latest/en/html/runtime-config-load-balancing.html
- https://www.pgpool.net/docs/latest/en/html/example-kubernetes.html
- https://www.youtube.com/watch?v=oc_FQHq2dPI
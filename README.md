These are various notes on high-altitude ballons.

## docker

to use the docker container

``` bash
docker compose -f docker-compose.yml build quarto
```

The julia packages are stored in a `.julia` directory created within the project so that they are accessible from within the container, specifically using the `JULIA_DEPOT_PATH` set as:

``` bash
export JULIA_DEPOT_PATH=/opt/project/.julia
```


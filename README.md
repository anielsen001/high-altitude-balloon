These are various notes on launching pico-balloons and high-altitude ballons.

## podman

to use the podman container

``` bash
podman-compose run quarto
```

The julia packages are stored in a `.julia` directory created within the project so that they are accessible from within the container, specifically using the `JULIA_DEPOT_PATH` set as:

``` bash
export JULIA_DEPOT_PATH=/opt/project/.julia
```

## remove image metadata

this removes metadata from all images in the current directory
```bash
exiftool -all= .
```

## resize images

resizes image to be 800 pixels height
```bash
convert in.jpg -resize 800 out.jpg
```

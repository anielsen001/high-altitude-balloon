Remove all metadata from photos in directory

``` bash
exiftool -all:all= -r ~/proj/balloon/_sources/launches/smore-001
```

Rotate image 90 degrees 

``` bash
convert IMG_20250810_094633323.jpg -rotate 90 IMG_20250810_094633323_rot90.jpg
```

Reduce image size 25%

``` bash
convert IMG_20250810_094633323_rot90.jpg -resize 25% IMG_20250810_094633323_rot90_25.jpg
```

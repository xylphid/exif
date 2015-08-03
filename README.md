# xy-exif

Xy-Exif is a fork of python exif-py library.

## Compatibility
Xy-Exif is tested on the following Python version :
* 3.3
* 3.4

## Usage

### Command line
Some examples :

    $ exif.py image1.jpg
    $ exif.py image2.jpg

### Python script
Step by step extraction :

    import exif

    # Create exif object
    exif = Exif(path_name)
    # Extract exif tags
    exif.process_file()

Auto process :
    
    import exif

    # Create exif object that auto process tag extraction
    exif = Exif(path_name, autoprocess=True)

Returned tags will be a dictionary mapping names of Exif tags to their values in the file named by path_name. You can process the tags as you wish. In particular, you can iterate through all the tags with:

    for tag in exif.tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print "Key: %s, value %s" % (tag, exif.tags[tag])

An if statement is used to avoid printing out a few of the tags that tend to be long or boring.

The tags dictionary will include keys for all of the usual Exif tags, and will also include keys for Makernotes used by some cameras, for which we have a good specification.
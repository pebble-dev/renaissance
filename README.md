# Renaissance

A metrically compatible replacement for Raster Gothic Condensed in Pebble font format.

Please see the [wiki](https://github.com/pebble-dev/renaissance/wiki) for more information.

While this project is still in its earliest stages, here are some thoughts on the font design process:

- Encoding the font source in plain text files is preferable because it allows viewing and editing with small overhead.
- A tool should be written to convert aforementioned text files to font files (described [here](https://github.com/pebble-dev/wiki/wiki/Firmware-Font-Format))
- Use `metrics.py` to extract metrics information from font files.
  I've extracted metrics for all Gothic fonts and placed this data into `metrics.json`.

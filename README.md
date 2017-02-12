# Renaissance's site.

Uses canvas to render text from b64-encoded pebble fonts.

> Wait, what?

This sounds ridiculous, but it actually makes sense. The entire page weighs
about 130 Kilobytes before gzipping (and about half that afterwards).

TTF/OTF/WOFF export from bitmap fonts can't be achieved quickly with
open-source tools, and canvas is pretty quick in modern browsers.

Using b85 to further reduce network usage is a possibility.

Any and all optimizations are welcome — for example:
- there are probably ways to end up with way faster canvas drawing: drawing 1x1
  rects simply isn't fast. The ImageData approach mentioned in multiple places
  could help.
- asm.js-specific optimizations could help with drawing glyphs
  Storing glyph data in a typed array would be considerably quicker.
- lazy-rendering text would be a huge benefit (compute dimensions immediately,
  but only blit when necessary.)

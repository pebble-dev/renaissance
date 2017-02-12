function unpack(fmt, data) {
    // Subset of python's unpacking. 8/16: signed & unsigned; 32: unsigned only
    // Always little-endian
    const widths = {'B': 1, 'b': 1, 'H': 2, 'h': 2, 'I': 4, 'x': 1},
           signs = {'B': 0, 'b': 1, 'H': 0, 'h': 1, 'I': 0, 'x': 1};
    let out = [];
    for (let chr of fmt) {
        let item = 0,
            exp = 0;
        for (let _ = 0; _ < widths[chr]; _++) {
            item += data[0] << exp;
            data = data.slice(1);
            exp += 8;
        }
        if (signs[chr] && (item > Math.pow(2, widths[chr] * 8 - 1) - 1)) {
            item -= Math.pow(2, widths[chr] * 8);
        }
        out.push(item);
    }
    return out;
}

class Loader {
    // Loads a base64 string and implements a file-like API.
    constructor(b64) {
        const bin = atob(b64);
        this.bytes = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) {
            this.bytes[i] = bin.charCodeAt(i);
        }
        this.bytes_read = 0;
    }
    read(num) {
        if (this.bytes.length < num)
            throw new Error('Not enough data left!');
        const tmp = this.bytes.slice(0, num);
        this.bytes = this.bytes.slice(num);
        this.bytes_read += num;
        return tmp;
    }
    read_all() {
        return this.bytes;
    }
}

class Font {
    constructor(fh) {
        // Loads font data from a Loader object.

        let hash_table_size = 255, codepoint_bytes = 4,
            size = null, features = 0;

        [this.version, this.max_height,
         this.glyph_amt, this.fallback_codepoint] = unpack('BBHH', fh.read(6));

        if (this.version >= 2)
            [hash_table_size, codepoint_bytes] = unpack('BB', fh.read(2));
        if (this.version >= 3)
            [size, features] = unpack('BB', fh.read(2));

        let offset_bytes = [4, 2][features & 1];

        // ---------------------------------------------------------------------

        let offset_table_data = [];

        for (let _it = 0; _it < hash_table_size; _it++) {
            let [hash_value, offset_table_size,
                 offset_table_offset] = unpack('BBH', fh.read(4));
            offset_table_data.push({'hash': hash_value,
                                    'size': offset_table_size,
                                    'offset': offset_table_offset});
        }

        offset_table_data.sort((a, b) => (a['offset'] - b['offset']));

        // ---------------------------------------------------------------------

        const first_offset_item = fh.bytes_read;
        let glyph_table_data = [];
        for (let offset_list of offset_table_data) {
            if (offset_list['size'] == 0)
                continue;
            if (offset_list['offset'] != fh.bytes_read - first_offset_item)
                throw new Error('Offset item at incorrect offset' + ' ' + fh.bytes_read + ' ' + first_offset_item + ' ' + offset_list['offset']);
            for (let _idx = 0; _idx < offset_list['size']; _idx++) {
                let [codepoint, offset] = unpack(
                    (codepoint_bytes == 2 ? 'H' : 'I') +
                    (offset_bytes == 2 ? 'H' : 'I'),
                    fh.read(codepoint_bytes + offset_bytes));
                glyph_table_data.push({'codepoint': codepoint, 'offset': offset});
            }
        }

        // ---------------------------------------------------------------------

        const glyph_data = fh.read_all();
        this.glyph_list = {};

        for (let glyph of glyph_table_data) {
            if (glyph['offset'] + 7 > glyph_data.length)
                throw new Error('Glyph offset too large.', glyph);
            let [width, height, left, top, advance] = unpack(
                'BBbbbxxx', glyph_data.slice(glyph['offset'], glyph['offset'] + 8));
            let raw_data = glyph_data.slice(glyph['offset'] + 5,
                glyph['offset'] + 5 + Math.ceil(width * height / 8)),
                bits = [], data = [];
            for (let _byte of raw_data) {
                for (let _exp = 0; _exp < 8; _exp++) {
                    bits.push((_byte >> _exp) & 1);
                    if (bits.length >= width) {
                        data.push(bits);
                        bits = [];
                        if (data.length >= height)
                            break;
                    }
                }
                if (data.length >= height)
                    break;
            }

            this.glyph_list[glyph['codepoint']] =
                {'width': width, 'height': height, 'left': left,
                 'top': top, 'advance': advance, 'data': data};
        }
    }
    drawCharacter(ctx, chr) {
        let g = this.glyph_list[chr.charCodeAt(0)], y = 0;
        if (typeof g == 'undefined') {
            g = this.glyph_list[this.fallback_codepoint]
        }
        for (let y of g['data'].keys())
            for (let x of g['data'][y].keys())
                if (g['data'][y][x])
                    ctx.fillRect(g.left + x, g.top + y, 1, 1);
        ctx.transform(1, 0, 0, 1, g.advance, 0);
    }
    getTextDimensions(text) {
        let maxX = 0, currentX = 0, y = this.max_height
        for (let chr of text) {
            if (chr == '\n') {
                y += this.max_height;
                currentX = 0
            } else {
                let c = chr.charCodeAt(0)
                currentX += this.glyph_list[c in this.glyph_list
                                            ? c : this.fallback_codepoint]['advance']
                if (currentX > maxX)
                    maxX = currentX
            }
        }
        return [maxX + 4, y + 5]
    }
    drawText(ctx, scale, style, text) {
        ctx.setTransform(scale, 0, 0, scale, 2, 0);
        ctx.fillStyle = style;
        let line = 0;
        for (let chr of text) {
            if (chr == '\n') {
                line++;
                ctx.setTransform(scale, 0, 0, scale, 2, line * this.max_height);
            } else {
                this.drawCharacter(ctx, chr);
            }
        }
    }
}

window.Loader = Loader;
window.Font = Font;

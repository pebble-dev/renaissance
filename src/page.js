let scrollItems = []

function addHeroParallax(item, strength) {
    let calculateOffset = (a) => ('translate(0, ' + Math.round(a * strength) + 'px)');
    scrollItems.push((a) => { item.style.transform = calculateOffset(a); })
    item.style.transform = calculateOffset(window.scrollY);
}

for (let canvas of document.querySelectorAll('[data-auto-draw]')) {
    let font = window.f
                [canvas.getAttribute('data-style')]
                [canvas.getAttribute('data-size')],
        scale = parseInt(canvas.getAttribute('data-scale')),
        text = canvas.getAttribute('data-text').replace(/\\n/g, '\n'),
        parallax = canvas.getAttribute('data-parallax');
    ctx = canvas.getContext('2d');
    let dim = font.getTextDimensions(text);
    [canvas.width, canvas.height] = [dim[0] * scale, dim[1] * scale];
    font.drawText(ctx, scale, window.getComputedStyle(canvas).color, text);
    if (parallax) {
        parallax = parseFloat(parallax);
        addHeroParallax(canvas, parallax);
    }
}

function samples(el, text, showName, color) {
    el.innerHTML = '';
    for (let style in window.f) {
        for (let size in window.f[style]) {
            let font = window.f[style][size],
                rowEl = document.createElement('div'),
                textEl = document.createElement('div');
                textCanvas = document.createElement('canvas'),
                textDim = font.getTextDimensions(text);

            rowEl.classList.add('specimen-row');
            rowEl.setAttribute('data-style', style);
            rowEl.setAttribute('data-size', size);

            if (showName) {
                let nameEl = document.createElement('div'),
                    name = 'Renaissance ' + style.replace('normal', '')
                                                 .replace('bold', 'bold ')
                                          + size,
                    nameCanvas = document.createElement('canvas'),
                    nameDim = font.getTextDimensions(name);
                nameEl.classList.add('specimen-name');
                [nameCanvas.width, nameCanvas.height] = [nameDim[0], nameDim[1]];
                font.drawText(nameCanvas.getContext('2d'), 1, color, name);
                nameEl.appendChild(nameCanvas);
                rowEl.appendChild(nameEl);
            }

            textEl.classList.add('specimen-text');
            [textCanvas.width, textCanvas.height] = [textDim[0], textDim[1]];
            font.drawText(textCanvas.getContext('2d'), 1, color, text);

            textEl.appendChild(textCanvas);
            rowEl.appendChild(textEl);
            el.appendChild(rowEl);
        }
    }
}

function floaters(el, chars) {
    fonts = [];
    for (let a in window.f)
        for (let b in window.f[a])
            if (b != '9')
                fonts.push(window.f[a][b])
    let iter = 0;
    for (let x = 25; x < 1000; x += 30) {
        for (let yPercent = 10; yPercent <= 90; yPercent += 14) {
            let chr = chars[iter % chars.length],
                font = fonts[iter % fonts.length],
                dim = font.getTextDimensions(chr),
                canvas = document.createElement('canvas'),
                ctx = canvas.getContext('2d');
            [canvas.width, canvas.height] = [dim[0] * 1, dim[1] * 1];
            font.drawText(ctx, 1, window.getComputedStyle(el).color, chr);

            canvas.style.left = x - Math.round(dim[0] / 2) + 'px';
            canvas.style.top = 'calc(' + yPercent + '% - ' + Math.round(dim[1] / 2) + 'px)';

            el.appendChild(canvas)
            iter += 1;
        }
    }
}

let sampleEl = document.querySelector('#sample-sentences')

samples(sampleEl, 'The quick brown fox jumps over the lazy dog.', true,
        window.getComputedStyle(sampleEl).color)
floaters(document.querySelector('#specials'),
         '\'∑"ˇ≠`>!-™@‚≈‰^:◊∂,“&˜‹]√˝∏†%∆<;∫Ω(≤˙˘ˆ#”˛÷=–⁄≥*+’˚‡—)$›−=[„•.×∞€π_/=?\\‘…')
floaters(document.querySelector('#diacritics'), 'ŽċŉĨĆěĞüŹŴĎĊĘųŨĚșìģŞóÑŮźÜÆŁĔÏŇĻĕÀŋùīÁķńĖœĽŠĀȘÇĭÙĈŒŚøůčŦőÂÕçØáýŔŎġũŭĉĹŗåâōËĵãŃĄĤŻÝęřþžĥÍĴÎūŅÿşĐŊŢĮèśņñĪïćÞŤëÉòÅűôąǾÈðİŌğăĜĠÄÚõǿĶäúÖţŸŘÃėľŷĺǼûŬéÔĢŕĝÒżČæŝǽŪŀďāÛēŖļňłíŏŵ')

let textInput = document.querySelector('#text-input'),
    customPreview = document.querySelector('#text-update'),
    textUpdateTimeout = null;
textInput.addEventListener('input', e => {
    if (textUpdateTimeout)
        return;
    if (textInput.value.length > 200) {
        textInput.value = textInput.value.substring(0, 200)
    }
    textUpdateTimeout = setTimeout((e) => {
        if (textInput.value.trim().length == 0) {
            samples(customPreview, 'Type something...', false, '#888')
        } else {
            samples(customPreview, textInput.value, false, window.getComputedStyle(customPreview).color)
        }
        textUpdateTimeout = null;
    }, 20);
})
samples(customPreview, textInput.value, false)

window.addEventListener('scroll', () => {
    for (let f of scrollItems) { f(window.scrollY) }
})

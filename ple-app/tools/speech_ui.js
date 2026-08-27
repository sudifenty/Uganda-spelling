/* ============================================================
   READ ALOUD — offline voice reading for the Notes section.

   The controlled narrator uses the downloaded Piper voice model. The browser only
   plays the resulting audio; it does not choose the narrator. The device voice is
   available only as an explicitly labelled fallback test option. Once the model
   installed, this works with no internet at all: no audio is fetched
   and no text is ever sent anywhere.

   The work done here is turning written notes into words a teacher
   would actually say — "3/4 + 1/4 = 1" becomes "three quarters plus
   one quarter equals one" — and following along with a highlight.
   ============================================================ */

/* ---------- number words ---------- */
const SP_ONES = ['zero','one','two','three','four','five','six','seven','eight','nine',
  'ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen',
  'eighteen','nineteen'];
const SP_TENS = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety'];

function spUnder1000(n){
  let out = [];
  if(n >= 100){ out.push(SP_ONES[Math.floor(n/100)], 'hundred'); n %= 100; if(n) out.push('and'); }
  if(n >= 20){
    const tens = SP_TENS[Math.floor(n/10)];
    out.push(n%10 ? `${tens}-${SP_ONES[n%10]}` : tens);   // twenty-five, not twenty five
  }
  else if(n > 0) out.push(SP_ONES[n]);
  return out.join(' ');
}
function spWholeWords(n){
  n = Math.trunc(Math.abs(n));
  if(n === 0) return 'zero';
  if(n > 999999999) return String(n);
  const parts = [];
  const groups = [[1000000000,'billion'],[1000000,'million'],[1000,'thousand']];
  for(const [v,name] of groups){
    if(n >= v){ parts.push(spUnder1000(Math.floor(n/v)), name); n %= v; }
  }
  if(n > 0){ if(parts.length && n < 100) parts.push('and'); parts.push(spUnder1000(n)); }
  return parts.join(' ').replace(/\s+/g,' ').trim();
}
function spNumber(raw){
  const neg = /^-|^−/.test(raw);
  const s = raw.replace(/[,\s]/g,'').replace(/^[-−]/,'');
  if(!/^\d+(\.\d+)?$/.test(s)) return raw;
  const [w, dec] = s.split('.');
  let out = spWholeWords(Number(w));
  if(dec) out += ' point ' + dec.split('').map(d=>SP_ONES[Number(d)]).join(' ');
  return (neg ? 'negative ' : '') + out;
}
/* ordinals used when saying fractions: 1/5 -> one fifth */
const SP_DEN = {2:['half','halves'],3:['third','thirds'],4:['quarter','quarters'],
  5:['fifth','fifths'],6:['sixth','sixths'],7:['seventh','sevenths'],8:['eighth','eighths'],
  9:['ninth','ninths'],10:['tenth','tenths'],12:['twelfth','twelfths'],
  16:['sixteenth','sixteenths'],20:['twentieth','twentieths'],
  100:['hundredth','hundredths'],1000:['thousandth','thousandths']};
function spFraction(a, b){
  const n = Number(a), d = Number(b);
  if(!Number.isFinite(n) || !Number.isFinite(d) || d === 0) return `${a} over ${b}`;
  if(n === 1 && d === 2) return 'a half';
  const names = SP_DEN[d];
  if(names && n <= 20) return `${spWholeWords(n)} ${n === 1 ? names[0] : names[1]}`;
  return `${spWholeWords(n)} over ${spWholeWords(d)}`;
}

/* ---------- years ----------
   A teacher says "nineteen sixty-seven", not "one thousand nine hundred and
   sixty-seven". A four-digit number written without a comma, in the range
   1400-2099, is treated as a year. Thousands in these notes always carry a
   comma (1,250), so the two never collide. */
const SP_TENS_PL = {twenty:'twenties', thirty:'thirties', forty:'forties',
  fifty:'fifties', sixty:'sixties', seventy:'seventies', eighty:'eighties',
  ninety:'nineties'};
function spYear(n){
  if(n === 2000) return 'two thousand';
  if(n > 2000 && n < 2010) return 'two thousand and ' + SP_ONES[n - 2000];
  const hi = Math.floor(n / 100), lo = n % 100;
  if(lo === 0) return spUnder1000(hi) + ' hundred';
  if(lo < 10)  return spUnder1000(hi) + ' oh ' + SP_ONES[lo];
  return spUnder1000(hi) + ' ' + spUnder1000(lo);
}
function spDecade(n){
  if(n % 100 === 0) return spUnder1000(Math.floor(n / 100)) + ' hundreds';
  const w = spYear(n).split(' ');
  const last = w[w.length - 1];
  if(SP_TENS_PL[last]){ w[w.length - 1] = SP_TENS_PL[last]; return w.join(' '); }
  return spYear(n) + 's';
}

/* ---------- units ---------- */
const SP_UNITS = [
  [/\bcm\u00b2/g,' square centimetres'], [/\bm\u00b2/g,' square metres'],
  [/\bkm\u00b2/g,' square kilometres'],  [/\bmm\u00b2/g,' square millimetres'],
  [/\bcm\u00b3/g,' cubic centimetres'],  [/\bm\u00b3/g,' cubic metres'],
  [/\bkm\/hr\b/gi,' kilometres per hour'], [/\bkm\/h\b/gi,' kilometres per hour'],
  [/\bm\/s\b/gi,' metres per second'],
  [/\bmm\b/g,' millimetres'], [/\bcm\b/g,' centimetres'], [/\bkm\b/g,' kilometres'],
  [/\bkg\b/g,' kilograms'],   [/\bml\b/g,' millilitres'], [/\bmls\b/g,' millilitres'],
  [/\bhrs?\b/gi,' hours'],    [/\bmins?\b/gi,' minutes'], [/\bsecs?\b/gi,' seconds'],
  [/\bUGX\b/g,' shillings'],  [/\bshs\b/gi,' shillings'],
  [/(\d)\s*%/g,'$1 percent'], [/(\d)\s*\u00b0C\b/g,'$1 degrees Celsius'],
  [/(\d)\s*\u00b0/g,'$1 degrees'],
];

/* ---------- symbols ---------- */
const SP_SYMS = [
  [/\u00d7/g,' multiplied by '], [/\u00f7/g,' divided by '],
  [/\u2260/g,' is not equal to '], [/\u2264/g,' is less than or equal to '],
  [/\u2265/g,' is greater than or equal to '],
  [/\u2192/g,' gives '], [/\u2194/g,' is equivalent to '],
  [/\u222a/g,' union '], [/\u2229/g,' intersection '],
  [/\u2208/g,' is a member of '], [/\u2209/g,' is not a member of '],
  [/\u2205/g,' the empty set '], [/\u221a/g,' the square root of '],
  [/\u00b7/g,', '], [/\u2022/g,', '],
  [/\s=\s/g,' equals '], [/\s\+\s/g,' plus '],
  [/\s[-\u2212\u2013]\s/g,' minus '],
  [/\s<\s/g,' is less than '], [/\s>\s/g,' is greater than '],
  [/\u00b2/g,' squared '], [/\u00b3/g,' cubed '],
];

/* ---------- the main text-to-speech normaliser ---------- */
function spSay(text){
  let s = ' ' + String(text == null ? '' : text) + ' ';

  s = s.replace(/`([^`]*)`/g, '$1');                 // code ticks
  s = s.replace(/\*\*([\s\S]+?)\*\*/g, '$1');        // bold
  s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1$2');   // italic
  s = s.replace(/\u2018|\u2019/g, "'").replace(/\u201c|\u201d/g, '"');

  // a.m. / p.m. before anything eats the dots
  s = s.replace(/\ba\.?m\.?\b/gi, ' a m ').replace(/\bp\.?m\.?\b/gi, ' p m ');

  // mixed numbers: 1 1/2 -> one and a half
  s = s.replace(/\b(\d+)\s+(\d+)\/(\d+)\b/g,
      (m,w,a,b)=>` ${spWholeWords(Number(w))} and ${spFraction(a,b)} `);
  // plain fractions
  s = s.replace(/\b(\d+)\s*\/\s*(\d+)\b/g, (m,a,b)=>` ${spFraction(a,b)} `);

  // ratios 3:2 and times 7:45 are different — a time has 2 digits after the colon
  s = s.replace(/\b(\d{1,2}):(\d{2})\b/g,
      (m,h,mi)=> ` ${spWholeWords(Number(h))} ${mi==='00' ? "o'clock" : spWholeWords(Number(mi))} `);
  s = s.replace(/\b(\d+)\s*:\s*(\d+)\b/g,
      (m,a,b)=>` ${spWholeWords(Number(a))} to ${spWholeWords(Number(b))} `);

  // decades first (1850s), then plain years (1967)
  s = s.replace(/(?<![\d,.])(1[4-9]\d{2}|20\d{2})s\b/g,
      (m,y)=>' ' + spDecade(Number(y)) + ' ');
  s = s.replace(/(?<![\d,.])(1[4-9]\d{2}|20\d{2})(?!\d|\.\d|,\d)/g,
      (m,y)=>' ' + spYear(Number(y)) + ' ');

  for(const [rx,to] of SP_UNITS) s = s.replace(rx,to);
  for(const [rx,to] of SP_SYMS)  s = s.replace(rx,to);

  // = + - at the very start of a fragment
  s = s.replace(/(^|\s)=(\s)/g, '$1 equals $2');

  // any remaining number, including 1,250 and 3.5 and negatives
  s = s.replace(/(^|[\s(\u2212-])(\d[\d,]*(?:\.\d+)?)(?=$|[\s).,;:!?])/g,
      (m,pre,num)=>{
        const neg = /[\u2212-]$/.test(pre);
        return (neg ? pre.slice(0,-1) : pre) + (neg ? 'negative ' : '') + spNumber(num);
      });

  s = s.replace(/\bL\.?C\.?\s?(\d)/g, (m,d)=>`L C ${spWholeWords(Number(d))}`);
  s = s.replace(/\s{2,}/g,' ').replace(/\s+([.,;:!?])/g,'$1').trim();
  return s;
}

/* ---------- is this pre block a picture or real working? ---------- */
function spPreKind(t){
  const letters = (t.match(/[A-Za-z]/g)||[]).length;
  const digits  = (t.match(/\d/g)||[]).length;
  const art     = (t.match(/[|\/\\+_\-\u2500-\u257f]/g)||[]).length;
  if(letters >= 8 && letters > art && letters > digits) return 'read';
  if(digits > letters) return 'working';
  return 'diagram';
}
/* kept for the tests and older calls */
function spIsDiagram(t){ return spPreKind(t) !== 'read'; }

/* ---------- voice choice ---------- */
let SP_VOICES = [], SP_READY = false;
function spVoices(){
  if(!('speechSynthesis' in window)) return [];
  const all = speechSynthesis.getVoices() || [];
  return all.filter(v => /^en(-|_|$)/i.test(v.lang));
}
/* names used for female voices by Android, iOS, Windows and Chrome */
const SP_FEMALE = /(female|woman|\bwomen\b|samantha|karen|moira|tessa|fiona|serena|kate|libby|sonia|hazel|susan|aria|jenny|michelle|ava|allison|joanna|salli|kendra|kimberly|amy|emma|nicole|olivia|zira|catherine|linda|heera|veena|rishi|tanishaa|asilia|imani|nia|zuri|amani|grace|lucy|sarah|mary|anne|clara|elsa|marie|google uk english female|en-gb-x-gba|en-gb-x-rjs|en-us-x-iom|en-us-x-tpc|en-us-x-sfg)/i;
const SP_MALE = /(male|\bman\b|daniel|oliver|arthur|george|guy|ryan|matthew|joey|justin|brian|alex|fred|tom|david|mark|james|thomas|rishabh|ravi|en-gb-x-gbb|en-gb-x-gbd)/i;

function spScore(v){
  let s = 0;
  const n = (v.name||'').toLowerCase();
  if(v.localService) s += 60;                  // offline voices first
  if(SP_FEMALE.test(n)) s += 120;              // a lady's voice, as asked for
  if(SP_MALE.test(n) && !SP_FEMALE.test(n)) s -= 100;
  if(/\b(en-ke|en-za|en-ng|en-tz)\b/i.test(v.lang)) s += 30;   // closest to Ugandan English
  if(/\b(en-gb|en_gb)\b/i.test(v.lang)) s += 24;
  if(/\b(en-in)\b/i.test(v.lang)) s += 10;
  if(/natural|neural|enhanced|premium|wavenet|studio/.test(n)) s += 40;
  if(/compact|eloquence|espeak|robot|novelty|whisper|zarvox|trinoids|bells/.test(n)) s -= 70;
  // the engines that give the flat, buzzy "robot" sound
  if(/pico|svox|espeak|e-speak|flite|festival|klatt|mbrola|sapi ?4|microsoft (sam|mike|mary)/.test(n)) s -= 200;
  if(/\bsamsung tts\b|vocalizer ?(compact|embedded)/.test(n)) s -= 90;
  // the good modern engines
  if(/google|siri|apple|microsoft (aria|jenny|libby|sonia|natasha|hazel|zira)/.test(n)) s += 45;
  if(/\+female|-female|_female/.test(n)) s += 20;
  return s;
}
/* a voice we would not choose unless there is nothing else */
const spIsPoor = v => /pico|svox|flite|festival|espeak|eloquence|compact|klatt|mbrola/i
  .test((v && v.name) || '');
const spIsFemale = v => v && SP_FEMALE.test((v.name||'').toLowerCase());

function spBest(){
  const vs = spVoices();
  if(!vs.length) return null;
  const saved = localStorage.getItem('ple_voice');
  if(saved){ const f = vs.find(v=>v.voiceURI===saved); if(f) return f; }
  return vs.slice().sort((a,b)=>spScore(b)-spScore(a))[0];
}
function spInit(){
  if(!('speechSynthesis' in window)) return;
  SP_VOICES = spVoices();
  SP_READY = SP_VOICES.length > 0;
  if(!SP_READY) speechSynthesis.onvoiceschanged = () => {
    SP_VOICES = spVoices();
    if(SP_VOICES.length && !SP_READY){ SP_READY = true; if(state.screen==='noteRead') render(); }
  };
}

/* class-appropriate reading speed — P.4 slower, P.7 confident */
const SP_RATE_FOR = {P4:0.78, P5:0.82, P6:0.86, P7:0.90}; // calm teacher pace
function spRate(){
  const saved = parseFloat(localStorage.getItem('ple_rate'));
  const mult = Number.isFinite(saved) ? saved : 1;
  return Math.max(0.5, Math.min(2, (SP_RATE_FOR[state.klass]||1) * mult));
}
function spVolume(){
  const v = parseFloat(localStorage.getItem('ple_vol'));
  return Number.isFinite(v) ? v : 1;
}

/* ---------- the player ---------- */
const SP = {on:false, paused:false, i:0, chunks:[], wordMode:false, timer:null};

function spStop(){
  if(SP.timer){ clearTimeout(SP.timer); SP.timer = null; }
  spStopAudio();
  SP.on = false; SP.paused = false; SP.i = 0;
  spClearMark();
  spBar();
}
function devSpeakOne(text, opts){
  const u = new SpeechSynthesisUtterance(text);
  const v = spBest(); if(v){ u.voice = v; u.lang = v.lang; } else { u.lang = 'en-GB'; }
  u.rate = spRate(); u.pitch = 1.04; u.volume = spVolume();
  Object.assign(u, opts||{});
  speechSynthesis.speak(u);
  return u;
}
function devSpeak(text){
  return new Promise((resolve, reject) => {
    const u = devSpeakOne(text);
    u.onend = () => resolve();
    u.onerror = () => reject(new Error('device voice failed'));
  });
}
/* one call, whichever engine is in use */
function spSpeak(text){
  if(nvMode() === 'natural'){
    if(!NV.ready){
      NV.error = 'The standard narrator is not installed on this device. Open Voice settings and download it once over wi-fi.';
      spBar();
      return Promise.reject(new Error(NV.error));
    }
    return nvSpeak(text).catch(err => {
      NV.error = 'The standard narrator could not play this part. Please try again or check the downloaded voice.';
      spBar();
      return Promise.reject(err);
    });
  }
  /* Explicit device mode remains available only as a clearly labelled test option. */
  return devSpeak(text);
}
/* say a single word out loud — used by "hear a word" and Repeat */
function spWord(w){
  spStopAudio();
  const say = spSay(w);
  if(nvMode() === 'natural'){
    if(NV.ready) nvSpeak(say).catch(()=>{ NV.error='The standard narrator could not play this word.'; spBar(); });
    else { NV.error='Download the standard narrator before listening.'; spBar(); }
  } else devSpeakOne(say, {rate: Math.max(0.6, spRate() - 0.15)});
}
function spStopAudio(){
  if('speechSynthesis' in window) speechSynthesis.cancel();
  nvStop();
}
function spPlay(){
  if(SP.paused){
    if(nvMode() === 'natural' && NV.ready) nvResume();
    else speechSynthesis.resume();
    SP.paused = false; SP.on = true; spBar(); return;
  }
  SP.chunks = spCollect();
  if(!SP.chunks.length) return;
  SP.on = true; SP.i = 0;
  spNext();
}
function spNext(){
  if(!SP.on) return;
  if(SP.i >= SP.chunks.length){ spStop(); toast('Finished this part'); return; }
  const c = SP.chunks[SP.i];
  spMark(c.el);
  spBar();
  if(nvMode() === 'natural' && NV.ready) nvPrefetch(SP.i + 1);   // no gap
  const step = () => {
    if(!SP.on || SP.paused) return;
    SP.i++;
    /* a real breath: longest after a heading, then a sentence, least mid-sentence */
    const gap = c.heading ? 520 : c.last ? 320 : 130;
    SP.timer = setTimeout(spNext, gap / Math.max(0.6, spRate()));
  };
  spSpeak(c.say).then(step, step);
}
/* say the current sentence again */
function spRepeat(){
  if(!SP.chunks.length){ spPlay(); return; }
  if(SP.timer){ clearTimeout(SP.timer); SP.timer = null; }
  spStopAudio();
  SP.on = true; SP.paused = false;
  spNext();
}
function spPause(){
  if(!SP.on) return;
  if(nvMode() === 'natural' && NV.ready) nvPause();
  else speechSynthesis.pause();
  SP.paused = true; spBar();
}
function spSkip(d){
  if(!SP.chunks.length) return;
  const n = SP.i + d;
  if(n < 0 || n >= SP.chunks.length) return;
  if(SP.timer){ clearTimeout(SP.timer); SP.timer = null; }
  spStopAudio();
  SP.i = n; SP.on = true; SP.paused = false;
  spNext();
}

/* ---------- reading the section off the page ---------- */
/* A long unbroken sentence is what makes cheap speech engines sound
   machine-gun. Break it at commas, semicolons and dashes so the voice
   takes a breath the way a teacher does. */
function spClauses(say){
  if(say.length <= 90) return [say];
  const bits = say.split(/(?<=[,;:\u2014])\s+/);
  const out = [];
  let buf = '';
  for(const b of bits){
    if((buf + ' ' + b).trim().length > 90 && buf){ out.push(buf.trim()); buf = b; }
    else buf = (buf + ' ' + b).trim();
  }
  if(buf) out.push(buf);
  return out;
}
function spCollect(){
  const art = document.querySelector('article.nt');
  if(!art) return [];
  const out = [];
  art.querySelectorAll('.sp-s').forEach(el => {
    const raw = el.getAttribute('data-raw') || el.textContent || '';
    const say = spSay(raw);
    if(!say || !/[a-z0-9]/i.test(say)) return;
    const heading = /^H[1-6]$/.test(el.parentElement ? el.parentElement.tagName : '')
                 || el.classList.contains('sp-head');
    const parts = spClauses(say);
    parts.forEach((p, i) => out.push({el, say:p,
      last: i === parts.length - 1,
      heading: heading && i === parts.length - 1}));
  });
  return out;
}
function spMark(el){
  spClearMark();
  if(!el) return;
  el.classList.add('sp-on');
  const box = document.getElementById('views');
  const r = el.getBoundingClientRect();
  if(box && (r.top < 90 || r.bottom > window.innerHeight - 150)){
    el.scrollIntoView({block:'center', behavior:'smooth'});
  }
}
function spClearMark(){
  document.querySelectorAll('.sp-on').forEach(e => e.classList.remove('sp-on'));
}

/* split the rendered section into sentences and wrap each one */
function spPrepare(){
  const art = document.querySelector('article.nt');
  if(!art || art.dataset.spDone === '1') return;
  art.dataset.spDone = '1';

  const blocks = art.querySelectorAll('p.nt-p, li, h3.nt-h1, h4.nt-h3, .nt-quote, td, th, pre.nt-pre');
  const isHead = b => /^H[1-6]$/.test(b.tagName);
  blocks.forEach(b => {
    if(b.querySelector('.sp-s')) return;
    const text = b.textContent || '';
    if(!text.trim()) return;

    if(b.tagName === 'PRE'){
      const kind = spPreKind(text);
      const say = kind === 'read' ? text
        : kind === 'working'
          ? 'A worked calculation is shown here. Follow the working with your eyes.'
          : 'A diagram is shown here. Look at it as you listen.';
      const sp = document.createElement('span');
      sp.className = 'sp-s sp-pre'; sp.setAttribute('data-raw', say);
      b.parentNode.insertBefore(sp, b);
      sp.appendChild(b);
      return;
    }
    /* split into sentences, keeping the punctuation */
    const parts = text.match(/[^.!?]+[.!?]*\s*/g) || [text];
    if(parts.length === 1){
      const html = b.innerHTML;
      b.innerHTML = `<span class="sp-s${isHead(b)?' sp-head':''}" data-raw="${spAttr(text)}">${html}</span>`;
      return;
    }
    /* more than one sentence: rebuild from plain text (drops inline bold, keeps meaning) */
    b.innerHTML = parts.map(p =>
      `<span class="sp-s" data-raw="${spAttr(p)}">${spEsc(p)}</span>`).join('');
  });

  /* tap a word to hear it */
  art.onclick = ev => {
    if(!SP.wordMode) return;
    const sel = window.getSelection();
    let word = '';
    if(sel && String(sel).trim().split(/\s+/).length === 1) word = String(sel).trim();
    if(!word){
      const t = ev.target;
      if(t && t.nodeType === 1 && t.textContent.trim().split(/\s+/).length === 1)
        word = t.textContent.trim();
    }
    if(!word){
      const r = document.caretRangeFromPoint ? document.caretRangeFromPoint(ev.clientX, ev.clientY) : null;
      if(r && r.startContainer && r.startContainer.nodeType === 3){
        const txt = r.startContainer.textContent, i = r.startOffset;
        const a = txt.slice(0, i).search(/[A-Za-z0-9'\u2019-]*$/);
        const b2 = txt.slice(i).match(/^[A-Za-z0-9'\u2019-]*/);
        word = (txt.slice(a, i) + (b2 ? b2[0] : '')).trim();
      }
    }
    word = word.replace(/[^A-Za-z0-9'\u2019-]/g,'');
    if(word){ spWord(word); toast('\ud83d\udd0a ' + word); }
  };
}
const spEsc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const spAttr = s => spEsc(s).replace(/"/g,'&quot;');

/* ---------- the control bar ---------- */
function spBar(){
  const el = document.getElementById('spBar');
  if(el) el.outerHTML = spBarHTML();
}
function spBarHTML(){
  if(!('speechSynthesis' in window) && !(nvMode()==='natural' && NV.ready))
    return `<span id="spBar" class="sp-in"><button class="sp-i" onclick="spSheet()" aria-label="Voice settings">⚙</button></span>`;
  if(!SP_READY)
    return `<span id="spBar" class="sp-in">
      <button class="sp-i" onclick="spSheet()" aria-label="Voice settings">\u2699</button></span>`;

  const total = SP.chunks.length;
  const pos = total ? Math.min(SP.i + 1, total) : 0;
  const live = SP.on || SP.paused;
  const playing = SP.on && !SP.paused;
  const nat = nvMode() === 'natural' && NV.ready;
  return `<span id="spBar" class="sp-in">
    <button class="sp-i go ${nat?'nat':''}" onclick="${playing?'spPause()':'spPlay()'}"
      aria-label="${playing?'Pause reading':'Read this part aloud'}"
      title="${playing?'Pause':'Listen'}">${playing?'\u23f8':'\ud83d\udd0a'}</button>
    ${live ? `<span class="sp-n">${pos}/${total}</span>
      <button class="sp-i" onclick="spSkip(-1)" aria-label="Previous sentence">\u23ee</button>
      <button class="sp-i" onclick="spRepeat()" aria-label="Say it again">\u21ba</button>
      <button class="sp-i" onclick="spSkip(1)" aria-label="Next sentence">\u23ed</button>
      <button class="sp-i" onclick="spStop()" aria-label="Stop">\u23f9</button>` : ''}
    <button class="sp-i ${SP.wordMode?'on':''}" onclick="spWordMode()"
      aria-label="Tap a word to hear it" title="Tap a word to hear it">\ud83d\udc46</button>
    <button class="sp-i" onclick="spSheet()" aria-label="Voice settings" title="Voice">\u2699</button>
  </span>`;
}

/* the settings live in a sheet so they never clutter the page */
const SP_SAMPLE = 'Good morning. Today we are learning about fractions. ' +
                  'Three quarters plus one quarter equals one.';

function spTry(uri){
  const v = SP_VOICES.find(x => x.voiceURI === uri);
  if(!v) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(SP_SAMPLE);
  u.voice = v; u.lang = v.lang;
  u.rate = spRate(); u.pitch = 1.04; u.volume = spVolume();
  speechSynthesis.speak(u);
}
function spUse(uri){ spSetVoice(uri); spSheet(); toast('Voice changed'); }

const AUDIO_TEST_URL='audio/test-voice.mp3';
function audioDiagnostic(){openSheet(`<h3>🔊 Audio Test</h3><p class="muted" style="margin:8px 0">This test uses one real generated MP3 from the standard narrator.</p><audio id="audioTest" controls preload="metadata" style="width:100%;margin:12px 0" src="${AUDIO_TEST_URL}"></audio><div id="audioStatus" class="hint-strip">Ready to test. Tap Play.</div><button class="btn btn-primary" style="margin-top:12px" onclick="runAudioTest()">▶ PLAY TEST VOICE</button><button class="btn btn-ghost" style="margin-top:10px" onclick="closeSheet()">CLOSE</button>`);}
function runAudioTest(){const a=document.getElementById('audioTest'),s=document.getElementById('audioStatus');if(!a||!s)return;a.playbackRate=1.0;s.innerHTML='🔄 Loading audio…';a.onloadedmetadata=()=>{s.innerHTML=`🟢 Audio ready · ${Math.round(a.duration)} seconds · playback 1×`;};a.onerror=()=>{s.innerHTML='🔴 Audio file could not be loaded or decoded.';};const p=a.play();if(p&&p.then)p.then(()=>{s.innerHTML=`🟢 Audio is playing · ${Math.round(a.duration||0)} seconds · playback 1×`;}).catch(()=>{s.innerHTML='🟡 Playback was blocked. Tap Play again.';});}
function spSheet(){
  const rate = parseFloat(localStorage.getItem('ple_rate')) || 1;
  const cur = spBest();
  const list = SP_VOICES.slice().sort((a,b)=>spScore(b)-spScore(a));
  const nat = nvMode() === 'natural' && NV.ready;
  const why = nvCapable();
  const ch = nvChosen();

  const natural = `
    <div class="nv-box ${nat?'on':''}">
      <div class="nv-h">
        <b>Natural voice</b>
        <span class="nv-tag">${NV.ready ? 'installed \u00b7 works offline' : 'one-time download'}</span>
      </div>
      <p class="nv-p">A real neural voice that runs on this phone. Downloaded once over
        wi-fi, then it works with no internet and nothing is ever sent anywhere.</p>

      ${why ? `<div class="sp-warn">${I.info(15)}<span>${why}</span></div>` : `
        <div class="nv-vs">
          ${NV_VOICES.map(v=>`<button class="nv-v ${v.id===NV.voiceId?'on':''}"
            onclick="nvPickVoice('${v.id}')">
            <b>${v.name}</b><span>${v.mb} MB \u00b7 ${v.note}</span></button>`).join('')}
        </div>

        ${NV.busy ? `
          <div class="nv-prog"><i id="nvBar" style="width:${NV.progress}%"></i></div>
          <div class="nv-pct">Downloading <span id="nvPct">${NV.progress}%</span> \u2014 keep this page open</div>`
        : NV.ready ? `
          <div class="nv-row">
            <span class="nv-tag">Standard narrator active</span>
            <button class="nv-del" onclick="nvRemove()">Remove</button>
          </div>`
        : `<button class="btn btn-primary" onclick="nvDownload()">
             Download ${ch.name} \u00b7 ${ch.mb} MB</button>
           <div class="nv-note">About ${ch.mb} MB for the voice, plus a few MB for the
             engine. Needs internet this once \u2014 use wi-fi if you can. After that it
             never needs internet again.</div>`}

        ${NV.error ? `<div class="sp-warn">${I.info(15)}<span>${spEsc(NV.error)}</span></div>` : ''}
      `}
    </div>`;

  openSheet(`
    <h3 style="margin-bottom:3px">Voice</h3>
    <p class="muted" style="font-size:12.5px;margin-bottom:13px">
      ${nat ? 'The same standard narrator is used on every device.'
            : 'Download the standard narrator once. The app will not silently switch to a device voice.'}</p>

    ${natural}

    <button class="btn btn-soft" style="margin-top:12px" onclick="audioDiagnostic()">🔊 Test standard narrator audio</button>

    <div class="sp-srow" style="margin-top:16px"><span class="sp-lab">Speed</span>
      ${[0.75,1,1.25,1.5].map(r=>`<button class="sp-chip ${rate===r?'on':''}"
        onclick="spSetRate(${r});spSheet()">${r}\u00d7</button>`).join('')}</div>
    <div class="sp-srow"><span class="sp-lab">Volume</span>
      <input class="sp-vol" type="range" min="0" max="1" step="0.1" value="${spVolume()}"
        oninput="spSetVol(this.value)" aria-label="Voice volume"></div>

    <details class="sp-help" ${nat?'':'open'}>
      <summary>Phone voices \u2014 try them and pick the best</summary>
      <div class="sp-vlist">
        ${list.map(x=>{
          const on = cur && x.voiceURI === cur.voiceURI && !nat;
          const tags = [];
          if(spIsFemale(x)) tags.push('lady');
          tags.push(x.localService ? 'offline' : 'needs internet');
          if(spIsPoor(x)) tags.push('basic sound');
          return `<div class="sp-v ${on?'on':''}">
            <div class="sp-vn">${spEsc(x.name)}<span class="sp-vt">${tags.join(' \u00b7 ')}</span></div>
            <button class="sp-try" onclick="spTry('${spAttr(x.voiceURI)}')">Try</button>
            ${on ? '<span class="sp-using">in use</span>'
                 : `<button class="sp-use" onclick="spUse('${spAttr(x.voiceURI)}')">Use</button>`}
          </div>`;}).join('')}
      </div>
      <p>To improve the phone voice itself \u2014 <b>Android:</b> Settings \u2192
      Text-to-speech \u2192 Google Speech Services \u2192 Install voice data.
      <b>iPhone:</b> Settings \u2192 Accessibility \u2192 Spoken Content \u2192 Voices
      \u2192 Enhanced or Premium.</p>
    </details>

    <button class="btn btn-primary" style="margin-top:15px" onclick="closeSheet()">Done</button>`);
}

function spWordMode(){
  SP.wordMode = !SP.wordMode;
  toast(SP.wordMode ? 'Tap any word to hear it' : 'Word tapping off');
  spBar();
}
function spSetRate(r){ localStorage.setItem('ple_rate', r);
  if(SP.on){ const i=SP.i; spStopAudio(); SP.i=i; spNext(); } spBar(); }
function spSetVol(v){ localStorage.setItem('ple_vol', v); }
function spSetVoice(uri){ localStorage.setItem('ple_voice', uri);
  if(SP.on){ const i=SP.i; spStopAudio(); SP.i=i; spNext(); } spBar(); }

spInit();
authInit();

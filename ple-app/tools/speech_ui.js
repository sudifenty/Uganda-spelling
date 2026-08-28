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
  /* The Listen button is always available: the voice is the app's own
     narrator (plus recorded files), never the device's voices. */
  SP_READY = true;
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
/* The narrator is the ONE voice of this app — identical on every device.
   If it is still downloading, the learner is told; a DIFFERENT (device)
   voice is never used, so the app never sounds different from phone to
   phone. */
let SP_DL_NOTED=0;
function spNarratorNotice(){
  const now=Date.now();
  if(now-SP_DL_NOTED<4000)return;
  SP_DL_NOTED=now;
  toast('The standard narrator is downloading \u2014 your audio will start when it is ready.');
}
let SP_MUTE_NOTED=0;
function spMutedNotice(){
  const now=Date.now();
  if(now-SP_MUTE_NOTED<4000)return;
  SP_MUTE_NOTED=now;
  toast('Sound is muted \u2014 tap the \u{1F507} button (bottom left) to unmute.');
}
/* one call, whichever engine is in use */
function spSpeak(text){
  /* Muted and still-downloading are NOT errors: the learner is told what
     is happening, so these resolve quietly — a rejected promise here would
     ripple out as an unhandled error and wrongly trigger the safety net. */
  if(typeof afxMuted==='function'&&afxMuted()){ spMutedNotice(); return Promise.resolve(); }
  if(!NV.ready){
    /* THE FIX: pressing Listen starts the one-time narrator download.
       This promise resolves only after the text has actually been
       spoken, so the sentence reader keeps its natural pacing instead
       of racing ahead through the whole section. */
    NV.pending = text;
    spNarratorNotice();
    const canStart = !NV.busy && Date.now()-(NV.lastAuto||0) > 30000;
    if(canStart){ NV.lastAuto = Date.now(); try{ nvDownload(false); }catch(e){} }
    if(canStart || NV.busy){
      return new Promise(res => {
        const prev = NV.pendingResolve; NV.pendingResolve = res;
        if(prev) prev();               /* release an earlier waiter cleanly */
      });
    }
    return new Promise(res => setTimeout(res, 1200));   /* a recent attempt failed: move on gently */
  }
  return nvSpeak(text).catch(err => {
    NV.error = 'The standard narrator could not play this part. Please try again or check the downloaded voice.';
    spBar();
    toast('Audio could not be played. Please try again.');
    return null;                    /* the failure has been reported to the learner */
  });
}
/* say a single word out loud — used by "hear a word" and Repeat */
function spWord(w){
  if(typeof afxMuted==='function'&&afxMuted()){ spMutedNotice(); return; }
  spStopAudio();
  const say = spSay(w);
  if(NV.ready) nvSpeak(say).catch(()=>{ NV.error='The standard narrator could not play this word.'; spBar(); });
  else { NV.pending = say; spNarratorNotice(); if(!NV.busy){ try{ nvDownload(false); }catch(e){} } }
}
function spStopAudio(){
  nvStop();
  spFileStop();
}
/* ============================================================
   PRE-GENERATED LESSON RECORDINGS — one voice, recorded once,
   played on every device. The device NEVER generates narration.
   When a section has a recording it is played directly; sections
   without one are read by the standard narrator (the same voice
   everywhere). Files live at /audio/<subject>/<class>/t<NN>/ and
   are cached by the service worker on first play (offline after
   that). Registry key: "<topicId>:<sectionIndex>".
   ============================================================ */
const LESSON_AUDIO = {
  'P4_SST_T01:0': './audio/sst/p4/t01/sec-01.mp3',
  'P4_SST_T01:1': './audio/sst/p4/t01/sec-02.mp3',
  'P4_SST_T01:2': './audio/sst/p4/t01/sec-03.mp3',
  'P4_SST_T01:3': './audio/sst/p4/t01/sec-04.mp3',
  'P4_SST_T01:4': './audio/sst/p4/t01/sec-05.mp3',
  'P4_SST_T01:5': './audio/sst/p4/t01/sec-06.mp3',
  'P4_SST_T01:6': './audio/sst/p4/t01/sec-07.mp3',
  'P4_SST_T01:7': './audio/sst/p4/t01/sec-08.mp3',
  'P4_SST_T01:8': './audio/sst/p4/t01/sec-09.mp3',
  'P4_SST_T01:9': './audio/sst/p4/t01/sec-10.mp3',
};
const FILEAUD = { key:'', url:'', el:null, state:'idle' };   /* idle|loading|playing|paused|error */
function spFileFor(key){ return LESSON_AUDIO[key] || null; }
function spCurrentSectionKey(){
  try{
    if(state.screen !== 'noteRead' && state.screen !== 'mathLesson') return null;
    const t = typeof noteById === 'function' ? noteById(state.ntopic) : null;
    if(!t) return null;
    return t.id + ':' + (state.nsec || 0);
  }catch(e){ return null; }
}
function spFileStop(){
  if(FILEAUD.el){ try{ FILEAUD.el.pause(); }catch(e){} }
  FILEAUD.state = 'idle'; FILEAUD.key = ''; spBar();
}
function spFileRetry(){ if(FILEAUD.key && FILEAUD.url) spFilePlay(FILEAUD.key, FILEAUD.url); }
function spFileToggle(){
  if(!FILEAUD.el) return;
  if(FILEAUD.el.paused){ FILEAUD.el.play().catch(()=>{ FILEAUD.state='error'; spBar(); toast('Could not play the recording. Check your connection and try again.'); }); FILEAUD.state='playing'; }
  else { FILEAUD.el.pause(); FILEAUD.state='paused'; }
  spBar();
}
function spFilePlay(key, url, onFail){
  if(typeof afxMuted==='function'&&afxMuted()){ spMutedNotice(); return; }
  spStopAudio();
  FILEAUD.onFail = onFail || null;
  FILEAUD.key = key; FILEAUD.url = url; FILEAUD.state = 'loading'; spBar();
  try{
    if(!FILEAUD.el){
      FILEAUD.el = document.createElement('audio');
      FILEAUD.el.preload = 'auto';
      FILEAUD.el.onplaying = () => { FILEAUD.state = 'playing'; spBar(); };
      FILEAUD.el.onpause  = () => { if(FILEAUD.state === 'playing'){ FILEAUD.state = 'paused'; spBar(); } };
      FILEAUD.el.onended  = () => { FILEAUD.state = 'idle'; SP.on = false; SP.paused = false; spBar(); };
      FILEAUD.el.onerror  = () => { FILEAUD.state = 'error'; spBar(); toast('The recording could not be loaded. Tap the speaker to retry.'); if(FILEAUD.onFail){ const f = FILEAUD.onFail; FILEAUD.onFail = null; try{ f(); }catch(e){} } };
    }
    FILEAUD.el.src = url;
    const p = FILEAUD.el.play();
    if(p && p.catch) p.catch(()=>{ FILEAUD.state='error'; spBar(); });
  }catch(e){ FILEAUD.state = 'error'; spBar(); }
}
function spPlay(){
  if(SP.paused){
    if(FILEAUD.state === 'playing' || FILEAUD.state === 'paused'){
      spFileToggle(); SP.paused = false; SP.on = true; spBar(); return;
    }
    if(NV.ready) nvResume();
    SP.paused = false; SP.on = true; spBar(); return;
  }
  const fkey = spCurrentSectionKey();
  const furl = fkey && spFileFor(fkey);
  if(furl){ SP.on = true; SP.paused = false; spBar(); spFilePlay(fkey, furl); return; }
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
  if(FILEAUD.state === 'playing'){ spFileToggle(); SP.paused = true; spBar(); return; }
  if(NV.ready) nvPause();
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
  /* One voice everywhere: the sample is the app's own narrator sample. */
  try{ if(typeof spSpeak==='function' && NV.ready){ spSpeak(SP_SAMPLE); return; } }catch(e){}
  toast('The standard narrator is still downloading.');
}
function spUse(uri){ spSheet(); toast('This app uses one standard narrator voice on every device.'); }

/* Embedded from ple-app/docs/test-voice.mp3 (58 KB) so the app stays one
   self-contained file and the audio test works fully offline. */
const AUDIO_TEST_URL='data:audio/mpeg;base64,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Nl3MaqlZ93oVmOvtLGBjTquxTCwlBEPEnf7yRZr//+3XZ0u/6wC7uJKhGd1HwSWBcEZxotFaaO8tK/78hMAetg5k0iMO1fK2283j2Sit7swy//NExLwRyR6tkspGpJWUrm1ZSkMRiy//+xnwZZI9SIUT///obZ//9dUAAxT5oBYQAZ3B0chKh8cAOJtet1IRWKVwHO8gpqBCmASUEdADUOTMUZ1Upn92czrX3+rQwkp2//NExMcSARrCNnjEsk/X/p3Cw8HhKsUlv///Nj0AA12pImcWAZ0wMHjYxoIqMActQrFGOX04eX4PINRuEk7aQlUVv6vn58Ly8QgMVKAyhV5/+z9GDRi/y9Vwx9LBWB1r//NExNIRyYq1nMGEkj8eM7hRKE////rLfwzEIOxiNqoACev13W8CgbvoMA8GGBGGFmovtWijnFoT1lc0ZwG10do+4plgU7tojInwSKGC5J4Uv+JRNvteDuSjCBdnf8////NExN0RsY6eXsjElL7QQDUwgGCUwdhz/////1kq8BYrAElt1l13AoHykliAfJw0lMVdKI1XkpSRL1kJPA7YCXJjZN2LMDuNEzOFKVa/vM1WdUQNc9/29cIZzDBQoYYE//NExOkVSbKOXtLGcMghzf/////UVQojjeDCgXAQJAcYmFkpmyudoHEpOvYoBlgoLnKsNvJu1qU5Y9bHl4GU4R8Zo0QoIx4QLvQSj3J9m8l62dX4KTaSXRAcm3OWXH5l//NExOYU+ZaWXsoGtK0dPKRQ6iVIM7PV0XIen//////////6qKME3L4pADdlsm23AoHXWNBUMBJWgRkLq5SpLeQlcanclcTKjre41g8KsjojMZ1or1paxEiKAcokd3Ky//NExOUSGY7CXnmEqlra91cpjsZxGElzTv/////5FQIgAEHEAFk075wCgaYeIGEl5oEMfWbgEUNPKFemHI5oAOoC+T+5LmiY0hVRAjW58eJeKiTHoEVSTczJIfSIPwKc//NExO8Zet5wPNpEvBeSRKJsOE1L6mCvABwDmDjDgUkdSGKMplGho54RkK4GMCFAGACYjDGxdOmpOH48urhdR2DjPmp8yTb///////////Wmehz6P6QCDKoACCEgjAG8//NExNwR4Y66X0koAu5yFYNKGrBNgtm33IDnnvuTWW88stxseQFAyUpV1LUQUtLU6Xh5QAMAQoApQNUqEJh/FhINZFUaIjMeg6pGjlE0bjK1o72mR04medDR2V18vmB8//NExOcjCppk8ZtoAMJA3+MJCSZGv0RtjVLHrWs6AlfQN6eMVYABDqUxKWxsJm0yvI5Lx5xN10sHXVUhG2P76+tYaYJyBsYAYG09uR58QOMqF1dXvZBcc8T0GCAGwR2P//NExK0caX5QTZqYAHt7fTD7jsFxnhyx3ha3729vxKB0bBPoGqROPerr/9dVTpxkDdBM4aEQcnBcH+//7f3y/Ny4gWyKE4PBsVB4IGV12mg1u112kzlBoOSoAAOCYf1r//NExI4e4ypIKY+AAiYDw0zMhQeRNZwHA8gNmw6i6KkPYYEkE1WEnNipEGaJFak8tb+hQmBwN4xJQInF/cx8wNhqTw9l5oCP/zHV/zgPy8EdejiBwdnf/+a317nZGJ6J//NExGUhmqsCX4xYAj8d43j+cHsNzWbnvvh8T//9/n2G5/PEyThpRMHsQfVmBMp3JFGUEAAIO6WFAyYUzFIit2baEkT5NfJetbZZbHxdX/25t2IwzOX7nTtv/6fE8Gxo//NExDEb0xamV8ZYATuXrmEf4vSc+ZNWWbPJJ138xbnVZ02fUo05J+5rdvw+v//a62td+6Ww7de7a1rjY98X//HLfbX8t/daJ07i6g2TQtgRTkQ8ScKbYqWOASRIeiZO//NExBQV8jKGVjFHEHfDSKt5K6LRWZpf0M7Q6Ba2ohl8tWxIBRxuvD2MKJa1V29Sv9jVasNSlVY1JqTQ//y/goS7bAoeWW5URRY0e6XrcPcqAE0l2arm4wE/6RiCRkR4//NExA8SMZaKXgmGbIg9MwhlwARHP6gguInoI9ABPMnOmkKi4gRCf/4iIgGfEcyqFvzosAENBdgEGw+14v4YaGP//L/c/67KwWPBAgghRkdwIZmE1nl7yg23bff7v3ZN//NExBkUmZ6IADINoD/jDDTDSR4hCEjyBM85VoUhWEwvGK17Bx00YgQHBLA+eLnp40/tM8RIXPpcQIEzYIXEX//1rfuR8fX4aQjSOM2ZeeFJTlXjba0tyt99sjL/pnvX//NExBkQeZqgAEmGfIIJigO+X2yCrIuJOc5dilQSEcw4cYhI8i5pdnZ2QSAyaICsZ//9lyfWccUrRA5GBKvhhdNURzQWIdumKMmQql4UvTRZ9KAgIldrR0IKgOJa9iIH//NExCoScO6yNhjGICwMmbniwJFpwHAoLljhENCK+sJCpkv4ue213bJ9bau6u9jbhJJRMDsoJBUEIWcsvnXqPn2WdUyiZGoRNElFS+q1U36fqwoQHVLnrSh/kDEitqSn//NExDMR+YqyVjBHAN2mq5E4QPAzH1pXNn9bX036/6vdH5I2/6aZuAQPuLUPvqTdpW+sUhhsGF4sOKTedHWMKHU92iTvoKCjw53OP/DImonFyKUjnAEqVEKnsd865Nfr//NExD4SeULGNgmGGpe39NC1sBUs8n2klHVKooQl2gepSUOrcgtyzWjHw6mLEyjRk8mJBTomJIw04mDCw8kzO2UhR6guwApMyQy9RXzHf9iw7UdZam0FQ+XFUk236FqW//NExEcSMPKqTjBE0IYmEsk/++5IAg4cWpTHKNBVR5tyh1yotRrR0uZKQ19yo7Ukky0So6ovv6tv2uJebxoimxhex0JrBQBp0fXkQFZlSTD380tLo7/qPlIGOAOjgS9F//NExFESATrCNgGQCskmlSUszXMvW61WGLnuY7tUyDUmdaMA84wVKV2Z/eVryxQ9Bp3lUVHA0MEALHRIHmr6RRpWxpB1RGz+lrNCtHtoCjLfAYqKBgz4CCCYgcljgIgl//NExFwSgW6NbgGKGKMygbiiMsGiH0xJzdivAEA9NqN/GbtR9MQYAogcJDQMiZT1gqHblnQXcm3jnnEGRBMoo//0bH/XOhAPgcgBfaV8eSjzidyQNXCvS6w46nf/zkVa//NExGUSePqKNhiTILkt2YKmQaYPX7tTUF8pQEWeX+bnAoZARhYzawhVRsYRQyGlMq08cr/cr0TzlSAvEAOUJRIlw6TVgNGpSZGnOJllxmSky57Fc5Fyi7ygWQwSSfu///NExG4R0YZw7DJHJMgoGpKZfmTak1Vh7Yx+pJGM1KEIhYwWeKCvoA1TiNASLbUKFEAgFIm38WKtoyMKxk2iMbQ4ookRM6vOTlYaq1A1Uiqw0TLHRk0GdQsopIa0lC7s//NExHkSGZpkNjGGfAxo9WemxmqMYEBMeKgkNFSyyApu+j0993/66ql+JsW9WuSphL8KIwwmDCd+z0S4RF2Ak0tfJnv6LRE477VjZKqARt9bRLj0xhplVM7TrMjBvyup//NExIMSkVJECEpGfJR3Rrz/xTUa/Zbeigqsk4KOI8AgpVk4cFkkCFAUQ4JqYh63ybQymMTxS+3/d6quiuqd1fY/+hNzOu1j71OcPoIc49xJTyTIjytWGLavk3mOtvk3//NExIsQ4P48AHmEsDszXJaCaXD3iw4g2L0uaBKg4hJW0glSSKgM/m3Ih1WvFgCPSpbLxxJT61FqNVd3IopIhHCYFzRsU4T+cWqGPXaWkESJ0mDINnwqLDR4E5YKCQiE//NExJoMsDpINnjGBNggpQfYS0fa61WtJV7m3tvHEnuTC6dN23UQ3xzXnatdCDjCjQcpwAKoTOWkDQQC1c1Cg4C7EpHJ5nkMBNJ2ETCj+37zv/tXJff5tfrxi4/Xvp9T//NExLoRIMYwAHmEHC3pNvfnVe3u5vyLTf9TG8OmfX9lrrMaEPMpV73aAiIorjzkrkfJfjE6NTEFB7lqA47CyhqWsDGgdjJ6exERvLmLBgYPEVi8rwx/UJFoSq+n6PMw//NExMgQaF4wAHmGLFLVaEuyQ766Q3u3kN75/yV78c5124fg4L90HOnVP93v1uoPEMAABgVmieBYmi9lyOlTsbdPChwMWcEnotV80dqy3F3yUM+7zN4yucr/ON7qu99r//NExNkT6FIsDHpMAX53J8+U+m2TPzNKb7z/36v7/1N8uV/RH578cxUi8GQTMoUHguTBUWbQGUl27GVzUGLAAkdYsQEmoViZbHn3pc8m5q2Ioh0nFgVgu4V+/HTThVA1//NExNwV0NokBMGGT8gBvIvRsvcqhj6ki7mOQMbRGLrQ3AfgWww+CAPuslQ3CmLleZqxWPBN98xhA3kfi7237k9Pl8WVd5Nr9eGz9s8gd4gyz78zyVU59lIA9rD5OqCV//NExNcTGHosCmBEiYr96vu80dNY++aeJjZ7lCkON6IBgRcBx0s3/yx/ubMnUqKFba3F9bk2AI//1RD2L6e5X4dFkeqO9R8+2703Fhhb/9vlfkdPZ4d2DHqsxzf+7cj9//NExN0SOGYoAnpGDLtnfd2bW7bV9rsMtlqMKTQRR5XQjaVC/n4gOam+c7nU5T7wzr81b1hljhv5Z3WeGGdftfjI4PABANM2stYrpwvj4JEDhiei43fzw/de/SSprliV//NExOcUcIIsDHmEFdPTSiMMMX0pB223LqM0EQAghdRTKBAQBZkQisjpNVKSWY2qlJnhn3V0gsGyAhAzhYePlEpWohNI5PkD4OARAhUqgcKACwoBOTl9s9+fMvGjNB5N//NExOgS+HIsCkhGhVMBNTW10zkHWg6l19OT1h42ZvpCYyfuHAkIiWZx0pfFh5U7P32I7gLHHGTigia1n+9/9//Gv/87pAgVj+BHeXhKCrG5+jUrIakOQtipV7e2IiZT//NExO8iSgowCMDxSAmhYDkQw03InBkTNSGMlLxyAPg+RDCso7+/o+77wQghl222222ruwGWp9FUxaHPadg5ZQaLnGAEZuzYNCDuyykfC9naylMvws2X1eebMhksxKLi//NExLghOd5kANselBJ1NVICsI8H6Qcng3PPKEFKuf/uvD3FvUyc8jxBhOQURoFUVBtUBxZEOJCXQ5QyblG/nmDjsWUPMuFfz/EZJAYt3dw7gmIAQTJirdHl+BAAAAEL//NExIYhAmbeXtpG+j+blVkGgmXAOMfi+ZSBjIFFM3IaMqSRu/eWTZd1lk/qc43SW+yLX3Qql92TdBF1fTU3TU/+MxRAIPq7Oww2WWTQf67sZPz+DCad2em93ER/nv7+//NExFUhqxrGNomZq9G0rKSkc0qc8CgR16pxtarEu6GT1oVpg8MFh4xsdP3l6+8FT+ji/++YJq3GnLcvGFYCQAUtscqATdG9by1CfG+06+YYmiTdtN3iURytMBStyPUK//NExCEaWUreXnmfBqmCC82QVemyhRODOzRr08k0NsXz8BgHStkva1gvzKfjUxIl4t639a+4doE1IH//+lFklt8cWLFA7KjKZtbiwFLRMtDYnOpSRRWAJyaySNM4M21///NExAoUWUbqXHoe6giRI/4vWEyqJz+O5CRIs616je9B4QUTpad0ptbpr7facMXnpdUi3tjWzbnVep85zjdYGM7gMzj4gURb+WArGj2//+fCJd/9SoAUy7jCA075QkAQ//NExAsTew7WJigHwfVjtUrvRSiDq9ZlRmNddL2u3sS5ml/+fP1t5P3+uPludP3c0/r09+sThkKCRYHdxfuBzCIu/uIRPd6/T098s0QAEB94d3bXbW2CxwBFHyxI9DHF//NExBAVuxsS/igNw1kqpSlYxqvtmsdVZKetHPkVmRJf3MpepWy//RP313bauiPlvl7l+Xx6z5N3UzveJ1L4ZtJxt/X8798NPmd1MtzZ8tCxvhAQeJiH+21tj0hCzTdo//NE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4i/1nZYlxL/kvqcqgBCo25sAc4XKWviBR2cjRzCIRQOZCFFgYt7AAARHiJMlQDfziJoW9XBBmwLjy5s+lO4e4XNihk5s//NExDkSUNadfjYGCMq46owWUWv/+jps1OpZ7/pqC9blT4PczAY1BJhanYmGRLAtBmZ2C1puVIaGzNgVhKMlgIFCSJehAVKkDST4hKCZHCycLnd7r2bqa2iu+0llBERx//NExEIRyW6YqNmE0AYSNE30VYC9HHHBbQKB3ffqM9g7u18GIzjv87K0mUsm/digey/3tSZfQYzqRCzIxuRTPJ//96Ki9js59KDkT1oQezammzNP//////5NAMFaSoC7//NExE0RsW7mXsCM9o4RElJHtAPNabcLMCIG7znRl4Q6FIu5GQAMnjG7OTZRU3cy4vYaARWjQbqHxXUe3OVtvcv/+VWQg0VYLDZ3Ejf0zCmtt0c1EFd/noHp6nDLFMff//NExFkRuWKhuNPKqeDcJNnxTyKWdEqGIRTNBAF39g41v2FgvaFyWgkvzO5/lW//0//VueSrO/HXf/1VPnR6v//VASygCqAGd27ARjlsAr5gKh0DmQmA0yPPVhwxUQQs//NExGURuZLNvnsOypfri+aT/0W/pA21OMwa27ONvuZcGpswChZ9fX0f////x20Vyf5QH2nHF337+mscHS+7/8gtwTUBgVy3bWWxgf+NASea4+KyGEDoW978kZDbLhBu//NExHEVIZKMftpKzFlTebICJ+mQsn2emY1N6TC1ifcVV5nsczy+67ct5q/KJX9PTo9KeEbMa4VIE1Y092mvyp9DShkh6P7Fknqer//HLj0MJ2yPVyxwf9/gJ0UgYu7K//NExG8Xsd6+XsPOftEUXA/PuOoq7Kmd8Ltntz7ME569mTLLV5fvU8TnMMqkQk50IAg87nE269Rj83b/y//u18jAh2RwMNdyCf+bui1e8XPMIoY0KVoD7n+LhNAmaBr///NExGMaMeq1vsFRLv/LHlg0YQnE7QLXB/JEB9grY1W0lSW14Sujf2jfWIVsZmmprfU0KWP7N+uQPx1qbwf////+AFfWA8rY4Qz8rgABQyvfYdCcD4IBQKwPnwNBACht//NExE0eexa4fnhZGdbJYliWrODA8xgQCwsive0B5yczXmZ+wZn7Bh1215/2LK+cHixxevfvdevuHqoNhCLX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qhz4rQWSpg1xubT27KshcosxuJ36l0HDgGNFqJRXaY6V//NExFAhAsa69t5KWR5FIFiBwCHAMHx07IokVU3/Z50comGXTS//WYxSFMgqkpjlZWMn///+lN4mU5FF32j8y0cvRFqIB6tyFNqSFyVRIi8kGI2S0+C9FtDaFaZRPUqa//NExB8WyRK1V094AEpy4rpCly7TrxCjdLoR5wqaZ9euNvdWtuuLfWPbNcbzq0t4sKHFBsJSTHeFQqkJD/+0YhYCT///kZZ6ztUFTdoAQxD8aGIxWZvGcKGI46g6YD+t//NExBYX0uJs0YxoARFCaDyGGMjYxJIul8viyF4xJEYQ0MnU1B1PUj2RfpJLRRqdN+YpW/////VttX///1IILfv7/9vur/oIGhugZHkzqRopH+XHUzcVqu26AchfQwGL//NExAkU6RqwAZjAAMPqbK0NBa5WsI3F2FDC/sinLZjsZhi1waNsIBTK6OWXiocQoV66asRkbEJFn//2IU+sbmpbqzz/5z/w1Xr65VwrX09DTSiI1Pz/QufQDbluFA+M//NExAgSKKbln88wAqYDL/huT2KuDHriGhVvAYZtyNc3ZAlRSA7/f+gPEIlQeFSCgKgCpOPsooeMYEriBY4ITQqjRjdH1///3kIs0+1NAOu3AYDurCaBE6kWDibXkeDf//NExBISCRbAXsMKONgmo+bAsbR6Cw/X153JLx8PhIV3LcSe7tOZC7aPy6ipFiBdmaZoAbDJKaWPfs////8rtaVElKqF14AC09DLhSYgEXusBCJjRUJO7ssRRQ2WVlfX//NExBwSUNKoNtPGMQEtddqDoRwaPafVIkMWJEMss63XOe54VF3j3/m3//LGBYUVEw9zxYpMl5x//uoACrhTEgYFwQBMRMjlLVNrFSOL8VPEo81HewAVs9BPQ2QCLAxi//NExCUR2Y6yHj5EEhFZnZAgGQxF/066hUIZy///84kERF0FWrilLRb////3Vnl1DqApOQICvfdsA1kQs9GyJV5H/ZuuGkjD62a8N2891u6pM8IjGYb5BTggZSqaMzmt//NExDASWR6o/1kYApDyn5/2KwYge/62h4+8WboDX5XNf///711KAs+65AGNSBocbKVSQEegDvQwVhlBElJO+7E/kpimeXUmP49h6lJGsmvZAKYGwI2XTU0NTZFaCC0C//NE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';
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

/* ============================================================
   NATURAL VOICE — Piper neural text-to-speech, running on the
   device itself.

   This is the "voice layer". Two engines sit behind one small
   interface, so either can be swapped without touching the Notes
   screens:

     device   — the phone's built-in speechSynthesis (always there,
                often robotic on cheap Android)
     natural  — Piper, a neural VITS model that runs in WebAssembly.
                The model is downloaded ONCE over wi-fi and stored
                by the browser. After that it needs no internet and
                no server: the text never leaves the phone.

   If the controlled narrator is not installed or cannot play, the app reports that clearly
   instead of silently switching to a different device voice.
   ============================================================ */

const NV_CDN = 'https://cdn.jsdelivr.net/npm/@mintplex-labs/piper-tts-web@1.0.4/+esm';

/* A short list on purpose. Every one is a woman's voice. */
/* Sizes checked against the catalogue the library itself downloads from
   (huggingface.co/diffusionstudio/piper-voices/voices.json) on 17 Aug 2026.
   They are all about the same size — there is no small option. */
const NV_VOICES = [{id:'en_GB-jenny_dioco-medium', name:'Jenny · Standard narrator', mb:60, note:'Warm, clear and consistent across supported devices.'}];
const NV_DEFAULT = 'en_GB-jenny_dioco-medium';

const NV = {
  lib:null,          // the loaded module
  ready:false,       // a model is downloaded and usable
  busy:false,
  voiceId: localStorage.getItem('ple_nv_voice') || NV_DEFAULT,
  progress:0,
  error:'',
  cache:new Map(),   // sentence -> object URL, so Repeat is instant
};

const nvChosen = () => NV_VOICES.find(v => v.id === NV.voiceId) || NV_VOICES[0];

/* which engine is in use */
function nvMode(){
  /* ONE narrator for every device. Device TTS is never used for narration. */
  return 'natural';
}
function nvSetMode(m){
  localStorage.setItem('ple_engine', m);
  spStop();
  spBar();
  toast(m === 'natural' ? 'Using the natural voice' : 'Using the phone voice');
}

/* ---------- can this device run it at all? ---------- */
function nvCapable(){
  if(typeof WebAssembly === 'undefined') return 'This browser has no WebAssembly.';
  /* Low-memory devices may take longer, but must not silently change narrator. */
  return '';
}

/* ---------- load the engine (once) ---------- */
async function nvLoad(){
  if(NV.lib) return NV.lib;
  const why = nvCapable();
  if(why) throw new Error(why);
  NV.lib = await import(/* webpackIgnore: true */ NV_CDN);
  return NV.lib;
}

/* ---------- is the model already stored on this device? ---------- */
async function nvCheckStored(){
  try{
    const lib = await nvLoad();
    const have = await lib.stored();
    NV.ready = Array.isArray(have) && have.includes(NV.voiceId);
  }catch(e){ NV.ready = false; }
  return NV.ready;
}

/* ---------- the one-time download ---------- */
async function nvDownload(){
  if(NV.busy) return;
  NV.busy = true; NV.error = ''; NV.progress = 0; spSheet();
  try{
    const lib = await nvLoad();
    await lib.download(NV.voiceId, p => {
      if(p && p.total){
        NV.progress = Math.round(p.loaded * 100 / p.total);
        const el = document.getElementById('nvBar');
        if(el){ el.style.width = NV.progress + '%'; }
        const t = document.getElementById('nvPct');
        if(t) t.textContent = NV.progress + '%';
      }
    });
    NV.ready = true;
    localStorage.setItem('ple_engine', 'natural');
    toast('Natural voice ready \u2014 it now works offline');
  }catch(e){
    NV.error = (e && e.message) || 'The download did not finish.';
    NV.ready = false;
  }
  NV.busy = false;
  spSheet(); spBar();
}
async function nvRemove(){
  try{ const lib = await nvLoad(); await lib.remove(NV.voiceId); }catch(e){}
  NV.ready = false; NV.cache.clear();
  localStorage.setItem('ple_engine', 'device');
  toast('Natural voice removed'); spSheet(); spBar();
}
function nvPickVoice(id){
  NV.voiceId = id; localStorage.setItem('ple_nv_voice', id);
  NV.cache.clear();
  nvCheckStored().then(()=>{ spSheet(); spBar(); });
}

/* ---------- synthesis ---------- */
async function nvWav(text){
  if(NV.cache.has(text)) return NV.cache.get(text);
  const lib = await nvLoad();
  const blob = await lib.predict({text, voiceId: NV.voiceId});
  const url = URL.createObjectURL(blob);
  if(NV.cache.size > 40){                       // keep memory small
    const first = NV.cache.keys().next().value;
    URL.revokeObjectURL(NV.cache.get(first));
    NV.cache.delete(first);
  }
  NV.cache.set(text, url);
  return url;
}
/* generate the next sentence while this one plays, so there is no gap */
function nvPrefetch(i){
  const c = SP.chunks[i];
  if(!c || NV.cache.has(c.say)) return;
  nvWav(c.say).catch(()=>{});
}

let NV_AUDIO = null;
function nvSpeak(text){
  if(typeof afxMuted==='function'&&afxMuted())return;
  return new Promise((resolve, reject) => {
    nvWav(text).then(url => {
      if(!SP.on){ resolve(); return; }
      const a = new Audio(url);
      NV_AUDIO = a;
      a.volume = spVolume();
      a.playbackRate = spRate();
      if('preservesPitch' in a) a.preservesPitch = true;
      a.onended = () => { NV_AUDIO = null; resolve(); };
      a.onerror = () => { NV_AUDIO = null; reject(new Error('playback failed')); };
      a.play().catch(reject);
    }).catch(reject);
  });
}
function nvPause(){ if(NV_AUDIO) NV_AUDIO.pause(); }
function nvResume(){ if(NV_AUDIO) NV_AUDIO.play().catch(()=>{}); }
function nvStop(){
  if(NV_AUDIO){ NV_AUDIO.pause(); NV_AUDIO.currentTime = 0; NV_AUDIO = null; }
}

/* check on start-up whether the model is already there */
if(typeof window !== 'undefined'){
  setTimeout(() => { nvCheckStored().then(()=>{ if(state.screen === 'noteRead') spBar(); }); }, 400);
}

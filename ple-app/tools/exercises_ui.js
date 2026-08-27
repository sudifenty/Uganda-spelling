/* ============================================================
   WRITTEN EXERCISES — class → subject → topic → set → questions
   → submit → mark → review → retry.
   Every question is re-checked against the selected class,
   subject and topic before it is shown. Answers are never put
   on screen before the learner submits.
   ============================================================ */
const EX_SUBJECTS = [
  {id:'SST',  name:'Social Studies', label:'SST',     icon:'globe'},
  {id:'MATH', name:'Mathematics',    label:'Maths',   icon:'calc'},
  {id:'SCI',  name:'Science',        label:'Science', icon:'flask'},
  {id:'ENG',  name:'English',        label:'English', icon:'book'},
];

/* ---- saved progress (offline, on this device only) ---- */
const EX_KEY = 'ple_exercises_v1';
function exLoad(){
  try{ const d = JSON.parse(localStorage.getItem(EX_KEY));
       if(d && d.att && d.prog){ delete d.prog.__run; return d; } }catch(e){}
  return {att:[], prog:{}};
}
function exSave(d){ try{ localStorage.setItem(EX_KEY, JSON.stringify(d)); }catch(e){} }
let EXDB = exLoad();

/* ---- bank access, with a purity re-check ---- */
function exFor(cls, subj){
  const c = EXERCISE_BANK[cls]; if(!c) return null;
  const b = c[subj]; if(!b) return null;
  const topics = (b.topics||[]).filter(t =>
      t.questions.length && t.questions.every(q => q.class===cls && q.subject===subj
                                                && q.topic===t.title));
  return topics.length ? {class:cls, subject:subj, subject_name:b.subject_name,
                          topics, total:b.total, sets:b.sets} : null;
}
function exTopicById(cls, subj, tid){
  const b = exFor(cls, subj); if(!b) return null;
  return b.topics.find(t => t.topic_id===tid) || null;
}
function exQ(topic, qid){ return topic.questions.find(q => q.id===qid) || null; }

/* ---- topic progress ---- */
function exStats(tid){
  const p = EXDB.prog[tid];
  if(!p || !p.attempted) return null;
  const pct = Math.round(p.correct / p.attempted * 100);
  return {attempted:p.attempted, correct:p.correct, pct,
          band: pct>=75 ? 'good' : pct>=50 ? 'fair' : 'weak'};
}
const EX_BAND = {good:['Good','var(--green)'], fair:['Needs practice','var(--amber)'],
                 weak:['Needs work','var(--rose)']};

/* ---- marking ---- */
function exNorm(s){
  return String(s==null?'':s).toLowerCase()
    .replace(/[\u2018\u2019]/g,"'").replace(/[\u201c\u201d]/g,'"')
    .replace(/[\u2013\u2014\u2212]/g,'-')
    .replace(/[^a-z0-9.\-/'\u00b0 ]/g,' ')
    .replace(/\s+/g,' ').trim();
}
function exNums(s){
  const m = String(s).replace(/,/g,'').match(/-?\d+(?:\.\d+)?/g);
  return m ? m.map(Number) : [];
}
function exLev(a,b){
  if(a===b) return 0;
  const m=a.length, n=b.length;
  if(!m) return n; if(!n) return m;
  let prev=Array.from({length:n+1},(_,i)=>i), cur=new Array(n+1);
  for(let i=1;i<=m;i++){
    cur[0]=i;
    for(let j=1;j<=n;j++){
      cur[j]=Math.min(prev[j]+1, cur[j-1]+1, prev[j-1]+(a[i-1]===b[j-1]?0:1));
    }
    [prev,cur]=[cur,prev];
  }
  return prev[n];
}
function exNear(a,b){
  if(a===b) return true;
  const tol = Math.max(1, Math.floor(Math.min(a.length,b.length)/6));
  return exLev(a,b) <= tol;
}
/* strip a leading working-out line: "2/3 x 45 = 10 goats" -> also try "10 goats" */
function exTail(s){
  const parts = String(s).split(/=/);
  return parts.length>1 ? parts[parts.length-1].trim() : s;
}
/* mark one question. returns {marks, max, state, spelling} 
   state: 'right' | 'part' | 'wrong' | 'self' */
function exMark(q, given){
  const g = exNorm(given), max = q.marks;
  if(!g) return {marks:0, max, state:'wrong', spelling:false};

  if(q.kind==='open') return {marks:max, max, state:'right', spelling:false};

  if(q.kind==='auto'){
    const model = q.accepted[0]||'';
    const cands = [model, exTail(model)].map(exNorm).filter(Boolean);
    const mn = exNums(model), gn = exNums(given);
    /* numeric answers: every number in the model must appear in the answer */
    if(mn.length && mn.length<=3){
      const tail = exNums(exTail(model));
      const want = tail.length ? tail : mn;
      if(want.every(x => gn.includes(x))) return {marks:max,max,state:'right',spelling:false};
    }
    for(const c of cands){
      if(!c) continue;
      if(g===c) return {marks:max,max,state:'right',spelling:false};
      if(g.includes(c) || c.includes(g)) return {marks:max,max,state:'right',spelling:false};
      if(exNear(g,c)) return {marks:max,max,state:'right',spelling:true};
    }
    /* word overlap — most content words present counts as right with a spelling note */
    const cw = (exNorm(exTail(model))||'').split(' ').filter(w=>w.length>3);
    if(cw.length){
      const hit = cw.filter(w => g.includes(w) || g.split(' ').some(x=>exNear(x,w))).length;
      if(hit === cw.length) return {marks:max,max,state:'right',spelling:true};
      if(hit >= Math.ceil(cw.length*0.6)) return {marks:Math.max(1,Math.round(max/2)),max,state:'part',spelling:true};
    }
    return {marks:0,max,state:'wrong',spelling:false};
  }

  if(q.kind==='list'){
    let hit=0, fuzzy=false;
    const gws = g.split(' ');
    for(const alt of q.accepted){
      const key = exNorm(alt).split(' ').filter(w=>w.length>3);
      if(!key.length) continue;
      const found = key.filter(w => g.includes(w) || gws.some(x=>exNear(x,w))).length;
      if(found >= Math.ceil(key.length*0.6)){ hit++; if(!g.includes(key[0])) fuzzy=true; }
    }
    const marks = Math.min(hit, max);
    return {marks, max, spelling:fuzzy,
            state: marks>=max ? 'right' : marks>0 ? 'part' : 'wrong'};
  }
  return {marks:0, max, state:'self', spelling:false};
}

/* ---- building a run ---- */
/* Fisher-Yates — an even shuffle. sort(()=>Math.random()-0.5) is not even. */
function exShuffle(a){
  const x = a.slice();
  for(let i=x.length-1;i>0;i--){
    const j = Math.floor(Math.random()*(i+1));
    [x[i],x[j]] = [x[j],x[i]];
  }
  return x;
}
/* Every run is built fresh and shuffled. Nothing is ever resumed: if the
   learner leaves an exercise and comes back, they get a new shuffle and
   start again at question 1. */
function exStart(cls, subj, tid, setId, mode){
  const t = exTopicById(cls, subj, tid); if(!t) return;
  let qids;
  if(mode==='random'){
    qids = exShuffle(t.questions.map(q=>q.id)).slice(0, Math.min(10, t.questions.length));
  }else{
    const s = t.sets.find(x=>x.id===setId); if(!s) return;
    qids = exShuffle(s.qids);
  }
  state.exRun = {cls, subj, tid, setId: mode==='random'?null:setId, mode,
                 qids, given:{}, i:0, done:false, result:null,
                 title: t.title,
                 setName: mode==='random' ? 'Random Practice'
                          : (t.sets.find(x=>x.id===setId)||{}).name};
  go('exDo');
}
/* leaving an exercise throws the attempt away on purpose */
function exLeave(){
  state.exRun = null;
  go('exTopic', false);
}
function exWrite(qid, v){
  if(!state.exRun) return;
  state.exRun.given[qid] = v;
}
function exSubmit(){
  const r = state.exRun; if(!r) return;
  const t = exTopicById(r.cls, r.subj, r.tid); if(!t) return;
  const rows = r.qids.map(id => {
    const q = exQ(t, id); if(!q) return null;
    const m = exMark(q, r.given[id]||'');
    return {id, q, given:(r.given[id]||'').trim(), ...m, self:null};
  }).filter(Boolean);
  r.result = rows; r.done = true;
  go('exResult');
}
/* learner self-marks a prose answer */
function exSelf(qid, verdict){
  const r = state.exRun; if(!r||!r.result) return;
  const row = r.result.find(x=>x.id===qid); if(!row) return;
  row.self = verdict;
  row.marks = verdict==='right' ? row.max : verdict==='part' ? Math.max(1,Math.round(row.max/2)) : 0;
  row.state = verdict;
  render();
}
function exFinish(){
  const r = state.exRun; if(!r||!r.result) return;
  const got = r.result.reduce((s,x)=>s+x.marks,0);
  const max = r.result.reduce((s,x)=>s+x.max,0);
  const right = r.result.filter(x=>x.state==='right').length;
  const p = EXDB.prog[r.tid] || {attempted:0, correct:0};
  p.attempted += r.result.length; p.correct += right;
  EXDB.prog[r.tid] = p;
  EXDB.att.unshift({cls:r.cls, subj:r.subj, tid:r.tid, topic:r.title,
                    set:r.setName, n:r.result.length, right,
                    wrong:r.result.length-right, got, max,
                    pct: max? Math.round(got/max*100):0,
                    when: new Date().toISOString().slice(0,10)});
  EXDB.att = EXDB.att.slice(0,60);
  exSave(EXDB);
  toast(`Saved — ${got} of ${max} marks`);
  go('exTopic', false);
}
function exRetry(){
  const r = state.exRun; if(!r) return;
  exStart(r.cls, r.subj, r.tid, null, 'random');
}
function exReviewWrong(){
  const r = state.exRun; if(!r||!r.result) return;
  const bad = r.result.filter(x=>x.state!=='right').map(x=>x.id);
  if(!bad.length){ toast('Nothing wrong to review — well done!'); return; }
  state.exRun = {...r, qids:bad, given:{}, i:0, done:false, result:null,
                 setName:'Review my mistakes', mode:'review'};
  go('exDo');
}

/* ---- navigation helpers ---- */
function setExClass(c){if(!checkClassAccess(c))return;state.klass=c;state.exTid=null;go('exercises',false);}
function setExSubject(id){ state.exsubject=id; state.exTid=null; go('exercises',false); }
function openExTopic(tid){ state.exTid=tid; go('exTopic'); }
function exGoQ(i){ if(state.exRun){ state.exRun.i=i; render(); } }
function exMove(d){
  const r=state.exRun; if(!r) return;
  const n=r.i+d; if(n<0||n>=r.qids.length) return;
  r.i=n; render();
  const v=document.getElementById('views'); if(v) v.scrollTop=0; window.scrollTo(0,0);
}

/* ---- Screen: class + subject + topic list ---- */
SCREENS.exercises = () => {
  const cls = state.klass, subj = state.exsubject;
  const bank = exFor(cls, subj);
  const meta = EX_SUBJECTS.find(s=>s.id===subj);
  const head = `
  <header class="pagehead">
    <span class="logo">${ART.books(34)}</span>
    <div><h2>Written Exercises</h2>
      <div class="sub">${cls} · ${meta.name} · answers stay hidden until you submit</div></div>
  </header>
  <div class="chips">${classOptions().map(c=>`
    <button class="chip ${c.id===cls?'on':''}" onclick="setExClass('${c.id}')">${c.id}</button>`).join('')}</div>
  <div class="chips">${EX_SUBJECTS.map(s=>`
    <button class="chip ${s.id===subj?'on':''}" onclick="setExSubject('${s.id}')">${s.label}</button>`).join('')}</div>`;

  if(!bank) return head + `
    <div class="card" style="text-align:center;padding:26px 18px">
      <div style="font-size:34px">📝</div>
      <h3 style="margin-top:8px">No exercises yet</h3>
      <p class="muted" style="margin-top:8px">
        There are no ${meta.name} written exercises for ${cls} in the app yet.
        Exercises are built from the topic notes, so they appear as soon as the
        notes for ${cls} ${meta.name} are written.</p>
    </div>
    <div class="hint-strip">${I.info(18)} <span>Nothing has been guessed. Only topics taken from the NCDC curriculum are listed here.</span></div>`;

  return head + `
  <div class="ex-sum">
    <div><b>${bank.topics.length}</b><span>topics</span></div>
    <div><b>${bank.sets}</b><span>exercise sets</span></div>
    <div><b>${bank.total}</b><span>questions</span></div>
  </div>
  <div class="section-title">Choose a topic</div>
  <div class="rows">
    ${bank.topics.map(t=>{
      const st = exStats(t.topic_id);
      const badge = st ? `<span class="ex-band" style="background:${EX_BAND[st.band][1]}">${st.pct}%</span>` : '';
      return `<button class="sec-btn" onclick="openExTopic('${t.topic_id}')">
        <span class="dot">${t.topic_no}</span>
        <span style="flex:1">${nEsc(t.title)}
          <span class="ex-meta">${t.sets.length} sets · ${t.total} questions${st?` · ${EX_BAND[st.band][0]}`:''}</span>
        </span>${badge}${I.chev(17)}
      </button>`;}).join('')}
  </div>
  <div class="spacer"></div>
  <button class="btn btn-soft" onclick="go('exMine')">${I.chart? I.chart(18):I.info(18)} My exercises</button>`;
};

/* ---- Screen: one topic — its sets ---- */
SCREENS.exTopic = () => {
  const cls=state.klass, subj=state.exsubject;
  const t = exTopicById(cls, subj, state.exTid);
  if(!t) return SCREENS.exercises();
  const st = exStats(t.topic_id);
  const meta = EX_SUBJECTS.find(s=>s.id===subj);
  return `
  <header class="pagehead">
    <button class="back" onclick="go('exercises')" aria-label="Go back">${I.back(22)}</button>
    <div><h2 style="font-size:18px">${nEsc(t.title)}</h2>
      <div class="sub">${cls} ${meta.name} · Topic ${t.topic_no}</div></div>
  </header>
  <div class="card" style="background:var(--sky-50);border-color:var(--sky-100)">
    <div class="muted">${t.total} questions · ${t.marks} marks · ${t.sets.length} sets</div>
    ${st ? `<div style="margin-top:10px">
        <div class="bar"><i style="width:0;background:${EX_BAND[st.band][1]}" data-grow="${st.pct}%"></i></div>
        <div class="muted" style="margin-top:7px">Attempted ${st.attempted} · correct ${st.correct} · ${st.pct}% — <b>${EX_BAND[st.band][0]}</b></div>
      </div>` : `<div class="muted" style="margin-top:8px">Not attempted yet.</div>`}
  </div>
  <div class="section-title">Exercise sets</div>
  <div class="rows">
    ${t.sets.map((s,i)=>`
      <button class="sec-btn" onclick="exStart('${cls}','${subj}','${t.topic_id}','${s.id}','set')">
        <span class="dot">${i+1}</span>
        <span style="flex:1">${s.name}<span class="ex-meta">${s.qids.length} questions · ${s.marks} marks</span></span>
        ${I.chev(17)}</button>`).join('')}
    <button class="sec-btn" onclick="exStart('${cls}','${subj}','${t.topic_id}',null,'random')">
      <span class="dot">↻</span>
      <span style="flex:1">Random Practice<span class="ex-meta">A shuffled set from this topic only</span></span>
      ${I.chev(17)}</button>
  </div>
  <div class="spacer"></div>
  <div class="hint-strip">${I.info(18)} <span>Every question here comes from <b>${nEsc(t.title)}</b> only — no other topic, subject or class is mixed in.</span></div>
  <div class="hint-strip">${I.shuffle(18)} <span><b>The questions are shuffled every time.</b> Open a set again and they come in a new order. If you leave before submitting, the exercise starts again from question 1 — your place is not saved.</span></div>`;
};

/* ---- Screen: answering ---- */
SCREENS.exDo = () => {
  const r = state.exRun;
  if(!r) return SCREENS.exercises();
  const t = exTopicById(r.cls, r.subj, r.tid);
  if(!t) return SCREENS.exercises();
  const q = exQ(t, r.qids[r.i]);
  if(!q) return SCREENS.exercises();
  const val = (r.given[q.id]||'').replace(/</g,'&lt;');
  const big = q.working || q.kind==='self' || q.kind==='list';
  const answered = r.qids.filter(id=>(r.given[id]||'').trim()).length;
  return `
  <header class="pagehead">
    <button class="back" onclick="exLeave()" aria-label="Leave this exercise">${I.back(22)}</button>
    <div><h2 style="font-size:17px">${nEsc(t.title)}</h2>
      <div class="sub">${r.setName} · question ${r.i+1} of ${r.qids.length}</div></div>
  </header>
  <div class="bar" style="margin-bottom:6px">
    <i style="width:0;background:var(--sky)" data-grow="${Math.round((r.i+1)/r.qids.length*100)}%"></i></div>
  <div class="muted" style="margin-bottom:12px">${answered} of ${r.qids.length} answered · ${q.marks} mark${q.marks>1?'s':''}</div>
  <div class="ex-qcard">
    <div class="ex-qno">Question ${r.i+1}</div>
    <div class="ex-qtext">${nMd(q.q)}</div>
  </div>
  ${q.working ? `<label class="ex-lab">Working</label>
    <textarea class="ex-area ex-work" id="exW" placeholder="Show your working here"
      oninput="exWrite('${q.id}__w', this.value)">${(r.given[q.id+'__w']||'').replace(/</g,'&lt;')}</textarea>` : ''}
  <label class="ex-lab">${q.working?'Final answer':'Answer'}</label>
  <textarea class="ex-area ${big&&!q.working?'ex-big':''}" id="exA"
    placeholder="Write your answer here"
    oninput="exWrite('${q.id}', this.value)">${val}</textarea>
  <div class="ex-grid">
    ${r.qids.map((id,i)=>`<button class="ex-dot ${i===r.i?'on':''} ${(r.given[id]||'').trim()?'fill':''}"
        onclick="exGoQ(${i})">${i+1}</button>`).join('')}
  </div>
  <div class="nt-foot">
    <button class="btn btn-ghost" ${r.i===0?'disabled style="opacity:.45"':''} onclick="exMove(-1)">Back</button>
    ${r.i===r.qids.length-1
      ? `<button class="btn btn-green" onclick="exSubmit()">${I.check(19)} SUBMIT</button>`
      : `<button class="btn btn-primary" onclick="exMove(1)">NEXT ${I.chev(18)}</button>`}
  </div>
  <div class="spacer"></div>
  <button class="btn btn-soft" onclick="exSubmit()">Submit now and mark what I have done</button>
  <div class="hint-strip" style="margin-top:12px">${I.shuffle(18)} <span>If you leave now, this exercise is not saved — you will get a freshly shuffled set next time.</span></div>`;
};

/* ---- Screen: results ---- */
SCREENS.exResult = () => {
  const r = state.exRun;
  if(!r || !r.result) return SCREENS.exercises();
  const got = r.result.reduce((s,x)=>s+x.marks,0);
  const max = r.result.reduce((s,x)=>s+x.max,0);
  const pct = max ? Math.round(got/max*100) : 0;
  const right = r.result.filter(x=>x.state==='right').length;
  const part  = r.result.filter(x=>x.state==='part').length;
  const wrong = r.result.filter(x=>x.state==='wrong').length;
  const pend  = r.result.filter(x=>x.state==='self').length;
  const hue = pct>=75?'green':pct>=50?'amber':'rose';
  return `
  <header class="pagehead">
    <div><h2>Results</h2><div class="sub">${nEsc(r.title)} · ${r.setName}</div></div>
  </header>
  <div class="card" style="text-align:center;background:var(--${hue}-50);border-color:var(--${hue}-100)">
    <div style="font-size:40px;font-weight:900;color:var(--${hue})">${pct}%</div>
    <div class="muted" style="margin-top:4px"><b>${got}</b> of <b>${max}</b> marks</div>
    <div class="ex-tally">
      <span class="t-right">${right} right</span>
      <span class="t-part">${part} partly</span>
      <span class="t-wrong">${wrong} wrong</span>
      ${pend?`<span class="t-self">${pend} to mark</span>`:''}
    </div>
  </div>
  ${pend?`<div class="hint-strip">${I.info(18)} <span>Some answers are written in your own words, so the app cannot mark them fairly. Compare yours with the answer given and tap how you did.</span></div>`:''}
  ${r.result.map((x,i)=>{
    const cls = x.state==='right'?'ok':x.state==='part'?'pt':x.state==='self'?'sf':'no';
    const badge = x.state==='right'?'✓ right':x.state==='part'?'~ partly':x.state==='self'?'mark this one':'✗ wrong';
    return `<div class="ex-res ${cls}">
      <div class="ex-res-h"><b>Question ${i+1}</b><span>${badge} · ${x.marks}/${x.max}</span></div>
      <div class="ex-qtext">${nMd(x.q.q)}</div>
      <div class="ex-lab2">Your answer</div>
      <div class="ex-given">${x.given ? nEsc(x.given) : '<i>left blank</i>'}</div>
      ${x.spelling && x.given ? `<div class="ex-spell">Spelling: the expected wording is <b>${nEsc(x.q.a)}</b> — the mark was still given.</div>` : ''}
      <div class="ex-lab2">Answer</div>
      <div class="ex-model">${nMd(x.q.a)}</div>
      ${x.state==='self' || x.self ? `<div class="ex-self">
        <button class="ex-sb r ${x.self==='right'?'on':''}" onclick="exSelf('${x.id}','right')">I got it right</button>
        <button class="ex-sb p ${x.self==='part'?'on':''}" onclick="exSelf('${x.id}','part')">Partly</button>
        <button class="ex-sb w ${x.self==='wrong'?'on':''}" onclick="exSelf('${x.id}','wrong')">Not right</button>
      </div>` : ''}
    </div>`;}).join('')}
  <div class="nt-foot">
    <button class="btn btn-ghost" onclick="exReviewWrong()">Review my mistakes</button>
    <button class="btn btn-primary" onclick="exRetry()">Try again</button>
  </div>
  <div class="spacer"></div>
  <button class="btn btn-green" onclick="exFinish()">${I.check(19)} Save and finish</button>`;
};

/* ---- Screen: my exercises ---- */
SCREENS.exMine = () => {
  const a = EXDB.att;
  return `
  <header class="pagehead">
    <button class="back" onclick="go('exercises')" aria-label="Go back">${I.back(22)}</button>
    <div><h2>My exercises</h2><div class="sub">Saved on this device only</div></div>
  </header>
  ${!a.length ? `<div class="card" style="text-align:center;padding:24px">
      <div style="font-size:32px">📄</div>
      <p class="muted" style="margin-top:8px">You have not finished any exercise yet.</p></div>`
    : `<div class="nt-tablewrap"><table class="nt-table">
      <thead><tr><th>Date</th><th>Topic</th><th>Set</th><th>Marks</th><th>Score</th></tr></thead>
      <tbody>${a.map(x=>`<tr>
        <td>${x.when}</td><td>${nEsc(x.cls)} ${nEsc(x.topic)}</td><td>${nEsc(x.set||'')}</td>
        <td>${x.got}/${x.max}</td><td><b>${x.pct}%</b></td></tr>`).join('')}
      </tbody></table></div>`}
  <div class="spacer"></div>
  <div class="hint-strip">${I.info(18)} <span>This history is stored in your browser on this device. It is not sent anywhere.</span></div>`;
};

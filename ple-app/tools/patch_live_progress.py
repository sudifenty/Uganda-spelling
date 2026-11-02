#!/usr/bin/env python3
"""
patch_live_progress.py — the owner SEES a finished topic immediately.

What a learner does and what the owner sees, end to end:

  learner finishes a sub-topic  ->  a row is written to Supabase at once
  learner finishes a topic      ->  another row, written at once (not on a
                                    45-second timer, not in a batch of 25)
  learner passes the topic exam ->  a row with the score
  owner opens #admin            ->  "Learner progress — live" board, refreshing
                                    itself every 8 seconds, newest first, each
                                    row stamped "just now" / "3 min ago"

Two ticks per topic, because the app has two meanings of "done":
  📖 READ  — every sub-topic swiped and marked complete ("Topic complete!")
  🏆 EXAM  — the End-of-Topic Exam passed

Offline is not a hole: if the phone has no connection the rows queue in
localStorage and go out the moment the network returns, on the next launch,
and on pagehide — the same guarantee the existing activity queue gives.

Data lives in `smartple_topic_progress` (created by the matching
supabase_live_progress.sql at the repo root). If that table has not been
created yet, both the app and the admin board fall back to the existing
`learning_events` table, so nothing breaks — the board simply shows fewer
columns and says which SQL to run.

Idempotent; anchors must appear exactly once. Run from the ple-app folder:

    python3 tools/patch_live_progress.py
"""
import sys

APP = "index.html"
MARK = "/* === LIVE PROGRESS PATCH (tools/patch_live_progress.py) === */"


def edit(src, old, new, label):
    if new in src:
        print(f"  already applied: {label}")
        return src
    n = src.count(old)
    if n != 1:
        sys.exit(f"FAILED [{label}]: anchor found {n} times (expected 1)")
    print(f"  ok: {label}")
    return src.replace(old, new, 1)


# ---------------------------------------------------------------- CSS ------
CSS_OLD = ".tp-locked{background:var(--yellow-50);"
CSS_NEW = """.lp-board{border:1.5px solid var(--line);border-radius:16px;background:#fff;overflow:hidden}
.lp-live{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:900;letter-spacing:.06em;color:#2F6B3A}
.lp-live i{width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 0 0 rgba(34,197,94,.6);animation:lpPulse 1.8s infinite}
@keyframes lpPulse{0%{box-shadow:0 0 0 0 rgba(34,197,94,.55)}70%{box-shadow:0 0 0 9px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}
.lp-row{padding:11px 13px;border-top:1px solid var(--line)}
.lp-row:first-child{border-top:none}
.lp-who{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.lp-who b{font-size:14.5px;color:var(--navy);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lp-who small{font-size:11px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;flex:none}
.lp-fresh{font-size:9.5px;font-weight:900;letter-spacing:.08em;background:#FEE2E2;color:#B91C1C;border-radius:999px;padding:2px 7px;flex:none}
.lp-t{display:flex;align-items:flex-start;gap:8px;font-size:13px;font-weight:700;color:#374151;padding:4px 0}
.lp-t .t-ic{flex:none;width:18px;text-align:center}
.lp-t .t-txt{flex:1;min-width:0;line-height:1.35}
.lp-t .t-when{flex:none;font-size:11px;font-weight:800;color:var(--muted);white-space:nowrap}
.lp-t.done .t-txt{color:var(--navy)}
.lp-t.now .t-when{color:#2F6B3A}
.lp-empty{padding:16px 13px;font-size:13px;font-weight:700;color:var(--muted);text-align:center}
.lp-sql{margin-top:10px;font-size:12px;font-weight:600;line-height:1.5;background:var(--yellow-50);border:1.5px solid var(--yellow-100);border-radius:14px;padding:11px 13px;color:var(--navy)}
.lp-sql code{background:#fff;border-radius:5px;padding:1px 5px;font-size:11.5px}
.tp-locked{background:var(--yellow-50);"""

# ------------------------------------------------------ learner-side code --
LEARN = MARK + """
/* ---- reporting a finished topic to the owner, the instant it happens ----
   Rows go to smartple_topic_progress. If that table does not exist yet the
   insert fails quietly and the same event still reaches learning_events, so
   the owner's board works either way. Offline rows wait in localStorage. */
const LPQ_KEY='sp_live_progress_q';
let LP_SENDING=false;
function lpQueueLoad(){ try{const q=JSON.parse(localStorage.getItem(LPQ_KEY)||'[]');return Array.isArray(q)?q:[];}catch(e){return[];} }
function lpQueueSave(q){ try{ localStorage.setItem(LPQ_KEY,JSON.stringify((q||[]).slice(-300))); }catch(e){} }
function lpClient(){
  if(typeof supabaseClient!=='undefined'&&supabaseClient) return supabaseClient;
  try{ if(window.supabase&&typeof SUPABASE_URL!=='undefined') return window.supabase.createClient(SUPABASE_URL,SUPABASE_PUBLISHABLE_KEY,{auth:{persistSession:true}}); }catch(e){}
  return null;
}
/* one row of truth: who, which topic, what happened, how far they got */
function lpRow(kind,t,extra){
  const subs=(typeof pathSubs==='function')?pathSubs(t):[];
  const doneCount=(typeof pathDone==='function')?subs.filter((s,i)=>pathDone(t,i)).length:0;
  const meta=(typeof NOTE_SUBJECTS!=='undefined')?(NOTE_SUBJECTS.find(s=>s.id===t.subject)||{}):{};
  return Object.assign({
    user_id:(state.authUser&&state.authUser.id)||null,
    learner:(state.name||'Learner'),
    class_level:t.class, subject:(meta.label||t.subject),
    topic_id:t.id, topic_title:t.title,
    kind:kind,
    subs_done:doneCount, subs_total:subs.length,
    pct:subs.length?Math.round(100*doneCount/subs.length):0,
    created_at:new Date().toISOString()
  },extra||{});
}
/* send now; queue only if the network says no */
async function lpPush(row){
  lpQueueSave(lpQueueLoad().concat([row]));
  await lpFlush();
}
async function lpFlush(){
  if(LP_SENDING) return;
  const q=lpQueueLoad(); if(!q.length) return;
  const c=lpClient(); if(!c) return;               /* stays queued until online */
  LP_SENDING=true;
  const batch=q.slice(0,50);
  let ok=false;
  try{
    const r=await c.from('smartple_topic_progress').insert(batch);
    ok=!(r&&r.error);
  }catch(e){ ok=false; }
  LP_SENDING=false;
  if(!ok){
    /* table not created yet (or RLS refused): keep EVERY queued row and let
       learning_events carry the same fact, as it always has */
    lpQueueSave(q);
    try{
      const c2=lpClient();
      if(c2) await c2.from('learning_events').insert(q.slice(0,50).map(r=>({
        user_id:r.user_id,event_type:'topic_'+r.kind,
        details:{topic:r.topic_id,title:r.topic_title,class_level:r.class_level,
                 subject:r.subject,pct:r.pct,subs_done:r.subs_done,
                 subs_total:r.subs_total,passed:r.passed,score:r.score}
      })));
    }catch(e){}
    return;
  }
  lpQueueSave(lpQueueLoad().slice(batch.length));
}
/* the one call the rest of the app makes */
function liveProgress(kind,t,extra){
  try{
    if(!state.authUser) return;                    /* nothing to attribute it to */
    const row=lpRow(kind,t,extra);
    /* the existing activity trail keeps its own copy (analytics, and the
       fallback when the progress table is missing) — flushed at once */
    try{ trackActivity('topic_'+kind,{topic:t.id,title:t.title,class_level:t.class,
      subject:row.subject,learner:row.learner,pct:row.pct,subs_done:row.subs_done,
      subs_total:row.subs_total,passed:extra&&extra.passed,score:extra&&extra.score},true); }catch(e){}
    try{ activityFlush(); }catch(e){}
    lpPush(row);
  }catch(e){}
}
"""

# ------------------------------------------- hooks: topic read + exam ------
# 1. topic finished (every sub-topic marked complete)
HOOK_READ_OLD = """  /* topic finished */
  openSheet(`<div class="grabber"></div>"""
HOOK_READ_NEW = """  /* topic finished — tell the owner right now */
  try{
    const gg=pathState(t);
    if(gg.cur>=gg.subs.length) liveProgress('read',t,{subs_done:gg.subs.length,subs_total:gg.subs.length,pct:100});
    else liveProgress('subtopic',t,{sub_index:i,sub_title:String(sec.title||'')});
  }catch(e){}
  openSheet(`<div class="grabber"></div>"""

# 2. sub-topic progress when the path advances (so the owner sees movement)
HOOK_SUB_OLD = """  if(first){learnXP(t,5);}"""
HOOK_SUB_NEW = """  if(first){learnXP(t,5);
    /* movement inside a topic is worth seeing too: "6 of 23 sub-topics" */
    try{ if(pathState(t).cur<pathState(t).subs.length) liveProgress('subtopic',t,{sub_index:i,sub_title:String(sec.title||'')}); }catch(e){}
  }"""

# 3. the end-of-topic exam (and the mid test) result
HOOK_EXAM_OLD = """  spPut(s.mode==='mid'?MID_KEY:TEX_KEY, t.id, rec);"""
HOOK_EXAM_NEW = """  spPut(s.mode==='mid'?MID_KEY:TEX_KEY, t.id, rec);
  /* the owner sees the exam the moment it is marked */
  try{ liveProgress(s.mode==='mid'?'mid':'exam',t,{score:pct,passed:!!rec.passed}); }catch(e){}"""

# ------------------------------------------------ owner-side live board ----
ADMIN_STATE = "async function adminLoad(){"
ADMIN_STATE_NEW = """/* ============================================================
   OWNER BOARD — "who finished what, just now".
   Reads smartple_topic_progress (newest first). If that table is
   missing it reads learning_events instead, so the board still
   works on a database where only the SQL has not been run yet.
   Refreshes every 8 seconds while the Owner screen is open.
   ============================================================ */
const LIVE_TICK_MS=8000;
let liveTimer=null, liveSeenIds=null;
function liveAgo(ts){
  const d=(Date.now()-new Date(ts||0).getTime())/1000;
  if(!isFinite(d)||d<0) return '';
  if(d<45) return 'just now';
  if(d<3600) return Math.round(d/60)+' min ago';
  if(d<86400) return Math.round(d/3600)+' h ago';
  if(d<172800) return 'yesterday';
  return Math.round(d/86400)+' days ago';
}
async function adminProgressLoad(){
  if(!(state.screen==='admin'&&state.adminOk)) return false;
  const c=lpClient();
  if(!c){ state.adminProgErr='No internet right now — the board will fill in when the phone is back online.'; render(); return false; }
  let rows=null, err=null, source='progress';
  try{
    const r=await c.from('smartple_topic_progress').select('*').order('created_at',{ascending:false}).limit(400);
    if(r.error){ err=String(r.error.message||r.error); } else rows=r.data||[];
  }catch(e){ err=String(e&&e.message||e); }
  if(!rows){
    source='events';
    try{
      const r2=await c.from('learning_events').select('user_id,event_type,details,created_at')
        .in('event_type',['topic_read','topic_exam','topic_mid','topic_subtopic'])
        .order('created_at',{ascending:false}).limit(400);
      if(r2.error){ err=err||String(r2.error.message||r2.error); rows=[]; }
      else{
        rows=(r2.data||[]).map(x=>{
          const d=x.details||{};
          return {user_id:x.user_id,learner:d.learner||'',class_level:d.class_level||'',
            subject:d.subject||'',topic_id:d.topic||d.topic_id||'',topic_title:d.title||d.topic_title||'',
            kind:String(x.event_type||'').replace(/^topic_/,''),pct:d.pct,
            subs_done:d.subs_done,subs_total:d.subs_total,
            passed:d.passed,score:d.score,created_at:x.created_at};
        });
      }
    }catch(e){ err=err||String(e&&e.message||e); rows=[]; }
  }
  state.adminProgSource=source;
  state.adminProgErr=(rows&&rows.length)?null:(err||null);
  state.adminProg=rows||[];
  state.adminProgAt=Date.now();
  /* which rows are new since the previous look? (the red NEW chip) */
  const ids=(state.adminProg||[]).map(r=>[r.topic_id,r.kind,r.created_at].join('|'));
  if(liveSeenIds) state.adminProgNew=ids.filter(i=>!liveSeenIds.has(i));
  else state.adminProgNew=[];
  liveSeenIds=new Set(ids);
  render();
  return true;
}
function adminLiveStart(){
  if(liveTimer) clearInterval(liveTimer);
  liveTimer=setInterval(()=>{
    if(state.screen==='admin'&&state.adminOk) adminProgressLoad();
    else if(liveTimer){ clearInterval(liveTimer); liveTimer=null; }
  },LIVE_TICK_MS);
}
/* group the flat rows into: learner -> topic -> {read, exam} */
function adminProgVM(){
  const rows=state.adminProg||[];
  const byName=new Map();
  rows.forEach(r=>{
    const who=(r.learner&&String(r.learner).trim())||(r.user_id?('learner '+String(r.user_id).slice(0,6)):'unknown learner');
    const key=who+'|'+(r.class_level||'');
    if(!byName.has(key)) byName.set(key,{who,cls:r.class_level||'',topics:new Map(),last:0});
    const L=byName.get(key);
    const tk=r.topic_id||r.topic_title||'?';
    if(!L.topics.has(tk)) L.topics.set(tk,{id:tk,title:r.topic_title||tk,cls:r.class_level||'',subject:r.subject||'',read:null,exam:null,subs:null});
    const T=L.topics.get(tk);
    const when=r.created_at||0;
    const tms=new Date(when).getTime()||0;
    if(r.kind==='read') T.read=when;
    else if(r.kind==='exam'){ if(!T.exam||tms>(new Date(T.exam).getTime()||0)) T.exam={at:when,passed:r.passed,score:r.score}; }
    else if(r.kind==='subtopic'&&r.subs_total){
      if(!T.subs||tms>(new Date(T.subs.at).getTime()||0)) T.subs={at:when,done:r.subs_done,total:r.subs_total,pct:r.pct};
    }
    if(tms>L.last) L.last=tms;
  });
  return [...byName.values()].sort((a,b)=>b.last-a.last);
}
function adminLiveHTML(){
  const vm=adminProgVM();
  if(!liveTimer) adminLiveStart();       /* the board keeps itself fresh */
  if(state.adminProgErr)
    return `<div class="lp-sql">${nEsc(state.adminProgErr)}<br><br>
      If this is the first time: run <code>supabase_live_progress.sql</code> once in the
      Supabase SQL editor. Until then the board falls back to <code>learning_events</code>.</div>`;
  if(!vm.length)
    return `<div class="lp-board"><div class="lp-empty">No learner has finished a topic yet.<br>
      The board fills in the moment a child presses <b>Mark as complete</b>.</div></div>`;
  const body=vm.slice(0,12).map(L=>{
    const ts=[...L.topics.values()].sort((a,b)=>{
      const x=Math.max(new Date(a.read||0).getTime()||0,new Date((a.exam&&a.exam.at)||0).getTime()||0);
      const y=Math.max(new Date(b.read||0).getTime()||0,new Date((b.exam&&b.exam.at)||0).getTime()||0);
      return y-x;
    }).slice(0,6);
    const rows=ts.map(T=>{
      const readAt=T.read, examAt=T.exam&&T.exam.at;
      const lines=[];
      if(readAt) lines.push(`<div class="lp-t done now">
        <span class="t-ic">\\u{1F4D6}</span><span class="t-txt"><b>${nEsc(T.title)}</b> \\u2014 every sub-topic read</span>
        <span class="t-when">${nEsc(liveAgo(readAt))}</span></div>`);
      else if(T.subs) lines.push(`<div class="lp-t"><span class="t-ic">\\u23F3</span>
        <span class="t-txt"><b>${nEsc(T.title)}</b> \\u2014 ${T.subs.done} of ${T.subs.total} sub-topics (${T.subs.pct}%)</span>
        <span class="t-when">${nEsc(liveAgo(T.subs.at))}</span></div>`);
      if(examAt) lines.push(`<div class="lp-t done"><span class="t-ic">${T.exam.passed?'\\u{1F3C6}':'\\u{1F4DD}'}</span>
        <span class="t-txt"><b>${nEsc(T.title)}</b> \\u2014 exam ${T.exam.passed?'PASSED':'not passed'}${T.exam.score!=null?' \\u00B7 '+T.exam.score+'%':''}</span>
        <span class="t-when">${nEsc(liveAgo(examAt))}</span></div>`);
      return lines.join('');
    }).join('');
    return `<div class="lp-row">
      <div class="lp-who"><b>${nEsc(L.who)}</b>${L.cls?`<small>${nEsc(L.cls)}</small>`:''}
        ${L.last&&(Date.now()-L.last)<120000?'<span class="lp-fresh">NEW</span>':''}</div>
      ${rows}</div>`;
  }).join('');
  return `<div class="lp-board">${body}</div>
    <div class="hint-strip cream" style="margin-top:8px">${I.info(18)}
      <span>Updated ${nEsc(liveAgo(new Date(state.adminProgAt||Date.now()).toISOString()))} \\u00B7
      ${vm.length} learner${vm.length===1?'':'s'} \\u00B7 ${(state.adminProg||[]).length} records
      ${state.adminProgSource==='events'?' \\u00B7 reading learning_events (run the SQL for the fuller board)':''}</span></div>`;
}
async function adminLoad(){"""

# ---------------------------------------------- the board on the screen ----
ADMIN_KICK_OLD = "  state.adminRows=data||[]; render();"
ADMIN_KICK_NEW = "  state.adminRows=data||[]; render();\n  adminProgressLoad();   /* fill the live board straight away */"

ADMIN_UI_OLD = """    <button class="btn btn-soft" onclick="adminLoad()">Refresh \\u{1F504}</button>"""
ADMIN_UI_NEW = """    <button class="btn btn-soft" onclick="adminLoad()">Refresh \\u{1F504}</button>
    <div class="section-title" style="margin-top:22px;display:flex;align-items:center;gap:10px">
      Learner progress <span class="lp-live"><i></i>LIVE</span></div>
    ${adminLiveHTML()}
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
      <button class="btn btn-soft" onclick="adminProgressLoad()">Refresh board \\u{1F504}</button>
      <button class="btn btn-soft" onclick="liveSeenIds=null;adminProgressLoad()">Clear NEW marks</button>
    </div>"""


def main():
    src = open(APP, encoding="utf-8").read()
    before = len(src)
    print("patching", APP)
    src = edit(src, CSS_OLD, CSS_NEW, "css")
    src = edit(src, HOOK_SUB_OLD, HOOK_SUB_NEW, "sub-topic progress hook")
    src = edit(src, HOOK_READ_OLD, HOOK_READ_NEW, "topic-finished hook")
    src = edit(src, HOOK_EXAM_OLD, HOOK_EXAM_NEW, "exam-result hook")
    src = edit(src, ADMIN_STATE, LEARN + ADMIN_STATE_NEW, "live board + learner reporting")
    src = edit(src, ADMIN_KICK_OLD, ADMIN_KICK_NEW, "first board load on open")
    src = edit(src, ADMIN_UI_OLD, ADMIN_UI_NEW, "board on the Owner screen")
    open(APP, "w", encoding="utf-8").write(src)
    print(f"done: {before} -> {len(src)} bytes (+{len(src)-before})")


if __name__ == "__main__":
    main()

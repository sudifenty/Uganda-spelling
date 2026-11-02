#!/usr/bin/env python3
"""
patch_topic_nav.py — "go back to a previous topic" navigation.

Owner's request: a learner who finished a topic and moved on must always be
able to get back to the topic they studied before.

Why this matters more than it looks: a learner now starts from Choose Subject
and is dropped straight onto the FIRST unfinished topic. The topic list screen
is the owner's, not the learner's. So once topic 1 was finished, there was no
route back to it anywhere in the app.

What this patch adds to index.html:

  1. LEARNING PATH — a "Topics in <class> <subject>" strip (every topic, with
     ✓ for finished and a dot for the current one) and PREVIOUS TOPIC /
     NEXT TOPIC cards, under the practice button.
  2. CARD READER — a small book button in the header opens the same topic
     strip in a sheet, so a learner can jump to another topic in one tap from
     anywhere inside a topic.
  3. TOPIC COMPLETE SHEET — offers the next topic, the previous topic and the
     topic list, instead of only "go to practice".
  4. Re-opening a FINISHED topic asks first ("review it again?").
  5. DEVICE BACK BUTTON — steps back through the app's own screens (and
     closes an open sheet) rather than throwing the learner out of the app.
  6. "Continue where you stopped" now records progress while the learner
     swipes cards (it used to freeze at "Part 1 · 0%") and resumes into the
     card reader at the right sub-topic.

Everything respects the features that already exist in this app:

  * a teacher's TOPIC lock — the strip is built from notesFor(), which already
    hides every other topic, so a locked learner sees one topic and no arrows;
  * a teacher's SUBTOPIC lock — the whole strip is replaced by a short notice;
  * the PAYWALL — a chip for a topic the learner has not paid for still goes
    through openNotePath(), which raises the paywall exactly as before;
  * the MID-TOPIC TEST gate — navigation never opens a sub-topic directly, it
    only opens the topic's path, so the gate stays in charge.

Idempotent: every replacement checks for its own output first, and every anchor
must appear exactly once. Run from the ple-app folder:

    python3 tools/patch_topic_nav.py
"""
import sys

APP = "index.html"
MARK = "/* === TOPIC NAV PATCH (tools/patch_topic_nav.py) === */"


def edit(src, old, new, label):
    if new in src:
        print(f"  already applied: {label}")
        return src
    n = src.count(old)
    if n != 1:
        sys.exit(f"FAILED [{label}]: anchor found {n} times (expected 1)")
    print(f"  ok: {label}")
    return src.replace(old, new, 1)


# ---------------------------------------------------------------- 1. CSS ----
CSS_OLD = ".path-back:active{transform:scale(.92)}"
CSS_NEW = """.path-back:active{transform:scale(.92)}
.kid-alltopics{min-width:40px;height:40px;padding:0 11px;border-radius:999px;background:#fff;border:2px solid #DBEAFE;box-shadow:0 3px 12px rgba(30,64,175,.18);display:grid;place-items:center;color:#2D4159;font-size:17px;font-weight:900;flex:none}
.kid-alltopics:active{transform:scale(.94)}
.tp-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:2px}
.tp-chip{display:flex;align-items:center;gap:6px;background:#fff;border:2px solid var(--line);border-radius:999px;padding:8px 13px;font-size:13.5px;font-weight:800;color:var(--navy);max-width:100%}
.tp-chip.on{border-color:var(--purple);background:var(--purple-50);color:var(--purple-ink)}
.tp-chip.done{border-color:var(--green);background:var(--green-50)}
.tp-chip:active{transform:scale(.97)}
.tp-chip b{font-weight:900;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:190px}
.tp-chip i{font-style:normal;font-size:11px;font-weight:900;color:var(--muted)}
.tp-navrow{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.tp-navbtn{display:block;text-align:left;background:#fff;border:2px solid var(--line);border-radius:16px;padding:11px 13px;min-height:58px}
.tp-navbtn:active{transform:scale(.98)}
.tp-navbtn small{display:block;font-size:10.5px;font-weight:900;letter-spacing:.05em;color:#6B7280;margin-bottom:3px}
.tp-navbtn b{font-size:14px;color:var(--navy);line-height:1.25;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tp-navbtn.off{opacity:.38;pointer-events:none;background:var(--bg)}
.tp-allbtn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;background:#fff;border:2px solid var(--line);border-radius:16px;padding:12px;font-weight:900;color:var(--navy);font-size:14px;margin-top:10px}
.tp-allbtn:active{transform:scale(.98)}
.tp-locked{background:var(--yellow-50);border:1.5px solid var(--yellow-100);border-radius:16px;padding:12px 14px;font-size:13px;font-weight:700;color:var(--navy);line-height:1.45}"""

# ------------------------------------------------- 2. helper functions -------
HELPERS = MARK + """
/* ---- getting back to the topic you studied before ----------------------
   topicSiblings() reads notesFor(), so a teacher's topic lock is honoured
   automatically: a locked learner gets one topic and no arrows. */
function topicSiblings(id){
  const t=noteFindAnywhere(id);
  if(!t)return {prev:null,next:null,all:[],idx:-1};
  const b=(typeof notesFor==='function')?notesFor(t.class,t.subject):null;
  const all=b?b.topics.slice().sort((x,y)=>x.topic_no-y.topic_no):[t];
  const i=all.findIndex(x=>x.id===t.id);
  return {prev:i>0?all[i-1]:null, next:(i>=0&&i<all.length-1)?all[i+1]:null, all, idx:i};
}
/* a teacher locked this learner to one topic or one sub-topic: no browsing */
function topicNavLocked(){
  try{
    if(typeof rcSubLocked==='function' && rcSubLocked()) return true;
    if(typeof rcTopicLocked==='function' && rcTopicLocked()) return true;
  }catch(e){}
  return false;
}
/* has the learner paid for this topic? (never opens it — openNotePath decides) */
function topicPaid(t){
  try{
    if(typeof spPaid!=='function' || typeof spFreeTopicId!=='function') return true;
    return spPaid() || t.id===spFreeTopicId(t.class);
  }catch(e){ return true; }
}
/* the strip of every topic in this subject */
function topicChipsHTML(t){
  const sib=topicSiblings(t.id);
  return `<div class="tp-chips">${sib.all.map(x=>{
    const d=(typeof noteDone==='function')?noteDone(x).pct:0;
    const cls=x.id===t.id?'on':(d>=100?'done':'');
    const lock=topicPaid(x)?'':(typeof LOCK_SVG!=='undefined'?'\\u{1F512} ':'\\u{1F512} ');
    const mark=x.id===t.id?'\\u25CF':(d>=100?'\\u2713':'');
    return `<button class="tp-chip ${cls}" onclick="openSiblingTopic('${x.id}')">
      <i>${mark||'&nbsp;'}</i><b>${nEsc(x.title)}</b>${lock?'<i>'+lock+'</i>':''}</button>`;
  }).join('')}</div>`;
}
/* the whole navigation block that sits under a topic's path */
function topicNavHTML(t){
  if(!t)return '';
  if(topicNavLocked())
    return `<div class="tp-locked">\\u{1F512} Your teacher has set the topic you should study, so you cannot move to another one yet.</div>`;
  const sib=topicSiblings(t.id);
  const meta=(typeof NOTE_SUBJECTS!=='undefined')?NOTE_SUBJECTS.find(s=>s.id===t.subject):null;
  const one=(dir,nt)=>{
    const lab=dir<0?'\\u2190 PREVIOUS TOPIC':'NEXT TOPIC \\u2192';
    if(!nt)return `<span class="tp-navbtn off"><small>${lab}</small><b>${dir<0?'This is the first topic':'This is the last topic'}</b></span>`;
    return `<button class="tp-navbtn" onclick="openSiblingTopic('${nt.id}')"><small>${lab}</small><b>${nEsc(nt.title)}</b></button>`;
  };
  return `
  <div class="section-title">Topics in ${t.class} ${meta?meta.name:''}</div>
  ${topicChipsHTML(t)}
  <div style="height:10px"></div>
  <div class="tp-navrow">${one(-1,sib.prev)}${one(1,sib.next)}</div>
  ${(typeof isAdmin==='function'&&isAdmin())?`<button class="tp-allbtn" onclick="go('notes')">${I.topics(18)} All ${t.class} ${meta?meta.name:''} topics</button>`:''}`;
}
/* hop to a brother topic: straight through, because the learner chose it */
function openSiblingTopic(id){
  if(!id)return;
  state.nsec=0;state.ki=0;state.kcards=null;
  openNotePath(id,true);
}
/* the same topic strip as a sheet, reachable from inside the cards */
function kidTopicSheet(){
  const t=noteById(state.ntopic)||noteFindAnywhere(state.ntopic);
  if(!t)return;
  if(topicNavLocked()){
    openSheet(`<div class="grabber"></div><h3>\\u{1F512} Your teacher's plan</h3>
      <p class="muted" style="margin:10px 0">You have been set this topic, so you cannot jump to another one until your teacher changes it.</p>
      <button class="btn btn-primary" style="margin-top:8px" onclick="closeSheet()">GOT IT</button>`);
    return;
  }
  openSheet(`<div class="grabber"></div>
    <h3>\\u{1F4DA} Topics in ${t.class} ${((typeof NOTE_SUBJECTS!=='undefined')&&(NOTE_SUBJECTS.find(s=>s.id===t.subject)||{}).name)||''}</h3>
    <p class="muted" style="margin:8px 0 12px;font-size:13px">Tap a topic to open it. Your progress is kept.</p>
    ${topicChipsHTML(t)}
    <button class="btn btn-ghost" style="margin-top:14px" onclick="closeSheet()">CLOSE</button>`);
}
/* feed the Home "Continue where you stopped" card with real progress */
function recordNoteProgress(t,i,ki,cards){
  try{
    const secs=noteSections(t), d=noteDone(t), n=secs[Math.max(0,i||0)]||{};
    const where=String(n.title||'').replace(/^\\d+\\.\\s*/,'');
    const meta=(typeof ki==='number'&&cards&&cards.length)
      ? `Card ${Math.min(ki+1,cards.length)} of ${cards.length} \\u00B7 ${d.read} of ${d.total} parts read`
      : `Part ${Math.min((i||0)+1,secs.length)} of ${secs.length} \\u00B7 ${d.read} of ${d.total} parts read`;
    recordLast({kind:'notes',klass:t.class,nsubject:t.subject,ntopic:t.id,nsec:Math.max(0,i||0),
      ki:Math.max(0,ki||0),label:t.title,sub:where,meta,pct:d.pct});
  }catch(e){}
}

"""

# ------------------------------- 3. openNotePath: skip flag + review question -
OPEN_SIG_OLD = "function openNotePath(id){"
OPEN_SIG_NEW = "function openNotePath(id, skipConfirm){"

PAYWALL_OLD = "  if(!spPaid()&&t.id!==spFreeTopicId(t.class)){ spOpenPaywall(); return; }"
PAYWALL_NEW = PAYWALL_OLD + """
  /* a topic that is ALREADY finished is re-opened only after a yes. Asked
     here, after the lock and the paywall, so the learner is never asked
     about a topic they were not allowed to open anyway. */
  if(!skipConfirm && state.pathConfirm!==id && noteDone(t).pct>=100){
    state.pathConfirm=id;
    openSheet(`<div class="grabber"></div>
      <div style="text-align:center">
        <div style="font-size:52px">\\u{1F3C6}</div>
        <h3 style="margin-top:6px">You already finished this topic</h3>
        <p class="muted" style="margin:8px 0 4px"><b>${nEsc(t.title)}</b> is marked complete. Open it again for revision?</p>
        <button class="btn btn-primary" style="margin-top:12px" onclick="closeSheet();state.pathConfirm=null;openNotePath('${t.id}',true)">\\u{1F4D6} REVIEW THIS TOPIC</button>
        <button class="btn btn-ghost" style="margin-top:8px" onclick="closeSheet();state.pathConfirm=null">NOT NOW</button>
      </div>`);
    return;
  }
  state.pathConfirm=null;
  state.ki=0;state.kcards=null;"""

# ---------------------------------------- 4. topic nav under the learning path
PATH_OLD = """    <div style="display:grid;gap:10px;margin-top:6px">
      <button class="btn btn-soft" onclick="lpPractice()">\\u{1F3AF} Go to Practice for this topic</button>
    </div>
    <div class="spacer"></div>"""
PATH_NEW = """    <div style="display:grid;gap:10px;margin-top:6px">
      <button class="btn btn-soft" onclick="lpPractice()">\\u{1F3AF} Go to Practice for this topic</button>
    </div>
    ${topicNavHTML(t)}
    <div class="spacer"></div>"""

# ------------------------- 5. topic-complete sheet: what comes next/previously
DONE_OLD = """      ${lpEndBtn(t)}
      <button class="btn btn-ghost" style="margin-top:8px" onclick="closeSheet();go('notePath')">BACK TO THE PATH</button>"""
DONE_NEW = """      ${lpEndBtn(t)}
      ${(()=>{ if(topicNavLocked()) return '';
        const s=topicSiblings(t.id);
        return `${s.next?`<button class="btn btn-primary" style="margin-top:10px;background:var(--green);border-color:var(--green)" onclick="closeSheet();openSiblingTopic('${s.next.id}')">NEXT TOPIC: ${nEsc(String(s.next.title).toUpperCase())} \\u27A1</button>`:''}
        ${s.prev?`<button class="btn btn-soft" style="margin-top:8px" onclick="closeSheet();openSiblingTopic('${s.prev.id}')">\\u2190 PREVIOUS TOPIC: ${nEsc(String(s.prev.title).toUpperCase())}</button>`:''}`;})()}
      <button class="btn btn-ghost" style="margin-top:8px" onclick="closeSheet();go('notePath')">BACK TO THE PATH</button>"""

# -------------------------- 6. book button in the card-reader header ---------
KID_OLD = """      <h2>${nEsc(String(sec.title).replace(/^\\d+\\.\\s*/,''))}</h2>
      ${dots}"""
KID_NEW = """      <h2>${nEsc(String(sec.title).replace(/^\\d+\\.\\s*/,''))}</h2>
      <button class="kid-alltopics" onclick="kidTopicSheet()" aria-label="Other topics" title="Other topics">${I.topics(18)}</button>
      ${dots}"""

# ------------------------------- 7. progress on opening a sub-topic ----------
LPOPEN_OLD = """  if(i>=g.half&&g.midDue&&!g.midOk){toast('Pass the Mid-Topic Test \\u{1F3AF} to unlock the second half');return;}
  state.nsec=i;
  go('noteSub');"""
LPOPEN_NEW = """  if(i>=g.half&&g.midDue&&!g.midOk){toast('Pass the Mid-Topic Test \\u{1F3AF} to unlock the second half');return;}
  state.nsec=i;
  recordNoteProgress(t,i);
  go('noteSub');"""

# ------------------------------- 8. progress on every card swipe -------------
SHOW_OLD = """  state.ki=Math.max(0,Math.min(i,cards.length));   /* cards.length = celebration */
  render();"""
SHOW_NEW = """  state.ki=Math.max(0,Math.min(i,cards.length));   /* cards.length = celebration */
  recordNoteProgress(t,Math.max(0,state.nsec||0),state.ki,cards);
  render();"""

# ------------------------------------------ 9. Continue where you stopped ----
RESUME_OLD = "  if(d.kind==='notes'&&d.ntopic&&noteById(d.ntopic)){state.nsubject=d.nsubject||state.nsubject;state.ntopic=d.ntopic;state.nsec=Math.max(0,d.nsec||0);go('noteRead');return;}"
RESUME_NEW = """  if(d.kind==='notes'&&d.ntopic&&noteFindAnywhere(d.ntopic)){
    /* resume into the card reader at the sub-topic the learner had reached */
    const t=noteFindAnywhere(d.ntopic);
    if(rcTopicLocked&&rcTopicLocked()){ const rt=rcResolveTopic(t); if(rt) t=rt; }
    if(state.klass!==t.class&&checkClassAccess(t.class))return;
    state.nsubject=t.subject;state.ntopic=t.id;
    state.nsec=Math.max(0,d.nsec||0);state.ki=0;state.kcards=null;
    if(t.subject==='MATH'){mathLessonStart(t.id);return;}
    go('noteSub');return;}"""

# ------------------------------- 9b. the classic contents page too --------
TOC_OLD = """  <div class="spacer"></div>
  ${SUBJ_META[t.subject] ? `<button class="btn btn-ghost" onclick="practiseFromNotes()">"""
TOC_NEW = """  <div class="spacer"></div>
  ${topicNavHTML(t)}
  <div class="spacer"></div>
  ${SUBJ_META[t.subject] ? `<button class="btn btn-ghost" onclick="practiseFromNotes()">"""

# --------------------------------------- 10. the device back button ----------
# Kept OUTSIDE the Read Aloud markers: tools/patch_speech.py rewrites
# everything between them on every build and would delete this.
HIST_OLD = "/* === READ ALOUD MODULE END === */"
HIST_NEW = """/* === READ ALOUD MODULE END === */

""" + MARK + """
/* DEVICE BACK BUTTON — pressing the phone's back button goes back ONE screen
   in the app (closing an open sheet first), never out of the app mid-lesson.
   One guard entry sits under the app so popping it cannot unload the page;
   at the very top the phone is allowed to leave, as it expects. */
let HIST_GUARD=false;
function histGuard(){
  if(HIST_GUARD)return; HIST_GUARD=true;
  const push=()=>{try{history.pushState({ple:1},'');}catch(e){}};
  push();
  window.addEventListener('popstate',()=>{
    const scrim=document.getElementById('scrim');
    if(scrim&&scrim.classList.contains('show')){push();closeSheet();return;}
    if(state.stack&&state.stack.length){push();back();return;}
    if(state.screen!=='home'&&state.screen!=='notes'){push();state.stack=[];state.tab='home';go('home',false);return;}
    /* at the very top: let the phone take the learner out */
  });
}
histGuard();
"""


def main():
    src = open(APP, encoding="utf-8").read()
    before = len(src)
    print("patching", APP)
    src = edit(src, CSS_OLD, CSS_NEW, "css")
    src = edit(src, OPEN_SIG_OLD, HELPERS + OPEN_SIG_NEW, "helper functions")
    src = edit(src, PAYWALL_OLD, PAYWALL_NEW, "review question for finished topics")
    src = edit(src, PATH_OLD, PATH_NEW, "topic nav under the learning path")
    src = edit(src, DONE_OLD, DONE_NEW, "topic-complete sheet nav")
    src = edit(src, KID_OLD, KID_NEW, "card reader topic button")
    src = edit(src, LPOPEN_OLD, LPOPEN_NEW, "progress on sub-topic open")
    src = edit(src, SHOW_OLD, SHOW_NEW, "progress on card swipe")
    src = edit(src, RESUME_OLD, RESUME_NEW, "continue-where-you-stopped")
    src = edit(src, TOC_OLD, TOC_NEW, "contents page nav")
    src = edit(src, HIST_OLD, HIST_NEW, "device back button")
    open(APP, "w", encoding="utf-8").write(src)
    print(f"done: {before} -> {len(src)} bytes (+{len(src)-before})")


if __name__ == "__main__":
    main()

/* force_assign_test.js — the admin override sits ON TOP of the learner's own
   study chain. It must narrow the app in LOCK_ONLY, add without hiding in
   EXTRA, and hand over a paper in EXAM. An expired override must behave as if
   it never existed. Driven through the app's real functions. */
'use strict';
const fs = require('fs');
const FILE = process.argv[2] || __dirname + '/../Uganda-spelling/ple-app/index.html';
const { JSDOM } = require('/tmp/navtest/node_modules/jsdom');

const dom = new JSDOM(fs.readFileSync(FILE, 'utf8'), {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://uganda-spelling.vercel.app/'
});
const w = dom.window;
const ev = c => w.eval(c);
const checks = [];
const check = (name, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  checks.push(ok);
  console.log((ok ? 'PASS  ' : 'FAIL  ') + name + '\n      got ' + JSON.stringify(got) + '  expected ' + JSON.stringify(want));
};
const done = () => {
  const bad = checks.filter(c => !c).length;
  console.log('\n' + (checks.length - bad) + '/' + checks.length + ' checks passed');
  process.exit(bad ? 1 : 0);
};

/* Build the assignment row the way the database hands it over. */
const row = o => ev(`rcApply(${JSON.stringify(Object.assign({
  forced_class: null, forced_subject: null, forced_topic: null, forced_subtopic: null,
  forced_tier: null, force_mode: null, forced_subtopic_id: null, forced_until: null,
  allow_notes: true, allow_practice_with_answers: true, allow_practice_no_answers: true
}, o))}); 'applied'`);

setTimeout(function () {
  try {
    ev(`supabaseClient = { from(){ const q={select:()=>q,eq:()=>q,order:()=>q,limit:()=>q,
          then:(f,r)=>Promise.resolve({data:[],error:null}).then(f,r)}; return q; } };
        state.authUser = { id: 'learner-1' };
        state.adminOk = false;
        spPaid = () => true;
        state.klass = 'P4'; state.nsubject = 'SST'; state.psubject = 'SST';`);

    const allTopics = ev(`notesFor('P4','SST').topics.length`);
    check('baseline: the learner sees every P4 SST topic', allTopics > 1, true);

    /* Section titles come from the corpus, not from this file — a hard-coded
       title silently stops matching the moment the notes are reworded, and the
       app then (correctly) falls back to showing everything. */
    const TOPIC_TITLE = ev(`(function(){
        const t=notesFor('P4','SST').topics.find(x=>x.id==='P4_SST_T04');
        return t.title; })()`);
    const SUB_TITLE = ev(`(function(){
        const t=notesFor('P4','SST').topics.find(x=>x.id==='P4_SST_T04');
        return noteSections(t)[0].title; })()`);
    check('the corpus really does offer that topic and subtopic',
      [!!TOPIC_TITLE, !!SUB_TITLE], [true, true]);
    const lockRow = extra => Object.assign({
      force_mode: 'LOCK_ONLY', forced_subtopic_id: 'P4_SST_T04#0',
      forced_topic: TOPIC_TITLE, forced_subtopic: SUB_TITLE
    }, extra || {});

    /* ---- LOCK_ONLY: everything but the target disappears ------------------ */
    row(lockRow());
    check('LOCK_ONLY is recognised', ev(`rcForceMode()`), 'LOCK_ONLY');
    check('LOCK_ONLY narrows the notes to one topic',
      ev(`notesFor('P4','SST').topics.length`), 1);
    check('LOCK_ONLY narrows to one subtopic',
      ev(`noteSections(notesFor('P4','SST').topics[0]).length`), 1);
    check('LOCK_ONLY hides practice', ev(`rcScreenDenied('ptopics')`), 'pwa');
    check('LOCK_ONLY hides past papers', ev(`rcScreenDenied('papers')`), 'pna');

    /* ---- EXTRA: adds a task, hides NOTHING ------------------------------- */
    row({ force_mode: 'EXTRA', forced_subtopic_id: 'P4_SST_T03#2' });
    check('EXTRA is recognised', ev(`rcForceMode()`), 'EXTRA');
    check('EXTRA is not treated as a lock', ev(`rcSubLocked()`), false);
    check('EXTRA leaves every topic reachable',
      ev(`notesFor('P4','SST').topics.length`), allTopics);
    check('EXTRA leaves practice open', ev(`rcScreenDenied('ptopics')`), null);
    check('EXTRA is flagged so the app can show the task', ev(`rcIsExtra()`), true);
    check('EXTRA carries the target to open', ev(`RC.forceTarget`), 'P4_SST_T03#2');

    /* ---- EXAM: hands over the paper, hides nothing else ------------------ */
    row({ force_mode: 'EXAM', forced_subtopic_id: '7' });
    check('EXAM is recognised', ev(`rcForceMode()`), 'EXAM');
    check('EXAM is flagged', ev(`rcIsExamForce()`), true);
    check('EXAM leaves the notes open', ev(`rcScreenDenied('noteRead')`), null);
    check('EXAM leaves every topic reachable',
      ev(`notesFor('P4','SST').topics.length`), allTopics);

    /* ---- an override that has lapsed is no override at all --------------- */
    const past = new Date(Date.now() - 86400000).toISOString();
    row(lockRow({ forced_until: past }));
    check('an expired override sets no mode', ev(`RC.forceMode`), null);
    check('an expired override stops hiding topics',
      ev(`notesFor('P4','SST').topics.length`), allTopics);
    check('an expired override stops hiding practice', ev(`rcScreenDenied('ptopics')`), null);

    /* a live forced_until keeps the lock on */
    row(lockRow({ forced_until: new Date(Date.now() + 86400000).toISOString() }));
    check('a future forced_until keeps the lock', ev(`notesFor('P4','SST').topics.length`), 1);

    /* ---- switching modes must not leave the old hiding behind ------------ */
    row({ force_mode: 'EXTRA', forced_subtopic_id: 'P4_SST_T03#2' });
    check('switching LOCK_ONLY -> EXTRA releases the topics',
      ev(`notesFor('P4','SST').topics.length`), allTopics);

    /* ---- backward compatibility with the lock already in production ------ */
    row({ forced_topic: TOPIC_TITLE, forced_subtopic: SUB_TITLE });
    check('a stored subtopic with no force_mode still locks (shipped behaviour)',
      ev(`rcForceMode()`), 'LOCK_ONLY');
    check('and still narrows the notes', ev(`notesFor('P4','SST').topics.length`), 1);

    /* ---- unlock: back to the learner's own chain ------------------------- */
    row({});
    check('unlocking clears the mode', ev(`RC.forceMode`), null);
    check('unlocking restores every topic', ev(`notesFor('P4','SST').topics.length`), allTopics);
    check('unlocking restores practice', ev(`rcScreenDenied('ptopics')`), null);

    /* ---- the owner is never affected ------------------------------------- */
    row(lockRow());
    ev(`state.adminOk = true`);
    check('the owner still sees everything while a learner is locked',
      ev(`notesFor('P4','SST').topics.length`), allTopics);
    check('the owner gets no banner', ev(`rcForceActive()`), false);
    ev(`state.adminOk = false`);

    /* ---- the study chain itself is untouched ----------------------------- */
    row({});
    check('the chain gate is still in place',
      ev(`typeof pbUnlocked`), 'function');
    /* Prove the gate still bites: with nothing read, the practice bank is
       smaller than once every section has been read. */
    const chainLocked = ev(`(function(){ state.noteSeen={}; return pbAll('P4').length; })()`);
    const chainOpen   = ev(`(function(){
        notesFor('P4','SST').topics.forEach(t=>noteSections(t).forEach((_,i)=>{state.noteSeen[t.id+':'+i]=true;}));
        return pbAll('P4').length; })()`);
    check('reading sections still unlocks more practice (chain intact)',
      chainOpen > chainLocked, true);

    /* ---- the reported bug: changing ONLY the subtopic ---------------------
       The learner is already forced to P6 SST and standing inside topic 1.
       The teacher changes nothing but the subtopic. The old snapshot did not
       include it, so rcForce() moved the learner and the screen never
       re-rendered — they kept reading topic 1. */
    ev(`state.adminOk=false; state.klass='P6'; state.nsubject='SST';
        state.ntopic='P6_SST_T01'; state.screen='notePath';`);
    const before = ev(`(function(){
        rcApply({user_id:'l1',forced_class:'P6',forced_subject:'SST',forced_topic:null,
          forced_subtopic:null,forced_tier:null,allow_notes:true,
          allow_practice_with_answers:true,allow_practice_no_answers:true});
        return rcSnapshot(); })()`);
    const after = ev(`(function(){
        rcApply({user_id:'l1',forced_class:'P6',forced_subject:'SST',
          forced_topic:'Responsible Living in the East African Environment',
          forced_subtopic:'6. SOLUTIONS TO THE ENVIRONMENTAL PROBLEMS',forced_tier:null,
          allow_notes:true,allow_practice_with_answers:true,allow_practice_no_answers:true});
        return rcSnapshot(); })()`);
    check('changing only the subtopic changes the snapshot, so the screen re-renders',
      before !== after, true);

    /* and the learner actually lands on the locked subtopic */
    ev(`rcForce()`);
    check('the learner is moved off the topic they were reading',
      ev(`state.ntopic`), 'P6_SST_T05');
    check('and only the locked subtopic is left',
      ev(`noteSections(noteById(state.ntopic)).map(s=>String(s.title))`),
      ['6. SOLUTIONS TO THE ENVIRONMENTAL PROBLEMS']);

    /* ---- the banners: a lock must never be silent ------------------------ */
    row(lockRow());
    check('a locked learner is told they are locked',
      ev(`(function(){const d=document.createElement('div');rcForceBannerInto(d);
            return /Teacher Assigned/.test(d.innerHTML);})()`), true);
    ev(`state.adminOk = true`);
    check('owner mode says it is bypassing the lock, instead of doing it silently',
      ev(`(function(){const d=document.createElement('div');rcForceBannerInto(d);
            return /Owner mode/.test(d.innerHTML);})()`), true);
    ev(`state.adminOk = false`);
    row({});
    check('no banner when nothing is locked',
      ev(`(function(){const d=document.createElement('div');rcForceBannerInto(d);
            return d.innerHTML===''})()`), true);

    done();
  } catch (e) {
    console.log('ERROR: ' + (e && e.stack || e));
    process.exit(1);
  }
}, 1200);

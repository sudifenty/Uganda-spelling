/* practice_log_test.js — the teacher can only read a practice run if the phone
   sends it, and only if the phone KEEPS it when there is no network. This sits a
   real practice run in the real app file and checks both.

   Usage:  node qa/practice_log_test.js [path/to/index.html]
*/
const fs = require('fs');
const { JSDOM } = require(process.env.JSDOM || '/tmp/navtest/node_modules/jsdom');
const FILE = process.argv[2] || '/home/user/Uganda-spelling/ple-app/index.html';
const dom = new JSDOM(fs.readFileSync(FILE, 'utf8'), {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://example.test/'
});
const w = dom.window;
let fails = 0, n = 0;
function check(name, actual, expected) {
  n++;
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (!ok) fails++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}\n      got ${JSON.stringify(actual)}${ok ? '' : '  expected ' + JSON.stringify(expected)}`);
}
const ev = c => w.eval(c);

/* ---- a supabase stub whose insert we can make fail on demand ---- */
ev(`
window.__calls = [];
window.__failInsert = false;
supabaseClient = { from(t){ const q = {
  select:()=>q, eq:()=>q, in:()=>q, order:()=>q, limit:()=>q, single:()=>q,
  insert:(rows)=>{
    if(window.__failInsert) return Promise.resolve({ data:null, error:{ message:'offline' } });
    window.__calls.push({ table:t, rows });
    return Promise.resolve({ data:rows, error:null });
  } }; return q; } };
state.authUser = { id:'learner-1', email:'kid@example.com' };
state.authReady = true; state.adminOk = false;
if (typeof spPaid === 'function') { try { spPaid = () => true; } catch(e){} }
`);

/* ================= 1. an answer is queued AND kept on the device ========= */
ev(`ACT_QUEUE.length = 0; localStorage.removeItem('sp_act_queue');
    trackActivity('practice_submitted', { topic:'East Africa', answers:[{ q:'Q?', given:'my writing' }] }, true);`);
check('answer-bearing event is queued', ev('ACT_QUEUE.length'), 1);
check('it is flagged as one to keep', ev('ACT_QUEUE[0].keep'), true);
check('it is written to localStorage, so closing the app cannot lose it',
  JSON.parse(ev("localStorage.getItem('sp_act_queue')")).length, 1);

/* ================= 2. a failed insert must NOT drop what they wrote ======= */
ev(`window.__failInsert = true;`);
ev(`activityFlush();`);
setTimeout(() => {
  check('after a failed insert the event is still queued', ev('ACT_QUEUE.length'), 1);
  check('a failed insert reached the database and was refused',
    ev('window.__calls.length'), 0);

  /* ---- 3. the same event goes through once the connection is back ---- */
  ev(`window.__failInsert = false; activityFlush();`);
  setTimeout(() => {
    const sent = ev(`window.__calls.filter(c=>c.table==='learning_events')`);
    check('the retry delivered it', sent.length, 1);
    check('the queue is empty after a successful send', ev('ACT_QUEUE.length'), 0);
    check('it landed as a practice_submitted row',
      sent[0] && sent[0].rows[0].event_type, 'practice_submitted');
    check('the internal keep flag never reaches the database',
      sent[0] && ('keep' in sent[0].rows[0]), false);
    check('localStorage is cleared once delivered',
      ev("localStorage.getItem('sp_act_queue')"), '[]');

    /* ============ 4. screen views stay disposable, answers do not ======== */
    ev(`ACT_QUEUE.length = 0; window.__failInsert = true;
        trackActivity('practice_submitted', { answers:[{ q:'keep me', given:'x' }] }, true);
        for (let i = 0; i < 260; i++) trackActivity('screen_view', { screen:'home' });`);
    const kept = ev(`ACT_QUEUE.filter(e=>e.keep).length`);
    check('260 screen views cannot push a written answer out of the queue', kept >= 1, true);
    check('the queue is capped', ev('ACT_QUEUE.length') <= 200, true);
    check('screen views were the ones dropped',
      ev(`ACT_QUEUE.filter(e=>e.event_type==='screen_view').length`) < 260, true);

    /* ============ 5. a real practice run sends what they wrote ============ */
    ev(`ACT_QUEUE.length = 0; window.__failInsert = false; window.__calls = [];
        const eb = EXERCISE_BANK['P6'] && EXERCISE_BANK['P6']['SST'];
        const t = eb.topics.find(x => (x.questions||[]).some(q => q.kind === 'self')) || eb.topics[0];
        window.__tid = t.topic_id; window.__tname = t.title;
        exStart('P6','SST', t.topic_id, null, 'random', true);`);

    const run = ev(`state.exRun ? { n: state.exRun.qids.length, title: state.exRun.title } : null`);
    check('a practice run started', !!run, true);
    if (!run) { report(); return; }

    /* answer every question in the run, in the learner's own words */
    ev(`state.exRun.qids.forEach((id, i) => exWrite(id, 'my own answer number ' + (i+1)));`);
    ev(`exSubmit();`);
    check('the run was marked', ev(`!!(state.exRun && state.exRun.result)`), true);

    /* self-mark any prose question the app could not mark, as a learner would */
    ev(`(state.exRun.result||[]).filter(r=>r.state==='self').slice(0,1)
          .forEach(r => exSelf(r.id, 'part'));`);
    ev(`exFinish();`);

    const ev2 = ev(`ACT_QUEUE.filter(e=>e.event_type==='practice_submitted')`);
    check('finishing the run produced one practice_submitted event', ev2.length, 1);
    const d = ev2[0] && ev2[0].details;
    check('it names the topic the learner practised', d && d.topic, ev(`window.__tname`));
    check('it carries every answer in the run', d && d.answers.length, run.n);
    check('each answer carries what they wrote',
      d && d.answers.every(a => typeof a.given === 'string' && a.given.length > 0), true);
    check('each answer carries the question itself',
      d && d.answers.every(a => typeof a.q === 'string' && a.q.length > 0), true);
    check('the model answer travels with it so the teacher can judge',
      d && d.answers.some(a => typeof a.answer === 'string' && a.answer.length > 0), true);
    check('marks are recorded per question',
      d && d.answers.every(a => typeof a.marks === 'number'), true);
    check('the learner self-verdict is recorded where they gave one',
      d && d.answers.some(a => a.self === 'part'), true);
    check('the run total is included', d && typeof d.pct === 'number', true);
    check('it is flagged keep:true, so an offline run survives', ev2[0].keep, true);

    /* and it actually reaches the table when flushed */
    ev(`activityFlush();`);
    setTimeout(() => {
      const rows = ev(`window.__calls.filter(c=>c.table==='learning_events')`);
      check('the practice run reached learning_events', rows.length >= 1, true);
      check('it was sent for the signed-in learner',
        rows[0] && rows[0].rows[0].user_id, 'learner-1');
      report();
    }, 30);
  }, 30);
}, 30);

function report() {
  console.log(`\n${n - fails}/${n} checks passed`);
  process.exit(fails ? 1 : 0);
}

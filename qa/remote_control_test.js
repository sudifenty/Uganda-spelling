/* remote_control_test.js — runs the REAL app file in jsdom with a stubbed
   Supabase client, then flips the owner's switches in smartple_assignments
   and checks what the learner's phone actually shows.

   Usage:  node qa/remote_control_test.js [path/to/index.html]
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
const view = () => ev("document.getElementById('views').innerHTML");
const tabs = () => ev("document.getElementById('tabbar').innerHTML");

/* the owner's admin panel writes exactly this row shape */
const row = o => Object.assign({
  id: 'a1', user_id: 'learner-1', forced_class: null, forced_subject: null,
  forced_topic: null, forced_tier: null, allow_notes: true,
  allow_practice_with_answers: true, allow_practice_no_answers: true, note: null
}, o);

/* a supabase client that answers .from().select().eq().limit() and
   .in().order().limit() — the two queries the app makes */
const STUB = `
window.__row = null;
supabaseClient = { from(t){ const q={ select:()=>q, eq:()=>q, in:()=>q, order:()=>q,
  limit:()=>Promise.resolve({data: t==='smartple_assignments'
    ? (window.__row?[window.__row]:[]) : [], error:null}) }; return q; } };
state.authUser={id:'learner-1',email:'kid@example.com'}; state.authReady=true;
state.adminOk=false; state.klass='P6'; state.psubject='SST'; state.nsubject='SST';
state.exsubject='SST'; state.ntopic=null; state.stack=[]; state.screen='home'; render();
`;
const sync = () => ev("(async()=>{ await rcFetch(); return true; })()");

(async () => {
  console.log('app file: ' + FILE + '\n');
  ev(STUB);
  ev('rcStart()');          /* authInit does this the moment a learner signs in */

  /* ---------- 1. no assignment row = nothing restricted ---------- */
  ev('window.__row=null'); await sync();
  check('no row -> notes allowed', ev('RC.notes'), true);
  check('no row -> both practice modes allowed', [ev('RC.pwa'), ev('RC.pna')], [true, true]);
  check('no row -> START card on home', view().includes('nh-start'), true);
  check('no row -> Notes tab present', tabs().includes('>Notes<'), true);
  check('no row -> 15-second poll running', !!ev('rcTimer'), true);

  /* ---------- 2. teacher hides the notes and forces P4 SST ---------- */
  ev(`window.__row=${JSON.stringify(row({ allow_notes: false, forced_class: 'P4', forced_subject: 'SST', note: 'Read your SST notes' }))}`);
  await sync();
  ev("state.screen='home'; render()");
  check('notes switch off -> RC.notes false', ev('RC.notes'), false);
  check('notes off -> START card gone from home', view().includes('nh-start'), false);
  check('notes off -> Notes tab gone', tabs().includes('>Notes<'), false);
  check('notes off -> PRACTICE card still there', view().includes('nh-practice'), true);
  check("teacher's note shown on home", view().includes('Read your SST notes'), true);
  check('forced class applied', ev('state.klass'), 'P4');
  check('forced subject applied', [ev('state.psubject'), ev('state.nsubject')], ['SST', 'SST']);
  check("go('notes') is unreachable", (ev("go('notes'); state.screen"), ev('state.screen')) !== 'notes', true);
  check("go('notePath') is unreachable", (ev("go('notePath'); state.screen"), ev('state.screen')) !== 'notePath', true);
  check('blocked learner lands on practice', ev('state.screen'), 'practice');
  ev("go('start')");
  check('Choose Subject shows only the forced subject', (view().match(/sc-card/g) || []).length, 1);
  check('forced class pill cannot be changed', view().includes("go('classPick')"), false);
  ev("setClass('P7')");
  check('learner cannot change a forced class', ev('state.klass'), 'P4');

  /* ---------- 3. teacher hides practice too, learner is mid-notes ---------- */
  ev(`window.__row=${JSON.stringify(row({ allow_notes: true, allow_practice_with_answers: false, allow_practice_no_answers: false, forced_class: 'P4', forced_subject: 'SST' }))}`);
  await sync();                                  /* notes back on, practice off */
  ev("state.ntopic='P4_SST_T01'; go('notePath')");
  check('learner is inside the learning path', ev('state.screen'), 'notePath');
  check('practice off -> both modes false', [ev('RC.pwa'), ev('RC.pna')], [false, false]);
  ev("state.screen='home'; render()");
  check('Exercises + Papers tabs gone', [tabs().includes('>Exercises<'), tabs().includes('>Papers<')], [false, false]);
  ev("startPractice('quick')");
  check('Practice WITH Answers refuses', ev('state.screen') !== 'question', true);
  ev('pmNoAnswers()');
  check('Practice NO Answers refuses', ev('state.screen') !== 'exDo', true);
  ev("state.screen='practice'; render()");
  check('both practice cards hidden on the practice screen',
    [view().includes('pm-card pm-with'), view().includes('pm-card pm-no')], [false, false]);

  /* ---------- 4. everything off at once: the learner is pushed home ---------- */
  ev(`window.__row=${JSON.stringify(row({ allow_notes: false, allow_practice_with_answers: false, allow_practice_no_answers: false, forced_class: 'P4', forced_subject: 'SST' }))}`);
  ev("state.ntopic='P4_SST_T01'; state.screen='noteSub'; render()");
  await sync();
  check('all off -> learner pushed off the notes', ev('state.screen'), 'home');
  check('all off -> home explains it, no error text',
    [view().includes('paused your sections'), view().includes('FAILED')], [true, false]);

  /* ---------- 5. teacher switches everything back on ---------- */
  ev(`window.__row=${JSON.stringify(row({}))}`);
  await sync();
  check('re-enabled -> START card back', view().includes('nh-start'), true);
  check('re-enabled -> all tabs back',
    [tabs().includes('>Notes<'), tabs().includes('>Exercises<'), tabs().includes('>Papers<')], [true, true, true]);
  check('re-enabled -> class free again', view().includes('nh-start'), true);

  /* ---------- 6. offline: the saved copy still holds the learner ---------- */
  ev(`window.__row=${JSON.stringify(row({ allow_notes: false }))}`);
  await sync();                                  /* writes the cache */
  ev('supabaseClient=null');                     /* the internet drops */
  ev('RC.at=0; RC.notes=true; RC.pwa=true; RC.pna=true');   /* fresh in-memory state */
  await sync();
  check('offline -> cached restriction restored', ev('RC.notes'), false);
  ev("state.screen='home'; render()");
  check('offline -> START still hidden', view().includes('nh-start'), false);

  /* ---------- 7. the owner is never restricted ---------- */
  ev("state.adminOk=true; state.klass='P6'; state.nsubject='SST'; state.screen='home'; render()");
  ev("go('notes')");
  check('owner still reaches the topics list with everything off', ev('state.screen'), 'notes');
  check('owner sees every topic', view().includes('The East African Community'), true);

  console.log(`\n${n - fails}/${n} checks passed`);
  process.exit(fails ? 1 : 0);
})();

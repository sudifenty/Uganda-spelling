/* exam_test.js — runs the REAL app file in jsdom and sits a whole exam:
   assignment appears -> card on home -> runner -> lock -> answer -> submit
   -> score written back -> unlocked.  Then: teacher releases it mid-exam.

   Usage:  node qa/exam_test.js [path/to/index.html]
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

const EXAM = {
  id: 'ex1', title: 'End of Topic Test', subject: 'SST', duration_minutes: 10, created_by: 'owner',
  questions: [
    { q: 'Which lake is the largest in Africa?', options: ['A. Victoria', 'B. Albert', 'C. Edward', 'D. George'], answer: 'A', marks: 2, topic: 'The East African Community' },
    { q: 'Name two member states of the East African Community.', options: [], kind: 'short', answer: 'Uganda and Kenya', marks: 3, topic: 'The East African Community' },
    { q: 'What is the capital of Uganda?', options: ['Kampala', 'Nairobi', 'Kigali', 'Dodoma'], answer: 'A', marks: 1 }
  ]
};
const ASSIGN = { id: 'as1', exam_id: 'ex1', user_id: 'learner-1', status: 'locked', score: null };
const ROW = { id: 'a1', user_id: 'learner-1', allow_notes: true, allow_practice_with_answers: true, allow_practice_no_answers: true };

const STUB = `
window.__row=${JSON.stringify(ROW)}; window.__exam=${JSON.stringify(EXAM)}; window.__ea=${JSON.stringify(ASSIGN)};
window.__calls=[];
supabaseClient={ from(t){ const q={ select:()=>q, eq:()=>q, in:()=>q, order:()=>q,
  insert:(rows)=>{ window.__calls.push({table:t,insert:rows}); return q; },
  update:(payload)=>{ window.__calls.push({table:t,payload}); return q; },
  limit:()=>Promise.resolve({data:
     t==='smartple_assignments'?(window.__row?[window.__row]:[]):
     t==='smartple_exams'?(window.__exam?[window.__exam]:[]):
     t==='smartple_exam_assignments'?(window.__ea?[window.__ea]:[]):[], error:null}) }; return q; } };
state.authUser={id:'learner-1',email:'kid@example.com'}; state.authReady=true; state.adminOk=false;
state.klass='P6'; state.ntopic=null; state.stack=[]; state.screen='home'; state.sx=null; render();
`;
const sync = () => ev("(async()=>{ await rcFetch(); return 1; })()");

(async () => {
  console.log('app file: ' + FILE + '\n');
  ev(STUB);
  ev("window.__ea=null"); await sync();
  ev("state.screen='home'; render()");
  check('no assignment -> no exam card on home', view().includes('NEW EXAM'), false);

  /* ---------- the teacher assigns an exam ---------- */
  ev(`window.__ea=${JSON.stringify(ASSIGN)}`);
  await sync();
  ev("state.screen='home'; render()");
  check('assignment -> big exam card on home', view().includes('NEW EXAM'), true);
  check('card names the exam', view().includes('End of Topic Test'), true);
  ev("go('smartExam')");
  check('tapping the card opens the exam page', ev('state.screen'), 'smartExam');
  check('intro shows questions + time', [view().includes('3 questions'), view().includes('10 minutes')], [true, true]);
  ev("sxStart()");
  check('exam started -> question 1', view().includes('Question 1'), true);
  check('clock is on screen', !!ev("document.getElementById('sxTime')"), true);
  check('tab bar hidden during the exam', ev("document.getElementById('tabbar').className").includes('hidden'), true);

  /* ---------- the lock ---------- */
  ev("go('home')");      check('locked: home is refused', ev('state.screen'), 'smartExam');
  ev("go('notes')");     check('locked: notes are refused', ev('state.screen'), 'smartExam');
  ev("tabTo('practice')"); check('locked: tabs cannot escape', ev('state.screen'), 'smartExam');
  ev("go('start')");     check('locked: START is refused', ev('state.screen'), 'smartExam');

  /* ---------- answering ---------- */
  ev("sxPick(0,'B')");
  check('a wrong tap is stored', ev('state.sx.ans[0]'), 'B');
  ev("sxPick(0,'A')");
  check('changing the answer works', ev('state.sx.ans[0]'), 'A');
  ev("sxGo(1)");
  check('moved to the written question', view().includes('Name two member states'), true);
  check('written question gets a typing box', view().includes('<textarea'), true);
  ev("sxAnswer(1,'Uganda and Kenya')");
  check('typed answer stored without a re-render', ev('state.sx.ans[1]'), 'Uganda and Kenya');
  ev("sxGo(2)");
  ev("sxPick(2,'A')");
  check('last question answered', ev('state.sx.ans[2]'), 'A');
  check('submit button on the last question', view().includes('SUBMIT'), true);

  /* ---------- submitting ---------- */
  await ev("(async()=>{ await sxSubmit(false); return 1; })()");
  check('both auto-marked questions correct -> 100%', ev('state.sx.score'), 100);
  check('results screen shown', view().includes('Exam submitted'), true);
  check('written answer flagged for the teacher', view().includes('will mark this one'), true);
  const calls = ev("JSON.stringify(window.__calls)");
  check('assignment set to completed (the DB\'s own word)', calls.includes('"table":"smartple_exam_assignments"') && calls.includes('"status":"completed"'), true);
  check('score written back', calls.includes('"score":100'), true);
  check('answers logged to learning_events', calls.includes('"table":"learning_events"') && calls.includes('exam_submitted'), true);
  ev("go('home')");
  check('unlocked after submitting', ev('state.screen'), 'home');
  check('exam card gone from home once done', view().includes('NEW EXAM'), false);

  /* ---------- the teacher releases an exam mid-way ---------- */
  ev("state.sx=null; window.__ea=" + JSON.stringify(ASSIGN));
  await sync();
  ev("go('smartExam')");
  check('learner is back in the exam', ev('state.screen'), 'smartExam');
  ev("window.__ea=null");
  await sync();                                  /* the 15-second poll lands */
  check('release mid-exam sends the learner home', ev('state.screen'), 'home');

  console.log(`\n${n - fails}/${n} checks passed`);
  process.exit(fails ? 1 : 0);
})();

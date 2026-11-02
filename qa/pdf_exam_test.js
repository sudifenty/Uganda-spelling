/* pdf_exam_test.js — a UNEB paper exam: the paper shape, boxes placed at the
   owner's coordinates, typed answers, auto-marked MCQ boxes, submit.

   pdf.js cannot run in jsdom, so pdfLoad is stubbed to fail — which is also
   the real offline path, and must stay graceful (no "FAILED" on screen).

   Usage:  node qa/pdf_exam_test.js [path/to/index.html]
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
  id: 2, title: 'UNEB 2010 SST · Section A', subject: 'SST', duration_minutes: 30,
  questions: {
    kind: 'pdf', pdf_path: 'abc123-uneb-2010-sst.pdf',
    boxes: [
      { id: 'b1', page: 1, x: 0.1, y: 0.2, w: 0.4, h: 0.05, type: 'text', n: 1, marks: 5, label: '(a) Name the longest river' },
      { id: 'b2', page: 1, x: 0.55, y: 0.2, w: 0.35, h: 0.05, type: 'mcq', n: 2, marks: 1, options: ['Kampala', 'Nairobi', 'Kigali', 'Dodoma'], answer: 'A' },
      { id: 'b3', page: 2, x: 0.1, y: 0.1, w: 0.8, h: 0.08, type: 'text', n: 3, marks: 4, label: '(b) Explain one benefit' }
    ]
  }
};
const ASSIGN = { id: 'as2', exam_id: 2, user_id: 'learner-1', status: 'locked', score: null };

const STUB = `
window.__row={id:'a1',user_id:'learner-1',allow_notes:true,allow_practice_with_answers:true,allow_practice_no_answers:true};
window.__exam=${JSON.stringify(EXAM)}; window.__ea=${JSON.stringify(ASSIGN)}; window.__calls=[];
supabaseClient={ from(t){ const q={ select:()=>q, eq:()=>q, in:()=>q, order:()=>q,
  insert:(r)=>{window.__calls.push({table:t,insert:r});return q;},
  update:(p)=>{window.__calls.push({table:t,payload:p});return q;},
  limit:()=>Promise.resolve({data: t==='smartple_assignments'?[window.__row]:
     t==='smartple_exams'?[window.__exam]: t==='smartple_exam_assignments'?[window.__ea]:[], error:null}) }; return q; },
  storage:{ from(){ return { createSignedUrl:()=>Promise.resolve({data:null,error:{message:'bucket exam-pdfs not found'}}) }; } } };
pdfLoad = async()=>{ throw new Error('pdf.js is not available offline'); };
state.authUser={id:'learner-1',email:'kid@example.com'}; state.authReady=true; state.adminOk=false;
state.klass='P6'; state.stack=[]; state.screen='home'; state.sx=null; state.sxPages=0; state.sxErr=null; render();
`;

(async () => {
  console.log('app file: ' + FILE + '\n');
  ev(STUB);
  await ev("(async()=>{ await rcFetch(); return 1; })()");
  ev("state.screen='home'; render()");
  check('PDF exam card on home', view().includes('UNEB 2010 SST'), true);
  ev("go('smartExam')");
  check('intro counts answer boxes, not questions', view().includes('3 answer boxes on the paper'), true);

  ev("sxStart()");
  await new Promise(r => setTimeout(r, 60));           /* let sxRenderPdf fail */
  check('runner opens on the paper', ev('state.screen'), 'smartExam');
  check('a paper that cannot load says so politely', view().includes('Try again'), true);
  check('no FAILED text anywhere', view().includes('FAILED'), false);
  check('the reason is shown', ev('state.sxErr').length > 0, true);

  /* the pages are painted: check the boxes land where the owner drew them */
  ev("state.sxErr=null; state.sxPages=2; render()");
  const html = view();
  check('both pages rendered', [html.includes('id="sxpdf1"'), html.includes('id="sxpdf2"')], [true, true]);
  check('text box at the owner\'s coordinates', html.includes('left:10.000%;top:20.000%;width:40.000%;height:5.000%'), true);
  check('written box is a real input', html.includes('<textarea'), true);
  check('MCQ box offers A–D', ['>A<', '>B<', '>C<', '>D<'].every(x => html.includes(x)), true);
  check('page 2 carries its own box', html.includes('placeholder="Q3"'), true);
  check('locked: cannot leave the paper', (ev("go('home')"), ev('state.screen')), 'smartExam');

  /* answering on the paper */
  ev("sxAnswer(0,'The Nile')");
  check('typed into box 1', ev('state.sx.ans[0]'), 'The Nile');
  ev("sxPick(1,'A')");
  check('MCQ box tapped', ev('state.sx.ans[1]'), 'A');
  ev("sxAnswer(2,'Trade between countries')");
  ev("render()");   /* sxAnswer never re-renders while typing, so refresh to read the counter */
  check('progress counts answered boxes', view().includes('3 of 3 answered'), true);

  await ev("(async()=>{ await sxSubmit(false); return 1; })()");
  check('the auto-marked box scored 100%', ev('state.sx.score'), 100);
  check('two written boxes go to the teacher', ev('state.sx.pending'), 2);
  check('results tell the learner that', view().includes('2 written answers'), true);
  const calls = ev("JSON.stringify(window.__calls)");
  check('assignment completed with the score', calls.includes('"status":"completed"') && calls.includes('"score":100'), true);
  check('answers logged for marking', calls.includes('"table":"learning_events"'), true);
  ev("go('home')");
  check('unlocked after submitting', ev('state.screen'), 'home');

  console.log(`\n${n - fails}/${n} checks passed`);
  process.exit(fails ? 1 : 0);
})();

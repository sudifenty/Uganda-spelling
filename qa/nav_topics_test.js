/* nav_topics_test.js — runs the REAL app file (ple-app/index.html) inside
   jsdom and walks the navigation paths that matter:

     student: Home -> START -> SST -> learning path -> back  == home
     student: Notes tab / any old route to the topics list  == learning path
     owner  : #admin + PIN -> "Open the topic list"         == topics list

   Usage:  node qa/nav_topics_test.js [path/to/index.html]
   Needs:  npm install jsdom   (in /tmp/navtest by default)
*/
const fs = require('fs');
const JSDOM_PATH = process.env.JSDOM || '/tmp/navtest/node_modules/jsdom';
const { JSDOM } = require(JSDOM_PATH);

const FILE = process.argv[2] || '/home/user/Uganda-spelling/ple-app/index.html';
const html = fs.readFileSync(FILE, 'utf8');
const dom = new JSDOM(html, {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://example.test/'
});
const w = dom.window;
w.addEventListener('error', e => console.log('  (page error) ' + e.message));

let fails = 0, n = 0;
function check(name, actual, expected) {
  n++;
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (!ok) fails++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}\n      got ${JSON.stringify(actual)}${ok ? '' : '  expected ' + JSON.stringify(expected)}`);
}
const ev = code => w.eval(code);
const view = () => ev("document.getElementById('views').innerHTML");

setTimeout(() => {
  console.log('app file: ' + FILE + '  (' + (html.length / 1e6).toFixed(2) + ' MB)\n');

  /* ---- a signed-in learner, fresh device, nothing unlocked ---- */
  ev(`state.authUser={id:'learner-1',email:'kid@example.com'}; state.authReady=true;
      state.adminOk=false; state.klass='P6'; state.nsubject='SST';
      state.ntopic=null; state.stack=[]; state.tab='home'; state.screen='home'; render();`);

  /* 1. the exact walk the owner described: Home -> START -> SST -> path -> back */
  ev("go('start')");
  check('START opens Choose Subject', ev('state.screen'), 'start');
  ev("startSubject('SST')");
  check('SST opens the learning path', ev('state.screen'), 'notePath');
  check('path picked a real topic', /_SST_T\d\d/.test(String(ev('state.ntopic'))), true);
  check('path screen shows the back button wired to pathBack()', view().includes('onclick="pathBack()"'), true);
  ev('pathBack()');
  check('BACK from the learning path goes home (not the topics list)', ev('state.screen'), 'home');

  /* 2. every old route into the topics list now lands on the path */
  ev("go('notes')");
  check("student go('notes') -> learning path", ev('state.screen'), 'notePath');
  check("student view has no topic-list header", view().includes('Study Notes'), false);
  check("student view has no topic cards", view().includes('class="tcard"'), false);
  ev("tabTo('notes')");
  check("student Notes tab -> learning path", ev('state.screen'), 'notePath');
  ev("state.nsubject='SST'; setNoteSubject('SST')");
  check("student subject chip -> learning path", ev('state.screen'), 'notePath');

  /* 3. no topics at all: Choose Subject, never the owner's list */
  ev("state.ntopic=null; state.nsubject='NONE'; go('notes')");
  check('student with no topics -> Choose Subject', ev('state.screen'), 'start');

  /* 4. fallback screens never hand a learner the topics list */
  ev("state.adminOk=false; state.nsubject='SST'; state.ntopic=null; state.njourney=null; go('noteJourney')");
  check('noteJourney fallback renders the path, not the list', view().includes('class="tcard"'), false);
  ev("state.ntopic=null; go('noteSub')");
  check('noteSub fallback renders the path, not the list', view().includes('class="tcard"'), false);

  /* 5. the owner still gets the full topic list */
  ev("state.adminOk=true; state.screen='admin'; state.adminRows=[]; render()");
  check('admin screen offers "Open the topic list"', view().includes('adminTopics()'), true);
  ev("adminTopics()");
  check('owner adminTopics() -> topics list', ev('state.screen'), 'notes');
  check('owner sees every topic (East African Community)', view().includes('The East African Community'), true);
  check('owner sees the topic cards', view().includes('class="tcard"'), true);
  ev("state.ntopic='P6_SST_T01'; go('notePath'); pathBack()");
  check('owner BACK from the path -> topics list', ev('state.screen'), 'notes');
  ev("go('noteTopic')");
  check('owner can still open a topic to set questions', ev('state.screen'), 'noteTopic');

  console.log(`\n${n - fails}/${n} checks passed`);
  process.exit(fails ? 1 : 0);
}, 800);

/* subtopic_lock_test.js — a teacher can lock a learner into one topic, or into
   one subtopic inside it, and the rest of the content disappears.
   Driven through the real functions the app uses to build its lists. */
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

setTimeout(function () {
  try {
    ev(`supabaseClient = { from(){ const q={select:()=>q,eq:()=>q,order:()=>q,limit:()=>q,
          then:(f,r)=>Promise.resolve({data:[],error:null}).then(f,r)}; return q; } };
        state.authUser = { id: 'learner-1' };
        state.adminOk = false;
        spPaid = () => true;
        state.klass = 'P4'; state.nsubject = 'SST'; state.psubject = 'SST';`);

    /* ---- baseline: nothing locked ---- */
    const allTopics = ev(`notesFor('P4','SST').topics.length`);
    const allSubs   = ev(`(function(){ const b=notesFor('P4','SST');
                          const t=b.topics.find(x=>x.title==='People in Our District');
                          return noteSections(t).length; })()`);
    check('before any lock the learner sees every P4 SST topic', allTopics > 1, true);
    check('that topic has more than one subtopic to choose from', allSubs > 1, true);
    const allPb = ev(`Object.keys(pbTopics('P4')).length`);
    check('practice offers more than one topic', allPb > 1, true);

    /* ---- lock to a single SUBTOPIC ---- */
    ev(`rcApply({ forced_class:'P4', forced_subject:'SST',
                  forced_topic:'People in Our District',
                  forced_subtopic:'1. PEOPLE IN OUR DISTRICT',
                  allow_notes:true, allow_practice_with_answers:true,
                  allow_practice_no_answers:true });
        rcForce();`);

    check('the topic lock is picked up', ev(`RC.topic`), 'People in Our District');
    check('the subtopic lock is picked up', ev(`RC.subtopic`), '1. PEOPLE IN OUR DISTRICT');
    check('the learner is placed inside the locked topic',
      ev(`(function(){ const t=noteById(state.ntopic); return t && t.title; })()`),
      'People in Our District');
    check('they start at the locked subtopic', ev(`state.nsec`), 0);

    check('every other topic has disappeared from the notes list',
      ev(`notesFor('P4','SST').topics.length`), 1);
    check('the one topic left is the locked one',
      ev(`notesFor('P4','SST').topics[0].title`), 'People in Our District');

    check('every other subtopic has disappeared',
      ev(`(function(){ const t=noteById(state.ntopic); return noteSections(t).length; })()`), 1);
    check('the one subtopic left is the locked one',
      ev(`(function(){ const t=noteById(state.ntopic); return noteSections(t)[0].title; })()`),
      '1. PEOPLE IN OUR DISTRICT');

    /* the practice banks use their own topic names, so a subtopic lock hides
       practice outright rather than guessing which topic it belongs to */
    check('a subtopic lock hides the practice screen',
      ev(`rcScreenDenied('ptopics')`), 'pwa');
    check('a subtopic lock hides the written exercises',
      ev(`rcScreenDenied('exercises')`), 'pna');
    check('a subtopic lock hides the past papers',
      ev(`rcScreenDenied('papers')`), 'pna');
    check('the locked notes screen itself stays reachable',
      ev(`rcScreenDenied('noteRead')`), null);

    /* ---- the owner is never locked out ---- */
    ev(`state.adminOk = true;`);
    check('the owner still sees every topic',
      ev(`notesFor('P4','SST').topics.length`), allTopics);
    check('the owner still sees every subtopic',
      ev(`(function(){ const b=notesFor('P4','SST');
            const t=b.topics.find(x=>x.title==='People in Our District');
            return noteSections(t).length; })()`), allSubs);

    check('the owner can still open practice while a learner is locked',
      ev(`rcScreenDenied('ptopics')`), null);

    /* ---- a stale or mistyped name must not lock the learner out ---- */
    ev(`state.adminOk = false;
        rcApply({ forced_class:'P4', forced_subject:'SST',
                  forced_topic:'A topic that was renamed last term',
                  forced_subtopic:'9. Nothing here',
                  allow_notes:true, allow_practice_with_answers:true,
                  allow_practice_no_answers:true });
        rcForce();`);
    check('an unmatched topic name leaves the whole subject reachable',
      ev(`notesFor('P4','SST').topics.length`), allTopics);
    check('an unmatched subtopic name leaves the whole topic reachable',
      ev(`(function(){ const b=notesFor('P4','SST');
            const t=b.topics.find(x=>x.title==='People in Our District');
            return noteSections(t).length; })()`), allSubs);

    /* ---- locking by topic id works as well as by title ---- */
    ev(`rcApply({ forced_class:'P4', forced_subject:'SST', forced_topic:'P4_SST_T07',
                  forced_subtopic:null,
                  allow_notes:true, allow_practice_with_answers:true,
                  allow_practice_no_answers:true });
        rcForce();`);
    check('a topic id locks just as well as a title',
      ev(`notesFor('P4','SST').topics[0].id`), 'P4_SST_T07');

    /* ---- clearing the lock gives everything back ---- */
    ev(`rcApply(null); rcForce();`);
    check('clearing the lock restores every topic',
      ev(`notesFor('P4','SST').topics.length`), allTopics);
    check('clearing the lock brings practice back',
      ev(`rcScreenDenied('ptopics')`), null);
    check('clearing the lock restores every subtopic',
      ev(`(function(){ const b=notesFor('P4','SST');
            const t=b.topics.find(x=>x.title==='People in Our District');
            return noteSections(t).length; })()`), allSubs);

    done();
  } catch (e) {
    console.error('THREW: ' + e.stack);
    done();
  }
}, 500);

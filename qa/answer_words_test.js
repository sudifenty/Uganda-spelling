/* answer_words_test.js — the teacher sees the WORDS the student chose, not a letter.
 *
 * The admin Answers page reads learning_events.details, so this test captures the
 * rows the phone hands to supabase .insert() — that is exactly what the teacher
 * will read. Two flows are covered:
 *   - exam runner  (sxSubmit)  -> event_type 'exam_submitted'
 *   - practice run (pFinish)   -> event_type 'practice_submitted'
 */
'use strict';
const fs = require('fs');
const FILE = process.argv[2] || __dirname + '/../Uganda-spelling/ple-app/index.html';
const { JSDOM } = require('/tmp/navtest/node_modules/jsdom');

const dom = new JSDOM(fs.readFileSync(FILE, 'utf8'), {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://example.test/'
});
const w = dom.window;
const ev = c => w.eval(c);
const checks = [];
const check = (name, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  checks.push({ name, got, want, ok });
  console.log((ok ? 'PASS  ' : 'FAIL  ') + name + '\n      got ' + JSON.stringify(got) + '  expected ' + JSON.stringify(want));
};

const done = () => {
  const bad = checks.filter(c => !c.ok).length;
  console.log('\n' + (checks.length - bad) + '/' + checks.length + ' checks passed');
  process.exit(bad ? 1 : 0);
};

/* A supabase stub that RECORDS every row handed to insert() — i.e. everything
 * that would land in learning_events — instead of pretending to send it. */
function wireSupabase() {
  ev(`window.__sent = [];
      supabaseClient = { from(t){
        const q = { select:()=>q, eq:()=>q, order:()=>q, limit:()=>q,
                    update:()=>q,                       /* .update().eq().eq() must stay chainable */
                    insert:(rows)=>{ (Array.isArray(rows)?rows:[rows]).forEach(r=>window.__sent.push(r));
                                     return Promise.resolve({error:null}); } };
        return q; } };
      state.authUser = { id: 'learner-1' };`);
}
const sent = type => ev(`window.__sent.filter(r => r.event_type === ${JSON.stringify(type)})`);

setTimeout(function () {
  try {
    /* ============ 1. the exam runner stores the chosen option in words ===== */
    wireSupabase();
    ev(`RC.examId = 77; RC.exam = { title: 'Morning paper' };
        state.sx = {
          qs: [
            { text: 'What is meant by Trade?', kind: 'mcq',
              options: ['Farming only', 'The buying and selling of goods and services',
                        'Building roads', 'Fishing in lakes'],
              answer: 'B', marks: 1 },
            { text: 'State one country in the East African Community.', kind: 'short',
              answer: 'Kenya', marks: 2 },
            { text: 'Name the currency used in Kenya.', kind: 'short', answer: 'Kenya shilling', marks: 1 }
          ],
          ans: ['B', 'Countries in one region working together for common goals', ''],
          done: false, i: 0, detail: null
        };`);
    check('option B is the second option in the list',
      ev(`state.sx.qs[0].options['B'.charCodeAt(0) - 65]`),
      'The buying and selling of goods and services');

    ev(`window.__p1 = sxSubmit(false);`);
    setTimeout(function () {
      const evs = sent('exam_submitted');
      check('submitting the exam produced one event', evs.length, 1);
      if (!evs.length) return done();
      const d = evs[0].details;
      check('the MCQ answer carries the option they chose, in words',
        d.answers[0].given_text, 'B. The buying and selling of goods and services');
      check('the letter is still there too, for marking', d.answers[0].given, 'B');
      check('the model answer is words as well, so the teacher can compare',
        d.answers[0].answer_text, 'B. The buying and selling of goods and services');
      check('a written answer keeps exactly what they typed',
        d.answers[1].given_text, 'Countries in one region working together for common goals');
      check('a blank stays blank rather than becoming a word', d.answers[2].given_text, '');

      /* ============ 2. the practice run stores the words too ============== */
      wireSupabase();
      ev(`state.klass = 'P6';
          spPaid = () => true;
          startPractice('quick');`);
      const total = ev(`state.session ? state.session.total : 0`);
      check('a practice session started', total > 0, true);
      check('it is the practice-question screen the learner sees', ev(`state.screen`), 'pquestion');
      if (!total) return done();

      for (let i = 0; i < total; i++) {
        ev(`state.session.i = ${i};
            const s = state.session, q = s.items[s.i];
            if (q.renderAs === 'fill') { pFinishItem(true, q, 'my typed answer'); }
            else if (q.renderAs === 'match') { q.pairs.forEach((pr, k) => { s.matches[k] = pr[1]; });
                                               pMatchCheck(); }
            else { pAnswer(0); }
            pNext();`);
      }
      check('finishing practice produced one practice_submitted event', sent('practice_submitted').length, 1);
      const p = sent('practice_submitted');
      if (p.length) {
        const pd = p[0].details;
        check('every practice answer is recorded', pd.answers.length, total);
        check('each one says what they chose, in words',
          pd.answers.every(a => typeof a.given === 'string' && a.given.length > 0 && !/^[A-D]$/.test(a.given)), true);
        check('the question text travels with it', pd.answers.every(a => typeof a.q === 'string' && a.q.length), true);
        check('the right answer travels with it, in words',
          pd.answers.every(a => typeof a.answer === 'string' && !/^[A-D]$/.test(a.answer)), true);
        check('the run total is included', pd.max, total);
        console.log('\nsample practice answer -> ' + JSON.stringify(pd.answers[0]));
      }

      /* ============ 3. offline: nothing is lost =========================== */
      ev(`window.__sent = []; supabaseClient = null;
          RC.examId = 78; RC.exam = { title: 'Offline paper' };
          state.sx = { qs: [{ text: 'Q?', kind: 'mcq', options: ['a', 'b', 'c', 'd'], answer: 'B', marks: 1 }],
                       ans: ['B'], done: false, i: 0, detail: null };`);
      ev(`window.__p3 = sxSubmit(false);`);
      setTimeout(function () {
        check('with no connection the words wait in the queue instead of vanishing',
          ev(`ACT_QUEUE.filter(r => r.event_type === 'exam_submitted').length >= 1`), true);
        check('they are kept, not dropped when the queue fills',
          ev(`ACT_QUEUE.filter(r => r.event_type === 'exam_submitted').every(r => r.keep === true)`), true);
        check('they survive a restart of the app, via localStorage',
          ev(`(function(){ const raw = JSON.parse(localStorage.getItem('sp_act_queue') || '[]');
                           return raw.some(r => r.event_type === 'exam_submitted'); })()`), true);
        ev(`ACT_QUEUE.length = 0; trackActivity('screen_view', { screen: 'home' });`);
        check('a disposable screen view is still not queued with no connection',
          ev(`ACT_QUEUE.length`), 0);
        done();
      }, 60);
    }, 60);
  } catch (e) {
    console.error('THREW: ' + e.stack);
    done();
  }
}, 400);

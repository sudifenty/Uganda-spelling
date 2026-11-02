/* approve_test.js — approving a payment must SAY what happened.
 *
 * adminApprove() used to wrap all four of its writes in try{}catch(e){} and
 * throw the results away. supabase-js does not throw on a rejected write, it
 * returns {error}, so the catch never fired AND the error was never read. The
 * function then toasted "Approved - the learner unlocks on their next sync"
 * unconditionally. That is how a CHECK-constraint rejection on status stayed
 * invisible: every approval looked fine and nobody unlocked.
 *
 * These tests drive adminApprove with a stub that returns whatever the database
 * would, and assert on what the owner is told.
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
  checks.push({ name, ok });
  console.log((ok ? 'PASS  ' : 'FAIL  ') + name + '\n      got ' + JSON.stringify(got) + '  expected ' + JSON.stringify(want));
};

/* a supabase stub whose every write resolves to `responder(table)` */
const stub = `responder => {
  supabaseClient = { from(t){
    const q = { update:()=>q, upsert:()=>q, insert:()=>q, select:()=>q,
                eq:()=>q, in:()=>q, order:()=>q, limit:()=>q,
                then:(f,r)=>Promise.resolve(responder(t)).then(f,r) };
    return q; } };
}`;

setTimeout(async () => {
  /* the owner is standing in the approve list with one pending payment */
  ev(`state.adminRows=[{id:7, phone:'+256700000000', user_id:'u-1'}]; state.adminErr='';`);
  ev(`var __toasts=[]; toast = m => __toasts.push(String(m));`);
  ev(`adminLoad = () => {};`);   /* keep the reload out of the way */

  /* ---- 1. the database rejects the unlock ------------------------------ */
  ev('(' + stub + `)((t) => t==='smartple_profiles'
        ? {data:[], error:{message:'new row for relation "smartple_profiles" violates check constraint'}}
        : {data:[], error:null});`);
  await ev('adminApprove(7,"u-1")');

  check('a rejected write is reported, not swallowed',
    ev(`/violates check constraint/.test(state.adminErr)`), true);
  check('and it says nobody was unlocked',
    ev(`/nobody was unlocked/i.test(state.adminErr)`), true);
  check('the success toast is NOT shown',
    ev(`__toasts.some(t=>/unlocks on their next sync/.test(t))`), false);
  check('the owner is told it did not work',
    ev(`__toasts.some(t=>/Not approved/i.test(t))`), true);

  /* ---- 2. the write succeeds ------------------------------------------- */
  ev(`__toasts=[]; state.adminErr='leftover';`);
  ev('(' + stub + `)((t) => t==='smartple_profiles'
        ? {data:[{user_id:'u-1'}], error:null}
        : {data:[], error:null});`);
  await ev('adminApprove(7,"u-1")');

  check('a successful approval says so',
    ev(`__toasts.some(t=>/unlocks on their next sync/.test(t))`), true);
  check('and clears any previous error', ev(`state.adminErr`), '');

  /* ---- 3. nothing matched at all: no silent "approved" ----------------- */
  ev(`__toasts=[]; state.adminErr='';`);
  ev('(' + stub + `)(() => ({data:[], error:null}));`);
  await ev('adminApprove(7,"u-1")');
  check('an approval that unlocks nobody is reported as a failure',
    ev(`/NOT approved/.test(state.adminErr)`), true);

  const failed = checks.filter(c => !c.ok);
  console.log(`\n${checks.length - failed.length}/${checks.length} checks passed`);
  process.exit(failed.length ? 1 : 0);
}, 1800);

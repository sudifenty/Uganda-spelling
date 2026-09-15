/* The status column on smartple_profiles carries CHECK (status in
   ('active','expired')) — installed by sql/student-management.sql.

   The phone app's payment unlock used to upsert status:'paid' into that table,
   and the write is wrapped in try{}catch(e){}, so the constraint rejected it
   SILENTLY: the learner saw "Approved — the learner unlocks on their next
   sync" and never unlocked. Confirmed against the live project: HTTP 400,
   code 23514 check_violation.

   This test reads the BUILT app and fails if any write to smartple_profiles
   carries a status outside the allowed set. It is static on purpose — the bug
   was invisible at runtime precisely because the error was swallowed. */
const fs = require('fs');
const path = require('path');

const APP = path.join(__dirname, '..', 'Uganda-spelling', 'ple-app', 'index.html');
const ALLOWED = ['active', 'expired'];

let pass = 0, fail = 0;
function check(name, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}`);
  if (!ok) { console.log(`      got ${JSON.stringify(got)}  expected ${JSON.stringify(want)}`); fail++; }
  else pass++;
}

const src = fs.readFileSync(APP, 'utf8');

/* every status literal in a write aimed at smartple_profiles. The write and the
   table are on the same statement, so matching within a window around each
   from('smartple_profiles') is enough and avoids catching other tables. */
function profileStatuses(text) {
  const out = [];
  const re = /from\('smartple_profiles'\)/g;
  let m;
  while ((m = re.exec(text))) {
    const window = text.slice(m.index, m.index + 400);
    /* stop at the end of the statement so a later table's status is not blamed */
    const cut = window.indexOf(';') > 0 ? window.slice(0, window.indexOf(';')) : window;
    for (const s of cut.matchAll(/status\s*:\s*'([^']+)'/g)) out.push(s[1]);
  }
  return out;
}

const found = profileStatuses(src);

check('the built app is the one on disk', /BUILD|<html/i.test(src.slice(0, 4000)), true);
check("no write to smartple_profiles uses status:'paid'", found.includes('paid'), false);
check('every status written to smartple_profiles is allowed',
  found.filter(s => !ALLOWED.includes(s)), []);
check('the unlock still writes a status at all (so the row is not left ambiguous)',
  found.length > 0, true);

/* the value it does write must be one the CHECK accepts */
check('the unlock writes an allowed status', found.every(s => ALLOWED.includes(s)), true);

console.log(`\n${pass}/${pass + fail} checks passed`);
process.exit(fail ? 1 : 0);

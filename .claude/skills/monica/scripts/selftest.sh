#!/usr/bin/env bash
# Live smoke test for the monica skill. Creates and fully removes ZZZ Selftest data.
set -u
S="$(dirname "$0")/monica"
pass=0; failn=0
step() { if "$@" >/tmp/monica-selftest-out.json 2>/tmp/monica-selftest-err.txt; then
  echo "PASS: $*"; pass=$((pass+1)); else
  echo "FAIL: $* -> $(cat /tmp/monica-selftest-err.txt)"; failn=$((failn+1)); fi }
jqid() { python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' </tmp/monica-selftest-out.json; }

step "$S" whoami
step "$S" contacts create --json '{"first_name":"ZZZ Selftest","last_name":"Alpha","birthdate":"1990-05-01"}'
A=$(jqid)
step "$S" contacts create --json '{"first_name":"ZZZ Selftest","last_name":"Beta"}'
B=$(jqid)
step "$S" contacts update "$A" --json '{"nickname":"Zed"}'
step "$S" fields add "$A" --type email --value zzz@example.com
step "$S" addresses add "$A" --json '{"name":"home","city":"Testville","country":"US"}'
step "$S" rel link "$A" --type friend --to "$B"
REL=$(jqid)
step "$S" notes add "$A" "selftest note"
step "$S" tags set "$A" zzz-selftest
step "$S" reminders add "$A" --title "zzz reminder" --date 2030-01-01
step "$S" tasks add "$A" --title "zzz task"
step "$S" rel unlink "$REL"
step "$S" tags unset "$A" zzz-selftest
step "$S" contacts delete "$A"
step "$S" contacts delete "$B"
echo "----"; echo "PASS=$pass FAIL=$failn"
[ "$failn" -eq 0 ]

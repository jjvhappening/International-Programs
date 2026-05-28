"""
Romania Risk Crawler — Register & Digest Eval Harness
Runs structural, regression, trend, and digest format evals.

Usage:
    # Validate register only (post-commit, compares against HEAD~1):
    python validate_register.py --auto-prev

    # Validate a digest message file before posting:
    python validate_register.py --digest digest.txt

    # Assert all qualifying risks have Notion pages (run after Step 6b):
    python validate_register.py --post-notion-sync

    # Full post-run validation:
    python validate_register.py --auto-prev --post-notion-sync

Exit codes:
    0 — all evals passed
    1 — one or more evals failed
"""
import sys, json, subprocess, argparse, os, re
from datetime import datetime, date
sys.stdout.reconfigure(encoding='utf-8')

REGISTER_PATH = os.path.join(os.path.dirname(__file__), 'risk-register.json')
VALID_STATUSES = {'open', 'Escalated', 'Resolved', 'Closed'}
VALID_TRENDS   = {'↑', '↓', '→', '🆕', 'up', 'down', 'stable', 'new'}
# Normalise word-based trends to arrow symbols for arithmetic comparisons
_TREND_NORM    = {'up': '↑', 'down': '↓', 'stable': '→', 'new': '🆕',
                  '↑': '↑', '↓': '↓', '→': '→', '🆕': '🆕'}
VALID_SEVERITIES = {'low', 'medium', 'high'}
MAX_SCORE = 30
REQUIRED_FIELDS = {'id', 'status', 'score', 'severity', 'occurrences', 'consecutive_misses', 'new_this_run'}


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def get_prev_register_from_git():
    """Fetch the most recent committed version of risk-register.json with a
    DIFFERENT run_number than the current working copy.

    Walks back through git history for this specific file until it finds a
    commit where run_number differs — handles the common case of multiple
    non-register commits landing after the run update (eval harness, cleanup, etc.).
    """
    repo_root = os.path.dirname(os.path.dirname(__file__))
    rel_path  = 'RO Migration to Betler/risk-register.json'

    # Load current run_number for comparison
    try:
        current_run = load_json(REGISTER_PATH).get('run_number')
    except Exception:
        current_run = None

    # Get the list of commits that touched this file
    try:
        log = subprocess.run(
            ['git', 'log', '--format=%H', '--follow', '--', rel_path],
            cwd=repo_root, capture_output=True, text=True, encoding='utf-8'
        )
        commits = log.stdout.strip().splitlines()
    except Exception:
        return None

    for i, sha in enumerate(commits):
        try:
            result = subprocess.run(
                ['git', 'show', f'{sha}:{rel_path}'],
                cwd=repo_root, capture_output=True, text=True, encoding='utf-8'
            )
            if result.returncode != 0:
                continue
            data = json.loads(result.stdout)
            if current_run is None or data.get('run_number') != current_run:
                label = 'HEAD' if i == 0 else f'HEAD~{i} ({sha[:7]})'
                print(f"  (using {label} — run {data.get('run_number')} | {data.get('last_run')})")
                return data
        except Exception:
            continue
    return None


# ── Eval runner ────────────────────────────────────────────────────────────────

class EvalRunner:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def check(self, name, condition, detail=''):
        if condition:
            self.passed.append(name)
        else:
            self.failed.append((name, detail))

    def warn(self, name, detail):
        self.warnings.append((name, detail))

    def report(self):
        total = len(self.passed) + len(self.failed)
        print(f"\n{'═'*60}")
        print(f"  Register Eval — {total} checks")
        print(f"  ✅  {len(self.passed)} passed   ❌  {len(self.failed)} failed   ⚠️   {len(self.warnings)} warnings")
        print(f"{'═'*60}")
        if self.failed:
            print("\n❌ FAILURES:")
            for name, detail in self.failed:
                print(f"  FAIL  {name}")
                if detail:
                    print(f"        {detail}")
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for name, detail in self.warnings:
                print(f"  WARN  {name}")
                if detail:
                    print(f"        {detail}")
        if not self.failed and not self.warnings:
            print("\n  All checks passed. Register looks healthy.")
        print()
        return len(self.failed) == 0


# ── Structural evals ───────────────────────────────────────────────────────────

def run_structural(runner, data):
    """Validate the shape and values of the register without any comparison."""

    # Top-level fields
    runner.check('top-level.run_number is positive int',
                 isinstance(data.get('run_number'), int) and data['run_number'] > 0,
                 f"run_number={data.get('run_number')!r}")

    last_run = data.get('last_run', '')
    try:
        datetime.strptime(last_run, '%Y-%m-%d')
        runner.check('top-level.last_run is valid date', True)
    except ValueError:
        runner.check('top-level.last_run is valid date', False, f"last_run={last_run!r}")

    runner.check('top-level.risks is non-empty list',
                 isinstance(data.get('risks'), list) and len(data['risks']) > 0)

    # Per-risk checks
    seen_ids = set()
    for r in data.get('risks', []):
        rid = r.get('id', '?')

        # Duplicate IDs
        runner.check(f'{rid}.id is unique', rid not in seen_ids,
                     f"Duplicate risk ID: {rid}")
        seen_ids.add(rid)

        # Required fields present
        missing = REQUIRED_FIELDS - set(r.keys())
        runner.check(f'{rid}.required_fields', not missing,
                     f"Missing fields: {missing}")

        status = r.get('status', '')
        score  = r.get('score', -1)
        sev    = r.get('severity', '')
        trend  = r.get('trend', r.get('score_trend', ''))
        occ    = r.get('occurrences', -1)
        misses = r.get('consecutive_misses', -1)

        # Valid status
        runner.check(f'{rid}.status valid',
                     status in VALID_STATUSES,
                     f"status={status!r}")

        # Score range
        runner.check(f'{rid}.score in range',
                     isinstance(score, (int, float)) and 0 <= score <= MAX_SCORE,
                     f"score={score}")

        # Closed risks must have score=0
        if status == 'Closed':
            runner.check(f'{rid}.closed_has_score_0',
                         score == 0,
                         f"Closed risk has score={score}")

        # Escalated risks must have score >= 6
        if status == 'Escalated':
            runner.check(f'{rid}.escalated_score_threshold',
                         score >= 6,
                         f"Escalated risk has score={score} (threshold is 6)")

        # Valid severity
        if status != 'Closed':
            runner.check(f'{rid}.severity valid',
                         sev in VALID_SEVERITIES,
                         f"severity={sev!r}")

        # Severity vs score alignment
        if status != 'Closed':
            if score >= 6:
                runner.check(f'{rid}.severity_matches_score_high',
                             sev == 'high',
                             f"score={score} but severity={sev!r} (expected 'high')")
            elif score >= 3:
                runner.check(f'{rid}.severity_matches_score_medium',
                             sev in ('medium', 'high'),
                             f"score={score} but severity={sev!r} (expected 'medium' or 'high')")
            else:
                runner.check(f'{rid}.severity_matches_score_low',
                             sev == 'low',
                             f"score={score} but severity={sev!r} (expected 'low')")

        # Valid trend symbol
        runner.check(f'{rid}.trend valid',
                     trend in VALID_TRENDS,
                     f"trend={trend!r}")

        # Occurrences non-negative
        runner.check(f'{rid}.occurrences non-negative',
                     isinstance(occ, int) and occ >= 0,
                     f"occurrences={occ}")

        # Consecutive misses non-negative
        runner.check(f'{rid}.consecutive_misses non-negative',
                     isinstance(misses, int) and misses >= 0,
                     f"consecutive_misses={misses}")

        # Active risk must not have consecutive_misses > 0
        if status not in ('Closed', 'Resolved'):
            runner.check(f'{rid}.active_has_zero_misses',
                         misses == 0,
                         f"Active risk ({status}) has consecutive_misses={misses}")

        # new_this_run must be bool
        runner.check(f'{rid}.new_this_run is bool',
                     isinstance(r.get('new_this_run'), bool),
                     f"new_this_run={r.get('new_this_run')!r}")


# ── Regression evals (current vs previous) ────────────────────────────────────

def run_regression(runner, curr, prev):
    """Compare current register against previous committed version."""
    if prev is None:
        runner.warn('regression.prev_register', 'No previous register available — skipping regression evals')
        return

    prev_by_id = {r['id']: r for r in prev.get('risks', [])}
    curr_by_id = {r['id']: r for r in curr.get('risks', [])}

    # run_number should increment by exactly 1
    curr_run = curr.get('run_number', 0)
    prev_run = prev.get('run_number', 0)
    runner.check('regression.run_number incremented by 1',
                 curr_run == prev_run + 1,
                 f"Previous={prev_run}, current={curr_run}")

    for rid, r in curr_by_id.items():
        p = prev_by_id.get(rid)
        if p is None:
            continue  # new risk added this run — skip regression

        curr_score  = r.get('score', 0)
        prev_score  = p.get('score', 0)
        curr_status = r.get('status', '')
        prev_status = p.get('status', '')
        curr_occ    = r.get('occurrences', 0)
        prev_occ    = p.get('occurrences', 0)

        # Occurrences never decrease for active risks
        if curr_status not in ('Closed',):
            runner.check(f'regression.{rid}.occurrences_non_decreasing',
                         curr_occ >= prev_occ,
                         f"occurrences went {prev_occ}→{curr_occ}")

        # Score doesn't swing by more than 15 in a single run (extreme change flag)
        delta = abs(curr_score - prev_score)
        if delta > 15:
            runner.warn(f'regression.{rid}.extreme_score_change',
                        f"Score changed by {delta} ({prev_score}→{curr_score}) in one run — verify intentional")

        # A Closed risk stays Closed unless explicitly reopened (status moves to open, not Escalated directly)
        if prev_status == 'Closed' and curr_status == 'Escalated':
            runner.check(f'regression.{rid}.closed_to_escalated_direct',
                         False,
                         f"Risk jumped from Closed to Escalated without going through 'open' first")

        # A risk that was Closed and is now active should have consecutive_misses=0
        if prev_status == 'Closed' and curr_status in ('open', 'Escalated'):
            runner.check(f'regression.{rid}.reopened_misses_reset',
                         r.get('consecutive_misses', 0) == 0,
                         f"Reopened risk still has consecutive_misses={r.get('consecutive_misses')}")

    # No risks should have disappeared (unless we explicitly delete — we don't)
    disappeared = set(prev_by_id.keys()) - set(curr_by_id.keys())
    runner.check('regression.no_risks_deleted',
                 not disappeared,
                 f"These IDs were in previous register but not current: {disappeared}")


# ── Trend evals ────────────────────────────────────────────────────────────────

def run_trend(runner, data):
    """Assert that stored trend symbol matches score arithmetic."""
    for r in data.get('risks', []):
        rid = r.get('id', '?')
        status = r.get('status', '')
        trend  = r.get('trend', r.get('score_trend', ''))
        score  = r.get('score', 0)
        score_last = r.get('score_last_run', 0)

        # Skip closed risks (their trend is not meaningful)
        if status == 'Closed':
            continue

        # Normalise to arrow symbol for arithmetic comparison
        trend = _TREND_NORM.get(trend, trend)

        # Skip 🆕 (genuinely new or reopened this run with score=0→0)
        if trend == '🆕':
            continue

        # For reopened risks: score=0, score_last=0, trend=↑ is valid
        # Detect this by: both scores 0 and occurrences == 1 (or consecutive_misses was reset)
        # We can't detect "just reopened" cleanly without git comparison, so we allow ↑ when
        # score == 0 and score_last_run == 0 — this is an acceptable false-negative.
        if score == 0 and score_last == 0 and trend == '↑':
            # Assume this was a reopened risk — skip trend arithmetic check
            continue

        # Trend arithmetic
        if score > score_last:
            expected = '↑'
        elif score < score_last:
            expected = '↓'
        else:
            expected = '→'

        runner.check(f'trend.{rid}',
                     trend == expected,
                     f"score {score_last}→{score} should give trend='{expected}' but got '{trend}'")


# ── Notion sync evals ─────────────────────────────────────────────────────────

def run_notion_sync(runner, data):
    """Assert that every qualifying risk has a notion_page_id after Notion sync.

    Qualifying = severity == 'high' OR occurrences >= 2.
    Excludes Closed and Resolved risks (they don't require active Notion pages).
    """
    for r in data.get('risks', []):
        rid    = r.get('id', '?')
        status = r.get('status', '')
        sev    = r.get('severity', '')
        occ    = r.get('occurrences', 0)
        pid    = r.get('notion_page_id')

        if status in ('Closed', 'Resolved'):
            continue

        if sev == 'high' or occ >= 2:
            runner.check(
                f'notion_sync.{rid}.page_id_set',
                pid is not None and pid != '',
                f"severity={sev}, occurrences={occ}, status={status} — notion_page_id is null"
            )


# ── Digest eval ────────────────────────────────────────────────────────────────

# Matches a correctly markdown-linked Jira key: [PROJECT-123](https://...)
_LINKED_KEY  = re.compile(r'\[([A-Z][A-Z0-9]+-\d+)\]\(https?://[^\)]+\)')
# Matches any raw URL (to strip before bare-key scan)
_RAW_URL     = re.compile(r'https?://\S+')
# Matches any standalone Jira key pattern
_JIRA_KEY    = re.compile(r'\b([A-Z][A-Z0-9]+-\d+)\b')

# Project prefixes that are always primary subjects and MUST be linked in digests.
# Keys from other prefixes appearing only in descriptive bullets are flagged as
# warnings rather than failures — reviewers can decide whether to link them.
PRIMARY_BOARDS = {'PLAYER', 'GAM', 'SPORTS', 'PLT', 'DAP', 'SOC', 'TRX', 'FPT',
                  'MANAGE', 'CASH', 'BCN', 'CCD', 'PLYRTPM'}

# Prefixes that match the Jira key pattern but are NOT Jira issue keys.
# RR-XXX = internal risk register IDs; exclude from all hyperlink checks.
NON_JIRA_PREFIXES = {'RR'}


def _board(key: str) -> str:
    return key.rsplit('-', 1)[0]


def run_digest_eval(runner, message: str):
    """Check that ALL Jira keys in a Slack digest message are hyperlinked.

    Every Jira key — whether a headline issue, a supporting epic reference,
    or a sub-task mentioned in a description — must be a markdown link.
    No distinction between primary and secondary context: bare = FAIL.
    """
    # Collect correctly linked keys
    linked_keys = {m.group(1) for m in _LINKED_KEY.finditer(message)}

    # Strip all linked patterns and raw URLs, then scan for remaining bare keys
    stripped = _LINKED_KEY.sub('\x00', message)   # replace linked with null byte
    stripped = _RAW_URL.sub('\x00', stripped)      # strip raw URLs

    bare_keys = {m.group(1) for m in _JIRA_KEY.finditer(stripped)
                 if _board(m.group(1)) not in NON_JIRA_PREFIXES}
    unlinked  = bare_keys - linked_keys

    runner.check('digest.all_jira_keys_linked',
                 not unlinked,
                 f"Bare (unlinked) Jira keys: {sorted(unlinked)}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Validate risk-register.json and/or Slack digest')
    parser.add_argument('--prev',             default=None,  help='Path to previous register for regression checks')
    parser.add_argument('--auto-prev',        action='store_true', help='Fetch previous register from git HEAD~1')
    parser.add_argument('--register',         default=REGISTER_PATH, help='Register file path')
    parser.add_argument('--digest',           default=None,  help='Path to a text file containing the draft Slack digest')
    parser.add_argument('--post-notion-sync', action='store_true', help='Assert all qualifying risks have a notion_page_id')
    args = parser.parse_args()

    runner = EvalRunner()

    # ── Register evals ──
    print(f"\nLoading register: {args.register}")
    data = load_json(args.register)
    print(f"Run {data.get('run_number')} | {data.get('last_run')} | {len(data.get('risks', []))} risks")

    prev = None
    if args.prev:
        print(f"Loading previous register: {args.prev}")
        prev = load_json(args.prev)
    elif args.auto_prev:
        print("Fetching previous register from git HEAD...")
        prev = get_prev_register_from_git()
        if prev:
            print(f"  Found: run {prev.get('run_number')} | {prev.get('last_run')}")
        else:
            print("  Not available — skipping regression evals")

    print("\nRunning structural evals...")
    run_structural(runner, data)

    print("Running regression evals...")
    run_regression(runner, data, prev)

    print("Running trend evals...")
    run_trend(runner, data)

    if args.post_notion_sync:
        print("Running Notion sync evals...")
        run_notion_sync(runner, data)

    # ── Digest eval ──
    if args.digest:
        print(f"\nRunning digest eval: {args.digest}")
        with open(args.digest, encoding='utf-8') as f:
            digest_text = f.read()
        run_digest_eval(runner, digest_text)

    passed = runner.report()
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()

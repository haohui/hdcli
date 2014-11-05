import curses, sys, subprocess

curses.setupterm()
setaf = curses.tigetstr("setaf")

def log_info(s):
    print curses.tparm(setaf, 2) + s + curses.tparm(setaf, 7)

def call(args, cwd, stdin=None, stdout=None, dry_run=False):
    log_info('Executing `%s` at `%s`' % (' '.join(args), cwd))

    if dry_run:
        return

    p = subprocess.Popen(args, cwd=cwd, stdin=stdin, stdout=stdout)
    p.wait()
    if p.returncode != 0:
        raise Exception('Executing `%s` at `%s` failed, return code = %d' % (' '.join(args), cwd, p.returncode))
    return p

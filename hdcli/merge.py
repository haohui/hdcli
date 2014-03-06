#!/usr/bin/python

import argparse, os, re, subprocess, sys

def get_dir(conf, branch):
    repo_dir = conf['hadoop_repo_directory']
    if branch == 'trunk':
        return '%s/%s' % (repo_dir, 'trunk')
    else:
        return '%s/branches/%s' % (repo_dir, branch)

def get_svn_uri(conf, branch):
    svn_base_uri = conf['svn_base_uri']
    if branch == 'trunk':
        return '%s/%s' % (svn_base_uri, 'trunk')
    else:
        return '%s/branches/%s' % (svn_base_uri, branch)

class MergeSteps:
    def __init__(self, conf, revision, from_branch, to_branch):
        self.conf = conf
        self.revision = revision
        self.from_branch = from_branch
        self.to_branch = to_branch
        self.dry_run = False

    def call(self, args, cwd):
        print 'Executing `%s` at `%s`' % (' '.join(args), cwd)

        if self.dry_run:
            return

        p = subprocess.Popen(args, cwd=cwd)
        p.wait()
        if p.returncode != 0:
            raise Exception('Executing `%s` at `%s` failed, return code = %d' % (' '.join(args), cwd, p.returncode))

    def get_merge_msg(self):
        return "Merge r%d from %s." % (self.revision, self.from_branch)

    def svn_up(self):
        self.call([self.conf['svn_binary'], 'up'], cwd=get_dir(self.conf, self.to_branch))
        return self

    def svn_merge(self):
        args = [self.conf['svn_binary'], 'merge', '--ignore-ancestry', '-c', self.revision, get_svn_uri(self.conf, self.from_branch)]
        self.call(args, cwd=get_dir(self.conf, self.to_branch))
        return self

    def test_compile(self):
        args = self.conf['test_compile_command'].split(' ')
        self.call(args, cwd=get_dir(self.conf, self.to_branch))
        return self

    def svn_commit(self):
        args = [self.conf['svn_binary'], 'ci', '-m', 'Merge r%s from %s.' % (self.revision, self.from_branch)]
        self.call(args, cwd=get_dir(self.conf, self.to_branch))
        return self

    def run(self):
        self.svn_up().svn_merge().test_compile().svn_commit()

def run(conf, argv):
    argparser = argparse.ArgumentParser(description='Merge a changeset into a branch')
    argparser.add_argument('--from', metavar='<changeset>@<branch>', required=True, help='The location of the changeset.', dest='src')
    argparser.add_argument('--to', metavar='<target-branch>', required=True, help='The target branch of the merge.')
    argparser.add_argument('--dry-run', action='store_true', help='Perform a dry-run')
    args = argparser.parse_args(argv[1:])

    src = re.match('(\d+)@([0-9a-zA-Z\-_]+)', args.src)

    revision = ''
    from_branch = ''
    to_branch = args.to

    if src == None:
        argparser.print_help()
        sys.exit(-1)
    else:
        revision, from_branch = src.group(1, 2)

    work = MergeSteps(conf=conf, revision=revision, from_branch=from_branch, to_branch=to_branch)

    if args.dry_run:
        work.dry_run = True

    work.run()

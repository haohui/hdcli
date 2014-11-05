#!/usr/bin/python

import argparse, os, re, sys, subprocess
import util

class MergeSteps:
    def __init__(self, conf, changeset, to_branch):
        self.conf = conf
        self.changeset = changeset
        self.to_branch = to_branch
        self.dry_run = False
        self.verify_changeset = True
        self.cwd = conf['hadoop_repo_directory']
        self.head = None
        self.dirty_tree = False

    def call(self, args, cwd, stdout=None):
        return util.call(args, cwd, stdout=stdout, dry_run=self.dry_run)

    def git_revparse(self):
        p = self.call([self.conf['git_binary'], 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=self.cwd, stdout=subprocess.PIPE)
        if p != None:
            with p.stdout as f:
                self.head = f.read().strip()
        return self

    def git_stash(self):
        p = self.call([self.conf['git_binary'], 'status', '--porcelain', '--untracked-files=no'],
                      cwd=self.cwd, stdout=subprocess.PIPE)
        if p != None:
            with p.stdout as f:
                self.dirty_tree = len(f.read().strip()) != 0

        if self.dirty_tree:
            self.call([self.conf['git_binary'], 'stash'], cwd=self.cwd)

        return self

    def git_checkout(self):
        self.call([self.conf['git_binary'], 'checkout', self.to_branch], cwd=self.cwd)
        return self

    def git_pull(self):
        self.call([self.conf['git_binary'], 'pull', '--rebase'], cwd=self.cwd)
        return self

    def git_cherrypick(self):
        args = [self.conf['git_binary'], 'cherry-pick', self.changeset]
        self.call(args, cwd=self.cwd)
        return self

    def test_compile(self):
        args = self.conf['test_compile_command'].split(' ')
        if self.verify_changeset:
            self.call(args, cwd=self.cwd)
        return self

    def git_push(self):
        args = [self.conf['git_binary'], 'push', self.conf['git_repo_name'], self.to_branch]
        self.call(args, cwd=self.cwd)
        return self

    def git_unstash(self):
        if self.dirty_tree:
            self.call([self.conf['git_binary'], 'stash', 'pop'], cwd=self.cwd)
        return self

    def git_restore(self):
        if self.head:
            self.call([self.conf['git_binary'], 'checkout', self.head], cwd=self.cwd)
        return self

    def run(self):
        self.git_revparse().git_stash()
        self.git_checkout().git_pull().git_cherrypick().test_compile().git_push()
        self.git_unstash().git_restore()

def run(conf, argv):
    argparser = argparse.ArgumentParser(description='Merge a changeset into a branch')
    argparser.add_argument('--from', metavar='<changeset>', required=True, help='The changeset, which can be the name of the branch of the commit ID.', dest='changeset')
    argparser.add_argument('--to', metavar='<target-branch>', required=True, help='The target branch of the merge.')
    argparser.add_argument('--dry-run', action='store_true', help='Perform a dry-run')
    argparser.add_argument('--no-verify', action='store_true', help='Do not compile and verify the changeset.', dest='noverify')

    args = argparser.parse_args(argv[1:])

    to_branch = args.to

    work = MergeSteps(conf=conf, changeset=args.changeset, to_branch=to_branch)

    if args.dry_run:
        work.dry_run = True

    if args.noverify:
        work.verify_changeset = False

    work.run()

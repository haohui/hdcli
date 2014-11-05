#!/usr/bin/python

import argparse, os, requests, tempfile, quik
import util

class CommitSteps:
    def __init__(self, conf, issue):
        self.conf = conf
        self.issue = issue
        self.commit_msg = None
        self.resolve_info = None
        self.request_json = None

    def get_issue_info(self):
        url = '%s/rest/api/2/issue/%s?fields=summary,assignee' % (self.conf['jira_base_uri'], self.issue)
        r = requests.get(url)
        r.raise_for_status()
        self.issue_info = r.json()
        return self

    def gen_message(self):
        loader = quik.FileLoader(os.path.expanduser('~/.hdcli'))
        tmpl = loader.load_template('commit-msg.tmpl')
        self.commit_msg = tmpl.render(self.issue_info)
        return self

    def git_commit(self):
        tmp_file = tempfile.mkstemp(suffix='.txt')
        try:
            f = open(tmp_file[1], 'w')
            f.write(self.commit_msg)
            f.close()

            util.call([self.conf['git_binary'], 'commit', '-F', tmp_file[1], '-e'], cwd=self.conf['hadoop_repo_directory'])
            return self
        finally:
            os.remove(tmp_file[1])

    def run(self):
        self.get_issue_info().gen_message().git_commit()
        pass

def run(conf, argv):
    argparser = argparse.ArgumentParser(description='Commit the local changes locally')
    argparser.add_argument('--issue', required=True, help='The issue ID of the jira')
    args = argparser.parse_args(argv[1:])

    work = CommitSteps(conf=conf, issue=args.issue)
    work.run()

#!/usr/bin/python

import argparse, json, quik, os, requests, shutil, subprocess, sys, tempfile, yaml


class ResolveSteps:
    def __init__(self, conf, issue):
        self.conf = conf
        self.issue = issue
        self.yaml_content = None
        self.resolve_info = None
        self.request_json = None

    def get_issue_info(self):
        url = '%s/rest/api/2/issue/%s?fields=assignee,reporter' % (self.conf['jira_base_uri'], self.issue)
        r = requests.get(url)
        r.raise_for_status()
        self.issue_info = r.json()
        return self

    def edit_yaml(self):
        loader = quik.FileLoader(os.path.expanduser('~/.hdcli'))
        tmpl = loader.load_template('resolve-jira.yaml.tmpl')
        self.yaml_content = tmpl.render(self.issue_info)
        return self

    def run_editor(self):
        tmp_file = tempfile.mkstemp(suffix='.yaml')
        try:
            f = open(tmp_file[1], 'w')
            f.write(self.yaml_content)
            f.close()

            args = self.conf['editor'].split(' ')
            args.append(tmp_file[1])
            p = subprocess.Popen(args)
            p.wait()
            if p.returncode != 0:
                raise Exception('Failed to edit the comment')

            try:
                self.resolve_info = yaml.load(open(tmp_file[1], 'r'))
            except:
                raise Exception('Failed to edit the comment')

            if self.resolve_info == None:
                print 'Stop resolving the jira.'
                sys.exit(1)

            return self
        finally:
            os.remove(tmp_file[1])

    def gen_json(self):
        r = self.resolve_info
        # ID = 741 -> mark as resolved
        j = {'update': {}, 'transition': { 'id': '741'}}
        if 'comment' in r:
            j['update']['comment'] = [{'add': {'body': str.strip(r['comment'])}}]
        if 'fixVersions' in r:
            j['update']['fixVersions'] = [{'add': {'name': r['fixVersions']}}]

        if 'Hadoop flags' in r and len(r['Hadoop flags']) > 0:
            j['update']['customfield_12310191'] = map(lambda x : {'add': {'value': x}}, r['Hadoop flags'])

        self.request_json = json.dumps(j)
        return self

    def send_request(self):
        headers = { 'Content-Type': 'application/json' }
        cred = (self.conf['jira_username'], self.conf['jira_password'])
        url = '%s/rest/api/2/issue/%s/transitions' % (self.conf['jira_base_uri'], self.issue)

        print 'Resolving issue `%s`' % self.issue

        r = requests.post(url, auth=cred, headers=headers, data=self.request_json)
        if r.status_code != 204:
            raise Exception('Status code %d, Text: %s' % (r.status_code, r.text))

        return self
        
    def run(self):
        self.get_issue_info().edit_yaml().run_editor().gen_json().send_request()
        pass

def run(conf, argv):
    argparser = argparse.ArgumentParser(description='Resolving a jira')
    argparser.add_argument('--issue', required=True, help='The issue ID of the jira')
    args = argparser.parse_args(argv[1:])

    work = ResolveSteps(conf=conf, issue=args.issue)
    work.run()

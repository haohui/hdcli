#/usr/bin/python

import argparse, requests, sys

def run(conf, argv):
    argparser = argparse.ArgumentParser(description='Upload a file to a specific jira')
    argparser.add_argument('--issue', required=True, help='The issue ID of the jira')
    argparser.add_argument('-f', required=True, help='The file to be uploaded')

    args = argparser.parse_args(argv[1:])

    headers = { 'X-Atlassian-Token': 'nocheck' }
    cred = (conf['jira_username'], conf['jira_password'])

    url = '%s/rest/api/2/issue/%s/attachments' % (conf['jira_base_uri'], args.issue)
    print 'Posting `%s` to `%s`' % (args.f, url)

    r = requests.post(url, auth=cred, headers=headers, files={'file': open(args.f, 'rb') })

    if r.status_code != requests.codes.ok:
        raise Exception(r.text)

#! /usr/bin/env python3

import common, json, sys, urllib.request

def main():
  headers = common.github_headers()
  version = common.version()
  build_type = common.build_type()
  target = common.target()
  machine = common.machine()
  classifier = common.classifier()

  try:
    # Check current repository instead of JetBrains original
    repo_url = 'https://api.github.com/repos/' + common.github_repo() + '/releases/tags/' + version
    resp = urllib.request.urlopen(urllib.request.Request(repo_url, headers=headers)).read()
    artifacts = [x['name'] for x in json.loads(resp.decode('utf-8'))['assets']]
    zip = 'Skia-' + version + '-' + target + '-' + build_type + '-' + machine + classifier + '.zip'
    if zip in artifacts:
      print('> Artifact "' + zip + '" exists, stopping')
      return 1
    return 0
  except urllib.error.URLError as e:
    return 0

if __name__ == '__main__':
  sys.exit(main())

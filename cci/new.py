#!/usr/bin/env python

from __future__ import print_function
import argparse
import hashlib
import json
import os
import re
import requests
import tempfile
import sys
try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve


token = os.environ["GITHUB_TOKEN"]

ENDPOINT = "https://api.github.com/graphql"
headers = {"Authorization": "bearer %s" % token}

query = """
query {{
  repositoryOwner (login: "{organization}") {{
    repository(name: "{name}") {{
      description
      homepageUrl
      licenseInfo {{
        spdxId
      }}
      latestRelease {{
        tag {{
          name

          target {{
            ... on Commit {{

              tarballUrl
            }}
          }}
        }}

        releaseAssets(first: 100) {{
           totalCount
           edges {{
             node {{
               downloadUrl
             }}
           }}
        }}
      }}
      refs(refPrefix: "refs/tags/", orderBy: {{direction: DESC, field: TAG_COMMIT_DATE}}, first: 100) {{
        edges {{
          node {{
            name
          }}
        }}
      }}
      repositoryTopics(first: 100) {{
        edges {{
          node {{
             topic {{
                name
             }}
          }}
        }}
      }}
    }}
  }}
}}
"""

def graphql_query(query):
    data = {"query": query}
    response = requests.post(ENDPOINT, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise Exception("request failed with status %s" % response.status_code)
    data = json.loads(response.text)
    return data

def sha256file(filename):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def main():
    parser = argparse.ArgumentParser('cci.new')
    parser.add_argument('URI')
    args = parser.parse_args()

    uri = args.URI

    r = re.compile(r"https://github\.com/([\w-]+)/([\w-]+)")
    m = r.search(uri)
    if m:
        organization = m.group(1)
        name = m.group(2)
        print(organization, name)

        query1 = query.format(organization=organization, name=name)
        data = graphql_query(query1)
        print(data)

        info = data['data']['repositoryOwner']['repository']
        description = info['description']
        homepage = info['homepageUrl'] or uri
        license = 'FIXME'
        if 'licenseInfo' in info and info['licenseInfo'] and 'spdxId' in info['licenseInfo']:
            license = info['licenseInfo']['spdxId']
        print('description:', description)
        print('homepage:', homepage)
        print('license:', license)

        topics = info['repositoryTopics']['edges']
        topics = [t['node']['topic']['name'] for t in topics]
        topics = ", ".join(["'%s'" % t for t in topics])
        print('topics:', topics)
        print(info)

        if 'latestRelease' in info and info['latestRelease']:
            version = info['latestRelease']['tag']['name']
        else:
            versions = []
            for tag in info['refs']['edges']:
                tagname = tag['node']['name']
                if 'beta' not in tagname and 'rc' not in tagname:
                    versions.append(tagname)
            print(versions)
            version = versions[0]
        # FIXME? tar_url = info['latestRelease']['tag']['target']['tarballUrl']

        tar_url = uri + '/archive/refs/tags/%s.tar.gz' % version
        print("url", tar_url)

        if version.startswith('v'):
            version = version[1:]
        if version.startswith('%s-' % name):
            version = version[len(name) + 1:]

        filename = os.path.join(tempfile.mkdtemp(), 'temp.tar.gz')
        urlretrieve(tar_url, filename)

        print("version:", version)

        sha256 = sha256file(filename)
        print("sha256", sha256)
        os.unlink(filename)

        args = {'description': description,
                'homepage': homepage,
                'license': license,
                'topics': topics,
                'url': tar_url,
                'sha256': sha256}

        args = ['-d "%s=%s"' % (n, v) for n, v in args.items()]

        reference = '{name}/{version}'.format(name=name.lower(), version=version)
        new_command = "conan new {reference} -m cci.cmake ".format(reference=reference)
        new_command += ' '.join(args)

        print(new_command)
        os.system(new_command)

    else:
        print('the URL "%s" does not appear to be a valid GitHub URL' % url)
        sys.exit(1)
    pass

if __name__ == '__main__':
    main()

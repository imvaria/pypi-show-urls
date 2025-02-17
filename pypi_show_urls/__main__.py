# Copyright 2013 Donald Stufft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import itertools
import sys
try:  # for python 2
    import urlparse
    import xmlrpclib
except ImportError:
    import urllib.parse
    import xmlrpc.client

import html5lib
import requests

from pkg_resources import safe_name, parse_requirements
from setuptools.package_index import distros_for_url


def installable(project, url):
    normalized = safe_name(project).lower()
    return bool([dist for dist in distros_for_url(url) if safe_name(dist.project_name).lower() == normalized])


def version_for_url(project, url):
    normalized = safe_name(project).lower()
    return [dist for dist in distros_for_url(url) if safe_name(dist.project_name).lower() == normalized][0].version


def process_page(html, package, url, verbose, requirements):
    if verbose:
        print("")
        print("  Candidates from %s" % url)
        print("  ----------------" + ("-" * len(url)))

    installable_ = set()
    for link in html.findall(".//a"):
        if "href" in link.attrib:
            try:
                if sys.version_info[0] < 3:
                    absolute_link = urlparse.urljoin(url, link.attrib["href"])
                else:
                    absolute_link = urllib.parse.urljoin(url, link.attrib["href"])
            except Exception:
                continue

            if installable(package, absolute_link):
                # If we have a requirements mapping, make sure the candidate
                #   we found matches at least one of the specs
                if requirements is not None:
                    version = version_for_url(package, absolute_link)
                    if not any([version in req for req in requirements[package]]):
                        continue

                if verbose:
                    print("    " + absolute_link)
                installable_.add((url, absolute_link))

    if not verbose:
        print("  %s Candidates from %s" % (len(installable_), url))

    return installable_


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")

    group = parser.add_argument_group('index')
    group.add_argument("-i", "--index-url", dest="index_url", default="https://pypi.org", nargs='?')
    group = parser.add_argument_group('type')
    group.add_argument("-p", "--packages", dest="is_packages", action="store_true")
    group.add_argument("-u", "--users", dest="is_users", action="store_true")
    group.add_argument("-r", "--requirement-file", dest="requirement_file", action="store_true")

    parser.add_argument("items", nargs="+")

    args = parser.parse_args()

    if len(list(filter(None, [args.is_packages, args.is_users, args.requirement_file]))) > 1:
        return "Must specify only one of -u, -p, and -r"

    if not args.is_packages and not args.is_users and not args.requirement_file:
        return "Must specify one of -u, -p, or -r"

    if args.is_packages:
        # A list of packages to look for
        packages = args.items

    if args.is_users:
        # a list of users
        users = args.items
        if sys.version_info[0] < 3:
            serverproxy = xmlrpclib.ServerProxy(args.index_url)
        else:
            serverproxy = xmlrpc.client.ServerProxy(args.index_url)
        packages = []
        for user in users:
            packages.extend([x[1] for x in serverproxy.user_packages(user) if x[1] is not None])

    requirements = None
    if args.requirement_file:
        # a list of requirements files to process
        files = args.items
        packages = []
        requirements = {}
        for filename in files:
            with open(filename) as reqs_file:
                for req in parse_requirements(reqs_file):
                    requirements.setdefault(req.project_name, []).append(req)
                    packages.append(req.project_name)

    # Should we run in verbose mode
    verbose = args.verbose

    session = requests.sessions.Session()

    for package in packages:
        print("")
        print("Download candidates for %s" % package)
        print("========================" + ("=" * len(package)))

        # Grab the page from PyPI
        url = "%s/simple/%s/" % (args.index_url, package)
        resp = session.get(url)
        if resp.status_code == 404:
            continue
        resp.raise_for_status()

        html = html5lib.parse(resp.content, namespaceHTMLElements=False)

        spider = set()
        installable_ = set()

        for link in itertools.chain(
                            html.findall(".//a[@rel='download']"),
                            html.findall(".//a[@rel='homepage']")):
            if "href" in link.attrib:
                try:
                    if sys.version_info[0] < 3:
                        absolute_link = urlparse.urljoin(url, link.attrib["href"])
                    else:
                        absolute_link = urllib.parse.urljoin(url, link.attrib["href"])
                except Exception:
                    continue

                if not installable(package, absolute_link):
                    parsed = urlparse.urlparse(absolute_link)
                    if parsed.scheme.lower() in ["http", "https"]:
                        spider.add(absolute_link)

        # Find installable links from the PyPI page
        installable_ |= process_page(html, package, url, verbose, requirements)

        # Find installable links from pages we spider
        for link in spider:
            try:
                resp = session.get(link)
                resp.raise_for_status()
            except Exception:
                continue

            html = html5lib.parse(resp.content, namespaceHTMLElements=False)
            installable_ |= process_page(html, package, link, verbose, requirements)

        # Find the ones only available externally
        allversions = set()
        for candidate in installable_:
            version = version_for_url(package, candidate[1])
            allversions.add(version)

        # Display information
        if verbose:
            print("")
            print("  Versions available")
            print("  ------------------")

            for version in allversions:
                print("    " + version)
        else:
            print("  %s versions available" % len(allversions))


if __name__ == "__main__":
    sys.exit(main())

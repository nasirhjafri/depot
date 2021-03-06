#
# Author:: Noah Kantrowitz <noah@coderanger.net>
#
# Copyright 2014, Noah Kantrowitz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# Author:: Noah Kantrowitz <noah@coderanger.net>
#
# Copyright 2014, Noah Kantrowitz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import six

from .base import YumMeta, YumData


class YumOtherPackage(YumData):
    def __init__(self, pkgid, name, arch, *args, **kwargs):
        super(YumOtherPackage, self).__init__(*args, **kwargs)
        self.pkgid = pkgid
        self.name = name
        self.arch = arch
        self.changelogs = []

    def version_from_element(self, key, elm):
        return elm.attrib

    def changelog_from_element(self, key, elm):
        self.changelogs.append((elm.attrib, elm.text))
        return self.NoInsert

    def version_to_element(self, E, key, value):
        elm = E(key)
        for a_key, a_value in six.iteritems(value):
            elm.attrib[a_key] = a_value
        return elm

    def root_to_element(self, E, sub):
        for changelog_attrib, changelog_text in self.changelogs:
            elm = E.changelog(changelog_text)
            elm.attrib['author'] = changelog_attrib['author']
            elm.attrib['date'] = changelog_attrib['date']
            sub.append(elm)
        root = E.package(*sub)
        root.attrib['pkgid'] = self.pkgid
        root.attrib['name'] = self.name
        root.attrib['arch'] = self.arch
        return root


class YumOther(YumMeta):
    PackageClass = YumOtherPackage
    nsmap = {None: 'http://linux.duke.edu/metadata/other'}

    @classmethod
    def from_element(cls, root, *args, **kwargs):
        self = cls(*args, **kwargs)
        for elm in root.findall('{*}package'):
            pkg = self.PackageClass.from_element(elm)
            self[pkg.pkgid] = pkg  # Should this be a (name, arch, ver) tuple like YumPrimary?
        return self

    def to_element(self, E):
        return E.otherdata(*[pkg.to_element(E) for pkg in six.itervalues(self)], packages=str(len(self)))

# Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Provides OpenStack version generators

This module defines a class for OpenStack
version and package information
generators for generating the model in
:mod:`oslo_reports.models.version`.
"""

from oslo_reports.models import version as vm


class PackageReportGenerator:
    """A Package Information Data Generator

    This generator returns
    :class:`oslo_reports.models.version.PackageModel`,
    extracting data from the given version object, which should follow
    the general format defined in Nova's version information (i.e. it
    should contain the methods vendor_string, product_string, and
    version_string_with_package).

    :param version_object: the version information object
    """

    def __init__(self, version_obj):
        self.version_obj = version_obj

    def __call__(self):
        if hasattr(self.version_obj, "vendor_string"):
            vendor_string = self.version_obj.vendor_string()
        else:
            vendor_string = None

        if hasattr(self.version_obj, "product_string"):
            product_string = self.version_obj.product_string()
        else:
            product_string = None

        if hasattr(self.version_obj, "version_string_with_package"):
            version_string_with_package = self.version_obj.\
                version_string_with_package()
        else:
            version_string_with_package = None

        return vm.PackageModel(vendor_string, product_string,
                               version_string_with_package)

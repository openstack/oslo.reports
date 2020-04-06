# Copyright 2011 OpenStack Foundation.
# All Rights Reserved.
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

import threading
from unittest import mock

import greenlet
from oslo_config import cfg
from oslotest import base
import six

from oslo_reports.generators import conf as os_cgen
from oslo_reports.generators import threading as os_tgen
from oslo_reports.generators import version as os_pgen
from oslo_reports.models import threading as os_tmod


class TestOpenstackGenerators(base.BaseTestCase):
    def test_thread_generator(self):
        model = os_tgen.ThreadReportGenerator()()
        # self.assertGreaterEqual(len(model.keys()), 1)
        self.assertTrue(len(model.keys()) >= 1)
        was_ok = False
        for val in model.values():
            self.assertIsInstance(val, os_tmod.ThreadModel)
            self.assertIsNotNone(val.stack_trace)
            if val.thread_id == threading.current_thread().ident:
                was_ok = True
                break

        self.assertTrue(was_ok)

        model.set_current_view_type('text')
        self.assertIsNotNone(six.text_type(model))

    def test_thread_generator_tb(self):
        class FakeModel(object):
            def __init__(self, thread_id, tb):
                self.traceback = tb

        with mock.patch('oslo_reports.models'
                        '.threading.ThreadModel', FakeModel):
            model = os_tgen.ThreadReportGenerator("fake traceback")()
            curr_thread = model.get(threading.current_thread().ident, None)
            self.assertIsNotNone(curr_thread, None)
            self.assertEqual("fake traceback", curr_thread.traceback)

    def test_green_thread_generator(self):
        curr_g = greenlet.getcurrent()

        model = os_tgen.GreenThreadReportGenerator()()

        # self.assertGreaterEqual(len(model.keys()), 1)
        self.assertTrue(len(model.keys()) >= 1)

        was_ok = False
        for tm in model.values():
            if tm.stack_trace == os_tmod.StackTraceModel(curr_g.gr_frame):
                was_ok = True
                break
        self.assertTrue(was_ok)

        model.set_current_view_type('text')
        self.assertIsNotNone(six.text_type(model))

    def test_config_model(self):
        conf = cfg.ConfigOpts()
        conf.register_opt(cfg.StrOpt('crackers', default='triscuit'))
        conf.register_opt(cfg.StrOpt('secrets', secret=True,
                                     default='should not show'))
        conf.register_group(cfg.OptGroup('cheese', title='Cheese Info'))
        conf.register_opt(cfg.IntOpt('sharpness', default=1),
                          group='cheese')
        conf.register_opt(cfg.StrOpt('name', default='cheddar'),
                          group='cheese')
        conf.register_opt(cfg.BoolOpt('from_cow', default=True),
                          group='cheese')
        conf.register_opt(cfg.StrOpt('group_secrets', secret=True,
                                     default='should not show'),
                          group='cheese')

        model = os_cgen.ConfigReportGenerator(conf)()
        model.set_current_view_type('text')

        # oslo.config added a default config_source opt which gets included
        # in our output, but we also need to support older versions where that
        # wasn't the case.  This logic can be removed once the oslo.config
        # lower constraint becomes >=6.4.0.
        config_source_line = '  config_source = \n'
        try:
            conf.config_source
        except cfg.NoSuchOptError:
            config_source_line = ''

        target_str = ('\ncheese: \n'
                      '  from_cow = True\n'
                      '  group_secrets = ***\n'
                      '  name = cheddar\n'
                      '  sharpness = 1\n'
                      '\n'
                      'default: \n'
                      '%s'
                      '  crackers = triscuit\n'
                      '  secrets = ***') % config_source_line
        self.assertEqual(target_str, six.text_type(model))

    def test_package_report_generator(self):
        class VersionObj(object):
            def vendor_string(self):
                return 'Cheese Shoppe'

            def product_string(self):
                return 'Sharp Cheddar'

            def version_string_with_package(self):
                return '1.0.0'

        model = os_pgen.PackageReportGenerator(VersionObj())()
        model.set_current_view_type('text')

        target_str = ('product = Sharp Cheddar\n'
                      'vendor = Cheese Shoppe\n'
                      'version = 1.0.0')
        self.assertEqual(target_str, six.text_type(model))

    def test_package_report_generator_without_vendor_string(self):
        class VersionObj(object):
            def product_string(self):
                return 'Sharp Cheddar'

            def version_string_with_package(self):
                return '1.0.0'

        model = os_pgen.PackageReportGenerator(VersionObj())()
        model.set_current_view_type('text')

        target_str = ('product = Sharp Cheddar\n'
                      'vendor = None\n'
                      'version = 1.0.0')
        self.assertEqual(target_str, six.text_type(model))

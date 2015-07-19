# Copyright 2014 Red Hat, Inc.
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

"""Provides a process model

This module defines a class representing a process,
potentially with subprocesses.
"""

import psutil

import oslo_reports.models.with_default_views as mwdv
import oslo_reports.views.text.process as text_views

PS1 = psutil.version_info[0] == 1


class ProcessModel(mwdv.ModelWithDefaultViews):
    """A Process Model

    This model holds data about a process,
    including references to any subprocesses

    :param process: a :class:`psutil.Process` object
    """

    def __init__(self, process):
        super(ProcessModel, self).__init__(
            text_view=text_views.ProcessView())

        self['pid'] = process.pid
        self['parent_pid'] = (process.ppid if PS1 else process.ppid())
        if hasattr(process, 'uids'):
            self['uids'] = {
                'real': (process.uids.real if PS1 else process.uids().real),
                'effective': (process.uids.effective if PS1
                              else process.uids().effective),
                'saved': (process.uids.saved if PS1 else process.uids().saved)
            }
        else:
            self['uids'] = {'real': None,
                            'effective': None,
                            'saved': None}

        if hasattr(process, 'gids'):
            self['gids'] = {
                'real': (process.gids.real if PS1 else process.gids().real),
                'effective': (process.gids.effective if PS1
                              else process.gids().effective),
                'saved': (process.gids.saved if PS1 else process.gids().saved)
            }
        else:
            self['gids'] = {'real': None,
                            'effective': None,
                            'saved': None}

        self['username'] = process.username if PS1 else process.username()
        self['command'] = process.cmdline if PS1 else process.cmdline()
        self['state'] = process.status if PS1 else process.status()

        children = process.get_children() if PS1 else process.children()
        self['children'] = [ProcessModel(pr) for pr in children]

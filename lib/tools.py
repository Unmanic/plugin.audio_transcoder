#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    plugins.tools.py

    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     14 June 2026

    Copyright:
        Copyright (C) 2021 Josh Sunnex

        This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
        Public License as published by the Free Software Foundation, version 3.

        This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
        implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
        for more details.

        You should have received a copy of the GNU General Public License along with this program.
        If not, see <https://www.gnu.org/licenses/>.

"""
from audio_transcoder.lib.encoders.aac import AacEncoder
from audio_transcoder.lib.encoders.lame import LameEncoder


def append_worker_log(worker_log, line: str):
    if worker_log is None or not isinstance(worker_log, list):
        return
    try:
        worker_log.append(str(line))
    except Exception:
        return


def available_encoders(settings=None, probe=None):
    return_encoders = {}
    encoder_libs = [
        LameEncoder,
        AacEncoder,
    ]
    for encoder_class in encoder_libs:
        encoder_lib = encoder_class(settings=settings, probe=probe)
        for encoder in encoder_lib.provides():
            return_encoders[encoder] = encoder_lib
    return return_encoders


def join_filtergraph(filter_id, filter_args, stream_id):
    filtergraph = ''
    count = 1
    for filter_string in filter_args:
        if filtergraph:
            filtergraph += ';'
        filtergraph += '[{}]'.format(filter_id)
        filtergraph += '{}'.format(filter_string)
        filter_id = '0:af:{}-{}'.format(stream_id, count)
        filtergraph += '[{}]'.format(filter_id)
        count += 1
    return filter_id, filtergraph

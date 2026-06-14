#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    plugins.global_settings.py

    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     10 Jun 2022, (6:52 PM)

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
from audio_transcoder.lib import tools

supported_codecs = {
    "aac": {
        "label": "AAC",
    },
    "mp3": {
        "label": "MP3",
    },
}


class GlobalSettings:
    def __init__(self, settings):
        self.settings = settings

    @staticmethod
    def options():
        return {
            "main_options":           {
                "mode": "basic",
            },
            "encoder_selection":      {
                "audio_codec":     "mp3",
                "force_transcode": False,
                "audio_encoder":   "libmp3lame",
            },
            "advanced_input_options": {
                "main_options":     "",
                "advanced_options": "-strict -2\n",
                "custom_options":   "libmp3lame\n"
                                    "-b:a 192k\n",
            },
            "output_settings":        {},
            "filter_settings":        {
                "apply_smart_filters":  False,
                "apply_custom_filters": False,
                "custom_audio_filters": "",
            },
        }

    def __set_default_option(self, select_options, key, default_option=None):
        """
        Sets the default option if the currently set option is not available

        :param select_options:
        :param key:
        :return:
        """
        available_options = []
        for option in select_options:
            available_options.append(option.get("value"))
            if not default_option:
                default_option = option.get("value")
        current_value = self.settings.get_setting(key)
        if not getattr(self.settings, 'apply_default_fallbacks', True):
            return current_value
        if current_value not in available_options:
            self.settings.settings_configured[key] = default_option
            return default_option
        return current_value

    def get_mode_form_settings(self):
        return {
            "label":          "Config mode",
            "input_type":     "select",
            "select_options": [
                {
                    "value": "basic",
                    "label": "Basic (Not sure what I am doing. Configure most of it for me.)",
                },
                {
                    "value": "standard",
                    "label": "Standard (I know how to transcode some audio. Let me tweak some settings.)",
                },
                {
                    "value": "advanced",
                    "label": "Advanced (Dont tell me what to do, I write FFmpeg commands in my sleep.)",
                },
            ],
        }

    def get_audio_codec_form_settings(self):
        values = {
            "label":          "Audio Codec",
            "input_type":     "select",
            "select_options": [],
        }
        for key in supported_codecs:
            values['select_options'].append(
                {
                    "value": key,
                    "label": supported_codecs.get(key, {}).get('label'),
                }
            )
        selected_codec = self.__set_default_option(values['select_options'], 'audio_codec', default_option='mp3')
        if getattr(self.settings, 'apply_default_fallbacks', True):
            current_value = self.settings.get_setting('audio_codec')
            if selected_codec and selected_codec != current_value:
                self.settings.set_setting('audio_codec', selected_codec)
        if self.settings.get_setting('mode') not in ['basic', 'standard', 'advanced']:
            values["display"] = 'hidden'
        return values

    def get_force_transcode_form_settings(self):
        values = {
            "label":       "Force transcoding even if the file is already using the desired audio codec",
            "description": "Will force a transcode of the audio stream even if it matches the selected audio codec.\n"
                           "A file will only be forced to be transcoded once.\n"
                           "After that it is flagged to prevent it being added to the pending tasks list in a loop.",
            "sub_setting": True,
        }
        if self.settings.get_setting('mode') not in ['basic', 'standard', 'advanced']:
            values["display"] = 'hidden'
        return values

    def get_audio_encoder_form_settings(self):
        values = {
            "label":          "Audio Encoder",
            "input_type":     "select",
            "select_options": [],
        }
        encoder_libs = tools.available_encoders(settings=self.settings)
        for encoder_name, encoder_lib in encoder_libs.items():
            encoder_details = encoder_lib.encoder_details(encoder_name)
            if encoder_details.get('codec') != self.settings.get_setting('audio_codec'):
                continue
            values['select_options'].append(
                {
                    "value": encoder_name,
                    "label": encoder_details.get('label'),
                }
            )
        selected_encoder = self.__set_default_option(values['select_options'], 'audio_encoder')
        if getattr(self.settings, 'apply_default_fallbacks', True):
            current_encoder = self.settings.get_setting('audio_encoder')
            if selected_encoder and selected_encoder != current_encoder:
                self.settings.set_setting('audio_encoder', selected_encoder)
        if self.settings.get_setting('mode') not in ['basic', 'standard']:
            values["display"] = 'hidden'
        return values

    def get_apply_smart_filters_form_settings(self):
        values = {
            "label":   "Enable plugin's smart audio filters",
            "tooltip": "Prepares the audio transcoder for filtergraph-based smart processing.",
        }
        if self.settings.get_setting('mode') not in ['basic', 'standard']:
            values["display"] = 'hidden'
        return values

    def get_apply_custom_filters_form_settings(self):
        values = {
            "label":       "Apply custom audio filters",
            "description": "Append one FFmpeg audio filter per line to the generated filtergraph.",
            "sub_setting": True,
        }
        if self.settings.get_setting('mode') not in ['basic', 'standard']:
            values["display"] = 'hidden'
        return values

    def get_custom_audio_filters_form_settings(self):
        values = {
            "label":      "Custom audio filters",
            "input_type": "textarea",
            "sub_setting": True,
        }
        if not self.settings.get_setting('apply_custom_filters'):
            values["display"] = 'hidden'
        if self.settings.get_setting('mode') not in ['basic', 'standard']:
            values["display"] = 'hidden'
        return values

    def get_main_options_form_settings(self):
        values = {
            "label":      "Write your own custom main options",
            "input_type": "textarea",
        }
        if self.settings.get_setting('mode') not in ['advanced']:
            values["display"] = 'hidden'
        return values

    def get_advanced_options_form_settings(self):
        values = {
            "label":      "Write your own custom advanced options",
            "input_type": "textarea",
        }
        if self.settings.get_setting('mode') not in ['advanced']:
            values["display"] = 'hidden'
        return values

    def get_custom_options_form_settings(self):
        values = {
            "label":      "Write your own custom audio options (starting with the encoder to use)",
            "input_type": "textarea",
        }
        if self.settings.get_setting('mode') not in ['advanced']:
            values["display"] = 'hidden'
        return values

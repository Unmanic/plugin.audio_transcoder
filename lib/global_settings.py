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
        "max_channels": 8,
    },
    "mp3": {
        "label": "MP3",
        "max_channels": 2,
        "multichannel_warning": "Warning: MP3 is effectively a stereo-target codec here. Using it on multichannel movie audio will downmix channels and is likely to be a poor fit for video libraries.",
    },
}

max_channel_count_options = [
    {
        "value": "same_as_source",
        "label": "Same as source",
    },
    {
        "value": "8",
        "label": "7.1",
    },
    {
        "value": "6",
        "label": "5.1",
    },
    {
        "value": "2",
        "label": "2.0",
    },
    {
        "value": "1",
        "label": "1.0",
    },
]


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
                "enable_smart_audio_filters": False,
                "max_channel_count": "same_as_source",
                "normalize_audio_volume": False,
                "apply_custom_filters": False,
                "custom_audio_filters": "",
            },
            "smart_output_target": {
                "enable_smart_output_target":                 True,
                "smart_output_target":                        "balanced",
                "reencode_matching_codecs_above_target":     False,
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
        selected_codec_details = supported_codecs.get(selected_codec, {})
        if selected_codec_details.get('multichannel_warning'):
            values["description"] = selected_codec_details.get('multichannel_warning')
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

    def get_enable_smart_output_target_form_settings(self):
        values = {
            "label":       "Enable smart output target",
            "description": "Automatically detect an audio bitrate target from the source file for Basic mode transcodes.",
        }
        if self.settings.get_setting('mode') not in ['basic']:
            values["display"] = 'hidden'
        return values

    def get_smart_output_target_form_settings(self):
        values = {
            "label":       "Smart output target",
            "description": "Choose how Basic mode balances quality retention against compression when selecting the target bitrate.",
            "sub_setting": True,
            "input_type":  "select",
            "select_options": [
                {
                    "value": "prefer_quality",
                    "label": "Prefer Quality",
                },
                {
                    "value": "balanced",
                    "label": "Balanced",
                },
                {
                    "value": "prefer_compression",
                    "label": "Prefer Compression",
                },
            ],
        }
        self.__set_default_option(values['select_options'], 'smart_output_target', default_option='balanced')
        if not self.settings.get_setting('enable_smart_output_target'):
            values["display"] = 'hidden'
        if self.settings.get_setting('mode') not in ['basic']:
            values["display"] = 'hidden'
        return values

    def get_reencode_matching_codecs_above_target_form_settings(self):
        values = {
            "label":       "Re-encode matching codecs above target",
            "description": "Also queue files that already use the selected codec when their bitrate is significantly above the smart output target window.",
            "sub_setting": True,
        }
        if not self.settings.get_setting('enable_smart_output_target'):
            values["display"] = 'hidden'
        if self.settings.get_setting('mode') not in ['basic']:
            values["display"] = 'hidden'
        return values

    def get_enable_smart_audio_filters_form_settings(self):
        values = {
            "label":       "Enable plugin's smart audio filters",
            "description": "Apply audio-aware output shaping such as channel-count limiting and loudness normalization.",
        }
        if self.settings.get_setting('mode') not in ['basic', 'standard']:
            values["display"] = 'hidden'
        return values

    def get_max_channel_count_form_settings(self):
        values = {
            "label":          "Set maximum channel count",
            "sub_setting":    True,
            "input_type":     "select",
            "select_options": max_channel_count_options,
        }
        self.__set_default_option(values['select_options'], 'max_channel_count', default_option='same_as_source')
        if not self.settings.get_setting('enable_smart_audio_filters'):
            values["display"] = 'hidden'
        if self.settings.get_setting('mode') not in ['basic', 'standard']:
            values["display"] = 'hidden'
        return values

    def get_normalize_audio_volume_form_settings(self):
        values = {
            "label":       "Normalise audio volume levels",
            "description": "Apply FFmpeg loudness normalization to the output audio stream.",
            "sub_setting": True,
        }
        if not self.settings.get_setting('enable_smart_audio_filters'):
            values["display"] = 'hidden'
        if self.settings.get_setting('mode') not in ['basic', 'standard']:
            values["display"] = 'hidden'
        return values

    def get_apply_custom_filters_form_settings(self):
        values = {
            "label":       "Apply custom audio filters",
            "description": "Append one FFmpeg audio filter per line to the generated filtergraph.",
        }
        if self.settings.get_setting('mode') not in ['standard']:
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
        if self.settings.get_setting('mode') not in ['standard']:
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

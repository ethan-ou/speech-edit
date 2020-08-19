from probe import Probe, is_ntsc
from pathlib import Path
import opentimelineio as otio

class Timeline:
    def __init__(self):
        self._masterclip = 1

    def create_timeline(self, name="Project 1", settings=None):
        if settings is None:
            settings = {
                'video': {
                    'frame_rate': 25,
                    'width': 1920,
                    'height': 1080
                },
                'audio': {
                    'sample_rate': 48000,
                    'channel_layout': 'stereo',
                    'channels': 2
                }
            }

        timeline_rate = {
            "ntsc": str(is_ntsc(settings['video']['frame_rate'])).upper(),
            "timebase": str(settings['video']['frame_rate'])
        }

        timeline_audio_channels = []
        for i in range(0, int(settings['audio']['channels'])):
            timeline_audio_channels.append({
                "channel": {
                    "index": str(i + 1)
                },
                "downmix": "0",
                "index": str(i + 1),
                "numchannels": "1"
            })

        self.timeline = otio.schema.Timeline(name, metadata={
            "fcp_xml": {
                "@id": "sequence-1",
                "media": {
                    "video": {
                        "format": {
                            "samplecharacteristics": {
                                "colordepth": "24",
                                "fielddominance": "none",
                                "width": str(settings['video']['width']),
                                "height": str(settings['video']['height']),
                                "pixelaspectratio": "square",
                                "rate": timeline_rate
                            }
                        }
                    },
                    "audio": {
                        "format": {
                            "samplecharacteristics": {
                                "depth": "16",
                                "samplerate": str(settings['audio']['sample_rate'])
                            }
                        },
                        "numOutputChannels": str(settings['audio']['channels']),
                        "outputs": {
                            "group": timeline_audio_channels
                        }
                    }
                },
                "rate": timeline_rate,
                "timecode": {
                        "displayformat": "DF" if is_ntsc(settings['video']['frame_rate']) else "NDF",
                        "rate": timeline_rate
                    }
            }
        })

        self.video_track_1 = otio.schema.Track(kind=otio.schema.track.TrackKind.Video, name="V1")
        self.audio_track_1 = otio.schema.Track(kind=otio.schema.track.TrackKind.Audio, name="A1", metadata={
            "fcp_xml": {                  
                "@premiereTrackType": settings['audio']['channel_layout'].capitalize(),
                "outputchannelindex": "1",
                "@currentExplodedTrackIndex": "0",
                "@totalExplodedTrackCount": str(settings['audio']['channels']),
            }
        })

        self.timeline.tracks.append(self.video_track_1)
        self.timeline.tracks.append(self.audio_track_1)

        return self

    def add_file(self, file_path, cuts):
        metadata = Probe(file_path).run()
        summary = metadata.extract_summary()

        timeline_rate = {
            "ntsc": str(is_ntsc(summary['video']['frame_rate'])).upper(),
            "timebase": str(summary['video']['frame_rate'])
        }

        masterclip_id = "masterclip-" + str(self._masterclip)

        clip = otio.schema.ExternalReference(
            target_url=file_path,
            available_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=0, rate=float(summary['video']['frame_rate'])),
                duration=otio.opentime.RationalTime(value=int(metadata.extract_video_data('nb_frames')), rate=float(summary['video']['frame_rate']))
            ),
            metadata={
                "fcp_xml": {
                    "masterclipid": masterclip_id,
                    "media": {
                        "audio": {
                            "channelcount": str(summary['audio']['channels']),
                            "samplecharacteristics": {
                                "depth": "16",
                                "samplerate": str(summary['audio']['sample_rate'])
                            }
                        },
                        "video": {
                            "samplecharacteristics": {
                                "anamorphic": "FALSE",
                                "fielddominance": "none",
                                "width": str(summary['video']['width']),
                                "height": str(summary['video']['height']),
                                "pixelaspectratio": "square",
                                "rate": timeline_rate
                            }
                        }
                    },
                    "rate": timeline_rate,
                    "timecode": {
                        "displayformat": "DF" if is_ntsc(summary['video']['frame_rate']) else "NDF",
                        "rate": timeline_rate
                    }
                }
            }
        )

        for cut in cuts:
            self.video_track_1.append(
                otio.schema.Clip(
                    name=Path(file_path).stem,
                    media_reference=clip,
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(value=cut['start'], rate=float(summary['video']['frame_rate'])),
                        duration=otio.opentime.RationalTime(value=cut['end'] - cut['start'], rate=float(summary['video']['frame_rate']))
                    ),
                    metadata={
                        "fcp_xml": {
                            "masterclipid": masterclip_id,
                            "pixelaspectratio": "square",
                        }
                    }
                )
            )

            self.audio_track_1.append(
                otio.schema.Clip(
                    name=Path(file_path).stem,
                    media_reference=clip,
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(value=cut['start'], rate=float(summary['video']['frame_rate'])),
                        duration=otio.opentime.RationalTime(value=cut['end'] - cut['start'], rate=float(summary['video']['frame_rate']))
                    ),
                    metadata={
                        "fcp_xml": {
                            "@premiereChannelType": summary['audio']['channel_layout'].capitalize(),
                            "masterclipid": masterclip_id,
                            "sourcetrack": {
                                "mediatype": "audio",
                                "trackindex": "1"
                            }
                        }
                    }
                )
            )

        self._masterclip += 1
        return self

    def export(self):        
        return otio.adapters.write_to_string(
            self.timeline,
            'fcp_xml'
        )
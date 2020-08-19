from decimal import Decimal
import ffmpeg
from .metadata_utils import adapt_common_frame_rate, is_ntsc

class Probe:
    def __init__(self, file_path):
        self.file_path = file_path

    def run(self):
        try:
            self.file_container = ffmpeg.probe(self.file_path)
        except ffmpeg.Error as e:
            print('stdout:', e.stdout.decode('utf8'))
            print('stderr:', e.stderr.decode('utf8'))
            raise e
        return self

    def extract_summary(self):
        return {
            'video': {
                'frame_rate': self.extract_video_frame_rate(),
                'width': int(self.extract_video_data(key='width')),
                'height': int(self.extract_video_data(key='height')),
            },
            'audio': {
                'sample_rate': int(self.extract_audio_data(key='sample_rate')),
                'channel_layout': "stereo" if int(self.extract_audio_data(key='channels')) == 2 else "mono",
                'channels': int(self.extract_audio_data(key='channels'))
            }
        }

    def extract_streams(self):
        file_streams = []
        for stream in self.file_container['streams']:
            file_streams.append(stream['codec_type'])

        return file_streams

    def extract_video_data(self, key):
        return next((stream for stream in self.file_container['streams'] if stream['codec_type'] == 'video'), None)[key]

    def extract_audio_data(self, key):
        return next((stream for stream in self.file_container['streams'] if stream['codec_type'] == 'audio'), None)[key]

    def extract_video_frame_rate(self):
        raw_frame_rate = next((stream for stream in self.file_container['streams'] if stream['codec_type'] == 'video'), None)['r_frame_rate']
        try_frame_rate = adapt_common_frame_rate(raw_frame_rate)

        if try_frame_rate is not None:
            return try_frame_rate
        else:
            split_frame_rate = raw_frame_rate.split('/')
            return Decimal(split_frame_rate[0]) / Decimal(split_frame_rate[1])

    def is_ntsc(self):
        return is_ntsc(self.extract_video_frame_rate())
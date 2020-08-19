from pathlib import Path
import ffmpeg

class Encoder:
    @staticmethod
    def wav_audio_temp(file_path, temp_dir):
        temp_audio_format = ".wav"
        temp_file_path = Path(temp_dir).joinpath(Path(file_path).with_suffix(temp_audio_format).name)
        
        try:
            ffmpeg.input(file_path).output(str(temp_file_path), ar="16000").overwrite_output().run(capture_stdout=True, capture_stderr=True)

        except ffmpeg.Error as e:
            print('stdout:', e.stdout.decode('utf8'))
            print('stderr:', e.stderr.decode('utf8'))
            raise e

        return temp_file_path

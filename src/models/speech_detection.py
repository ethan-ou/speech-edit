from .utils import convert_to_frames, cleanup_cuts
from pyannote.audio.utils.signal import Binarize
from pyannote.audio.features.wrapper import Wrapper
from pathlib import Path

class SpeechDetection:
    def __init__(self, batch_size=16, threshold=0.15, model="ami", device="cuda"):
        if batch_size is None:
            batch_size = 16
        
        if threshold is None:
            threshold = 0.15

        self.batch_size = batch_size
        self.threshold = threshold
        self.model = model
        self.device = device

        SAD_AMI_PATH = 'sad_ami/train/ami.train/weights/0140.pt'
        SAD_DIHARD_PATH = 'sad_dihard/train/dihard.train/weights/0231.pt'

        if self.model == "ami":
            model = SAD_AMI_PATH
        elif self.model == "dihard":
            model = SAD_DIHARD_PATH
        else:
            model = SAD_AMI_PATH

        self.pipeline = Wrapper(Path(Path(__file__).resolve().parent).joinpath(model), 
                    batch_size=self.batch_size, device=self.device)

    def run(self, file_path):
        diarization = self.pipeline({'audio': file_path})
        binarize = Binarize(offset=self.threshold, onset=self.threshold, pad_onset=0.3, pad_offset=0.3, log_scale=True, 
                    min_duration_off=0.5, min_duration_on=2)
        result_list = binarize.apply(diarization, dimension=1).for_json()['content']

        self.raw_result = cleanup_cuts(result_list)
        return self

    def to_frames(self, frame_rate):
        self.frame_result = convert_to_frames(self.raw_result, frame_rate)
        return self.frame_result
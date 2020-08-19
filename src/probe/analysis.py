from .probe import Probe
from .utils import most_frequent, process_dict_list, merge_dicts

"""
Analyses a group of clips.
"""
class Analysis:
    def __init__(self, clips=[]):
        self.clips = clips

    def summary(self):
        file_summary = []
        for clip in self.clips:
            summary = Probe(clip).run().extract_summary()
            file_summary.append(summary)
        
        final_list = None

        for item in file_summary:
            if final_list == None:
                final_list = item
            else:
                final_list = merge_dicts(final_list, item)

        return process_dict_list(final_list, most_frequent)

        
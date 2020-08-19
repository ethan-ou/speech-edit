from decimal import Decimal

def convert_to_frames(cut_list, frame_rate):
  START_THRESHOLD = 0.5
  out = []

  for i, cut in enumerate(cut_list):
    # Clean first pyannote audio start time
    if cut['start'] < START_THRESHOLD and cut['end'] > START_THRESHOLD and i == 0:
      out.append({'start': 0, 'end': int(frame_rate * Decimal(cut['end']))})
    else:
      out.append({'start': int(frame_rate * Decimal(cut['start'])), 'end': int(frame_rate * Decimal(cut['end']))})

  return out

def cleanup_cuts(cut_list):
  cut_events = []
  
  for cut in cut_list:
    cut_events.append({'start': cut['start']})
    cut_events.append({'end': cut['end']})

  cut_events.sort(key=lambda x: x.get('start') if 'start' in x else x.get('end'))

  stack = []
  out = []
  
  for event in cut_events:
    if 'start' in event:
      stack.append(event)
    
    else:
      popped = stack.pop()
      
      if len(stack) == 0:
        out.append({'start': popped['start'], 'end': event['end']})

  return out

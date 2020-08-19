from decimal import Decimal

def most_frequent(input_list):
    def get_small_mode(input_list, out_mode):
        numbers = []
        decimal = False
        for i in input_list:
            if isinstance(i, Decimal):
                numbers.append(float(i))
                decimal = True
            else:
                numbers.append(i)
        counts = {k:numbers.count(k) for k in set(numbers)}
        modes = sorted(dict(filter(lambda x: x[1] == max(counts.values()), counts.items())).keys())
        if out_mode=='smallest':
            return convert_to_decimal(modes[0], decimal)
        elif out_mode=='largest':
            return convert_to_decimal(modes[-1], decimal)
        else:
            return convert_to_decimal(modes, decimal)

    def convert_to_decimal(number, isDecimal):
        return Decimal(number) if isDecimal else number

    return get_small_mode(input_list, 'largest')

def merge_dicts(d1, d2):
    if isinstance(d1, dict) and isinstance(d2, dict):
        # Unwrap d1 and d2 in new dictionary to keep non-shared keys with **d1, **d2
        # Next unwrap a dict that treats shared keys and recursively merge them
        return {
            **d1, **d2,
            **{k: merge_dicts(d1[k], d2[k])
            for k in {*d1} & {*d2}}
        }
    else:
        # This case happens when values are merged
        # It bundle values in a list, making sure
        # to flatten them if they are already lists
        return [
            *(d1 if isinstance(d1, list) else [d1]),
            *(d2 if isinstance(d2, list) else [d2])
        ]

def process_dict_list(input_dict, fn):
    out = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            out[key] = process_dict_list(value, fn)
        elif isinstance(value, list):
            out[key] = fn(value)
        else:
            out[key] = value
      
    return out
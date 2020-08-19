from decimal import Decimal

def adapt_common_frame_rate(frame_rate):
    common_frame_rates = {
        '1/1': Decimal('1'),
        '10/1': Decimal('10'),
        '15/1': Decimal('15'),
        '20/1': Decimal('20'),
        '24000/1001': Decimal('23.976'),
        '24/1': Decimal('24'),
        '25/1': Decimal('25'),
        '30000/1001': Decimal('29.97'),
        '30/1': Decimal('30'),
        '48000/1001': Decimal('47.952'),
        '48/1': Decimal('48'),
        '50/1': Decimal('50'),
        '60000/1001': Decimal('59.94'),
        '60/1': Decimal('60')
    }

    if frame_rate in common_frame_rates:
        return common_frame_rates[frame_rate]
    else:
        return None

def is_ntsc(frame_rate):
    return Decimal(frame_rate) % Decimal('29.97') == Decimal('0')
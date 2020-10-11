class Utils:

    @staticmethod
    def duration_to_seconds(duration):
        mult = {
            's': 1,
            'min': 60,
            'h': 60 * 60,
            'day': 60 * 60 * 24,
            'wk': 60 * 60 * 24 * 7,
            'mo': -1,
            'yr': -1,
            'decade': -1
        }

        return duration['amount'] * mult[duration['unit']]

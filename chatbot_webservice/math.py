
class Math:

    @staticmethod
    def integrate(y_values, x_values):
        if len(x_values) != len(y_values):
            raise AttributeError

        result = []
        for i in range(len(x_values)):
            a = y_values[i]

            if i == 0:
                result.append(0)
                continue

            c = y_values[i - 1]
            h = x_values[i] - x_values[i - 1]
            area = (a + c) * h * 0.5
            previous = result[i - 1]
            cum_int = area + previous
            result.append(cum_int)

        return result

def filter_combinations(candidates, client):
    """
    Filters a list of binary ON/OFF sequences to keep only those that satisfy
    the temperature constraints defined in the client's comfort schedule.

    Parameters:
        candidates (List[List[int]]): List of binary sequences representing heater schedules.
        client (ParameterClient): Client-specific parameters including comfort constraints.

    Returns:
        List[List[int]]: A list of sequences that satisfy all comfort constraints.
    """
    valid = []
    step = 24 / client.n
    constraints = [(0, 0)] + sorted(client.points.items()) + [(24, 0)]

    for seq in candidates:
        temperatures = [client.t0]
        is_valid = True

        for i in range(len(constraints) - 1):
            start_hour, _ = constraints[i]
            end_hour, target_temp = constraints[i + 1]

            idx_start = int(start_hour / step)
            idx_end = int(end_hour / step)

            for j in range(idx_start, min(idx_end, len(seq))):
                delta = client.pente_positive if seq[j] else client.pente_negative
                new_temp = temperatures[-1] + delta

                for shower in client.horaire:
                    if shower >= j * step and shower < (j + 1) * step:
                        new_temp -= client.douche

                temperatures.append(new_temp)

            # Check if constraint is satisfied at end of interval
            if temperatures[-1] < target_temp:
                is_valid = False
                break

        if is_valid:
            valid.append(seq)

    return valid

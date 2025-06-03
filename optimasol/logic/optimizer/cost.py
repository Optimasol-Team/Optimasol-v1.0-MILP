def compute_cost(sequence, client, production, tariffs):
    """
    Computes the net cost (or gain) of a given ON/OFF heating schedule
    by evaluating electricity drawn from the grid and surplus PV energy sold.

    Parameters:
        sequence (List[int]): Binary list indicating ON (1) or OFF (0) heater state.
        client (ParameterClient): System and economic parameters for the user.
        production (np.ndarray): PV production in watts per time step.
        tariffs (Dict[str, Dict]): Dictionary with 'creuse' and 'pleine' tariff info.

    Returns:
        float: Net cost in EUR (positive means cost, negative means net gain).
    """
    cost = 0.0
    revenue = 0.0
    step_duration = 24 / client.n

    for i in range(client.n - 1):
        on = sequence[i]
        hour = i * step_duration
        creuse, pleine = time_overlap(hour, step_duration, tariffs)

        heating_kwh = on * client.P * step_duration / 1000
        pv_kwh = production[i] * step_duration / 1000

        from_grid = max(0, heating_kwh - pv_kwh)
        to_grid = max(0, pv_kwh - heating_kwh)

        total = creuse + pleine
        if total == 0:
            price = 0
        else:
            price = (
                (creuse * tariffs["creuse"]["prix"] + pleine * tariffs["pleine"]["prix"]) / total
            )

        cost += from_grid * price
        revenue += to_grid * client.pv_prix

    return cost - revenue


def time_overlap(start, duration, tariffs):
    """
    Determines how much of a time interval falls within off-peak (creuse)
    and peak (pleine) hours.

    Parameters:
        start (float): Start time of the interval in hours (e.g., 13.5).
        duration (float): Length of the interval in hours.
        tariffs (Dict[str, Dict]): Tariff dictionary with time ranges.

    Returns:
        Tuple[float, float]: (creuse_duration, pleine_duration) in hours.
    """
    def str_to_float(s):
        h, m = map(int, s.split(":"))
        return h + m / 60

    def overlap(a, b, c, d):
        return max(0, min(b, d) - max(a, c))

    creuse_start = str_to_float(tariffs["creuse"]["debut"])
    creuse_end = str_to_float(tariffs["creuse"]["fin"])
    end = start + duration

    if creuse_start <= creuse_end:
        creuse = overlap(start, end, creuse_start, creuse_end)
    else:
        creuse = overlap(start, end, creuse_start, 24) + overlap(start, end, 0, creuse_end)

    pleine = duration - creuse
    return round(creuse, 3), round(pleine, 3)
#
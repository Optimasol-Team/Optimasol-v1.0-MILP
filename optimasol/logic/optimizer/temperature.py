def simulate_temperature(sequence, client):
    """
    Simulates the evolution of the water tank temperature over time based on a given
    ON/OFF heating schedule.

    Parameters:
        sequence (List[int]): A list of 0/1 values indicating heater OFF/ON for each interval.
        client (ParameterClient): The parameter object containing system characteristics.

    Returns:
        List[float]: A list of temperatures corresponding to each time step, starting from t0.
    """
    temperatures = [client.t0]

    for i in range(len(sequence)):
        # Apply positive or negative slope based on heater state
        if sequence[i]:
            delta = client.pente_positive
        else:
            delta = client.pente_negative

        new_temp = temperatures[-1] + delta

        # Subtract shower-induced temperature drop if current step includes a shower time
        for shower_time in client.horaire:
            if shower_time >= i * 24 / client.n and shower_time <= (i + 1) * 24 / client.n:
                new_temp -= client.douche

        temperatures.append(new_temp)

    return temperatures

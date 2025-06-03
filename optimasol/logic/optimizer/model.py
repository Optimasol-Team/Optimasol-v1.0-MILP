class ParameterClient:
    """
    A class representing the client-specific thermal and economic parameters
    used in the solar water heater optimization process.

    Attributes:
        Tamb (float): Ambient temperature in degrees Celsius.
        P (float): Heating power of the water heater in Watts.
        volume (float): Tank volume in liters.
        k (float): Thermal loss coefficient (W/\u00b0C).
        max (float): Maximum allowed water temperature in the tank (\u00b0C).
        points (dict): Schedule of target temperatures, as {hour (float): temperature (\u00b0C)}.
        pente_positive (float): Computed heating rate in \u00b0C/hour.
        pente_negative (float): Cooling rate in \u00b0C/hour (typically negative).
        douche (float): Temperature drop due to shower usage (\u00b0C).
        horaire (list): List of decimal hour values when showers are expected.
        n (int): Number of time intervals in the optimization horizon (e.g., 24).
        t0 (float): Initial temperature of the tank (\u00b0C).
        pv_prix (float): Selling price of PV surplus energy in EUR/kWh.
    """

    def __init__(self,
                 Tamb: float,
                 P: float,
                 volume: float,
                 k: float,
                 max_temp: float,
                 schedule: dict,
                 slope_cooling: float,
                 shower_times: list,
                 shower_drop: float,
                 n: int,
                 t0: float,
                 pv_price: float):
        self.Tamb = Tamb
        self.P = P
        self.volume = volume
        self.k = k
        self.max = max_temp
        self.points = schedule
        self.pente_positive = P / 4.18 / volume  # heating rate in deg/hour
        self.pente_negative = slope_cooling
        self.douche = shower_drop
        self.horaire = shower_times
        self.n = n
        self.t0 = t0
        self.pv_prix = pv_price

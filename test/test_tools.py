from src.tools.geocode_nominatim import NominatimClient
from src.tools.weather_open_meteo import OpenMeteoClient


def test_nominatim_geocode_placeholder_returns_tuple():
    client = NominatimClient()
    latlon = client.geocode("Boston")
    assert isinstance(latlon, tuple) and len(latlon) == 2


def test_open_meteo_summary_placeholder_shape():
    wx = OpenMeteoClient()
    summary = wx.forecast_summary(42.36, -71.06)
    assert set(summary.keys()) == {"summary", "temp_c", "precip_prob"}

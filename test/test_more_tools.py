from src.tools.timezone_worldtimeapi import WorldTimeApiClient
from src.tools.currency_exchangerate import ExchangeRateClient
from src.tools.routing_osrm import OSRMClient


def test_worldtimeapi_timezone_placeholder():
    tz = WorldTimeApiClient().timezone_for_latlon(42.36, -71.06)
    assert isinstance(tz, str)


def test_exchangerate_convert_placeholder():
    ex = ExchangeRateClient()
    assert ex.convert(100, "USD", "EUR") == 90
    assert ex.convert(100, "EUR", "USD") == 110
    assert ex.convert(100, "USD", "USD") == 100


def test_osrm_distance_placeholder():
    osrm = OSRMClient()
    km = osrm.route_distance_km((42.36, -71.06), (40.71, -74.00))
    assert isinstance(km, float)
    assert km > 0

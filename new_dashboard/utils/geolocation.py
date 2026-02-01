"""
Módulo de geolocalização por IP usando IP-API.com (gratuita).
Fornece informações de País, Estado, Cidade, ISP e coordenadas.
"""

import aiohttp
import asyncio
import time

# Cache em memória para evitar consultas repetidas
_geo_cache = {}
_last_request_time = 0
_MIN_REQUEST_INTERVAL = 1.5  # IP-API.com: max 45 req/min = ~1.3s/req


async def get_location_by_ip(ip_address):
    """
    Obtém informações de geolocalização para um endereço IP de forma assíncrona.

    Args:
        ip_address (str): Endereço IP público

    Returns:
        dict: Dados de localização ou None se falhar
        {
            'country': 'Brazil',
            'region': 'São Paulo',
            'city': 'Campinas',
            'isp': 'Vivo',
            'lat': -22.9056,
            'lon': -47.0608
        }
    """
    global _last_request_time

    # Validação básica
    if not ip_address or ip_address in ["127.0.0.1", "localhost", "0.0.0.0"]:
        return None

    # Verifica cache
    if ip_address in _geo_cache:
        return _geo_cache[ip_address]

    # Rate limiting (respeitar limite da API)
    current_time = time.time()
    time_since_last = current_time - _last_request_time
    if time_since_last < _MIN_REQUEST_INTERVAL:
        await asyncio.sleep(_MIN_REQUEST_INTERVAL - time_since_last)

    try:
        # Consulta IP-API.com
        url = f"http://ip-api.com/json/{ip_address}"
        params = {"fields": "status,country,regionName,city,isp,lat,lon,query"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()

                    if data.get("status") == "success":
                        location_data = {
                            "country": data.get("country", "Unknown"),
                            "region": data.get("regionName", "Unknown"),
                            "city": data.get("city", "Unknown"),
                            "isp": data.get("isp", "Unknown"),
                            "lat": data.get("lat"),
                            "lon": data.get("lon"),
                        }

                        # Salva no cache
                        _geo_cache[ip_address] = location_data
                        _last_request_time = time.time()

                        print(
                            f"[GEO] {ip_address} -> {location_data['city']}, {location_data['region']}, {location_data['country']}"
                        )
                        return location_data
                    else:
                        print(
                            f"[GEO] Falha ao localizar IP {ip_address}: {data.get('message', 'Unknown error')}"
                        )
                        return None
                else:
                    print(f"[GEO] Erro HTTP {response.status} ao consultar {ip_address}")
                    return None

    except asyncio.TimeoutError:
        print(f"[GEO] Timeout ao consultar IP {ip_address}")
        return None
    except Exception as e:
        print(f"[GEO] Erro ao consultar IP {ip_address}: {e}")
        return None


def format_location_short(location_data):
    """
    Formata dados de localização em string curta para exibição.

    Args:
        location_data (dict): Dados retornados por get_location_by_ip()

    Returns:
        str: Formato "Campinas, SP, BR"
    """
    if not location_data:
        return "Unknown"

    city = location_data.get("city", "?")
    region = location_data.get("region", "?")
    country = location_data.get("country", "?")

    # Abrevia país
    country_abbr = {
        "Brazil": "BR",
        "United States": "USA",
        "Canada": "CA",
        "Argentina": "AR",
        "Mexico": "MX",
        "Portugal": "PT",
        "Spain": "ES",
        "France": "FR",
        "Germany": "DE",
        "United Kingdom": "UK",
    }.get(country, country[:3].upper())

    # Abrevia estado brasileiro
    if country == "Brazil":
        region_abbr = {
            "São Paulo": "SP",
            "Rio de Janeiro": "RJ",
            "Minas Gerais": "MG",
            "Bahia": "BA",
            "Paraná": "PR",
            "Rio Grande do Sul": "RS",
            "Santa Catarina": "SC",
            "Goiás": "GO",
            "Pernambuco": "PE",
            "Ceará": "CE",
        }.get(region, region[:2].upper())
    else:
        region_abbr = region[:2].upper() if len(region) > 2 else region

    return f"{city}, {region_abbr}, {country_abbr}"


def format_location_full(location_data):
    """
    Formata dados de localização em string completa com ISP.

    Args:
        location_data (dict): Dados retornados por get_location_by_ip()

    Returns:
        str: Formato "Campinas, SP, BR [Vivo]"
    """
    if not location_data:
        return "Unknown"

    short = format_location_short(location_data)
    isp = location_data.get("isp", "Unknown ISP")

    return f"{short} [{isp}]"

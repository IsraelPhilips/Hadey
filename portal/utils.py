# portal/utils.py
import geoip2.database
import requests
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def is_nigerian_user(request):
    """
    Determine if the user is from Nigeria based on their IP address.
    Returns True if Nigerian, False otherwise.
    """
    try:
        ip_address = get_client_ip(request)
        
        # Skip for local development IPs
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            # For testing, you can force a value here
            return False  # Change to True for testing Nigerian flow
        
        reader = geoip2.database.Reader(settings.GEOIP_PATH)
        response = reader.country(ip_address)
        country_code = response.country.iso_code
        reader.close()
        
        return country_code == 'NG'
    except Exception as e:
        logger.error(f"Error detecting country: {e}")
        # Default to False if detection fails
        return False

def get_usd_to_ngn_rate():
    """
    Fetch current USD to NGN exchange rate from Flutterwave.
    Returns the rate or a fallback rate if API fails.
    """
    try:
        url = "https://api.flutterwave.com/v3/rates"
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
        }
        params = {
            "from": "USD",
            "to": "NGN",
            "amount": "1"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success':
            rate = Decimal(str(data['data']['to']['rate']))
            return rate
        else:
            logger.warning("Flutterwave rate API returned non-success status")
            return Decimal('1650.00')  # Fallback rate
            
    except Exception as e:
        logger.error(f"Error fetching exchange rate: {e}")
        return Decimal('1650.00')  # Fallback rate

def convert_usd_to_ngn(usd_amount):
    """Convert USD amount to NGN using current exchange rate."""
    rate = get_usd_to_ngn_rate()
    return (Decimal(str(usd_amount)) * rate).quantize(Decimal('0.01'))

def get_currency_context(request, usd_amount):
    """
    Get currency context for templates.
    Returns dictionary with currency information and user location.
    """
    is_nigerian = is_nigerian_user(request)
    exchange_rate = get_usd_to_ngn_rate()
    ngn_amount = convert_usd_to_ngn(usd_amount)
    
    return {
        'is_nigerian': is_nigerian,
        'usd_amount': usd_amount,
        'ngn_amount': ngn_amount,
        'exchange_rate': exchange_rate,
        'primary_currency': 'NGN' if is_nigerian else 'USD',
        'secondary_currency': 'USD' if is_nigerian else 'NGN',
    }
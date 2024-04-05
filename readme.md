pip install psycopg2 - does not install gives error:
ERROR: Could not build wheels for psycopg2, which is required to install pyproject.toml-based projects
to fix this issue, do the following

sudo apt-get install libpq-dev python3-dev

issues while getting latitude and longitude using geopy library.
rate limit is 1000/day

I've done reverse geocoding of ~10K different lat-lon combinations in less than a day. Nominatim doesn't like bulk queries, so the idea is to prevent looking like one. Here's what I suggest:

Make sure that you only query unique items. I've found that repeated queries for the same lat-lon combination is blocked by Nominatim. The same can be true for addresses. You can use unq_address = df['address'].unique() and then make a query using that series. You could even end up with less addresses.

The time between queries should be random. I also set the user_agent to have a random number every time. In my case, I use the following code:

#################################################################
from time import sleep
from random import randint
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

user_agent = 'user_me_{}'.format(randint(10000,99999))
geolocator = Nominatim(user_agent=user_agent)
def reverse_geocode(geolocator, latlon, sleep_sec):
    try:
        return geolocator.reverse(latlon)
    except GeocoderTimedOut:
        logging.info('TIMED OUT: GeocoderTimedOut: Retrying...')
        sleep(randint(1*100,sleep_sec*100)/100)
        return reverse_geocode(geolocator, latlon, sleep_sec)
    except GeocoderServiceError as e:
        logging.info('CONNECTION REFUSED: GeocoderServiceError encountered.')
        logging.error(e)
        return None
    except Exception as e:
        logging.info('ERROR: Terminating due to exception {}'.format(e))
        return None

#############################################################################

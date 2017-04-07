from django.core.management.base import BaseCommand, CommandError

import datetime, pytz, requests
from django.utils import timezone
from drchrono.models import Kiosk
from django.conf import settings

class Command(BaseCommand):
    help = 'Refresh stored drchrono tokens, discarding those no longer valid.'

    def handle(self, *args, **options):
        def check_current_access(access_token):
            endpoint_list = ['https://drchrono.com/api/doctors','https://drchrono.com/api/patients','https://drchrono.com/api/appointment_profiles', 'https://drchrono.com/api/allergies']

            for endpoint in endpoint_list:
                response = requests.get(endpoint, headers={ 'Authorization': 'Bearer %s' % access_token })
                if response.status_code != 200:
                    return False
            return True

        instances = Kiosk.objects.all()
        for instance in instances:
            print '### Checking instance: '+str(instance.guid)

            if not check_current_access(instance.access_token):
                print '#   Token access suspect: instance removed'
                instance.delete()
                break

            if instance.expire_check_time + datetime.timedelta(seconds=instance.expires_in) < timezone.now()+ datetime.timedelta(seconds=3600):
                print '#   Need to refresh token'

                response = requests.post('https://drchrono.com/o/token/', data={
                    'refresh_token': instance.refresh_token,
                    'grant_type': 'refresh_token',
                    'client_id': settings.SOCIAL_AUTH_DRCHRONO_KEY,
                    'client_secret': settings.SOCIAL_AUTH_DRCHRONO_SECRET,
                })

                if response.status_code == 200:
                    data = response.json()
                    instance.access_token = data['access_token']
                    instance.refresh_token = data['refresh_token']
                    instance.expires_in = data['expires_in']
                    instance.expire_check_time = timezone.now()
                    instance.save()

                    print '#   Token updated'

                else:
                    print '#   Token update failed: instance removed'
                    instance.delete()
            else:
                print '#   Token update unneeded'

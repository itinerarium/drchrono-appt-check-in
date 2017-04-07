# Create your views here.
import datetime, requests, urllib
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required
from django.contrib.auth import logout
import dateutil.parser
from django.utils import timezone

from drchrono.models import Kiosk, Visit, Average_wait
from drchrono.forms import AppointmentSelectionForm, PatientVerificationForm, PatientUpdateForm

def check_current_access(user):
    access_token = user.social_auth.get(provider='drchrono').extra_data['access_token']
    endpoint_list = ['https://drchrono.com/api/doctors','https://drchrono.com/api/patients','https://drchrono.com/api/appointment_profiles', 'https://drchrono.com/api/allergies']

    for endpoint in endpoint_list:
        response = requests.get(endpoint, headers={ 'Authorization': 'Bearer %s' % access_token })
        if response.status_code != 200:
            return False
    return True

def api_get(access_token, url, params=None):
    if params:
        query_string = urllib.urlencode(params)
        url = url + '?' + query_string
    header = { 'Authorization': 'Bearer %s' % access_token }
    response = requests.get(url, headers=header)
    if response.status_code != 200:
        return False
    return response.json()

def api_patch(access_token, url, data):
    header = { 'Authorization': 'Bearer %s' % access_token }
    response = requests.patch(url, headers=header, data=data)
    if response.status_code not in (200, 204):
        return False
    return True
    # TODO: handle failures; assume success for now

def home(request):
    # if the current user is authorized, store the tokens for future use
    if request.user.is_authenticated():
        user_access_status = check_current_access(request.user)
        if user_access_status:
            access_token = request.user.social_auth.get(provider = 'drchrono').extra_data['access_token']
            current_doctor = api_get(access_token, 'https://drchrono.com/api/users/current')

            if current_doctor == False:
                logout(request)
                return render(request, 'index.html', { 'user_access_status': False })

            kiosk_instance = Kiosk.objects.get_or_none(doctor_id = current_doctor['doctor'])

            # TODO: refresh token every half hour?
            if not kiosk_instance:
                kiosk_instance = Kiosk(doctor_id=current_doctor['doctor'], refresh_token=request.user.social_auth.get(provider='drchrono').extra_data['refresh_token'], access_token=request.user.social_auth.get(provider='drchrono').extra_data['access_token'], expires_in=request.user.social_auth.get(provider='drchrono').extra_data['expires_in'],
                expire_check_time=datetime.datetime.utcnow())
                kiosk_instance.save()
            elif kiosk_instance.expire_check_time + datetime.timedelta(0, kiosk_instance.expires_in) < timezone.now() + datetime.timedelta(0, 3600):
                kiosk_instance.refresh_token=request.user.social_auth.get(provider='drchrono').extra_data['refresh_token']
                kiosk_instance.access_token=request.user.social_auth.get(provider='drchrono').extra_data['access_token']
                kiosk_instance.expires_in=request.user.social_auth.get(provider='drchrono').extra_data['expires_in']
                kiosk_instance.expire_check_time=datetime.datetime.utcnow()
                kiosk_instance.save()

            wait_object = Average_wait.objects.get_or_none(doctor_id=current_doctor['doctor'])
            if not wait_object:
                wait_object = Average_wait(doctor_id=doctor_id)
                wait_object.time_sum = datetime.timedelta(0)
                wait_object.visit_count = 0
                wait_object.save()

            logout(request)

            return redirect('kiosk', instance_guid=kiosk_instance.guid)
        else:
            logout(request)
            return render(request, 'index.html', { 'user_access_status': user_access_status })
    else:
        return render(request, 'index.html', {})

def kiosk(request, instance_guid):
    instance = Kiosk.objects.get_or_none(guid=instance_guid)
    if not instance:
        return redirect('home')

    # TODO: assuming instance access/credentials have not been revoked
    # TODO: appointment sliding windows
    appts_response = api_get(instance.access_token, 'https://drchrono.com/api/appointments', {'doctor': instance.doctor_id, 'date': str(datetime.date.today())})

    if appts_response == False:
        logout(request)
        return render(request, 'index.html', { 'user_access_status': False })

    appts_for_day = []
    for appt in appts_response['results']: # returned in order
        if not appt['status'] and appt['patient']:
            appt_object = {}
            appt_object['id'] = appt['id']
            appt_object['patient'] = appt['patient']
            appt_object['scheduled_time'] = dateutil.parser.parse(appt['scheduled_time'])
            appts_for_day.append(appt_object)

    return render(request, 'kiosk.html', { 'appts_for_day': appts_for_day, 'instance_guid': instance_guid })

def checkin(request, instance_guid):
    if request.method == 'POST':
        form = AppointmentSelectionForm(request.POST)
        if form.is_valid():
            instance = Kiosk.objects.get_or_none(guid=instance_guid)
            if not instance:
                return redirect('home')

            appt_id = form.cleaned_data.get('appt_id')
            appt = api_get(instance.access_token, 'https://drchrono.com/api/appointments/'+str(appt_id))

            if appt == False:
                logout(request)
                return render(request, 'index.html', { 'user_access_status': False })

            if appt['doctor'] != instance.doctor_id or appt['status'] != '':
                return redirect('error', instance_guid=instance_guid)

            form = PatientVerificationForm(initial={ 'appt_id': appt_id })
            return render(request, 'verification.html', { 'form': form, 'instance_guid': instance_guid })
        else:
            return redirect('error', instance_guid=instance_guid)
    else:
        return redirect('error', instance_guid=instance_guid)

def update(request, instance_guid):
    if request.method == 'POST':
        form = PatientVerificationForm(request.POST)

        if form.is_valid():
            instance = Kiosk.objects.get_or_none(guid=instance_guid)
            if not instance:
                return redirect('home')

            appt_id = form.cleaned_data.get('appt_id')
            appt = api_get(instance.access_token, 'https://drchrono.com/api/appointments/'+str(appt_id))

            if appt == False:
                logout(request)
                return render(request, 'index.html', { 'user_access_status': False })

            if appt['doctor'] != instance.doctor_id or appt['status'] != '':
                return redirect('error', instance_guid=instance_guid)

            patient = api_get(instance.access_token, 'https://drchrono.com/api/patients/'+str(appt['patient']))

            if patient == False:
                logout(request)
                return render(request, 'index.html', { 'user_access_status': False })

            if patient['gender'] and patient['gender'] != form.cleaned_data.get('gender'):
                return redirect('error', instance_guid=instance_guid)

            if patient['first_name'] and patient['first_name'] != form.cleaned_data.get('first_name'):
                return redirect('error', instance_guid=instance_guid)

            if patient['last_name'] and patient['last_name'] != form.cleaned_data.get('last_name'):
                return redirect('error', instance_guid=instance_guid)

            patient['appt_id'] = appt_id

            update_form = PatientUpdateForm(initial=patient)
            return render(request, 'update.html', { 'form': update_form, 'instance_guid': instance_guid })
        else:
            return redirect('error', instance_guid=instance_guid)
    else:
        return redirect('error', instance_guid=instance_guid)

def complete(request, instance_guid):
    if request.method == 'POST':
        form = PatientUpdateForm(request.POST)
        if form.is_valid():
            instance = Kiosk.objects.get_or_none(guid=instance_guid)
            if not instance:
                return redirect('home')

            appt_id = form.cleaned_data.get('appt_id')
            appt = api_get(instance.access_token, 'https://drchrono.com/api/appointments/'+str(appt_id))

            if appt == False:
                logout(request)
                return render(request, 'index.html', { 'user_access_status': False })

            if appt['doctor'] != instance.doctor_id or appt['status'] != '':
                return redirect('error', instance_guid=instance_guid)

            api_patch(instance.access_token, 'https://drchrono.com/api/patients/'+str(appt['patient']), form.cleaned_data)

            api_patch(instance.access_token, 'https://drchrono.com/api/appointments/'+str(appt_id), { 'status': 'Arrived' })

            # register attendance
            new_visit = Visit(appt_id=appt['id'], doctor_id=instance.doctor_id, patient_id=appt['patient'], appt_time=dateutil.parser.parse(appt['scheduled_time']))
            new_visit.save()

            return render(request, 'complete.html', { 'form': form, 'instance_guid': instance_guid })
        else:
            return render(request, 'update.html', { 'form': form, 'instance_guid': instance_guid })
    else:
        return redirect('error', instance_guid=instance_guid)

@login_required
def doctor(request):
    access_token = request.user.social_auth.get(provider = 'drchrono').extra_data['access_token']

    current_doctor = api_get(access_token, 'https://drchrono.com/api/users/current')

    if current_doctor == False:
        logout(request)
        return render(request, 'index.html', { 'user_access_status': False })

    doctor_id = current_doctor['doctor']

    if request.method == 'POST':
        form = AppointmentSelectionForm(request.POST)
        if form.is_valid():
            appt_id = form.cleaned_data.get('appt_id')
            # patch
            url = 'https://drchrono.com/api/appointments/'+str(appt_id)
            api_patch(access_token, url, { 'status': 'In Session' })

            # update objects
            visit = Visit.objects.get_or_none(appt_id=str(appt_id))
            if visit:
                visit.time_seen = timezone.now()
                visit.save()

                wait_object = Average_wait.objects.get_or_none(doctor_id=doctor_id)

                if wait_object:
                    wait_object.visit_count += 1
                    #! TODO: revisit time sum
                    wait_object.time_sum = wait_object.time_sum +  (visit.time_seen-visit.arrival_time)
                    wait_object.save()

    appts_response = api_get(access_token, 'https://drchrono.com/api/appointments', {'doctor': doctor_id, 'date': str(datetime.date.today())})

    if appts_response == False:
        logout(request)
        return render(request, 'index.html', { 'user_access_status': False })

    appts_for_day = []
    now = timezone.now()
    for appt in appts_response['results']: # returned in order
        if appt['patient']:
            appt_object = {}
            appt_object['status'] = appt['status']
            appt_object['id'] = appt['id']
            appt_object['patient'] = appt['patient']
            appt_object['scheduled_time'] = dateutil.parser.parse(appt['scheduled_time'])

            if appt['status'] == 'Arrived':
                visit = Visit.objects.get_or_none(appt_id=appt['id'])
                if visit:
                    appt_object['arrival_time'] = visit.arrival_time
            appts_for_day.append(appt_object)

    wait_object = Average_wait.objects.get_or_none(doctor_id=doctor_id)
    wait_divisor = wait_object.visit_count
    if wait_divisor == 0:
        wait_divisor = 1

    wait = wait_object.time_sum / wait_divisor

    return render(request, 'doctor.html', { 'appts_for_day': appts_for_day, 'wait': wait, 'now': datetime.datetime.utcnow() })

def error(request, instance_guid):
    return render(request, 'error.html', { 'instance_guid': instance_guid })

def leave(request):
    logout(request)
    return redirect('home')

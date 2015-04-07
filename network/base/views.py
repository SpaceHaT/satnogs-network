import ephem
from datetime import datetime, timedelta

from django.contrib import messages
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from network.base.models import (Station, Transponder, Observation,
                                 Data, Satellite, Antenna)
from network.base.forms import StationForm


def index(request):
    """View to render index page."""
    observations = Observation.objects.all()
    featured_station = Station.objects.filter(online=True).latest('featured_date')

    ctx = {
        'latest_observations': observations.filter(end__lt=now()),
        'scheduled_observations': observations.filter(end__gte=now()),
        'featured_station': featured_station
    }

    return render(request, 'base/home.html', ctx)


def observations_list(request):
    """View to render Observations page."""
    observations = Observation.objects.all()

    return render(request, 'base/observations.html', {'observations': observations})


@login_required
def observation_new(request):
    """View for new observation"""
    me = request.user
    if request.method == 'POST':
        sat_id = request.POST.get('satellite')
        trans_id = request.POST.get('transponder')
        start = request.POST.get('start-time')
        end = request.POST.get('end-time')
        sat = Satellite.objects.get(norad_cat_id=sat_id)
        trans = Transponder.objects.get(id=trans_id)
        obs = Observation(satellite=sat, transponder=trans,
                          author=me, start=start, end=end)
        obs.save()
        total = int(request.POST.get('total'))
        for item in range(total):
            start = request.POST.get('{}-starting_time'.format(item))
            end = request.POST.get('{}-ending_time'.format(item))
            station_id = request.POST.get('{}-station'.format(item))
            ground_station = Station.objects.get(id=station_id)
            Data.objects.create(start=start, end=end, ground_station=ground_station,
                                observation=obs)

        return redirect(reverse('base:observation_view', kwargs={'id': obs.id}))

    satellites = Satellite.objects.filter(transponder__alive=True)
    transponders = Transponder.objects.filter(alive=True)

    return render(request, 'base/observation_new.html', {'satellites': satellites,
                                                         'transponders': transponders})


def prediction_windows(request, sat_id, start_date, end_date):
    sat = get_object_or_404(Satellite, norad_cat_id=sat_id)
    satellite = ephem.readtle(str(sat.tle0), str(sat.tle1), str(sat.tle2))

    end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M')

    data = []

    stations = Station.objects.all()
    for station in stations:
        observer = ephem.Observer()
        observer.lon = str(station.lng)
        observer.lat = str(station.lat)
        observer.elevation = station.alt
        observer.date = str(start_date)
        station_match = False
        keep_digging = True
        while keep_digging:
            tr, azr, tt, altt, ts, azs = observer.next_pass(satellite)

            if ephem.Date(tr).datetime() < end_date:
                if not station_match:
                    station_windows = {
                        'id': station.id,
                        'name': station.name,
                        'window': []
                    }
                    station_match = True

                if ephem.Date(ts).datetime() > end_date:
                    ts = end_date
                    keep_digging = False
                else:
                    time_start_new = ephem.Date(ts).datetime() + timedelta(minutes=1)
                    observer.date = time_start_new.strftime("%Y-%m-%d %H:%M:%S.%f")

                station_windows['window'].append(
                    {
                        'start': ephem.Date(tr).datetime().strftime("%Y-%m-%d %H:%M:%S.%f"),
                        'end': ephem.Date(ts).datetime().strftime("%Y-%m-%d %H:%M:%S.%f"),
                        'az_start': azr
                    })

            else:
                # window start outside of window bounds
                break

        if station_match:
            data.append(station_windows)

    return JsonResponse(data, safe=False)


def observation_view(request, id):
    """View for single observation page."""
    observation = get_object_or_404(Observation, id=id)
    data = Data.objects.filter(observation=observation)

    return render(request, 'base/observation_view.html',
                  {'observation': observation, 'data': data})


def stations_list(request):
    """View to render Stations page."""
    stations = Station.objects.all()
    form = StationForm()
    antennas = Antenna.objects.all()

    return render(request, 'base/stations.html',
                  {'stations': stations, 'form': form, 'antennas': antennas})


def station_view(request, id):
    """View for single station page."""
    station = get_object_or_404(Station, id=id)
    form = StationForm(instance=station)
    antennas = Antenna.objects.all()

    return render(request, 'base/station_view.html',
                  {'station': station, 'form': form, 'antennas': antennas})


@require_POST
def station_edit(request):
    """Edit or add a single station."""
    if request.POST['id']:
        pk = request.POST.get('id')
        station = get_object_or_404(Station, id=pk, owner=request.user)
        form = StationForm(request.POST, request.FILES, instance=station)
    else:
        form = StationForm(request.POST, request.FILES)
    if form.is_valid():
        f = form.save(commit=False)
        f.owner = request.user
        f.save()
        form.save_m2m()
        messages.success(request, ('Successfully saved Ground Station. '
                                   'Run the Health Check to activate it.'))
        return redirect(reverse('base:station_view', kwargs={'id': f.id}))
    else:
        messages.error(request, 'Some fields missing on the form')
        return redirect(reverse('users:view_user', kwargs={'username': request.user.username}))

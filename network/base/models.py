from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now
from django.conf import settings

from network.users.models import User


ANTENNA_BANDS = ['HF', 'VHF', 'UHF', 'L', 'S', 'C', 'X', 'KU']
ANTENNA_TYPES = (
    ('dipole', 'Dipole'),
    ('yagi', 'Yagi'),
    ('helical', 'Helical'),
    ('parabolic', 'Parabolic'),
)
MODE_CHOICES = ['FM', 'AFSK', 'BFSK', 'APRS', 'SSTV', 'CW', 'FMN']


class Antenna(models.Model):
    """Model for antennas tracked with SatNOGS."""
    frequency = models.FloatField(validators=[MinValueValidator(0)])
    band = models.CharField(choices=zip(ANTENNA_BANDS, ANTENNA_BANDS),
                            max_length=5)
    antenna_type = models.CharField(choices=ANTENNA_TYPES, max_length=15)

    def __unicode__(self):
        return "%s - %s - %s" % (self.band, self.antenna_type, self.frequency)


class Station(models.Model):
    """Model for SatNOGS ground stations."""
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=45)
    image = models.ImageField(upload_to='ground_stations', blank=True)
    alt = models.PositiveIntegerField(help_text='In meters above ground')
    lat = models.FloatField(validators=[MaxValueValidator(90),
                                        MinValueValidator(-90)])
    lng = models.FloatField(validators=[MaxValueValidator(180),
                                        MinValueValidator(-180)])
    location = models.CharField(max_length=255, null=True, blank=True)
    antenna = models.ManyToManyField(Antenna, null=True, blank=True,
                                     help_text=('If you want to add a new Antenna '
                                                'contact SatNOGS Team'))
    featured_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True, blank=True)

    def get_image(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return settings.STATION_DEFAULT_IMAGE

    def __unicode__(self):
        return "%d - %s" % (self.pk, self.name)


class Satellite(models.Model):
    """Model for SatNOGS satellites."""
    norad_cat_id = models.PositiveIntegerField()
    name = models.CharField(max_length=45)
    tle0 = models.CharField(max_length=100, null=True)
    tle1 = models.CharField(max_length=200, null=True)
    tle2 = models.CharField(max_length=200, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    def __unicode__(self):
        return self.name


class Transponder(models.Model):
    """Model for antennas transponders."""
    description = models.TextField()
    alive = models.BooleanField(default=True)
    uplink_low = models.PositiveIntegerField(blank=True, null=True)
    uplink_high = models.PositiveIntegerField(blank=True, null=True)
    downlink_low = models.PositiveIntegerField(blank=True, null=True)
    downlink_high = models.PositiveIntegerField(blank=True, null=True)
    mode = models.CharField(choices=zip(MODE_CHOICES, MODE_CHOICES),
                            max_length=10)
    invert = models.BooleanField(default=False)
    baud = models.FloatField(validators=[MinValueValidator(0)])
    satellite = models.ForeignKey(Satellite, related_name='transponder',
                                  null=True)

    def __unicode__(self):
        return self.description


class Observation(models.Model):
    """Model for SatNOGS observations."""
    satellite = models.ForeignKey(Satellite)
    transponder = models.ForeignKey(Transponder, null=True)
    author = models.ForeignKey(User)
    start = models.DateTimeField()
    end = models.DateTimeField()

    @property
    def is_past(self):
        return self.end < now()

    @property
    def is_future(self):
        return self.end > now()

    def __unicode__(self):
        return "%d" % self.id


class Data(models.Model):
    """Model for observation data."""
    start = models.DateTimeField()
    end = models.DateTimeField()
    observation = models.ForeignKey(Observation)
    ground_station = models.ForeignKey(Station)
    payload = models.FileField(upload_to='data_payloads', blank=True, null=True)

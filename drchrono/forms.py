from django import forms

GENDER_OPTIONS = (
    ('Male','Male'),
    ('Female','Female'),
    ('Other','Other'),
)

ETHNICITY_OPTIONS = (
    ('blank', ''),
    ('hispanic', 'Hispanic/Latino'),
    ('not_hispanic', 'Not Hispanic/Latino'),
    ('decline', 'Decline to specify'),
)

RACE_OPTIONS = (
    ('blank', ''),
    ('indian', 'Native Indian/Alaska Native'),
    ('asian', 'Asian'),
    ('black', 'Black or African American'),
    ('hawaiian', 'Native Hawaiian or Other Pacific Islander'),
    ('white', 'White'),
    ('declined', 'Declined to specify'),
)

LANGUAGE_OPTIONS = (
    ('blank', ''),
    ('eng', 'English'),
    ('zho', 'Chinese'),
    ('fra', 'French'),
    ('ita', 'Italian'),
    ('jpn', 'Japanese'),
    ('por', 'Portuguese'),
    ('rus', 'Russian'),
    ('spa', 'Spanish; Castilian'),
    ('other', 'Other'),
    ('unknown', 'Unknown'),
    ('declined', 'Declined to specify'),
)

STATE_OPTIONS = (
    ('','-Select a State-'),
    ('AL','Alabama'),
    ('AK','Alaska'),
    ('AS','American Samoa'),
    ('AZ','Arizona'),
    ('AR','Arkansas'),
    ('AA','Armed Forces Americas'),
    ('AE','Armed Forces Europe'),
    ('AP','Armed Forces Pacific'),
    ('CA','California'),
    ('CO','Colorado'),
    ('CT','Connecticut'),
    ('DE','Delaware'),
    ('DC','District of Columbia'),
    ('FL','Florida'),
    ('GA','Georgia'),
    ('GU','Guam'),
    ('HI','Hawaii'),
    ('ID','Idaho'),
    ('IL','Illinois'),
    ('IN','Indiana'),
    ('IA','Iowa'),
    ('KS','Kansas'),
    ('KY','Kentucky'),
    ('LA','Louisiana'),
    ('ME','Maine'),
    ('MD','Maryland'),
    ('MA','Massachusetts'),
    ('MI','Michigan'),
    ('MN','Minnesota'),
    ('MS','Mississippi'),
    ('MO','Missouri'),
    ('MT','Montana'),
    ('NE','Nebraska'),
    ('NV','Nevada'),
    ('NH','New Hampshire'),
    ('NJ','New Jersey'),
    ('NM','New Mexico'),
    ('NY','New York'),
    ('NC','North Carolina'),
    ('ND','North Dakota'),
    ('MP','Northern Mariana Islands'),
    ('OH','Ohio'),
    ('OK','Oklahoma'),
    ('OR','Oregon'),
    ('PA','Pennsylvania'),
    ('PR','Puerto Rico'),
    ('RI','Rhode Island'),
    ('SC','South Carolina'),
    ('SD','South Dakota'),
    ('TN','Tennessee'),
    ('TX','Texas'),
    ('UT','Utah'),
    ('VT','Vermont'),
    ('VI','Virgin Islands'),
    ('VA','Virginia'),
    ('WA','Washington'),
    ('WV','West Virginia'),
    ('WI','Wisconsin'),
    ('WY','Wyoming'),
)

TIMEZONE_OPTIONS = (
    ('US/Eastern','US Eastern'),
    ('US/Pacific','US Pacific'),
    ('US/Central','US Central'),
    ('US/Mountain','US Mountain'),
    ('US/Alaska','Alaska'),
    ('US/Arizona','Arizona'),
    ('US/Hawaii','Hawaii'),
    ('UTC','Coordinated Universal Time'),
)

# forms go here
class AppointmentSelectionForm(forms.Form):
    appt_id = forms.CharField(max_length=1024) # described in API as either a number or 'Unique identifier. Usually numeric, but not always.'

class PatientVerificationForm(forms.Form):
    appt_id = forms.CharField(widget=forms.HiddenInput(),max_length=1024)
    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)
    gender = forms.ChoiceField(choices=GENDER_OPTIONS)
    date_of_birth = forms.DateField(required=False, widget=forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}))

class PatientUpdateForm(forms.Form):
    appt_id = forms.CharField(widget=forms.HiddenInput(),max_length=1024)
    #social_security_number = forms.CharField(max_length=11, required=False, label='SSN, if available')
    preferred_language = forms.ChoiceField(choices=LANGUAGE_OPTIONS, required=False, label='Preferred Language')

    cell_phone = forms.CharField(max_length=1024, required=False, label='Mobile/SMS-capable phone')
    home_phone = forms.CharField(max_length=1024, required=False, label='Home Phone')

    address = forms.CharField(max_length=1024, required=False, label='Street',)
    city = forms.CharField(max_length=1024, required=False, label='City')
    state = forms.ChoiceField(choices=STATE_OPTIONS, required=False, label='State')
    zip_code = forms.CharField(max_length=10, required=False, label='ZIP')

    emergency_contact_name = forms.CharField(max_length=1024, required=False, label='Emergency contact: Name')
    emergency_contact_phone = forms.CharField(max_length=1024, required=False, label='Emergency contact: Phone')
    emergency_contact_relation = forms.CharField(max_length=1024, required=False, label='Emergency contact: Relation')

    employer = forms.CharField(max_length=1024, required=False, label='Employer: Name')
    employer_address = forms.CharField(max_length=1024, required=False, label='Employer: Street')
    employer_city = forms.CharField(max_length=1024, required=False, label='Employer: City')
    employer_state = forms.ChoiceField(choices=STATE_OPTIONS, required=False, label='Employer: State')
    employer_zip_code = forms.CharField(max_length=10, required=False, label='Employer: ZIP')

    race = forms.ChoiceField(choices=RACE_OPTIONS, required=False, label='Race')
    ethnicity = forms.ChoiceField(choices=ETHNICITY_OPTIONS, required=False, label='Ethnicity')

class SettingsUpdateForm(forms.Form):
    timezone = forms.ChoiceField(choices=TIMEZONE_OPTIONS, label="Timezone")

class TerminateKioskInstanceForm(forms.Form):
    action = forms.CharField(max_length=1024, required=False, label='Enter terminate below to sign out of your kiosks')

import datetime
from urllib.request import urlopen
import json

def hcAPICall(date):
    return(
        'http://www.hebcal.com/hebcal/?v=1&cfg=json&maj=on&min=on&nx=on&mf=on&ss=on&mod=on&s=on&c=on&geo=zip&zip=19103&m=42&d=off&o=on&year='
         + str(date.year)
         + '&month='
         + str(date.month)
    )

def roundmin(t, n):
    if t.minute % n > n/2:
        return t + datetime.timedelta(minutes = (n - t.minute % n))
    else:
        return t + datetime.timedelta(minutes = -(t.minute % n))

def truncmin(t, n):
    return t + datetime.timedelta(minutes = -(t.minute % n))


today = datetime.date.today()

# while True:
#     option = input('[1] Current week\n[2] Next week\n> ')
#     if option == '1' or option == '2':
#         break
#
# if option == '1':
#     dateBegin = today
#     dateEnd = today + timedelta(days = (5 - today.isoweekday()) % 7)
# elif option == '2':
dateBegin = today + datetime.timedelta(days = (5 - today.isoweekday()) % 7)
dateEnd = dateBegin + datetime.timedelta(days = 7)

oudata =   json.loads(
                urlopen(
                    'http://db.ou.org/zmanim/getCalendarData.php?mode=drange&dateBegin='
                     + (dateBegin + datetime.timedelta(days = -1)).strftime('%m/%d/%Y')
                     + '&dateEnd='
                     + dateEnd.strftime('%m/%d/%Y')
                     + '&lat=39.951285&lng=-75.174136&timezone=America/New_York'
                ).read().decode('utf-8', 'strict')
            )['days']

hcdata =   json.loads(
                urlopen(
                    hcAPICall(dateBegin)
                ).read().decode('utf-8', 'strict')
            )['items']

if (dateBegin.year, dateBegin.month) != (dateEnd.year, dateEnd.month):
    hcdata =    hcdata + json.loads(
                    urlopen(
                        hcAPICall(dateEnd)
                    ).read().decode('utf-8', 'strict')
                )['items']

hcdata = [item  for item 
                in hcdata 
                if item['date'][0:10] >= dateBegin.strftime('%Y-%m-%d') 
                and item['date'][0:10] <= dateEnd.strftime('%Y-%m-%d')]

newsletter = ''

fileName        =  'newsletter-' + dateBegin.strftime('%Y-%m-%d') + '-to-' + dateEnd.strftime('%Y-%m-%d') + '.html'

print('Newsletter calendar from ' + dateBegin.strftime('%m/%d/%Y') + ' to ' + dateEnd.strftime('%m/%d/%Y') + '\nsaved in ' + fileName)

file    = open(fileName, 'w')

# HEADER OF THE NEWSLETTER
# Name of the parasha of the week
parashaName = [item['title'] 
                for item 
                in hcdata 
                if item['category'] == 'parashat'][0]
hebrewDate  = [item['hebDateString']
                for item
                in oudata
                if item['engDateString'] == (dateBegin + datetime.timedelta(days = 1)).strftime('%m/%d/%Y')][0]

newsletter = newsletter + '<h3 style="text-align: center;">' + parashaName + '</h3>\n'

# Hebrew and secular dates for that Shabbat
newsletter = newsletter + '<p style="text-align: center;">' + dateBegin.strftime('%B %-d') + '-' + str(dateBegin.day + 1) + ' ' + str(dateBegin.year) + '<br/>\n' + hebrewDate + '<br/>\n'

# Link to eruv status
newsletter = newsletter + '<a href="http://www.centercityeruv.org/">Eruv Status</a></p><hr />\n<p style="text-align: center;">Do you have something to post in Mekor\'s weekly newsletter?<br />\nContact the newsletter\'s <a href="newsletter@mekorhabracha.org">editorial team</a> by next Thursday at 6pm</p>'

# WEEKLY AGENDA SECTION
# Title of the agenda section
newsletter = newsletter + '<hr />\n<h1>This Week at Mekor Habracha</h1>\n'

for d in range(8):
    
    #Create Date object with the date of each of the days covered by the newsletter
    day = dateBegin + datetime.timedelta(days = d)
    
    #Title of the day in the agenda section
    newsletter = newsletter + '\n<h4>' + day.strftime('%A, %B %-d' + '</h4>\n\n<p>\n')
    
    #Calculate sunset for that day, as a DateTime object
    sunset = datetime.datetime.strptime(
                [item['zmanim']['sunset'] 
                    for item 
                    in oudata 
                    if item['engDateString'] == day.strftime('%m/%d/%Y')][0],
                    '%H:%M:%S')
                    
    chatzot = datetime.datetime.strptime(
                [item['zmanim']['chatzos'] 
                    for item 
                    in oudata 
                    if item['engDateString'] == day.strftime('%m/%d/%Y')][0],
                    '%H:%M:%S')
                    
    previouschatzot = datetime.datetime.strptime(
                [item['zmanim']['chatzos'] 
                    for item 
                    in oudata 
                    if item['engDateString'] == (day + datetime.timedelta(days = -1)).strftime('%m/%d/%Y')][0],
                    '%H:%M:%S')
    
    if (chatzot - previouschatzot).total_seconds() < -3000:
        newsletter = newsletter + '<strong>Fall back! Daylight Savings Time ends.</strong><br/></p>\n<p>'
    elif (chatzot - previouschatzot).total_seconds() > 3000:
        newsletter = newsletter + '<strong>Spring forward! Daylight Savings Time begins.</strong><br/></p>\n<p>'
    
    #Specify the standard time shacharit starts as a function of the day of the week
    if day.isoweekday()==1:     #Monday
        shacharit = datetime.time(6,45)
    elif day.isoweekday()==2:   #Tuesday
        shacharit = datetime.time(7)
    elif day.isoweekday()==3:   #Wednesday
        shacharit = datetime.time(7)
    elif day.isoweekday()==4:   #Thursday
        shacharit = datetime.time(6,45)
    elif day.isoweekday()==5:   #Friday
        shacharit = datetime.time(7)
    elif day.isoweekday()==6:   #Saturday
        #RH: 'Shacharit: 9:15 am – 11:45 am'
        shacharit = datetime.time(9,15)
    elif day.isoweekday()==7:   #Sunday
        shacharit = datetime.time(9)
        
    #On weekdays (Mo-Fr) add the morning seder at 6am
    if day.isoweekday()<6:
        newsletter = newsletter + '6:00am &mdash; Morning Learning Seder<br/>\n'
        
    newsletter = newsletter + shacharit.strftime('%-I:%M%p').lower() + ' &mdash; Shacharit<br/>\n'
    
    #On Fridays calculate time for mincha and hadliqat nerot
    if day.isoweekday()==5:
        
        #We subtract 18 minutes, truncating the seconds data
        nerot = sunset + datetime.timedelta(minutes = -18)
        
        #RH: 'Mincha Erev Shabbat: 5-10 mins after candle lighting'
        #RH: 'Kabalat Shabbat: lump with mincha'
        mincha = roundmin(nerot + datetime.timedelta(minutes = 5), 5)
        newsletter = newsletter + nerot.strftime('%-I:%M%p').lower()  + ' &mdash; Candle lighting<br/>\n'
        newsletter = newsletter + mincha.strftime('%-I:%M%p').lower() + ' &mdash; Mincha, Kabbalat Shabbat and Ma\'ariv<br/>\n'
        
    if day.isoweekday()==6:
        newsletter = newsletter + '10:45am &mdash; Tot Shabbat<br/>\n'
        newsletter = newsletter + '11:45am &mdash; Kiddush, <a href="mailto:mekorkiddush@gmail.com">still available to be sponsored</a><br/>\n'
        
        sunset  = sunset + datetime.timedelta(minutes = round(sunset.second / 60))
        
        mincha  = truncmin(sunset + datetime.timedelta(minutes = -30), 15)
        seuda   = roundmin(sunset + datetime.timedelta(minutes = -15), 5)
        maariv  = roundmin(sunset + datetime.timedelta(minutes = 32), 5)
        havdala = sunset + datetime.timedelta(minutes = 42)
        
        newsletter = newsletter + mincha.strftime('%-I:%M%p').lower()  + ' &mdash; Mincha<br/>\n'
        newsletter = newsletter + seuda.strftime('%-I:%M%p').lower()   + ' &mdash; Third meal, <a href="mailto:mekorkiddush@gmail.com">still available to be sponsored</a><br/>\n'
        newsletter = newsletter + maariv.strftime('%-I:%M%p').lower()  + ' &mdash; Ma\'ariv<br/>\n'
        newsletter = newsletter + havdala.strftime('%-I:%M%p').lower() + ' &mdash; Havdala / Shabbat ends<br/>\n'
        
    newsletter = newsletter + '</p>\n'

file.write(newsletter)
file.close()
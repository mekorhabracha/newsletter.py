WEEKS_OFFSET = 0

from datetime import date, time, datetime, timedelta
from urllib.request import urlopen
import json

def hcAPICall(date):
    return(
        'http://www.hebcal.com/hebcal/?v=1&cfg=json&maj=on&min=on&nx=on&mf=on&ss=on&mod=on&s=on&c=on&geo=zip&zip=19103&m=42&d=off&o=on&year='
         + str(date.year)
         + '&month='
         + str(date.month)
    )

def hcAjax(dateBegin, dateEnd):
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
  return  [item   for item 
                  in hcdata 
                  if item['date'][0:10] >= dateBegin.strftime('%Y-%m-%d') 
                  and item['date'][0:10] <= dateEnd.strftime('%Y-%m-%d')]

def ouAjax(dateBegin, dateEnd):
  return  json.loads(
            urlopen(
                'http://db.ou.org/zmanim/getCalendarData.php?mode=drange&dateBegin='
                 + (dateBegin + timedelta(days = -1)).strftime('%m/%d/%Y')
                 + '&dateEnd='
                 + dateEnd.strftime('%m/%d/%Y')
                 + '&lat=39.951285&lng=-75.174136&timezone=America/New_York'
            ).read().decode('utf-8', 'strict')
          )['days']

def roundmin(t, n):
  if t.minute % n > n/2:
    return t + timedelta(minutes = (n - t.minute % n), seconds = -t.second)
  else:
    return t + timedelta(minutes = -(t.minute % n), seconds = -t.second)

def truncmin(t, n):
  return t + timedelta(minutes = -(t.minute % n), seconds = -t.second)

def ftime(time):
  return time.strftime('%-I:%M%p').lower()
def isLeapYear(year):
  if year % 4 == 0 and year % 100 == 0:
    if year % 400 != 0:
      return False
    if year % 400 == 0:
      return True
  if year % 4 == 0 and year % 100 != 0:
    return True
  if year % 4 != 0 :
    return False

def birkatHashanim(date):
  veTenTal = '**At Ma\'ariv we begin reciting *veTen Tal uMatar* in *Birkat haShanim***\n\n'
# TODO Add veTenBracha conditions
  if   date.month == 12 and date.day == 4 and not isLeapYear(date.year + 1) and date.isoweekday() != 5:
    return veTenTal
  elif date.month == 12 and date.day == 5 and not isLeapYear(date.year + 1) and date.isoweekday() == 6:
    return veTenTal
  elif date.month == 12 and date.day == 5 and     isLeapYear(date.year + 1) and date.isoweekday() != 5:
    return veTenTal
  elif date.month == 12 and date.day == 6 and     isLeapYear(date.year + 1) and date.isoweekday() == 6:
    return veTenTal
  else:
    return ''

def daylightSavingsTime(day, noon, oudata):
  noonYesterday = datetime.strptime(
              [item['zmanim']['chatzos'] 
                  for item 
                  in oudata 
                  if item['engDateString'] == (day + timedelta(days = -1)).strftime('%m/%d/%Y')][0],
                  '%H:%M:%S')
  if (noon - noonYesterday).total_seconds() < -3000:
    return '**Fall back! Daylight Savings Time ends.**\n\n'
  elif (noon - noonYesterday).total_seconds() > 3000:
    return '**Spring forward! Daylight Savings Time begins.**\n\n'
  else:
    return ''

def holidays(day, hcdata):
  return  [item['title'] 
            for item 
            in hcdata 
            if item['category'] == 'holiday'
            and item['date'][0:10] == day.strftime('%Y-%m-%d')]

def hasHallel(holidays):
  hag = 0
  hag = hag + sum(['Chanukah' in item for item in holidays if '1 Candle' not in item])
  hag = hag + sum(['Rosh Chodesh' in item for item in holidays])
  # TODO Add Chol haMoed and other hallels
  return hag > 0

def hanukaCandles(day, hcdata):
  candles = [item
              for item
              in holidays(day, hcdata)
              if 'Chanukah' in item
              and 'Candle' in item]
  if len(candles) > 0:
    return candles[0].split(': ')[1].lower()
  else:
    return ''

def shacharitTime(day, hcdata, oudata):
  #Specify the standard time shacharit starts as a function of the day of the week
  if day.isoweekday()==1:     #Monday
      shacharit = time(6,45)
  elif day.isoweekday()==2:   #Tuesday
      shacharit = time(7)
  elif day.isoweekday()==3:   #Wednesday
      shacharit = time(7)
  elif day.isoweekday()==4:   #Thursday
      shacharit = time(6,45)
  elif day.isoweekday()==5:   #Friday
      shacharit = time(7)
  elif day.isoweekday()==6:   #Saturday
      #RH: 'Shacharit: 9:15 am – 11:45 am'
      shacharit = time(9,15)
  elif day.isoweekday()==7:   #Sunday
      shacharit = time(9)
  
  shacharit = datetime.combine(day, shacharit)
  
  if hasHallel(holidays(day, hcdata)) and day.isoweekday()<6:
    shacharit = shacharit + timedelta(minutes = -15)
  # TODO Add other modifiers of shacharit
  return shacharit

def zmanim(day, zman, oudata):
  return  datetime.strptime(
            [item['zmanim'][zman] 
                for item 
                in oudata 
                if item['engDateString'] == day.strftime('%m/%d/%Y')][0],
                '%H:%M:%S')

today = date.today() + timedelta(weeks = WEEKS_OFFSET)

# while True:
#     option = input('[1] Current week\n[2] Next week\n> ')
#     if option == '1' or option == '2':
#         break
#
# if option == '1':
#     dateBegin = today
#     dateEnd = today + timedelta(days = (5 - today.isoweekday()) % 7)
# elif option == '2':
dateBegin = today + timedelta(days = (5 - today.isoweekday()) % 7)
dateEnd = dateBegin + timedelta(days = 7)

oudata = ouAjax(dateBegin, dateEnd)
hcdata = hcAjax(dateBegin, dateEnd)

newsletter = ''

fileName = 'newsletter-' + dateBegin.strftime('%Y-%m-%d') + '-to-' + dateEnd.strftime('%Y-%m-%d') + '.md'

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
                if item['engDateString'] == (dateBegin + timedelta(days = 1)).strftime('%m/%d/%Y')][0]

newsletter += '<h3 style="text-align: center;">' + parashaName + '</h3>\n'

# Hebrew and secular dates for that Shabbat
newsletter += '<p style="text-align: center;">' + dateBegin.strftime('%B %-d') + '-' + str(dateBegin.day + 1) + ' ' + str(dateBegin.year) + '<br />' + hebrewDate + '<br />[Eruv Status](http://www.centercityeruv.org/)</p>\n'

# Link to eruv status
newsletter += '\n---\n\n<p style="text-align: center;">Do you have something to post in Mekor\'s weekly newsletter?\nContact the newsletter\'s [editorial team](mailto:newsletter@mekorhabracha.org) by next Thursday at 6pm</p>\n'

# WEEKLY AGENDA SECTION
# Title of the agenda section
newsletter += '\n---\n\n#<br/ >This Week at Mekor Habracha\n'

for d in range(8):
  
    #Create Date object with the date of each of the days covered by the newsletter
    day = dateBegin + timedelta(days = d)
    
    #Title of the day in the agenda section
    newsletter += '\n####<br />' + day.strftime('%A, %B %-d')
    if len(holidays(day, hcdata)) > 0:
      newsletter += ' --- ' + ', '.join(holidays(day,hcdata))
    newsletter += '\n\n'
    
    #Calculate times for that day, as datetime objects
    noon = zmanim(day, 'chatzos', oudata) 
    sunset = zmanim(day, 'sunset', oudata) 
    earlyMincha = zmanim(day, 'mincha_gedola_ma', oudata) 
    havdala = truncmin(zmanim(day, 'tzeis_42_minutes', oudata) + timedelta(minutes=1), 1)
    
    #Add mention to changes in Daylight Savings Time
    newsletter += daylightSavingsTime(day, noon, oudata)

    #Add mention to changes in Birkat haShanim
    newsletter += birkatHashanim(day)

    # TODO Luach string: Hallel, alHaNissim, Yaale, Birkat haShanim

    shacharit = shacharitTime(day, hcdata, oudata)
    
    #On weekdays (Mo-Fr) add the morning seder at 6am
    if day.isoweekday()<6:
        newsletter += '6:00am --- Morning Learning Seder\n'
        
    newsletter += ftime(shacharit) + ' --- Shacharit'  
    # if hasHallel(holidays(day, hcdata)):
    #   newsletter += ' (including Hallel)'
    newsletter += '\n'

    if day.isoweekday()!= 5 and day.isoweekday()!= 6 and hanukaCandles(day, hcdata) != '':
      newsletter += ftime(havdala) + ' --- Earliest menora lighting (' + hanukaCandles(day, hcdata) + ')\n'
    
    #On Fridays calculate time for mincha and hadliqat nerot
    if day.isoweekday()==5:
      
      #We subtract 18 minutes, truncating the seconds data
      nerot = sunset + timedelta(minutes = -18)
      
      #RH: 'Mincha Erev Shabbat: 5-10 mins after candle lighting'
      #RH: 'Kabalat Shabbat: lump with mincha'
      mincha = roundmin(nerot + timedelta(minutes = 5), 5)
      if hanukaCandles(day, hcdata) != '':
        newsletter += ftime(nerot)  + ' --- Menora (' + hanukaCandles(day, hcdata) + ') and Shabbat candle lighting\n'
      else:
        newsletter += ftime(nerot)  + ' --- Candle lighting\n'
      newsletter += ftime(mincha) + ' --- Mincha, Kabbalat Shabbat and Ma\'ariv\n'
        
    if day.isoweekday()==6:
        newsletter += '10:45am --- Tot Shabbat\n'
        newsletter += '11:45am --- Kiddush, [still available to be sponsored](mailto:mekorkiddush@gmail.com)\n'
        
        sunset  = truncmin(sunset + timedelta(minutes = 1), 1)
        
        if noon.hour < 12:
            mincha = truncmin(earlyMincha, 15) + timedelta(minutes = 15)
        elif noon.hour >= 12:
            mincha  = truncmin(sunset + timedelta(minutes = -30), 15)
        
        seuda   = roundmin(sunset + timedelta(minutes = -15), 5)
        maariv  = roundmin(sunset + timedelta(minutes = 32), 5)
        
        newsletter += ftime(mincha)  + ' --- Mincha\n'
        newsletter += ftime(seuda)   + ' --- Third meal, [still available to be sponsored](mailto:mekorkiddush@gmail.com)\n'
        newsletter += ftime(maariv)  + ' --- Ma\'ariv\n'
        if hanukaCandles(day, hcdata) != '':
          newsletter += ftime(havdala) + ' --- Havdala / Shabbat ends / Earliest menora lighting (' + hanukaCandles(day, hcdata) + ')\n'
        else:
          newsletter += ftime(havdala) + ' --- Havdala / Shabbat ends\n'
        
    newsletter += '\n'

file.write(newsletter)
file.close()
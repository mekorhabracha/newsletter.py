import datetime
from urllib.request import urlopen
import json

def ouTimeSearch(oudata, date, string):
    for data in oudata:
        if data["engDateString"]==date.strftime("%m/%d/%Y"):
            return datetime.datetime.strptime(data["zmanim"][string], "%H:%M:%S")

def hcParashaSearch(hcdata, date):
    date = date + datetime.timedelta(days = 1)
    for data in hcdata:
        if data["date"][0:10]==date.strftime("%Y-%m-%d"):
            return data["title"]

def round5min(t):
    if t.minute % 5 > 2:
        return t + datetime.timedelta(minutes = (5 - t.minute % 5))
    else:
        return t + datetime.timedelta(minutes = -(t.minute % 5))

today = datetime.date.today()

# while True:
#     option = input("[1] Current week\n[2] Next week\n> ")
#     if option == "1" or option == "2":
#         break
#
# if option == "1":
#     dateBegin = today
#     dateEnd = today + timedelta(days = (5 - today.isoweekday()) % 7)
# elif option == "2":
dateBegin = today + datetime.timedelta(days = (5 - today.isoweekday()) % 7)
dateEnd = dateBegin + datetime.timedelta(days = 7)

print("Calendar from " + dateBegin.strftime("%m/%d/%Y") + " to " + dateEnd.strftime("%m/%d/%Y"))

oudata = urlopen("http://db.ou.org/zmanim/getCalendarData.php?mode=drange&dateBegin=" + dateBegin.strftime("%m/%d/%Y") + "&dateEnd=" + dateEnd.strftime("%m/%d/%Y") + "&lat=39.951285&lng=-75.174136&timezone=America/New_York").read().decode("utf-8", "strict")
oudata = json.loads(oudata)["days"]

hcdata = urlopen("http://www.hebcal.com/hebcal/?v=1&cfg=json&maj=on&min=on&mod=on&nx=on&mf=on&ss=on&s=on&ss=on&mf=on&c=on&geo=zip&zip=19103&m=42&year=" + str(dateBegin.year) + "&month=" + str(dateBegin.month)).read().decode("utf-8", "strict")
hcdata = json.loads(hcdata)["items"]

fileName = "newsletter-"+dateBegin.strftime("%Y-%m-%d")+"-to-"+dateEnd.strftime("%Y-%m-%d")+".md"
file = open(fileName, "w")
file.write("###" + hcParashaSearch(hcdata, dateBegin) + "\n")
file.write(dateBegin.strftime("%B %-d") + "-" + str(dateBegin.day + 1) + " " + str(dateBegin.year) + "\n")
file.write(oudata[1]["hebDateString"] + "\n")
file.write("[Eruv Status](http://www.centercityeruv.org/)\n\n* * *\n\n")
file.write("#This Week at Mekor Habracha\n")

for d in range(8):
    dat = dateBegin + datetime.timedelta(days = d)
    file.write("\n####" + dat.strftime("%A, %B %-d" + "\n"))

    if dat.isoweekday()==1:
        shacharit = datetime.time(6,45)
    elif dat.isoweekday()==2:
        shacharit = datetime.time(7)
    elif dat.isoweekday()==3:
        shacharit = datetime.time(7)
    elif dat.isoweekday()==4:
        shacharit = datetime.time(6,45)
    elif dat.isoweekday()==5:
        shacharit = datetime.time(7)
    elif dat.isoweekday()==6:
        shacharit = datetime.time(9,15)
    elif dat.isoweekday()==7:
        shacharit = datetime.time(9)

    if dat.isoweekday()<6:
        file.write("6:00am --- Morning Learning Seder\n")
        
    file.write(shacharit.strftime("%-I:%M%p").lower() + " --- Shacharit\n")

    if dat.isoweekday()==5:
        nerot = ouTimeSearch(oudata, dat, "sunset") + datetime.timedelta(minutes = 18)
        mincha = round5min(nerot + datetime.timedelta(minutes = 5))
        file.write(nerot.strftime("%-I:%M%p").lower()  + " --- Candle lighting\n")
        file.write(mincha.strftime("%-I:%M%p").lower() + " --- Mincha, Kabbalat Shabbat and Ma'ariv\n")

    if dat.isoweekday()==6:
        file.write("10:45am --- Tot Shabbat\n")
        file.write("11:45am --- Kiddush, [still available to be sponsored](mailto:mekorkiddush@gmail.com)\n")

        sunset  = ouTimeSearch(oudata, dat, "sunset")
        sunset  = sunset + datetime.timedelta(minutes = round(sunset.second / 60))

        mincha  = round5min(sunset + datetime.timedelta(minutes = -45))
        seuda   = round5min(sunset + datetime.timedelta(minutes = -15))
        maariv  = round5min(sunset + datetime.timedelta(minutes = 32))
        havdala = sunset + datetime.timedelta(minutes = 42)
        
        file.write(mincha.strftime("%-I:%M%p").lower()  + " --- Mincha\n")
        file.write(seuda.strftime("%-I:%M%p").lower()   + " --- Third meal, [still available to be sponsored](mailto:mekorkiddush@gmail.com)\n")
        file.write(maariv.strftime("%-I:%M%p").lower()  + " --- Ma'ariv\n")
        file.write(havdala.strftime("%-I:%M%p").lower() + " --- Havdala / Shabbat ends\n")


file.close()
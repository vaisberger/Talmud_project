import urllib.request
import urllib.error

mishnayot = []  
citations = []
mishna=""
citation=""
raw_data=""
daf=""
url=input("Please enter the url\n")
try:
    raw_data=urllib.request.urlopen(url).read().decode('utf-8')
except urllib.error.URLError as e:
    print("Error accessing URL")

found_start=False
index=0
lineS=0
lineE=0
for line in raw_data.split('\n'):
   if "Daf" in line:
       daf=line.split(' ')[1]

   if not found_start and "<big><strong>מתני׳</strong></big>" in line:
       found_start=True
       start=line.index("<big><strong>מתני׳</strong></big>")+len("<big><strong>מתני׳</strong></big>")
   elif not found_start and "מתני׳ <big><strong>" in line:
       found_start=True
       start=line.index("</strong></big>")+len("</strong></big>")
   if found_start: 
     if ":" in line:
        found_start=False
        end=line.index(":")
        if ":" in line[start:]:
         mishna+=line[start:end]+"\n"
        else:
           mishna+=line[:end]+"\n"
        index+=1
        mishnayot.append({"index":{index},"daf":{daf},"mishna":{mishna}})
        mishna=""
     else:
       if "<big><strong>" not in line:
        mishna+=line+'\n'
       else:
        mishna+=line[start:]+'\n'

                    
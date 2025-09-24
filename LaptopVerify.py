import platform
import psutil
import subprocess
import datetime
import wmi
from bs4 import BeautifulSoup


print(platform.processor())

os = platform.platform()
print("OS Version: " + os) #windows version

def ram():

    ram_bytes = psutil.virtual_memory().total
    return round(ram_bytes / (1024**3))


print("RAM: "+str(ram()) + " GB")


def getRamDetails():
    try:
        c = wmi.WMI()
        ram_modules = []
        for mem in c.Win32_PhysicalMemory():
            ram_modules.append({
                "manufacturer": mem.Manufacturer,
                "capacity (GB)": round(int(mem.Capacity) / (1024**3)),
                "speed (Mhz)": mem.Speed,
            })
        return ram_modules
    except Exception as e:
        return f"RAM info unavailable: {e}"


RamDetails = getRamDetails()
print("RAM slots used: "+str(len(RamDetails)))
c=0
for i in RamDetails:
    c+=1
    print("Stick "+str(c) + ": " + str(i))





def diskDetails():

    typDiskSizes = [32,64,128,256,512,1000,2000]
    details = []


    du = psutil.disk_usage('/')

    diskSize = round(du.total / 1000000000)
    approxSize  = min(typDiskSizes, key=lambda x: abs(x - diskSize))
    details.append(approxSize)
    details.append(round(du.used / 1000000000))
    details.append(round(du.free / 1000000000))
    details.append(round(du.percent))



    return details


diskDetTitles = ["Total","Used","Free","Percent"]
disk =  dict(zip(diskDetTitles,diskDetails()))
print("Storage: "+str(disk))


def BatteryHealth():


    report = subprocess.check_output("powercfg /batteryreport /output battery.html", shell=True)

    f = open("battery.html","r",encoding="utf-8")

    soup = BeautifulSoup(f, "lxml")
    tables = soup.find_all("table")
    #print(tables)
    battery_table = None
    for table in tables:
        if "design capacity" in table.text.lower():
            battery_table = table
            break

    if not battery_table:
        print("Battery table not found.")
        return None

    # Extract rows
    info = {}
    rows = battery_table.find_all("tr")
    for row in rows:
        cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
        if len(cols) == 2:  # key-value pairs
            key, value = cols
            info[key] = value


    # design_capacity = info.get("DESIGN CAPACITY", "Unknown")
    # full_capacity = info.get("FULL CHARGE CAPACITY", "Unknown")
    # cycle_count = info.get("CYCLE COUNT", "Unknown")
    #
    # # print("Design Capacity: "+str(design_capacity))
    # # print("Full Capacity: "+str(full_capacity))
    # # print("Cycle Count: "+str(cycle_count))

    return info








print(BatteryHealth())
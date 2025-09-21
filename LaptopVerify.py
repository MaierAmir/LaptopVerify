import platform
import psutil
import subprocess
import datetime
import wmi


print(platform.processor())

os = platform.platform()
print("OS Version: " + os) #windows version

def ram():

    ram_bytes = psutil.virtual_memory().total
    return round(ram_bytes / (1024**3))


print("RAM: "+str(ram()) + " GB")


def get_ram_details():
    try:
        c = wmi.WMI()
        ram_modules = []
        for mem in c.Win32_PhysicalMemory():
            ram_modules.append({
                "manufacturer": mem.Manufacturer,
                "capacity (gb)": round(int(mem.Capacity) / (1024**3)),
                "speed (mhz)": mem.Speed,
            })
        return ram_modules
    except Exception as e:
        return f"RAM info unavailable: {e}"

RamDetails = get_ram_details()
print("RAM slots used: "+str(len(RamDetails)))
c=0
for i in RamDetails:
    c+=1
    print("Stick "+str(c) + ": " + str(i))





def diskdetails():

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



print("Storage: "+str(diskdetails())+" GB")
print("git test")
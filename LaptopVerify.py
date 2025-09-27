import platform
import subprocess
import wmi
from bs4 import BeautifulSoup
import json

def cpu():
    c=wmi.WMI()

    for cpu in c.Win32_Processor():
        return [cpu.Name, cpu.NumberOfCores, cpu.NumberOfLogicalProcessors, cpu.MaxClockSpeed, cpu.Manufacturer]

print(cpu())

os = platform.platform()
print("OS Version: " + os) #windows version


def pc():
    c = wmi.WMI()
    info = {}

    for i in c.Win32_ComputerSystem():
        info['Manufacturer'] = i.Manufacturer
        info['Model'] = i.Model


    for j in c.Win32_BIOS():
        info['BIOSSerialNumber'] = j.SerialNumber
        info['BIOSVersion'] = j.SMBIOSBIOSVersion
        info['BIOSManufacturer'] = j.Manufacturer

        # System Product (product id / sku)
    for k in c.Win32_ComputerSystemProduct():
        info['ProductVersion'] = k.Version
        info['ProductUUID'] = k.UUID
        info['ProductName'] = k.Name

    for system in c.Win32_BIOS():
        info['SN']=system.SerialNumber

    return info

print(pc())


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



def ram():
    total = 0
    for i in getRamDetails():
        total +=  i['capacity (GB)']

    return total

print("Total RAM (GB):"+str(ram()))

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


    info = {}
    rows = battery_table.find_all("tr")
    for row in rows:
        cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
        if len(cols) == 2:
            key, value = cols
            info[key] = value


    return info

print(BatteryHealth())



def diskDetails():
    cmd = [
        "powershell",
        "-Command",
        "Get-PhysicalDisk | Select FriendlyName,MediaType,BusType,Size | ConvertTo-Json -Compress"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("PowerShell command failed: " + result.stderr)

    try:
        disks = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse JSON: " + result.stdout)


    if isinstance(disks, dict):
        disks = [disks]

    for d in disks:
        if "Size" in d and d["Size"] is not None:
            d["SizeGB"] = round(int(d["Size"]) / (1000**3))

    return disks


for d in diskDetails():
    print(f"Name: {d['FriendlyName']}\nMedia: {d['MediaType']}\nBus: {d['BusType']}\n{d['SizeGB']} GB")



pcinfo = str(BatteryHealth()) + str(diskDetails()) + str(getRamDetails()) + str(ram()) + str(pc()) + str(cpu())
print(pcinfo)

###############################################################

#Render backend:
#Authenticity Scan (powered by gemini AI)

###############################################################

import requests

def send_pcinfo(pcinfo):
    url = "https://laptopverifybackend.onrender.com/authenticityCheck"
    try:
        response = requests.post(url, json={"pcinfo": pcinfo})
        response.raise_for_status()
        return response.json().get("result")
    except Exception as e:
        return f"Error contacting backend: {e}"

print(send_pcinfo(pcinfo))

#TODO
#GPU


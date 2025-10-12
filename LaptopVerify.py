import platform
import subprocess
import wmi
from PySide6.QtGui import QFont, QColor
from bs4 import BeautifulSoup
import json
import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QFileDialog, QGridLayout, \
    QLabel, QGraphicsDropShadowEffect, QFrame

hasBattery = True

def cpu():
    c=wmi.WMI()

    for cpu in c.Win32_Processor():
        return [cpu.Name, cpu.NumberOfCores, cpu.NumberOfLogicalProcessors, cpu.MaxClockSpeed, cpu.Manufacturer]

print(cpu())

os = platform.platform()
print("OS Version: " + os) #windows version

def gpu():
    c=wmi.WMI()
    gpus = []

    for gpu in c.Win32_VideoController():
        gpus.append({"gpu": gpu.name})

    return gpus
print(gpu())

def pc():
    global hasBattery
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

    if  len(c.Win32_Battery()) <1:
        hasBattery = False

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
if hasBattery:
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


if hasBattery:
    pcinfo = str(BatteryHealth()) + str(diskDetails()) + str(getRamDetails()) + str(ram()) + str(pc()) + str(cpu()) +str(gpu())
else:
    pcinfo =str(diskDetails()) + str(getRamDetails()) + str(ram()) + str(pc()) + str(cpu()) + str(gpu())
print(pcinfo)

###############################################################

#Render backend:
#Authenticity Scan (powered by gemini AI)

###############################################################



def send_pcinfo(pcinfo):
    url = "https://laptopverifybackend.onrender.com/authenticityCheck"
    try:
        response = requests.post(url, json={"pcinfo": pcinfo})
        response.raise_for_status()
        return response.json().get("result")
    except Exception as e:
        return f"Error contacting backend: {e}"

#print(send_pcinfo(pcinfo))


#input("Press any key to continue...")


#TODO
# Listing Analyzer
# Front end UI
# Backend wait time (Render spin down)


app = QApplication([])
window = QWidget()

layout = QGridLayout()

btnPcInfo = QPushButton("Authenticity Check")

output = QTextEdit()

font = QFont("Segoe UI", 12)
font.setBold(True)
btnPcInfo.setFont(font)

specSS = """
QTextEdit {
    background-color: #2b2b30;        
    color: #ffffff;                    
    border: 1px solid #3c3c3c;           
    border-radius: 12px;               
    padding: 10px;                         
    font-family: 'Segoe UI';              
    font-size: 12pt;                      
}
QTextEdit:focus {
    border: 1px solid #4CAF50;           
}
"""

cpu = cpu()
cpustr ="CPU: "+cpu[4]+"\n\n"+ str(cpu[0]) + "\n\nCores: " + str(cpu[1]) +"\n\nThreads: " + str(cpu[2])+"\n\nClock speed: " +str(cpu[3]) + " Mhz"



ramstr ="RAM: " + str(ram()) + " GB\nSlots Used: " + str(len(getRamDetails()))+"\n"
slot = 1
for i in getRamDetails():

    ramstr += "\nSlot "+str(slot)+":\nManufacturer: "+str(i['manufacturer'])+"\nCapacity (GB): "+str(i['capacity (GB)'])+"\nSpeed (Mhz): "+str(i['speed (Mhz)'])+"\n"
    slot += 1

ramText = QTextEdit()
ramText.setReadOnly(True)
ramText.setStyleSheet(specSS)
ramText.setText(ramstr)
ramText.setFont(font)


diskstr = ""
disks = 1
for i in diskDetails():
    diskstr += "Disk "+str(disks)+":\n\nName: "+str(i['FriendlyName'])+"\n\nType: " + str(i['MediaType'])+" "+str(i['BusType'])+"\n\nCapacity: "+str(i['SizeGB'])+" GB\n"
    disks += 1

diskText = QTextEdit()
diskText.setReadOnly(True)
diskText.setStyleSheet(specSS)
diskText.setText(diskstr)
diskText.setFont(font)

batstr = ""
if hasBattery:


    b = BatteryHealth()
    dsgncapInt = ""
    for i in str(b['DESIGN CAPACITY']):
        if i.isdigit():
            dsgncapInt += str(i)

    fcCapInt = ""
    for i in str(b['FULL CHARGE CAPACITY']):
        if i.isdigit():
           fcCapInt+= str(i)
    print(fcCapInt)

    dsgnCapInt = int(dsgncapInt)
    fcCapInt = int(fcCapInt)
    batstr += "Battery:\n\nManufacturer: "+b['MANUFACTURER']+"\n\nSerial No.: "+b['SERIAL NUMBER']+"\n\nDesign Capacity: "+b['DESIGN CAPACITY']+"\n\nFull Charge Capacity: "+b['FULL CHARGE CAPACITY']+"\n\nHealth: "+str(round((fcCapInt/dsgnCapInt)*100,2))+" %\n\nCycle Count: "+str(b['CYCLE COUNT'])

    batteryText = QTextEdit()
    batteryText.setReadOnly(True)
    batteryText.setStyleSheet(specSS)
    batteryText.setText(batstr)
    batteryText.setFont(font)



manText = QTextEdit()
manText.setReadOnly(True)
manText.setStyleSheet(specSS)
manText.setText(str(pc()))

manText.setFont(font)


gpuText = QTextEdit()
gpuText.setReadOnly(True)
gpuText.setStyleSheet(specSS)
gpuText.setText(str(gpu()))
gpuText.setFont(font)


def createShadowedLabel(text):
    container = QFrame()
    container.setStyleSheet("background: transparent;")

    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(25)
    shadow.setOffset(0, 5)
    shadow.setColor(QColor(0, 0, 0, 160))
    container.setGraphicsEffect(shadow)

    label = QLabel()
    label.setText(text)
    label.setFont(font)
    label.setStyleSheet("""
        background-color: #2b2b30;
        color: #ffffff;
        border-radius: 12px;
        padding: 10px;
    """)

    label.setWordWrap(True)

    layout_container = QVBoxLayout(container)
    layout_container.setContentsMargins(0, 0, 0, 0)
    layout_container.addWidget(label)
    container.setMinimumSize(150, 400)
    container.setMaximumSize(600, 800)


    return container, label


cpuContainer, cpuLabel = createShadowedLabel(cpustr)
layout.addWidget(cpuContainer, 0, 0)

ramContainer, ramLabel = createShadowedLabel(ramstr)
layout.addWidget(ramContainer, 0, 1)

diskContainer, diskLabel = createShadowedLabel(diskstr)
layout.addWidget(diskContainer, 0, 3)

manContainer, manLabel = createShadowedLabel(str(pc()))
layout.addWidget(manContainer, 0, 2)

gpuContainer, gpuLabel = createShadowedLabel(str(gpu()))
layout.addWidget(gpuContainer, 0, 4)

if hasBattery:
    batteryContainer, batteryLabel = createShadowedLabel(batstr)
    layout.addWidget(batteryContainer, 0, 5)


btnPcInfo.setStyleSheet("""
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
""")

output.setStyleSheet("border: 1px solid green; border-radius: 5px; padding: 5px;")

layout.addWidget(btnPcInfo,1,0)
layout.addWidget(output,1,1)

window.setLayout(layout)
window.show()





def runtest():
    output.setText(send_pcinfo(pcinfo))


btnPcInfo.clicked.connect(runtest)


app.exec()
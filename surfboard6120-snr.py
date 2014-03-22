#!/usr/bin/env python

# used values found at http://www.dslreports.com/faq/5862 as a guide for warning and critical levels

import urllib
import re
import sys

def print_config(channel_output):
    config_text = """multigraph snr_pwr_sb
graph_title SB6141 Signal to Noise (dB) & Power (dBmV)
graph_vlabel dB / dBmV
graph_category network
%s""" % channel_output
    config_text += "\nmultigraph uptime_sb\n"
    config_text += "graph_title SB6141 System Up Time (Days)\n"
    config_text += "graph_vlabel days\n"
    config_text += "graph_category network\n"
    print config_text

snr_output = "multigraph snr_pwr_sb\n"
channel_output = ""
pdOutput = ""
cmOutput = urllib.urlopen("http://192.168.100.1/cmSignalData.htm").read()

# Pull apart and put back together the ugly HTML output from the SB6120
cmOutput = re.sub('\n','', cmOutput)
cmOutput = re.sub('&nbsp;', '', cmOutput)
cmOutput = re.sub(r'<.*?>', '', cmOutput)
cmOutput = " ".join(cmOutput.split())

dOutput = re.search(r"(Downstream.*)(Upstream Bonding Channel.*)", cmOutput).group(1)
pdOutput = re.search(r"(this Page for a new reading )(.*)(Upstream Bonding Channel ValueChannel)", cmOutput).group(2)
uOutput = re.search(r"(Downstream.*)(Upstream Bonding Channel.*)", cmOutput).group(2)

downstreamSnrOutput = re.search(r"Signal to Noise Ratio(.*dB).*Downstream", dOutput).group(1)
upstreamSnrOutput = re.search(r"Power Level.*Upstream Modulation", uOutput).group(0)

counter = 0
# Iterate over DOWNSTREAM SNR Values
for current in re.finditer(r"\d+", downstreamSnrOutput):
    snr_output = snr_output + "downstreamsnr%d.value %s\n" % (counter, current.group(0))
    counter = counter + 1

# Iterate over DOWNSTREAM Power Values
counter = 0
for current in re.finditer(r"\d+", pdOutput):
    snr_output = snr_output + "downstreampwr%d.value %s\n" % (counter, current.group(0))
    counter = counter + 1

counter = 0
# Iterate over UPSTREAM SNR Values
for current in re.finditer(r"\d+", upstreamSnrOutput):
    snr_output = snr_output + "upstreampwr%d.value %s\n" % (counter, current.group(0))
    counter = counter + 1

# Iterate over Downstream Channels SNR
smChannels = re.search(r"Channel ID([0-9\s]+)", dOutput).group(1)
counter = 0
for current in re.finditer(r"\d+\s", smChannels):
    channel_output = channel_output + "downstreamsnr%d.label Downstream SNR (CHL %s)\n" % (counter, current.group(0))
    channel_output = channel_output + "downstreamsnr%d.warning 33:\n" % (counter)
    channel_output = channel_output + "downstreamsnr%d.critical 30:\n" % (counter)
    counter = counter + 1

# Iterate over Downstream Channels Power
smChannels = re.search(r"Channel ID([0-9\s]+)", dOutput).group(1)
counter = 0
for current in re.finditer(r"\d+\s", smChannels):
    channel_output = channel_output + "downstreampwr%d.label Downstream Power (CHL %s)\n" % (counter, current.group(0))
    channel_output = channel_output + "downstreampwr%d.warning -12:12\n" % (counter)
    channel_output = channel_output + "downstreampwr%d.critical -15:15\n" % (counter)
    counter = counter + 1

# Iterate over Upstream Channels
smChannels = re.search(r"Channel ID([0-9\s]+)", uOutput).group(1)
counter = 0
for current in re.finditer(r"\d+\s", smChannels):
    channel_output = channel_output + "upstreampwr%d.label Upstream Power (CHL %s)\n" % (counter, current.group(0))
    channel_output = channel_output + "upstreampwr%d.warning 35:52\n" % (counter)
    channel_output = channel_output + "upstreampwr%d.critical 8:55\n" % (counter)
    counter = counter + 1

if len(sys.argv) > 1:
    if sys.argv[1] == "config":
        print_config(channel_output)
        sys.exit(0)

cmOutput = urllib.urlopen("http://192.168.100.1/indexData.htm").read()
dOutput = re.search(r"(\d+)\s+days\s+(\d+)h:(\d+)m:(\d+)s", cmOutput)
days = (((float(dOutput.group(2))*3600) + (float(dOutput.group(3))*60) + float(dOutput.group(4))) / 86400) + float(dOutput.group(1))
snr_output += "\nmultigraph uptime_sb\n"
snr_output += "uptime.value %.2f\n" % (days)

print snr_output
sys.exit(0)

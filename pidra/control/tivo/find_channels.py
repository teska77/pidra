import argparse, time, json, requests
from pidra.control.tivo import TiVoRemote

# Get channel names from this lovely JSON mapping
r = requests.get("http://www.bigsoft.co.uk/media/blogs/home/quick-uploads/p599/virgin_channel_guide.json")
raw_mappings = json.loads(r.text)
mappings = dict()
for channel in raw_mappings['channels']:
    mappings[channel['num']] = channel['name']


def wait(time_span):
    for i in range(time_span, 0, -1):
        print("Waiting for {} seconds...".format(str(i).zfill(2)), end='\r')
        time.sleep(1)

channels_available = []

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("-p", "--port", default=31339)
parser.add_argument("-o", "--output", required=False)
parser.add_argument("-l", "--limit", default=300)

args = parser.parse_args()

tivo = TiVoRemote(args.host, args.port)

print("Checking power status...", end='')
if tivo.power:
    print("OK")
else:
    print("FAIL")
    print("Powering on...")
    tivo.power_on()
    wait(30)

# tivo.set_channel(100)
wait(5)
tivo.go_tv()
for i in range(0, args.limit):
    current_channel = tivo.channel
    while current_channel == None:
        # Sometimes, the int cast will not work on the string, so we wait until we get a proper result.
        current_channel = tivo.channel
        time.sleep(1)
    channels_available.append(current_channel)
    if not current_channel in mappings:
        mappings[current_channel] = "UNKNOWN"
    print("Added {} ({}) to available channels. ({} to go)".format(current_channel, mappings[current_channel], args.limit - i))
    wait(5)

    if args.output:
        writer = open(args.output, 'a')
        writer.write("{},{}\n".format(current_channel, mappings[current_channel]))
        writer.close()

    tivo.channel_up()

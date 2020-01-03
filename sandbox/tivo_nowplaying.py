import requests, json, argparse, time, datetime

HOST = "web-api-pepper.horizon.tv"
PATH = "oesp/api/GB/eng/web"

parser = argparse.ArgumentParser(description="Fetches now playing information for a given channel.")
parser.add_argument("channel", help="Channel number (e.g. 101)")
args = parser.parse_args()

r = requests.get("https://{host}/{path}/channels".format(host=HOST, path=PATH))
raw_channel_dict = json.loads(r.text)['channels']
channel_dict = {}

def get_guide_for_channel(channel):
    start_time = int(time.time() - 3600) * 1000
    end_time = int(time.time() + 3600) * 1000
    r = requests.get("https://{host}/{path}/listings?byStationId={id}&byStartTime={start_time}~{end_time}&sort=startTime".format(
        host=HOST, path=PATH, id=channel['id'], start_time=start_time, end_time=end_time
    ))

    raw_epg = json.loads(r.text)['listings']
    channel['guide'] = []
    for listing in raw_epg:
        program = listing['program']
        prog_id = program['id']
        # No try/catch for this, as if we don't have a title, there's no point.
        title = program['title']
        # Description
        try:
            description = program['longDescription']
        except KeyError:
            # longDescription does not exist
            description = "N/A"
        # Summary
        try:
            summary = program['description']
        except KeyError:
            summary = description # Re-use the long description, or also set to N/A
        # Image
        try:
            image = program['images'][0]['url']
        except Exception:
            image = "https://raw.githubusercontent.com/xbmc/xbmc/master/addons/skin.estuary/media/DefaultVideoCover.png"
        
        start = datetime.datetime.utcfromtimestamp(listing['startTime'] / 1000)
        end = datetime.datetime.utcfromtimestamp(listing['endTime'] / 1000)
        prog_info = {
            "id": prog_id,
            "title": title,
            "summary": summary,
            "description": description,
            "image": image,
            "start": start,
            "end": end
        }
        channel['guide'].append(prog_info)
        print(json.dumps(channel, indent=4, default=str))


for channel in raw_channel_dict:
    channel_dict[str(channel['channelNumber'])] = {
        "id": channel['stationSchedules'][0]['station']['id'],
        "name": channel['title'],
        "logo": channel['stationSchedules'][0]['station']['images'][2]['url'],
        "thumbnail": channel['stationSchedules'][0]['station']['images'][0]['url']
    }

# Fetch EPG data for said channel

for channel in channel_dict:
    get_guide_for_channel(channel_dict.get(channel))

pass
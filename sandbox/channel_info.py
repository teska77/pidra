import json, requests
r = requests.get("https://web-api-pepper.horizon.tv/oesp/v3/GB/eng/web/channels?byLocationId=65535&includeInvisible=true&personalised=false&sort=channelNumber")
raw_json = r.text
raw_dict = json.loads(raw_json)['channels']
channel_dict = dict()
for channel in raw_dict:
    info = {
        'name' : channel['title'],
        'image' : channel['stationSchedules'][0]['station']['images'][2]['url'].split('?')[0],
        'hd' : channel['stationSchedules'][0]['station']['isHd']
    }
    channel_dict[str(channel['channelNumber'])] = info

print(json.dumps(channel_dict, indent=4))

existing_listing_file = open('channels.csv')
new_listing_file = open('channels_with_logos.csv', 'w')
split = existing_listing_file.read().split('\n')
for entry in split:
    channel_split = entry.split(',')
    if channel_split[0] == "Channel":
        new_listing_file.write("Channel,Name,Logo\n")
    elif channel_dict.get(channel_split[0]):
        print(channel_dict[channel_split[0]])
        new_listing_file.write(entry + "," + channel_dict[channel_split[0]]['image'] + '\n')
    else:
        new_listing_file.write(entry + '\n')
new_listing_file.close()
existing_listing_file.close()
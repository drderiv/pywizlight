import asyncio
import time
import cgi
from http.server import BaseHTTPRequestHandler, HTTPServer
from pywizlight import wizlight, PilotBuilder, discovery

hostName = "localhost"
serverPort = 8080

class wizServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        except:
            self.send_response(404, 'File Not Found')
            self.end_headers()
            self.wfile.write(bytes("File not found", 'utf-8'))

    def do_POST(self):
        if self.path == '/submit':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            response_content = "<html><body><h1>Form Data:</h1>"
            for field in form.keys():
                response_content += f"<p>{field}: {form.getvalue(field)}</p>"
            response_content += "</body></html>"
            self.wfile.write(bytes(response_content, "utf-8"))
        else:
             self.send_response(404, 'Not Found')
             self.end_headers()
             self.wfile.write(b'Not found')

async def main():
    """Sample code to work with bulbs."""
    # Discover all bulbs in the network via broadcast datagram (UDP)
    # function takes the discovery object and returns a list of wizlight objects.
    bulbs = await discovery.discover_lights(broadcast_space="10.66.5.255")
    # Print the IP address of the bulb on index 0
    print(f"Bulb IP address: {bulbs[0].ip}")

    # Iterate over all returned bulbs
    for bulb in bulbs:
        print(bulb.__dict__)
        # Turn off all available bulbs
        # await bulb.turn_off()

'''
    # Set up a standard light
    light = wizlight(bulbs[0].ip)
    # Set up the light with a custom port
    #light = wizlight("your bulb's IP address", port=12345)

    # The following calls need to be done inside an asyncio coroutine
    # to run them from normal synchronous code, you can wrap them with
    # asyncio.run(..).

    # Turn the light on into "rhythm mode"
    await light.turn_on(PilotBuilder())
    # Set bulb brightness
    await light.turn_on(PilotBuilder(brightness = 255))

    # Set bulb brightness (with async timeout)
    timeout = 10
    await asyncio.wait_for(light.turn_on(PilotBuilder(brightness = 255)), timeout)

    # Set bulb to warm white
    await light.turn_on(PilotBuilder(warm_white = 255))

    # Set RGB values
    # red to 0 = 0%, green to 128 = 50%, blue to 255 = 100%
    await light.turn_on(PilotBuilder(rgb = (0, 128, 255)))

    # Get the current color temperature, RGB values
    state = await light.updateState()
    print(state.get_colortemp())
    red, green, blue = state.get_rgb()
    print(f"red {red}, green {green}, blue {blue}")

    # Start a scene
    await light.turn_on(PilotBuilder(scene = 4)) # party

    # Get the name of the current scene
    state = await light.updateState()
    print(state.get_scene())
'''

    # Get the features of the bulb
    bulb_type = await bulbs[0].get_bulbtype()
    print("IP:", bulbs[0].ip)
    print("Bightness:", bulb_type.features.brightness) # returns True if brightness is supported
    print("Colored:", bulb_type.features.color) # returns True if color is supported
    print("Temperatured:", bulb_type.features.color_tmp) # returns True if color temperatures are supported
    print("Effected:", bulb_type.features.effect) # returns True if effects are supported
    print("Max K:", bulb_type.kelvin_range.max) # returns max kelvin in INT
    print("Min K:", bulb_type.kelvin_range.min) # returns min kelvin in INT
    print("Mod Name:", bulb_type.name) # returns the module name of the bulb

    # Turn the light off
    await light.turn_off()

    # Do operations on multiple lights in parallel
    #bulb1 = wizlight("<your bulb1 ip>")
    #bulb2 = wizlight("<your bulb2 ip>")
    # --- DEPRECATED in 3.10 see [#140](https://github.com/sbidy/pywizlight/issues/140)
    # await asyncio.gather(bulb1.turn_on(PilotBuilder(brightness = 255)),
    #    bulb2.turn_on(PilotBuilder(warm_white = 255)))
    # --- For >3.10 await asyncio.gather() from another coroutine
    # async def turn_bulbs_on(bulb1, bulb2):
    #    await asyncio.gather(bulb1.turn_on(PilotBuilder(warm_white=255)), bulb2.turn_on(PilotBuilder(warm_white=255)))
    #  def main:
    #    asyncio.run(async turn_bulbs_on(bulb1, bulb2))

    webServer = HTTPServer((hostName, serverPort), wizServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

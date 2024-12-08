#!/usr/bin/env python3
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

Gst.init(None)

class RTSPServer:
    def __init__(self):
        self.server = GstRtspServer.RTSPServer()
        self.factory = GstRtspServer.RTSPMediaFactory()

        self.factory.set_launch((
            "nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=30/1 "
            "! omxh264enc ! rtph264pay name=pay0 pt=96"
        ))

        self.factory.set_shared(True)
        self.server.get_mount_points().add_factory("/test", self.factory)
        self.server.attach(None)

if __name__ == "__main__":
    server = RTSPServer()
    loop = GObject.MainLoop()
    loop.run()

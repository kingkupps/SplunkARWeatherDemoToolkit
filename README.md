# Splunk AR Weather Sensor Toolkit

This repo contains a Raspberry Pi image and a Splunk dashboard to make experimenting with Splunk AR painless. With this
toolkit, you can transform a Raspberry Pi into an AR asset, much like you would another machine in production, and view
AR dashboards for live weather events being emitted from the Raspberry Pi's Sense Hat add-on.

The rest of this documentation covers how to configure and use this toolkit including:

- Required hardware setup
- Using the pre-made Sense Hat dashboards in this repository
- Using the toolkit's web frontend
- Setting up a Splunk AR asset and workspace

## Prerequisites

This toolkit requires that you have the following hardware/equipment

- An iOS device
- An ethernet cable and an ethernet port with internet access
- A Splunk Enterprise instance
- [A Raspberry Pi 3 B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/)
- A Raspberry Pi [Sense Hat Add-On](https://www.raspberrypi.org/products/sense-hat/)
- An SD Card with at least 32 GB of available storage

You can get the last three items from this [Amazon bundle](https://www.amazon.com/gp/product/B07CHVB12D/ref=ox_sc_act_title_1?smid=A6EGA15UEFYEQ&psc=1)
or independently from your seller of choice.

## Installation

### 1. Set up your Splunk dashboard for weather events

The Raspberry Pi will upload weather events into Splunk through the [HTTP Event Collector (HEC)](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector).
By default, events are sent to an index called `ar-weather-demo` but you can use whichever index you
like provided the HEC token you provide has permission to upload to that index. Follow the directions
[here](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector) for enabling HEC on your
Splunk instance.

Next, create a new dashboard for monitoring weather events from the Sense Hat. We've provided one for you in
`weatherdemo-dashboard.xml`. To use this dashboard

1. Go to the "Search and Reporting App"
2. Click the "Dashboards" tab
3. Click the "Create New Dashboard" button
4. Fill in whatever title and description you want
5. Next to "Edit Dashboard" in the top left, click on the "Source" option
6. Copy and paste `weatherdemo-dashboard.xml` into the editor
7. Click "Save" in the top right corner

The dashboard will not have data until you start emitting events from your Raspberry Pi and Sense Hat through the web
UI which is covered in the Usage section below.

### 2. Configure your Raspberry Pi and Sense Hat

First, flash an SD card with the image provided in this repo called `weatherdemo.dmg`. This image makes your Raspberry
Pi a Wifi hot spot and starts a web server that you will use later to start and stop Sense Hat readings from flowing
into Splunk as events. We recommend using [balenaEtcher](https://www.balena.io/etcher/) for flashing your SD card. Once
you have downloaded balenaEtcher,

1. Download `weatherdemo.dmg`
2. Insert your SD card into your computer
3. Open balenaEtcher
4. Select `weatherdemo.dmg` as the image and your SD card as the drive
5. Click Flash

Once your SD card has been flashed with the image, assemble your Raspberry Pi and Sense Hat.

1. Connect your ethernet cable to an ethernet port with internet access
2. Connect your ethernet cable to your Raspberry Pi
3. Insert your SD card into the Raspberry Pi
4. Attach your Sense Hat add-on to the Raspberry Pi making sure that all of your Raspberry Pi's GPIO pins are fully
connected to all of the GPIO pin holes in your Sense Hat
5. Turn on the Raspberry Pi by plugging it into its power source

You should see the Sense Hat's LEDs light up when you plug in the Raspberry Pi to power if set up is done correctly. The
LEDs should turn off several seconds after the Raspberry Pi boots up.

### 3. Set up Splunk AR for use with your Raspberry Pi

Configure your iOS device, Splunk Enterprise instance, and Raspberry Pi for use with Splunk AR. See the following
documentation on:

- [Setting up Splunk AR](https://docs.splunk.com/Documentation/AR/1.5.0/UseSplunkAR/GetStartedWithAR#Set_up_Splunk_AR).
- [Setting up your Raspberry Pi as an Asset](https://docs.splunk.com/Documentation/AR/1.5.0/UseSplunkAR/GetStartedWithAR#Set_up_and_use_asset_tags).

Make sure to add the dashboard created from step 1 to the asset you create.

### 4. Use the web UI to start emitting weather data and view your dashboard in AR

Once your Raspberry Pi is on, you should see a wifi network called "SplunkARWeatherDemo". From another computer, connect
to this network and navigate to TODO in a web browser to view the web UI. From here you can start and stop weather
events generated from your Raspberry Pi from being sent to the Splunk instance of your choice.

Fill out the Splunk instance form on the right and click "Start Polling". The most recent uploaded event will be
displayed on the left.

To view see this data through AR dashboards, with the Splunk AR app, scan your Raspberry Pi asset tag. You should see
dashboards populated with the data emitted from the Raspberry Pi and Sense Hat! From here you should be able to drag
and move around the dashboards on your device. 

## Limitations

The web UI used to start emitting events from the Sense Hat should only be used by one demo or user at a time. If this
becomes an issue, please file an issue using the link below.

## Feedback

If you run into any issues at all using this toolkit, please [file issues](https://github.com/kingkupps/SplunkARWeatherDemoToolkit/issues/new?assignees=&labels=&template=bug_report.md&title=)
to this repository with a step by step method for reproducing your issue.

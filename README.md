# Splunk AR Weather Sensor Toolkit

This repository contains a Raspberry Pi image, a Splunk dashboard, and documentation to help you get started with Splunk AR. With this
toolkit, you can register a Raspberry Pi as an asset, much like you would another machine in production. Then use Splunk AR to view
augmented reality dashboards for live weather events from the Raspberry Pi's Sense Hat add-on.

In this documentation, you can find the following resources:

- Hardware setup requirements
- How to use the Sense Hat dashboards in this repository
- How to use the toolkit's web frontend UI
- How to register Splunk AR asset and create an AR workspace.

## Requirements

To use Splunk AR with this toolkit, you need the following hardware:

- An iOS device
- An ethernet cable
- An ethernet port with internet access
- A Splunk Enterprise or Splunk Cloud instance
- [A Raspberry Pi 3 B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/)
- A Raspberry Pi [Sense Hat add-on](https://www.raspberrypi.org/products/sense-hat/)
- An SD card with at least 32GB of available storage

## 1. Set up an HTTP Event Collector

Set up an HTTP Event Collector so that the Raspberry Pi uploads weather events into Splunk. By default, events are sent to an index called `ar-weather-demo`. However, you can use any index you want given that the HEC token you provide has permission to upload to that index. 

To learn how to set up an HEC, see [Set up and use the HTTP Event Collector in Splunk Web](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector).

## 2. Set up a Splunk dashboard for weather events

Next, create a dashboard for monitoring weather events from the Sense Hat add-on. Use the dashboard `weatherdemo-dashboard.xml` provided in this toolkit:

1. Navigate to the Search & Reporting app.
2. Click the "Dashboards" tab.
3. Click "Create New Dashboard".
4. Enter a title and description.
5. Next to "Edit Dashboard", click the "Source".
6. Copy and paste the `weatherdemo-dashboard.xml` contents into the editor.
7. Click "Save".

## 2. Configure your Raspberry Pi and Sense Hat add-on

Flash the SD card with the `weatherdemo.dmg` image. This image makes your Raspberry Pi a Wifi hot spot, which leads to a webpage that you can use to start and stop Sense Hat readings flowing into Splunk as events.

You can use [balenaEtcher](https://www.balena.io/etcher/) to flash your SD card:

1. Download `weatherdemo.dmg`.
2. Insert your SD card into your computer.
3. Use balenaEtcher, or another tool for flashing images into SD cards, to flash your SD card.

## 3.Assemble your Raspberry Pi and Sense Hat add-on

Connect your Raspberry Pi to internet, and assemble your Raspberry Pi with your SD card and Sense Hat add-on.

1. Connect your ethernet cable to an ethernet port with internet access.
2. Connect your ethernet cable to your Raspberry Pi.
3. Insert your SD card into your Raspberry Pi.
4. Attach your Sense Hat add-on to your Raspberry Pi. Make sure that all of your Raspberry Pi's GPIO pins are fully
connected to all of the GPIO pin holes on your Sense Hat.
5. Connect Raspberry Pi to a power source.

After assembling the Raspberry Pi and Sense Hat, the Sense Hat's LEDs light up and turn off after the Raspberry Pi turns on.

### 4. Set up Splunk AR for use with your Raspberry Pi

Download Splunk AR, register your iOS device, and register your Raspberry Pi as an asset to create an AR workspace.

1. See [Set up Splunk AR](https://docs.splunk.com/Documentation/AR/latest/UseSplunkAR/GetStartedWithAR#Set_up_Splunk_AR) to get started with Splunk AR.
2. See [Set up and use asset tags](https://docs.splunk.com/Documentation/AR/latest/UseSplunkAR/GetStartedWithAR#Set_up_and_use_asset_tags) to register your Raspberry Pi as an asset and create an AR workspace. Use the dashboard for weather events that you created earlier to create an AR workspace.

### 5. Get weather data into your Splunk instance

Use the webpage to start getting weather data into your Splunk instance.

1. Once your Raspberry Pi is on, connect to the WiFi network "SplunkARWeatherDemo" on your computer.
2. Navigate to TODO in a web browser.
3. Use the web page to start and stop weather events flowing from your Raspberry Pi to your Splunk instance.
4. Fill out the Splunk instance form on the right.
5. Click "Start Polling" to start getting data into Splunk.

Only one user can use the webpage to emit events from the Sense Hat add-on at a time. If this is an issue, file an issue [here](https://github.com/kingkupps/SplunkARWeatherDemoToolkit/issues/new?assignees=&labels=&template=bug_report.md&title=).

### 6. Use Splunk AR to view the weather data in augmented reality

Scan the asset tag, view AR weather data, and adjust visualizations in augmented reality with Splunk AR.

1. Scan your Raspberry Pi asset tag to view the weather data in augmented reality. See [View Splunk dashboards and AR workspaces](https://docs.splunk.com/Documentation/AR/latest/UseSplunkAR/ViewSplunkDashboards) for more information about how to scan asset tags.
2. Adjust the AR workspace so that you can easily view the data. See [Adjust AR workspaces and visualizations using Splunk AR](https://docs.splunk.com/Documentation/AR/1.5.0/UseSplunkAR/AdjustARWorkspaces) to learn how to adjust the AR workspace.

## Feedback

If you run into any issues with this toolkit, file issues to this [repository](https://github.com/kingkupps/SplunkARWeatherDemoToolkit/issues/new?assignees=&labels=&template=bug_report.md&title=) and include a step-by-step method for reproducing your issue.

## Acknowledgements

The favicon logo for the webpage was made by [Freepik](https://www.flaticon.com/authors/freepik) from
[Flaticon](https://www.flaticon.com/).

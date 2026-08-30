"""Generate Aria Home product manuals as PDFs for the RAG corpus.

Every product gets its own manual with the same section order, but the *facts*
are deliberately product-specific (reset hold times, battery figures, error
codes, LED patterns), so a retrieval test can tell whether the right manual —
not a look-alike — came back.

Run:  uv run --with reportlab python make_manuals.py out/
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

# ─────────────────────────────────────────────────────────────── catalogue
# sku: (name, category, price, specs{}, box[], setup[], leds{}, troubleshooting[(symptom, fix)],
#       errors{code: meaning/fix}, power, warranty_months, compat[])

PRODUCTS: dict[str, dict] = {
    "ARIA-THERM": dict(
        name="Aria Thermostat",
        category="thermostat",
        price=129,
        specs={
            "Display": "2.4-inch colour LCD, auto-dim",
            "Sensors": "temperature, humidity, proximity",
            "HVAC support": "1H/1C conventional, heat pump with O/B",
            "Wiring": "R, C, W, Y, G, O/B (C-wire required)",
            "Temperature range": "50–90 °F setpoint, accuracy ±0.5 °F",
            "Wi-Fi": "2.4 GHz 802.11 b/g/n only",
        },
        box=["Thermostat", "wall plate", "4 screws + anchors", "wire labels", "quick start card"],
        setup=[
            "Switch off HVAC power at the breaker before removing your old thermostat.",
            "Label each wire with the supplied stickers, then remove the old base.",
            "Mount the Aria wall plate and insert wires until the tab clicks.",
            "Attach the thermostat; it powers from the C-wire and shows the Aria logo.",
            "In the Aria app tap Add device, choose Thermostat, and scan the QR code on the back.",
            "Join a 2.4 GHz Wi-Fi network; 5 GHz networks are not supported.",
        ],
        leds={
            "Solid green ring": "connected and idle",
            "Pulsing orange ring": "heating",
            "Pulsing blue ring": "cooling",
            "Blinking red ring": "no C-wire power — check the C terminal",
            "Blinking white ring": "pairing mode",
        },
        troubleshooting=[
            ("Screen is blank", "No power on the C-wire. Check the breaker, then confirm the C terminal has a wire seated with the tab down."),
            ("Reads 3–4 degrees warmer than the room", "Proximity wake keeps the backlight on; set Display > Auto-dim to On and keep the unit out of direct sun."),
            ("Shows Offline in the app", "Hold the dial for 5 seconds until the ring blinks white to re-enter pairing, then rejoin a 2.4 GHz network."),
            ("Cooling runs but house never reaches setpoint", "Enable Compressor Protection off only if your installer confirms; otherwise check the filter and the O/B setting."),
            ("Schedule does not run", "Eco mode overrides schedules; turn Eco off from the home screen."),
        ],
        errors={
            "E1": "Temperature sensor fault — restart by holding the dial 10 seconds; replace if it persists.",
            "E4": "No C-wire detected — the thermostat will not power the display without a common wire.",
            "E7": "Heat pump reversing valve (O/B) mismatch — swap the O/B setting in Settings > Equipment.",
            "E12": "Firmware update interrupted — leave powered for 15 minutes; it recovers automatically.",
        },
        power="24 V AC from the C-wire; no batteries. Draws under 1 W.",
        reset="Hold the dial for 10 seconds until the ring turns red, then release. Wi-Fi and schedules are erased.",
        warranty=24,
        compat=["Aria app iOS 15+/Android 10+", "Google Home", "Amazon Alexa", "Apple Home via Aria Hub"],
    ),
    "ARIA-THERM-V2": dict(
        name="Smart Thermostat V2",
        category="thermostat",
        price=159,
        specs={
            "Display": "3.0-inch OLED, 320×320",
            "Sensors": "temperature, humidity, occupancy radar, ambient light",
            "HVAC support": "2H/2C conventional, dual-fuel, heat pump with aux",
            "Wiring": "R, C, W1, W2, Y1, Y2, G, O/B, AUX — works without a C-wire using the included Power Bridge",
            "Temperature range": "45–95 °F setpoint, accuracy ±0.3 °F",
            "Wi-Fi": "2.4 GHz and 5 GHz",
        },
        box=["Thermostat", "trim plate", "Power Bridge", "screws", "wire labels"],
        setup=[
            "If you have no C-wire, install the Power Bridge at the furnace control board first.",
            "Mount the base, seat each wire, then click the display on.",
            "The V2 supports 5 GHz Wi-Fi; either band works.",
            "Scan the QR code in the Aria app and follow the equipment wizard.",
        ],
        leds={
            "Soft white glow": "occupied, idle",
            "Amber sweep": "heating",
            "Blue sweep": "cooling",
            "Purple": "auxiliary heat running",
            "Red outline": "wiring fault — see the app for the terminal",
        },
        troubleshooting=[
            ("Furnace short-cycles after install", "The Power Bridge is on the wrong terminals; it goes on W and Y at the control board, never at the thermostat."),
            ("Occupancy shows Away while someone is home", "The radar needs clear line of sight; move furniture more than 3 feet away or lower Sensitivity."),
            ("Aux heat runs too often", "Raise the Aux lockout temperature in Settings > Equipment > Heat pump balance."),
        ],
        errors={
            "V2-01": "Power Bridge not detected — check the bridge LED is green at the furnace.",
            "V2-05": "Y2 called with single-stage compressor — set Stages to 1 in the equipment wizard.",
            "V2-09": "Radar sensor blocked — clean the front panel.",
        },
        power="24 V AC with or without a C-wire (Power Bridge). Internal backup cell keeps time for 48 hours.",
        reset="Press and hold the display for 15 seconds until it shows Restoring, then release.",
        warranty=24,
        compat=["Aria app", "Google Home", "Amazon Alexa", "Apple Home", "Matter over Wi-Fi"],
    ),
    "ARIA-DBELL": dict(
        name="Aria Doorbell Cam",
        category="camera",
        price=179,
        specs={
            "Video": "1536×1536 head-to-toe view, HDR, 30 fps",
            "Field of view": "150° horizontal, 150° vertical",
            "Night vision": "colour night vision with ambient light; infrared below 1 lux",
            "Audio": "two-way talk with noise cancellation",
            "Storage": "cloud via Aria Video plan; 3 hours of event history without a plan",
            "Operating temperature": "-5 °F to 120 °F",
        },
        box=["Doorbell", "mounting bracket", "15° wedge", "USB-C cable", "screws", "diode for chime kits"],
        setup=[
            "Charge the internal battery with the USB-C cable until the light is solid green (about 5 hours).",
            "Mount the bracket at 48 inches from the ground; use the wedge if the door is at an angle.",
            "For wired mode, connect the existing doorbell wires to the two terminals; 16–24 V AC is required.",
            "Scan the QR code inside the battery cover in the Aria app.",
        ],
        leds={
            "Solid blue ring": "streaming or two-way talk",
            "Pulsing white": "pairing",
            "Solid green (while charging)": "charged",
            "Flashing red": "battery under 10 percent",
        },
        troubleshooting=[
            ("Battery drains in a few days", "Motion sensitivity is too high or the zone includes a street; reduce Motion zones to the porch only. Expected life is 3 to 6 months per charge in battery mode."),
            ("Existing chime does not ring", "Install the supplied diode on the chime's Front terminal, then enable Mechanical chime in device settings."),
            ("Video is delayed or stutters", "Wi-Fi RSSI below -70 dBm; move the router or add an Aria Hub as an extender."),
            ("Motion alerts but no video recorded", "Event recording needs the Aria Video plan or the 3-hour history; check the plan status in Account."),
        ],
        errors={
            "D-01": "Battery temperature out of range — charging pauses below 32 °F.",
            "D-06": "Chime voltage too low (under 16 V AC) — use battery mode or upgrade the transformer.",
            "D-14": "Storage sync failed — the doorbell keeps recording locally for 3 hours and retries.",
        },
        power="Internal 6,040 mAh battery, 3 to 6 months per charge, or hardwired 16–24 V AC.",
        reset="Hold the setup button under the faceplate for 20 seconds until the ring flashes white three times.",
        warranty=24,
        compat=["Aria app", "Aria Video plan", "Google Home", "Amazon Alexa (Echo Show live view)"],
    ),
    "ARIA-DBELL-PRO": dict(
        name="Aria Doorbell Pro",
        category="camera",
        price=249,
        specs={
            "Video": "2K (2560×1920) with dual-band HDR",
            "Field of view": "180° horizontal",
            "Detection": "radar-based 3D motion with package detection",
            "Audio": "two-way talk, pre-recorded quick replies",
            "Power": "hardwired only, 16–24 V AC, 30 VA transformer",
        },
        box=["Doorbell Pro", "bracket", "wedge kit", "transformer bypass module", "screws"],
        setup=[
            "The Doorbell Pro has no battery; it must be hardwired to 16–24 V AC.",
            "Install the bypass module in your chime box; this replaces the diode used by the standard Doorbell Cam.",
            "Mount at 48 inches and scan the QR code on the rear.",
        ],
        leds={
            "Blue ring": "live",
            "Amber ring": "transformer under 16 V",
            "White breathing": "pairing",
        },
        troubleshooting=[
            ("Reboots when the chime rings", "Transformer is below 30 VA; replace with a 16–24 V, 30 VA transformer."),
            ("Package detection never triggers", "Draw a package zone at least 2 feet square on the ground plane in Motion settings."),
        ],
        errors={
            "P-02": "Bypass module missing — chime will not ring.",
            "P-11": "Radar calibration failed — remove the doorbell and reseat it flat on the bracket.",
        },
        power="Hardwired 16–24 V AC, 30 VA minimum. No battery.",
        reset="Hold the orange button on the back for 15 seconds until the ring turns amber.",
        warranty=24,
        compat=["Aria app", "Aria Video plan", "Google Home", "Amazon Alexa", "Apple Home via Aria Hub"],
    ),
    "ARIA-FLOOD": dict(
        name="Aria Floodlight Cam",
        category="camera",
        price=229,
        specs={
            "Video": "1080p HD, HDR, 140° field of view",
            "Lights": "two adjustable LED panels, 2,000 lumens total, 3000 K",
            "Siren": "105 dB remote-activated",
            "Detection": "passive infrared, 270° motion coverage",
            "Weather rating": "IP65",
            "Power": "hardwired 100–240 V AC to a junction box",
        },
        box=["Floodlight Cam", "mounting plate", "wire nuts", "gasket", "screws"],
        setup=[
            "Turn off the breaker and confirm with a tester before touching wires.",
            "Connect black to black, white to white, and green to the ground screw on the plate.",
            "Tilt each light panel; the camera aims independently.",
            "Pair from the Aria app by holding the setup button on the underside for 3 seconds.",
        ],
        leds={
            "Blue dot": "live view",
            "Red dot": "recording",
            "Both lights flashing": "siren active",
        },
        troubleshooting=[
            ("Lights turn on all night", "Light schedule is set to Dusk to dawn; change to Motion only under Lights."),
            ("Motion missed on the driveway", "PIR is best at 90° to the path; angle the unit so cars cross the field rather than approach head-on. Range is 30 feet."),
            ("Camera works but lights never come on", "Lights are controlled separately; confirm Lights > Motion-activated is On and brightness is above 20 percent."),
        ],
        errors={
            "F-03": "Light driver over-temperature — lights dim until the unit cools.",
            "F-08": "Siren circuit fault — the siren is disabled until restart.",
        },
        power="Hardwired 100–240 V AC. Average draw 12 W with lights off, 27 W with lights on.",
        reset="Hold the underside setup button for 30 seconds until the light panels blink twice.",
        warranty=24,
        compat=["Aria app", "Aria Video plan", "Google Home", "Amazon Alexa"],
    ),
    "ARIA-CAM-IN": dict(
        name="Indoor Camera",
        category="camera",
        price=59,
        specs={
            "Video": "1080p, 130° field of view",
            "Privacy": "physical lens shutter, closes when Home mode is set",
            "Audio": "two-way talk",
            "Power": "USB-C, 5 V 1 A adapter included (6 ft cable)",
            "Mount": "magnetic base, wall or shelf",
        },
        box=["Indoor Camera", "magnetic base", "USB-C cable", "power adapter"],
        setup=[
            "Plug in the camera; the shutter opens and the light pulses white.",
            "In the Aria app, tap Add device, Indoor Camera, and scan the QR code on the base.",
            "Set Home and Away modes so the shutter closes automatically when you are home.",
        ],
        leds={
            "White pulse": "pairing",
            "Solid white": "connected, shutter open",
            "No light with shutter closed": "privacy mode",
        },
        troubleshooting=[
            ("Shutter stays closed", "Privacy mode is on. Tap the camera in the app and turn Privacy off, or change Home mode."),
            ("Image is dark at night", "Indoor Camera uses infrared night vision up to 15 feet; remove reflective glass in front of the lens."),
        ],
        errors={
            "IC-02": "Shutter motor jammed — power cycle; if it persists the unit is replaced under warranty.",
        },
        power="USB-C 5 V 1 A. No battery.",
        reset="Hold the button on the underside for 10 seconds until the light pulses white.",
        warranty=24,
        compat=["Aria app", "Aria Video plan", "Google Home"],
    ),
    "ARIA-LOCK": dict(
        name="Aria Smart Lock",
        category="lock",
        price=199,
        specs={
            "Fits": "most single-cylinder deadbolts; keeps your existing keys",
            "Access": "app, auto-unlock by proximity, schedules for guests",
            "Radio": "Bluetooth LE; Wi-Fi through the Aria Hub or Aria Wi-Fi Bridge",
            "Motor": "auto-lock after 30 seconds to 30 minutes",
            "Battery": "4 × AA alkaline, about 6 months",
        },
        box=["Lock body", "mounting plate", "three tailpiece adapters", "4 AA batteries", "screws"],
        setup=[
            "Remove the interior thumb-turn of your deadbolt; keep the exterior side and keys.",
            "Fit the adapter that matches your tailpiece (D, cross, or square).",
            "Attach the mounting plate, then slide the lock body on until it clicks.",
            "Insert 4 AA batteries; the lock calibrates by turning fully both ways.",
            "Pair in the Aria app over Bluetooth, then add the Wi-Fi Bridge for remote access.",
        ],
        leds={
            "Green flash": "unlocked",
            "Red flash": "locked",
            "Amber double flash": "battery low",
            "Blue breathing": "pairing",
        },
        troubleshooting=[
            ("Lock sticks or grinds in cold weather", "The deadbolt is binding in the strike plate; the motor cannot push through. Loosen the strike plate screws a quarter turn and re-run Calibrate from lock settings. Lubricate the bolt with dry graphite, not oil."),
            ("Auto-unlock does not trigger", "Auto-unlock needs Location Always and Bluetooth on; it arms only after you have been more than 200 meters away."),
            ("Says Jammed in the app", "Door was not fully closed. Close it, then tap Retry."),
            ("Battery lasts only a few weeks", "Auto-lock set to under 1 minute doubles motor cycles; set to 5 minutes or use door-sense."),
        ],
        errors={
            "L-01": "Calibration failed — remove and reseat the lock body, then Calibrate again.",
            "L-04": "Bolt blocked — the door is misaligned; check the strike plate.",
            "L-07": "Battery critical — fewer than 10 operations remain.",
        },
        power="4 × AA alkaline, about 6 months. Lithium AA is not recommended (voltage curve fools the gauge).",
        reset="Remove the batteries, hold the reset button inside the battery bay while reinserting them, keep holding for 10 seconds until the light turns blue.",
        warranty=24,
        compat=["Aria app", "Aria Hub", "Aria Wi-Fi Bridge", "Google Home", "Amazon Alexa", "Apple Home via Hub"],
    ),
    "ARIA-LOCK-PRO": dict(
        name="Door Lock Pro",
        category="lock",
        price=269,
        specs={
            "Fits": "replaces the full deadbolt, exterior keypad and fingerprint reader",
            "Access": "fingerprint (up to 50 prints), 6-digit codes (up to 100), app, key",
            "Radio": "Wi-Fi 2.4 GHz built in — no bridge required",
            "Weather rating": "IP54 keypad",
            "Battery": "rechargeable 5,000 mAh pack, about 4 months",
        },
        box=["Exterior keypad", "interior body", "bolt", "strike plate", "battery pack", "USB-C cable", "keys"],
        setup=[
            "Replace the entire deadbolt: bolt, exterior keypad and interior body.",
            "Charge the pack until the keypad shows 100.",
            "Enrol a master fingerprint first; the app then lets you add codes and guests.",
        ],
        leds={
            "Keypad white": "ready",
            "Keypad red flash three times": "wrong code or unrecognised print",
            "Keypad amber": "battery under 20 percent",
        },
        troubleshooting=[
            ("Fingerprint fails in the rain", "Wipe the sensor and the finger; enrol the same finger twice from different angles."),
            ("Keypad locks out", "After 5 wrong codes the keypad disables for 60 seconds; use the app or a key."),
            ("Wi-Fi drops daily", "Built-in Wi-Fi is 2.4 GHz only; disable band steering on the router."),
        ],
        errors={
            "LP-02": "Fingerprint sensor fault — clean with a dry cloth; replace if persistent.",
            "LP-05": "Keypad tamper detected — the lock records the event and disables the keypad for 5 minutes.",
        },
        power="Rechargeable 5,000 mAh pack, about 4 months; a 9 V battery on the exterior contacts gives emergency power.",
        reset="Hold the interior reset button for 8 seconds until the keypad flashes red, then enter the master code.",
        warranty=24,
        compat=["Aria app", "Google Home", "Amazon Alexa", "Apple Home"],
    ),
    "ARIA-SENSE": dict(
        name="Aria Motion Sensor",
        category="sensor",
        price=39,
        specs={
            "Detection": "passive infrared, 40 feet, 110° horizontal",
            "Pet immunity": "ignores animals under 40 lb when mounted at 7 feet",
            "Radio": "Zigbee 3.0 via the Aria Hub",
            "Battery": "1 × CR123A lithium, about 2 years",
            "Extras": "temperature and light level reporting",
        },
        box=["Motion Sensor", "mounting bracket", "CR123A battery", "adhesive strip"],
        setup=[
            "Pull the battery tab; the light blinks green.",
            "Mount in a corner at 7 feet, angled down, away from heaters and windows.",
            "In the Aria app tap Add device, Motion Sensor, then press the button on the sensor once.",
        ],
        leds={
            "Green blink": "motion detected (first 30 minutes after pairing only)",
            "Red blink every 30 seconds": "battery low",
            "Green triple blink": "pairing",
        },
        troubleshooting=[
            ("Shows Not reporting / no signal in the app", "The battery is flat or the sensor lost the hub. Replace the CR123A (about 2 years of life), then press the button once; if it still does not report, it is more than 60 feet from the Hub — add an Aria Smart Plug as a repeater."),
            ("Triggered by the dog", "Pet immunity only works when mounted at 7 feet pointing down; lower mounting or a cat on furniture will trigger it. Set Sensitivity to Low."),
            ("False alerts near a window", "Sunlight and HVAC vents look like motion to PIR; move it out of direct sun and away from vents."),
        ],
        errors={
            "S-01": "Tamper — the sensor was removed from its bracket.",
            "S-03": "Battery under 10 percent — replace within 7 days.",
        },
        power="1 × CR123A lithium, about 2 years. Alkaline cells are not supported.",
        reset="Hold the button for 5 seconds until the light blinks red, release, then press once to pair.",
        warranty=24,
        compat=["Aria app", "Aria Hub (required)"],
    ),
    "ARIA-SENSE-4PK": dict(
        name="Smart Sensor four pack",
        category="sensor",
        price=99,
        specs={
            "Contents": "four Aria Smart Sensors (door/window contact) with magnets",
            "Detection": "magnetic reed contact, gap up to 0.75 inch",
            "Radio": "Zigbee 3.0 via the Aria Hub",
            "Battery": "1 × CR2032 each, about 18 months",
            "Extras": "vibration sensing for glass break alerts",
        },
        box=["4 Smart Sensors", "4 magnets", "adhesive pads", "4 CR2032 batteries"],
        setup=[
            "Mount the sensor on the frame and the magnet on the door, arrows aligned, within 0.75 inch.",
            "Pull the tab on each sensor and add them one at a time in the app.",
        ],
        leds={
            "Blue blink": "open/close event during setup",
            "Red blink": "battery low",
        },
        troubleshooting=[
            ("Sensor shows Open when the door is closed", "Gap between sensor and magnet exceeds 0.75 inch or the arrows are not aligned."),
            ("Glass break alerts from wind", "Set Vibration sensitivity to Low; sliding doors rattle."),
            ("One sensor of the four will not pair", "Remove and reinsert the CR2032 with the + side up, then add it alone."),
        ],
        errors={
            "SS-02": "Magnet not found during setup — check alignment.",
        },
        power="1 × CR2032 per sensor, about 18 months.",
        reset="Hold the sensor's pinhole button for 5 seconds until the light blinks blue three times.",
        warranty=24,
        compat=["Aria app", "Aria Hub (required)"],
    ),
    "ARIA-HUB": dict(
        name="Aria Hub",
        category="hub",
        price=79,
        specs={
            "Radios": "Zigbee 3.0, Thread border router, Bluetooth LE, Wi-Fi 2.4/5 GHz, Ethernet",
            "Devices": "up to 128 Zigbee/Thread devices",
            "Backup": "internal battery for 4 hours; optional LTE via USB dongle",
            "Local automation": "runs schedules and alarms with no internet",
        },
        box=["Hub", "power adapter", "Ethernet cable"],
        setup=[
            "Connect Ethernet for the most reliable link; Wi-Fi is the fallback.",
            "The ring turns solid white once online; then add sensors and locks through the Hub.",
        ],
        leds={
            "White": "online",
            "Amber": "no internet — local automation still runs",
            "Red": "no power, on battery",
        },
        troubleshooting=[
            ("Sensors drop offline at the far end of the house", "Zigbee range is about 60 feet indoors; add an Aria Smart Plug between the Hub and the sensors as a repeater."),
            ("Hub reboots every few minutes", "USB dongle drawing too much power; use the supplied adapter, not a TV USB port."),
        ],
        errors={
            "H-01": "Zigbee network full — remove unused devices.",
            "H-09": "Thread border router conflict — only one Aria Hub can be primary.",
        },
        power="5 V 3 A USB-C adapter. Internal backup battery runs the Hub for 4 hours.",
        reset="Hold the recessed button for 20 seconds until the ring flashes red; all paired devices are removed.",
        warranty=24,
        compat=["Aria app", "Matter", "Apple Home", "Google Home", "Amazon Alexa"],
    ),
    "ARIA-PLUG": dict(
        name="Aria Smart Plug",
        category="plug",
        price=24,
        specs={
            "Load": "15 A resistive, 1,800 W max",
            "Radio": "Zigbee 3.0 — also acts as a range repeater for sensors",
            "Energy": "reports watts and kWh",
        },
        box=["Smart Plug"],
        setup=["Plug in; the light blinks green; add it in the app under Plug."],
        leds={"Green": "on", "Off": "off", "Green blink": "pairing"},
        troubleshooting=[
            ("Turns off by itself", "Overload protection trips above 15 A; do not run a space heater and another appliance on one plug."),
            ("Energy reading is zero", "Some LED bulbs draw under 1 W and read as zero; this is normal."),
        ],
        errors={"PL-01": "Overload — unplug the load and press the button to restore."},
        power="120 V AC passthrough.",
        reset="Hold the button for 8 seconds until the light blinks green rapidly.",
        warranty=24,
        compat=["Aria app", "Aria Hub (required)", "Google Home", "Amazon Alexa"],
    ),
    "ARIA-LEAK": dict(
        name="Aria Water Leak Sensor",
        category="sensor",
        price=34,
        specs={
            "Detection": "two contact probes on the base plus a 4-foot rope probe",
            "Alerts": "app push, 85 dB local siren, temperature and freeze warning below 41 °F",
            "Radio": "Zigbee 3.0 via the Aria Hub",
            "Battery": "2 × AAA, about 3 years",
        },
        box=["Leak Sensor", "rope probe", "2 AAA batteries"],
        setup=["Place on the floor under the water heater or sink; lay the rope where water pools."],
        leds={"Blue blink": "water detected", "Red blink": "battery low"},
        troubleshooting=[
            ("Siren keeps going after the floor is dry", "Dry the probes on the base; a film of water on the contacts still reads as wet."),
            ("Freeze alert but the room is warm", "The sensor reads its own location; it may be on a cold slab. Raise the freeze threshold in settings."),
        ],
        errors={"W-02": "Rope probe disconnected — reseat the 3.5 mm plug."},
        power="2 × AAA alkaline, about 3 years.",
        reset="Remove the batteries for 30 seconds, then hold the button while reinserting them.",
        warranty=24,
        compat=["Aria app", "Aria Hub (required)"],
    ),
    "ARIA-VIDEO-PLAN": dict(
        name="Aria Video subscription",
        category="plan",
        price=0,
        specs={
            "Basic": "$3.99 per month per camera — 30 days of event history, person detection",
            "Plus": "$9.99 per month for all cameras — 60 days of history, package and vehicle detection, 24/7 recording on wired cameras",
            "Without a plan": "live view, two-way talk, and the most recent 3 hours of events",
            "Billing": "monthly or yearly (two months free); cancel any time from Account > Plan",
        },
        box=[],
        setup=["Go to Account > Plan in the Aria app and choose Basic or Plus.", "A plan applies to cameras on the same account within minutes."],
        leds={},
        troubleshooting=[
            ("Recordings stop after 3 hours", "That is the no-plan history limit; add Basic or Plus."),
            ("Charged twice in one month", "A yearly plan started mid-month; the app shows a prorated credit on the next invoice."),
        ],
        errors={},
        power="",
        reset="",
        warranty=0,
        compat=["Aria Doorbell Cam", "Aria Doorbell Pro", "Aria Floodlight Cam", "Indoor Camera"],
    ),
}


# ─────────────────────────────────────────────────────────────── rendering


def build(sku: str, p: dict, out: Path) -> Path:
    styles = getSampleStyleSheet()
    h1 = styles["Title"]
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], spaceBefore=12)
    body = ParagraphStyle("body", parent=styles["BodyText"], leading=14)
    doc = SimpleDocTemplate(
        str(out), pagesize=LETTER, leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        title=f"{p['name']} — Owner's Manual", author="Aria Home",
    )
    s: list = []
    s.append(Paragraph(f"{p['name']} — Owner's Manual", h1))
    s.append(Paragraph(f"Aria Home · SKU {sku} · {p['category']}" + (f" · ${p['price']}" if p["price"] else ""), body))
    s.append(Spacer(1, 10))
    s.append(Paragraph(f"This manual covers the {p['name']} (model {sku}) only. Other Aria products have their own manuals; procedures and error codes are not interchangeable between models.", body))

    s.append(Paragraph("1. Specifications", h2))
    rows = [[k, v] for k, v in p["specs"].items()]
    t = Table(rows, colWidths=[1.8 * inch, 4.6 * inch])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("FONTSIZE", (0, 0), (-1, -1), 9)]))
    s.append(t)

    if p["box"]:
        s.append(Paragraph("2. In the box", h2))
        s.append(Paragraph(", ".join(p["box"]) + ".", body))

    s.append(Paragraph("3. Setup", h2))
    for i, step in enumerate(p["setup"], 1):
        s.append(Paragraph(f"{i}. {step}", body))

    if p["leds"]:
        s.append(Paragraph("4. Status light", h2))
        for k, v in p["leds"].items():
            s.append(Paragraph(f"<b>{k}</b>: {v}.", body))

    if p["power"]:
        s.append(Paragraph("5. Power and battery", h2))
        s.append(Paragraph(f"{p['name']}: {p['power']}", body))

    s.append(Paragraph("6. Troubleshooting", h2))
    for sym, fix in p["troubleshooting"]:
        s.append(Paragraph(f"<b>{p['name']} — {sym}.</b> {fix}", body))

    if p["errors"]:
        s.append(Paragraph("7. Error codes", h2))
        for code, meaning in p["errors"].items():
            s.append(Paragraph(f"<b>{p['name']} error {code}</b>: {meaning}", body))

    if p["reset"]:
        s.append(Paragraph("8. Factory reset", h2))
        s.append(Paragraph(f"To factory reset the {p['name']}: {p['reset']}", body))

    s.append(Paragraph("9. Warranty and compatibility", h2))
    if p["warranty"]:
        window = 14 if p["category"] in ("lock",) or "doorbell" in p["name"].lower() else 30
        s.append(Paragraph(f"The {p['name']} carries a two-year standard warranty covering manufacturing defects, from the delivery date. Unwanted returns follow the Aria Home returns policy: {window} days from delivery for the {p['name']} ({'security devices have a 14-day window' if window == 14 else 'most devices have a 30-day window'}). Damage caused by the customer is handled as a warranty repair, not a refund.", body))
    s.append(Paragraph("Works with: " + ", ".join(p["compat"]) + ".", body))
    doc.build(s)
    return out


def main() -> None:
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    for sku, p in PRODUCTS.items():
        f = build(sku, p, out_dir / f"{sku.lower()}-manual.pdf")
        print(f"wrote {f} ({f.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

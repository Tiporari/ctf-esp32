# ESP32 Hidden-Network CTF — Parents' Guide

A short, self-contained capture-the-flag game for a curious kid (built for a 12-year-old), run entirely from a ~$10 ESP32 board. The board broadcasts its own **hidden Wi-Fi network** and hosts a small web server. There is no internet involved and nothing on your home network is touched.

> **Spoiler warning:** this guide contains every answer. Keep it away from the player. That's why this repo is private.

## What the player experiences

| Level | Task | Skill practiced | Flag |
|---|---|---|---|
| 0 | Find and join a Wi-Fi network that doesn't show up in the list | How Wi-Fi works, hidden SSIDs | *(no flag, reaching the login page is the goal)* |
| 1 | Log in to the "Lab Console", then turn a wall of text into an image | Default passwords, Base64, file signatures | `FLAG{b64_decoded_nice_work}` |
| 2 | Listen to a Morse message on `/radio` and type what you hear | Morse code, patience | `FLAG{dits_and_dahs_decoded}` |

Every page has a "Got a flag?" box. A correct flag unlocks the next step. Total playing time is roughly 30–90 minutes depending on the kid.

## What you need

- An **ESP32 dev board** (built and tested on an ESP32-WROOM / ESP32-D0WD-V3 with a CP210x USB chip) and a USB data cable.
- A Windows/Mac/Linux computer for the one-time setup. Examples below use Windows PowerShell; on Mac/Linux use the equivalent `.venv/bin/...` paths.
- **Python 3.9+**.
- A USB charger or power bank to run the board afterwards (the computer isn't needed once it's set up).
- For the player: a phone, tablet or laptop **with sound** (needed for Level 2).

## One-time setup

1. **Clone and create a Python environment**
   ```powershell
   git clone https://github.com/Tiporari/ctf-esp32.git
   cd ctf-esp32
   python -m venv .venv
   .\.venv\Scripts\pip install esptool mpremote pillow
   ```
2. **Find the board's COM port** (Windows: Device Manager → Ports; look for "CP210x" or "USB Serial", e.g. `COM7`). On Mac/Linux it looks like `/dev/ttyUSB0` or `/dev/cu.usbserial-*`. You may need the [CP210x driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers).
3. **Download MicroPython** for "ESP32_GENERIC" from <https://micropython.org/download/ESP32_GENERIC/> (this guide was built on v1.29.0) and save the `.bin` in `firmware/`.
4. **Flash the board.** This erases whatever was on it.
   ```powershell
   .\.venv\Scripts\esptool --port COM7 erase-flash
   .\.venv\Scripts\esptool --port COM7 --baud 460800 write-flash 0x1000 firmware\ESP32_GENERIC-<version>.bin
   ```
   If it can't connect, hold the board's **BOOT** button while the command says "Connecting....".
5. **Customize** `device/config.py` (see below), then **deploy**:
   ```powershell
   .\deploy.ps1 -Port COM7
   ```
   The board reboots and the network goes live within a few seconds. From now on it starts automatically whenever it has power.

## Customize before the game (do this!)

Edit [`device/config.py`](device/config.py), then re-run `.\deploy.ps1`:

| Setting | What it does |
|---|---|
| `SSID` | Hidden network name. Pick something that won't be guessed. |
| `PASSWORD` | WPA2 password (8+ characters). **Change the default**. Empty string = open network. |
| `HIDDEN` | `True` hides the name from normal Wi-Fi lists. |
| `LOGIN_USER` / `LOGIN_PASS` | Default is `admin` / `password` (the lesson: default credentials are the most common security mistake). |
| `MORSE_KEY` | The message played in Level 2. |
| `LEVELS` | Flags and the success messages. |

To change the Level 1 image: `python tools/make_image.py "FLAG{your_flag}" vault.b64`, update the flag in `LEVELS[0]`, redeploy.

## Setting up the game for your kid

Give the player only:

- The name of the game / a story hook ("There's a secret network somewhere in the house...").
- The **hint that a hidden network exists.**
- The **Wi-Fi password** (decide whether it's part of the puzzle: a note somewhere, or just hand it over. The hidden-name part is already challenging).

The ESP32 has **no internet**. While the phone/laptop is on the CTF network it can't reach websites. For Level 1 he'll need a way to decode Base64 offline (see hints), or he can copy the text, switch back to home Wi-Fi, decode it online, then rejoin. Letting him figure that out is part of the fun.

## Walkthrough (spoilers!)

### Level 0 — Find the network
The SSID is hidden, so it won't appear in a Wi-Fi list. He has to add it manually: Wi-Fi settings → *Add network / Other* → type the exact name → WPA2 → password. Then open <http://192.168.4.1> (plain `http`, not `https`).

How does he learn the name? That's up to you: a clue card, a sticky note, a scanner app that shows hidden networks (e.g. a Wi-Fi analyzer), or for older kids a laptop sniffing tool. Hidden SSIDs are *not real security*; they're a fun first puzzle.

### Level 1 — Fake login + Base64 image
- The login page accepts **`admin` / `password`**. Lesson: default or weak passwords are the #1 real-world weakness.
- Subtle clue in the page source: `<!-- TODO: remove test account before launch -->` (View source / long-press in some browsers).
- After login he sees a long block of text starting with `iVBOR...`. That's a **Base64-encoded PNG image** (every PNG starts with `iVBOR` when encoded).
- Decode it to a `.png` and open it: it shows `FLAG{b64_decoded_nice_work}`.
  - Online: paste into [CyberChef](https://gchq.github.io/CyberChef/) → "From Base64" → "Render Image" (needs internet, so off the CTF network).
  - Windows (offline): save the text as `vault.txt`, then `certutil -decode vault.txt flag.png`.
  - Mac/Linux: `base64 -d vault.txt > flag.png`.
- Enter the flag in the box. The next page points to `/radio`.

### Level 2 — Morse code on `/radio`
- `/radio` plays a Morse message through the device's speakers (not the ESP32's). Press **Play**, pick Slow / Very slow / Medium. A light on the page blinks with each tone. The Morse alphabet is displayed on the page.
- The message is **`OPEN SESAME`**. Typing it (any case, spaces optional) shows `FLAG{dits_and_dahs_decoded}`.
- Entering that flag in the box gives the victory message.

## Hint ladder (so you can help without spoiling)

**Can't find / join the network**
1. "Wi-Fi names don't have to be broadcast. What if you had to type in the name yourself?"
2. "Where would someone leave the name?" (point to your clue card)

**Stuck on the login**
1. "Think about what the laziest, most common username and password would be."
2. "What would you type if you were the admin and you didn't care?"

**Stuck on the Base64 text**
1. "That's not random. It's *encoded*. Computers use it to hide files inside text."
2. "Look at the first few letters. Could it be a picture?" (The `iVBOR` start is a PNG signature.)
3. "Search for 'Base64 to image'. You may need to leave this Wi-Fi to look it up."

**Stuck on Morse**
1. "Close your eyes and just count the long and short beeps for one letter at a time."
2. "Use the chart on the page, and use *Very slow*. Replay as many times as you want."
3. "Type what you think you heard, even if you're unsure. A wrong answer costs nothing."

## Troubleshooting

| Problem | Fix |
|---|---|
| Can't see the COM port | Install the CP210x driver; try a different USB *data* cable (some are charge-only). |
| esptool can't connect | Hold BOOT while connecting; close any serial monitor using the port. |
| Network not found after power-up | Wait ~10 s. Check SSID/password spelling in `config.py`. Phones sometimes need Wi-Fi toggled off and on. |
| Phone says "no internet" / disconnects | Expected. Choose "stay connected". The board has no internet. |
| Page won't load | Use `http://192.168.4.1` and not `https`. Turn off mobile data or VPN on the phone. |
| No sound on `/radio` | Tap **Play** (browsers require a tap first), unmute, check volume. |
| Want to see what the board is doing | `.\.venv\Scripts\mpremote connect COM7` opens a serial console. Note that this interrupts the server; press the board's reset button or run `.\deploy.ps1` to restart. |
| Want to restart the game / reset | Unplug and replug power. There is no stored progress. |

## Safety and expectations

- The board only creates its own tiny network (up to 4 devices). It does not connect to your home Wi-Fi or the internet and can't expose anything on them.
- The "login" is a fake page that only checks against the values in `config.py`. No real accounts are involved.
- Hidden network names and Base64 are **not** security measures. Use the game as a springboard: talk about why real systems use strong passwords, encryption (not just encoding), and how defenders find hidden things.
- Only point these techniques at devices you own or have permission to test. That's the first rule of every real CTF.

## Repo layout

```
device/          # files that run on the ESP32 (MicroPython)
  main.py        # starts the hidden access point + web server
  config.py      # SSID, password, flags, Morse message — edit this
  challenges.py  # all routes / levels
  webserver.py   # tiny asyncio HTTP server
  morse.py       # Morse table + encoder
  radio.html     # Level 2 page (plays Morse in the browser)
  vault.b64      # Level 1 base64 image
tools/make_image.py   # render a flag into a Base64 PNG
deploy.ps1            # copy device/ to the board and reboot it
firmware/             # put the MicroPython .bin here (not committed)
```

## Ideas for more levels

Cookie tampering, `robots.txt` hidden paths, ROT13/hex puzzles, `User-Agent` checks, and hardware challenges (LoRa beacons or NFC tags with an M5 Cardputer). New levels are added in `device/challenges.py` and `device/config.py`.

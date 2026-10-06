# Edit these, then push with: .\deploy.ps1
SSID = "CTF-Lab-7f3a"        # visible in the Wi-Fi list (see HIDDEN)
PASSWORD = "cardputer"     # WPA2 needs 8+ chars; set to "" for an open network
CHANNEL = 6
HIDDEN = False               # some Android versions can't join hidden networks
MAX_CLIENTS = 4
AP_IP = "192.168.0.1"

LOGIN_USER = "admin"
LOGIN_PASS = "password"

# Progressive levels. Submitting flag N shows `next` (the clue for level N+1).
# Level 1's flag is rendered inside device/vault.b64 (see tools/make_image.py).
MORSE_KEY = "OPEN SESAME"   # level 2 (final): played as Morse on /radio; typing it reveals the flag

LEVELS = [
    {
        "flag": "FLAG{b64_decoded_nice_work}",
        "next": 'Level 1 complete! A signal is coming in on <a href="/radio">/radio</a>.',
    },
    {
        "flag": "FLAG{dits_and_dahs_decoded}",
        "next": "You did it. You found the hidden network, cracked the login, decoded the image and "
                "the radio signal. Mission complete. Go tell your dad.",
    },
]

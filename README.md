# DXHR TYM Shuttle Fix

A save fix for a bug in **Deus Ex: Human Revolution – Director's Cut**: in Hengsha, the Tai Yong Medical employee shuttle never arrives. That blocks the objective *"Go to TYM via the Employee Shuttle"*.

Forum threads about this bug usually end with "load an older save". This script fixes the save you already have.

## Do you have this bug?

- The hacked badge opens the shuttle station door, but the shuttle never pulls in, however long you wait.
- Reloading that save, or any newer one, doesn't help.
- **Quick check:** the public metro in Jiu Shichang doesn't arrive either. If no metro train comes after a minute on its platform, you almost certainly have this bug. The metro's ticket scanners don't work on that side anyway (a separate level bug), so jump the turnstiles.

## Requirements

- Deus Ex: Human Revolution – Director's Cut (Steam)
- Python 3. Only the standard library is used.

## How to use

1. Make a manual save in Lower Hengsha, then **quit the game completely**.
2. Find your save folder:
   - Windows: `C:\Program Files (x86)\Steam\userdata\<your id>\238010\remote\`
   - Linux / Proton: `~/.steam/steam/userdata/<your id>/238010/remote/`
3. **Back up the whole folder.** The script makes its own backups, but a full copy is cheap insurance.
4. Run the script on the folder, which uses your newest save, or on one save file:
   ```
   python dxhr_tym_shuttle_fix.py "<path to the remote folder>"
   ```
   On Windows, `py` works in place of `python`. The script should report that it cleared 3 copies of the Part 1 flag.
5. Start the game. If Steam reports a Cloud sync conflict, keep the **local** files.
6. Load the fixed save. Walk into the **L.I.M.B. clinic** next to the TYM station, then straight back out through its front door.
7. If a bare menu appears with **Option1 … Option4**, pick **Option1**. It's a leftover developer menu.
8. Go to the TYM platform and **ride the shuttle in the same session**. Don't reload in between, because the game sets the flag again once the fix has worked. To retry, load the fixed save again or run the script on your newer save.

## What the script changes

The script does not touch the game or its code. With the game closed, it:

1. decompresses the save (one zlib stream);
2. finds the scenario chooser's "Hengsha Part 1 done" flag (object `0xC0C8`, flag `0x139C`, stored 3 times) and sets each copy from 1 to 0;
3. compresses the save again with the game's settings (zlib level 6) and updates the save's size in `saveindex`.

Before writing anything, it saves a backup of the save and of `saveindex` (`.bak-<timestamp>`). If the flag isn't set, or the save isn't from Hengsha, it exits without changing anything.

## Why the bug happens

The TYM shuttle and both Lower Hengsha metro trains are each run by a small *sequence*: when you step on the platform, the sequence tells the train to arrive. The game's Hengsha setup (**Hengsha Part 1**) starts all of these sequences, and a hidden "scenario chooser" object decides when to run that setup.

- Running sequences are **not** stored in saves, so after a load something has to restart them.
- The chooser doesn't re-check on a plain load. It only re-checks when you arrive through certain spawn points, one of which is just outside the L.I.M.B. clinic's front door.
- When it does re-check, it skips Part 1 if Part 1's "done" flag is set. In an affected save, nothing ever restarts the train sequences, so no train in the district is ever called.

Clearing the flag and walking out of the clinic makes the chooser run Part 1 again, which restarts the trains.

It's still unknown how a save gets into this state, or why most players never hit it.

### Details for modders

| What | Value |
|---|---|
| Chooser object | `scenario_chooser`, unique ID `0xC0C8` in `sha_city__masterunit.drm`, script `0x12071` (base class `0x2145`) |
| Part 1 condition | smart bool `0xF3E4` |
| Sticky "done" flags | `0x139C` (Part 1), `0x139E`, `0x13A0`, `0x13A2` |
| Train sequences | `0x120B9` (Jiu Shichang metro), `0x120BA` (Youzhao metro), `0x120BB` (TYM shuttle) |
| Save format | one zlib stream (level 6), 2,334,720 bytes once decompressed; sticky flags are 9-byte records `{u32 owner, u32 flag, u8 value}` |
| `saveindex` | u32 count, then 53-byte records: `name[33]`, u32 compressed size, u64 FILETIME, u32, u32 |
| Clinic spawn point | `0xD12A` in `sha_city_lowernightlife`, reached through the door `0xD12B` in `sha_city_lowerlimbclinic` |

## Caveats

- **Tested on one playthrough**: the Steam Director's Cut, run through Proton on Linux. Steam saves are the same files on Windows.
- The original 2011 release and the GOG version are untested. If their IDs differ, the script just reports that it found nothing to change.
- Running Hengsha Part 1 a second time restarts that area's setup. No side effects showed up in testing, but this can't be promised for every save.
- Back up your saves before using it.

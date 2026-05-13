# How to Run Job Matcher (Easy Guide)

This guide is for **anyone** — you don't need to know programming. Just follow the steps.

---

## What You Need

Only **ONE thing**: **Docker Desktop** (a free app that runs everything for you)

---

## STEP 1: Install Docker Desktop

Docker is like a magic box that runs the entire app for you. You install it once and forget about it.

### On Windows:
1. Go to https://www.docker.com/products/docker-desktop/
2. Click **"Download for Windows"**
3. Open the downloaded file and follow the installer
4. **Restart your computer** when it asks
5. After restart, open **Docker Desktop** from your Start Menu
6. Wait until you see a green icon that says **"Running"** (may take 1-2 minutes)

### On Mac:
1. Go to https://www.docker.com/products/docker-desktop/
2. Click **"Download for Mac"** (choose Apple Chip if you have M1/M2/M3, or Intel)
3. Open the downloaded `.dmg` file
4. Drag Docker to Applications
5. Open **Docker** from Applications
6. Wait until the whale icon in your top menu bar stops animating (means it's ready)

### On Linux:
1. Go to https://docs.docker.com/engine/install/
2. Follow the instructions for your distribution
3. Also install Docker Compose

---

## STEP 2: Download the Project

### Option A: Download as ZIP (Easiest)
1. Go to https://github.com/hossamfarag966-png/Hossam
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip the folder somewhere you can find it (like your Desktop)
5. Open the folder: go into `Hossam` then into `job-matcher`

### Option B: Using Terminal/Command Prompt
```
git clone https://github.com/hossamfarag966-png/Hossam.git
```
Then open the `Hossam/job-matcher` folder.

---

## STEP 3: Start the App

### On Windows:
1. Open the `job-matcher` folder
2. **Double-click `start.bat`**
3. A black window will appear — follow the questions it asks
4. Wait 2-3 minutes (it's downloading and setting things up)
5. When it says "ALL DONE!" — you're ready!

### On Mac/Linux:
1. Open **Terminal** (search for "Terminal" in Spotlight/Applications)
2. Type these commands:
```
cd ~/Desktop/Hossam-main/job-matcher
chmod +x start.sh
./start.sh
```
3. Follow the questions it asks
4. Wait 2-3 minutes
5. When it says "ALL DONE!" — you're ready!

---

## STEP 4: Open the App

Open your web browser (Chrome, Safari, Firefox — any) and go to:

**http://localhost:3000**

You should see the Job Matcher Dashboard!

---

## STEP 5: Upload Your CV

1. In the app, click **"Settings"** in the top menu
2. Click **"Choose File"** under "Upload CV"
3. Select your CV/resume file (PDF or Word document)
4. Wait a few seconds — it will parse your skills and experience automatically!

---

## STEP 6: Set Your Preferences

Still on the Settings page:

1. **Target Roles** — Type what jobs you want, separated by commas
   - Example: `Software Engineer, Data Analyst, Product Manager`

2. **Target Locations** — Where you want to work
   - Example: `Remote, Dubai, London`

3. **Work Mode** — Choose: Remote, Hybrid, Onsite, or Any

4. **Minimum Salary** — Your floor (in USD)
   - Example: `60000`

5. **Target Seniority** — Check the boxes: Junior, Mid, Senior, etc.

6. **Deal Breakers** — Companies/industries you want to avoid
   - Example: `gambling, crypto`

7. Click **"Save Preferences"**

---

## STEP 7: Get Your Job Matches!

1. Click **"Dashboard"** in the top menu
2. Click the **"Fetch New Jobs"** button
3. Wait about 30 seconds
4. Refresh the page (F5 or Ctrl+R)
5. You'll see jobs ranked by how well they match you!

---

## What Each Number Means

| What you see | What it means |
|--------------|---------------|
| **Match: 85%** | How well this job fits YOUR skills and preferences |
| **~$95k/yr** | Estimated salary for this role |
| **Acceptance: 70%** | How likely they'd call you for an interview |
| **Skill Coverage** | What % of their required skills you have |

---

## Daily Email (Optional)

Want to wake up to a daily email with your top job matches? You need a Gmail App Password:

1. Go to https://myaccount.google.com/apppasswords
   - (You need 2-factor authentication enabled on your Google account)
2. Create an app password for "Mail"
3. Copy the 16-character password
4. Open the `.env` file in the `job-matcher` folder with any text editor (Notepad, TextEdit)
5. Replace `your-app-password` with the password you copied
6. Save the file
7. Restart the app (run `stop.bat` then `start.bat`, or `./stop.sh` then `./start.sh`)

---

## How to Give Feedback (Makes it Smarter!)

On each job card, you'll see buttons:
- **Interested** — "I like this, show me more like it"
- **Applied** — "I applied to this one"
- **Not Relevant** — "This doesn't fit me, show less like it"

The more feedback you give, the better your future matches will be!

---

## How to Stop the App

### Windows:
Double-click **`stop.bat`**

### Mac/Linux:
```
./stop.sh
```

---

## How to Start Again Later

Just double-click `start.bat` (Windows) or run `./start.sh` (Mac/Linux) again.
It will start much faster the second time (no need to rebuild).

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Docker is not installed" | Install Docker Desktop (Step 1) |
| "Docker is not running" | Open Docker Desktop app and wait for it to show "Running" |
| Page won't load | Wait 2-3 minutes, the app is still starting |
| No jobs showing | Click "Fetch New Jobs" and wait 30 seconds, then refresh |
| "No profile found" | Go to Settings and upload your CV first |
| Email not working | You need a Gmail App Password (see "Daily Email" section above) |
| Everything broken | Run stop, then start again. If still broken: run `docker compose down -v` then start again (this resets everything) |

---

## Need an OpenAI Key? (Optional but Recommended)

An OpenAI key makes the matching MUCH smarter. Without it, the app still works but uses simpler matching.

1. Go to https://platform.openai.com/api-keys
2. Create an account (or sign in)
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Open the `.env` file and paste it after `OPENAI_API_KEY=`
6. Add $5 credit at https://platform.openai.com/account/billing (this lasts months for personal use)
7. Restart the app

---

## That's it!

You now have your own personal job-matching AI that:
- Scans 3 job platforms automatically
- Scores every job against YOUR specific skills
- Estimates salary ranges
- Predicts your chances of getting an interview
- Can email you the best matches every morning

Enjoy your job search! 

# PhysioLive: A Wireless Physiotherapy Monitoring System

PhysioLive is an open-source project aimed at creating a wireless system for physiotherapy patient monitoring. The system focuses on tracking exercises and reporting movement or vital data in real time, aiming to improve both patient outcomes and therapeutic efficiency.

## Features 
1. Wireless Monitoring: Collects patient movement and/or health parameters remotely.

2. Physiotherapy Support: Designed specifically to assist physiotherapists and patients during rehabilitation sessions.

3. Data Logging: Records and stores relevant exercise and physiological data for progress tracking.

4. Web Interface: May include a dashboard for visualizing sessions, tracking patient improvement, and managing protocols.

5. Python/HTML/CSS Stack: Core logic written in Python, with frontend components in HTML and CSS.


## How It Works 

1. Sensors record patient movements and/or vital signs during physiotherapy.

2. Data is logged wirelessly to a central system.

3. Web dashboard displays session data and progress for practitioners and patients.

4. Supports personalized exercise plans and rehabilitation routines.

## Installation

1. #### Clone the Repository

```
git clone https://github.com/shbhm-chvnk/PhysioLive-A-Wireless-Physiotherapy-Monitoring-System.git
cd PhysioLive-A-Wireless-Physiotherapy-Monitoring-System
```

2. #### Install Dependencies

    • Ensure you have Python 3.8+ and pip installed.

    • Install required Python packages:
```
pip install -r requirements.txt
```

3. #### Connect Hardware

    • Configure supported sensors according to /docs/hardware.md.
   
    • Connect your microcontroller as described.

4. #### Run the Application
```
python src/main.py
```

5. #### Open the Web Dashboard

    • Access the dashboard in your browser at http://localhost:5000.

## Repository Layout
```
PhysioLive-A-Wireless-Physiotherapy-Monitoring-System/
├── src/
│   ├── index.html
│   ├── dashboard.html
│   ├── import_serial.py
│   ├── physio_dashboard.py
│   ├── import_serial.py
│   ├── style.css
│   └── about.html
├── data/
│   ├── alert_log.csv
│   └── live_data.csv
├── docs/
│   ├── logo.png
│   ├── AVLE.png
│   ├── LAHLE.png
│   ├── RHHWUE.png
│   ├── RHWUD.png
│   ├── alert.mp3
│   ├── abt1.png
│   ├── abt2.png
│   ├── abt3.png
│   └── linkedin.png
├── requirements.txt
└── README.md
```

## 📄 License
This project was developed as a part of the Israeli-Indian Hackathon 2025.

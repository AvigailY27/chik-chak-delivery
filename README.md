ChikChak Delivery – Optimal Delivery Route Management System
This project is a smart delivery management system that calculates the optimal delivery route for couriers, based on deadlines, traffic load, and road constraints. It includes both a client-side interface and a Python backend for logic and optimization.
Project Purpose

- Assign delivery addresses to couriers efficiently based on their available delivery windows.
- Cluster addresses into geographical zones to minimize total delivery areas.
- Calculate real-time road congestion using OpenStreetMap (OSM) and vehicle detection from video.
- Build a weighted graph from road data, where:
  - Nodes = junctions
  - Edges = roads between them
  - Edge weight = travel time (based on distance, speed, and traffic)

Key Features
•	Zone Clustering:
The system begins with one delivery zone and tries to fit all deliveries into minimal areas, considering each courier’s time constraints.
•	Graph-Based Route Planning:
The road network is represented as a weighted directed graph. Edge weight is calculated using:
  weight = distance / speed
  Speed is estimated from:
  permitted_speed - (road_load_factor)
•	Vehicle Detection (YOLO):
Real-time detection of vehicles on road segments helps calculate traffic load using:
  (Number of vehicles * road length) / (Number of lanes)
•	Priority Queue of Deliveries:
Deliveries are organized into a min-heap where the top-priority delivery is the one with the earliest end time.
•	Optimized Path Construction:
The priority queue is converted into a doubly-linked list that represents the actual optimized path, fitting in lower-priority deliveries without delaying higher-priority ones.
•	Delay Heap Calculation:
The system calculates possible delays between current time and the deadline using:
  delay_time = (end_time - start_time) - estimated_travel_time
•	Smart Insertion of Optional Deliveries:
If a low-priority delivery can be inserted into the path without violating delay constraints, it is added and assigned a fractional serial number.
How It Works (Workflow Summary)

1. Manager enters deliveries with start and end time.
2. Deliveries are clustered into zones.
3. Each zone is mapped on a graph using OSM data.
4. Traffic load is analyzed using video detection (YOLO).
5. Routes are computed using edge weights based on travel time.
6. A priority queue is built and converted to a delivery route.
7. Optional deliveries are added if possible without delay.
8. Final route is optimized and returned to the courier.

Installation
Requirements

- Python 3.x
- Node.js + npm
- Recommended: VSCode

Running the Frontend

cd src/
npm install
npm start

Running the Backend

cd backend/
python server.py

If dependencies are required:
pip install -r requirements.txt

Author

Developed by Avigail Y., 2025
For project or academic use only.

GitHub Repo:
https://github.com/AvigailY27/chikchakdelivery


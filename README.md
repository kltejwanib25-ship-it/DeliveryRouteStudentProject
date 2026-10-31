# Smart Delivery Route Planner — DAA mini project

A simple Python desktop project that arranges delivery stops in an efficient order.

## Requirements
Python 3.10+ with Tkinter (included in most normal Windows Python installers). No pip packages, API keys, or internet needed.

## Run
On Windows, double-click `START_WINDOWS.bat`, or open a terminal in this folder and run:

```bash
python app.py
```

## Usage
1. Click **Optimize route** to use the included six-stop example.
2. The **first row is the delivery office/depot**. The driver begins and ends here.
3. Select a row to edit; enter X/Y coordinates and click **Update**. Add or remove delivery stops as needed.
4. Click **Optimize route** to calculate the best found order; export a CSV if desired.

Coordinates are on a **fictional 2D map**. Each grid coordinate unit represents one kilometre. Distance uses Euclidean straight-line distance, **not driving roads**, traffic, or real GPS locations. The example names are fictional.

## Algorithms
- Nearest Neighbor (Greedy): from the current location, pick the closest unvisited stop.
- 2-opt (local search): reverse a route section if it reduces the total round-trip distance.
- The initial route is the stops in the order entered; this baseline is compared to the optimized result. For this demo, the optimizer also never returns a worse route than that baseline.
- For a small student project, this is simpler to explain than exact exponential-time Traveling Salesperson algorithms.

## Complexity
For n delivery stops, greedy Nearest Neighbor is O(n²). This straightforward implementation of 2-opt tests O(n²) swaps per improvement pass and recalculates O(n) route distance for each swap, so each pass is O(n³). The number of passes depends on the input. The method **does not guarantee a globally shortest route**.

## Tests
```bash
python -m unittest discover -v
```

## Project files
- `app.py`: Tkinter interface, drawing and CSV export
- `optimizer.py`: routing algorithms
- `test_optimizer.py`: algorithm tests
- `START_WINDOWS.bat`: Windows launcher

No PPT or video script included.

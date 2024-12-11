# org-booking-simulation
Collective Action Problem Class Project for simulating university organizations booking venue spots in their campus, and what the effect is of overbooking and not overbooking. 
The simulation incorporates mechanisms to study strategies like overbooking and venue sharing, analyzing their impact on fairness, efficiency, and outcomes.

## Problem Statement

University organizations realistically face challenges in booking event spaces due to:
- **Limited availability of venues.**
- **Random university cancellations.**
- **Risks associated with overbooking (penalties for unused bookings).**

This simulation models these challenges to analyze how strategies like overbooking and mechanisms like venue sharing affect the overall system.

## Features

### Mechanisms/Simulation Aspects
1. **Random University Cancellations:** Events randomly canceled in the simulation to emulate a university taking precedence and reserving a venue, overriding any organization that may have booked it
2. **Overbooking Strategy:** Organizations can hedge against cancellations by double booking venues for the same time slots, booking more than required in total. 
3. **Venue Sharing:** Simulation mechanism to determine if sharing venue spaces by organizations provides a better outcome in terms of venue utilization. 
4. **Priority-Based Venue Selection:** Reputation system implemented to reward organizations whose strategies yield better utilization of venues. 
5. **Time Slot Availability:** Time slots implemented for venues and organizations to improve realism and simulate real-world scenario where both have set availability times/meeting times, respectively. 

### Game Theoretic Enhancements
- **Payoff Calculation:** Payoffs for organizations consider various factors like venue popularity, penalties for unused bookings, and reward for proper utilization. 
- **Statistical Analysis:** Utilized Gini Coefficient for fairness and comparison metrics, along with tables and plotted graphs to show performance over time for strategies & organizations to understand larger picture. 

---

## Simulation Components

### Classes and Their Roles
1. **`Organization`:** Models university organizations with attributes like reputation, budget, and strategy (normal booking or overbooking).
2. **`Venue`:** Represents event venues with attributes like popularity level and time slot availability.
3. **`Simulation`:** Coordinates the booking process, cancellations, and mechanism application.

---

## Calculations and Metrics

### Payoff Function
Payoff = Total Rewards from Successful Bookings - Penalties for Unused Bookings
- **Reward:** Based on venue popularity levels.
- **Penalty:** Scaled by unused bookings and penalty cost per round that increases with more unused bookings.

### Gini Coefficient
Used to measure fairness in score distribution:
Gini = 2 \sum_{i=1}^{n} i \cdot x_i}{n \cdot \sum_{i=1}^{n} x_i} - \frac{n+1}{n} \]
Where x_i are the sorted scores.

---

## Results
Key outcomes of the simulation:
- **Average Scores:** Higher with venue sharing.
- **Unused Bookings:** Reduced significantly with venue sharing.
- **Fairness:** Gini coefficient is lower with venue sharing, indicating improved fairness.




## How to Run

### Prerequisites
1. Python 3.8+
2. Required libraries:
   - `matplotlib`
   - `numpy`

### Steps
1. Clone the repository:
   ```
   git clone <repository-link>
   cd <repository-folder>
   

2. Install dependencies
    ```
    pip install -r requirements.txt

3. Run the simulation
    ```
    python main.py --num_orgs 10 --num_venues 20 --num_periods 10 --cancellation_rate 0.3 --venue-sharing


   
#### Command-Line Arguments
Argument	Default	Description
--num_orgs	10	Number of organizations in the simulation.
--num_venues	20	Number of venues available.
--num_periods	10	Number of simulation periods.
--cancellation_rate	0.3	Probability of random venue cancellations.
--venue-sharing	False	Enable the venue-sharing mechanism.

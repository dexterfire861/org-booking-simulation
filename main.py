import argparse
from simulation import Simulation

def main():
    parser = argparse.ArgumentParser(description="Run the organization booking simulation.")
    parser.add_argument('--num_orgs', type=int, default=10, help='Number of organizations')
    parser.add_argument('--num_venues', type=int, default=15, help='Number of venues')
    parser.add_argument('--num_periods', type=int, default=10, help='Number of periods')
    parser.add_argument('--cancellation_rate', type=float, default=0.3, help='Cancellation rate')
    parser.add_argument('--venue-sharing', action='store_true', default=False, help='Enable venue sharing')

    args = parser.parse_args()

    sim = Simulation(num_orgs=args.num_orgs, num_venues=args.num_venues, num_periods=args.num_periods, cancellation_rate=args.cancellation_rate, enable_mechanism=args.venue_sharing)

    sim.run_simulations()

    # sim.run()
    # sim.print_results()

    # sim.track_strategy_changes()
    # sim.calculate_gini_coefficient()

    # sim.plot_results()
    # sim.compare_strategy_performance()
    # sim.analyze_strategy_impact()

if __name__ == "__main__":
    main()
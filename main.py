import argparse
import sim


def parse_arguments():
    parser = argparse.ArgumentParser(description="Simulation of Student Organizations Booking Venues")
    parser.add_argument('--num_rounds', type=int, default=5, help='Number of rounds in the simulation')
    parser.add_argument('--round_length', type=int, default=7, help='Number of days per round')
    parser.add_argument('--cancellation_rate', type=float, default=0.1, help='Rate at which events get canceled')
    parser.add_argument('--num_organizations', type=int, default=3, help='Number of student organizations')
    parser.add_argument('--num_venues', type=int, default=5, help='Number of venues available')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    sim = sim.Simulation(
        num_rounds=args.num_rounds,
        round_length=args.round_length,
        cancellation_rate=args.cancellation_rate,
        num_organizations=args.num_organizations,
        num_venues=args.num_venues
    )
    sim.run_simulation()

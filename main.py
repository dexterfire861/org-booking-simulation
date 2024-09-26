from simulation import Simulation

def main():
    sim = Simulation(num_orgs=10, num_venues=5, num_periods=20, cancellation_rate=0.2)
    sim.run()
    sim.print_results()

if __name__ == "__main__":
    main()
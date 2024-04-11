
class Model:

    def __init__(self, comm, params):
        self.comm = comm
        self.context = ctx.SharedContext(comm)
        self.rank = self.comm.Get_rank()

        self.runner = schedule.init_schedule_runner(comm)
        self.runner.schedule_repeating_event(1, 1, self.step)
        self.runner.schedule_stop(params['stop.at'])
        self.runner.schedule_end_event(self.at_end)

        box = space.BoundingBox(
            0, params['world.width'], 0, params['world.height'], 0, 0)
        self.grid = space.SharedGrid('grid', bounds=box, borders=BorderType.Sticky, occupancy=OccupancyType.Multiple,
                                     buffer_size=2, comm=comm)
        self.context.add_projection(self.grid)
        self.space = space.SharedCSpace('space', bounds=box, borders=BorderType.Sticky, occupancy=OccupancyType.Multiple,
                                        buffer_size=2, comm=comm, tree_threshold=100)
        self.context.add_projection(self.space)
        self.ngh_finder = GridNghFinder(0, 0, box.xextent, box.yextent)

        self.counts = Counts()
        loggers = logging.create_loggers(
            self.counts, op=MPI.SUM, rank=self.rank)
        self.data_set = logging.ReducingDataSet(
            loggers, self.comm, params['counts_file'])

        world_size = comm.Get_size()

        total_human_count = params['human.count']
        pp_human_count = int(total_human_count / world_size)
        if self.rank < total_human_count % world_size:
            pp_human_count += 1

        local_bounds = self.space.get_local_bounds()
        for i in range(pp_human_count):
            h = Human(i, self.rank)
            self.context.add(h)
            x = random.default_rng.uniform(
                local_bounds.xmin, local_bounds.xmin + local_bounds.xextent)
            y = random.default_rng.uniform(
                local_bounds.ymin, local_bounds.ymin + local_bounds.yextent)
            self.move(h, x, y)

        total_zombie_count = params['zombie.count']
        pp_zombie_count = int(total_zombie_count / world_size)
        if self.rank < total_zombie_count % world_size:
            pp_zombie_count += 1

        for i in range(pp_zombie_count):
            zo = Zombie(i, self.rank)
            self.context.add(zo)
            x = random.default_rng.uniform(
                local_bounds.xmin, local_bounds.xmin + local_bounds.xextent)
            y = random.default_rng.uniform(
                local_bounds.ymin, local_bounds.ymin + local_bounds.yextent)
            self.move(zo, x, y)

        self.zombie_id = pp_zombie_count

    def at_end(self):
        self.data_set.close()

    def move(self, agent, x, y):
        # timer.start_timer('space_move')
        self.space.move(agent, cpt(x, y))
        # timer.stop_timer('space_move')
        # timer.start_timer('grid_move')
        self.grid.move(agent, dpt(int(math.floor(x)), int(math.floor(y))))
        # timer.stop_timer('grid_move')

    def step(self):
        # print("{}: {}".format(self.rank, len(self.context.local_agents)))
        tick = self.runner.schedule.tick
        self.log_counts(tick)
        self.context.synchronize(restore_agent)

        # timer.start_timer('z_step')
        for z in self.context.agents(Zombie.TYPE):
            z.step()
        # timer.stop_timer('z_step')

        # timer.start_timer('h_step')
        dead_humans = []
        for h in self.context.agents(Human.TYPE):
            dead, pt = h.step()
            if dead:
                dead_humans.append((h, pt))

        for h, pt in dead_humans:
            model.remove_agent(h)
            model.add_zombie(pt)

        # timer.stop_timer('h_step')

    def run(self):
        self.runner.execute()

    def remove_agent(self, agent):
        self.context.remove(agent)

    def add_zombie(self, pt):
        z = Zombie(self.zombie_id, self.rank)
        self.zombie_id += 1
        self.context.add(z)
        self.move(z, pt.x, pt.y)
        # print("Adding zombie at {}".format(pt))

    def log_counts(self, tick):
        # Get the current number of zombies and humans and log
        num_agents = self.context.size([Human.TYPE, Zombie.TYPE])
        self.counts.humans = num_agents[Human.TYPE]
        self.counts.zombies = num_agents[Zombie.TYPE]
        self.data_set.log(tick)

        # Do the cross-rank reduction manually and print the result
        if tick % 10 == 0:
            human_count = np.zeros(1, dtype='int64')
            zombie_count = np.zeros(1, dtype='int64')
            self.comm.Reduce(
                np.array([self.counts.humans], dtype='int64'), human_count, op=MPI.SUM, root=0)
            self.comm.Reduce(np.array(
                [self.counts.zombies], dtype='int64'), zombie_count, op=MPI.SUM, root=0)
            if (self.rank == 0):
                print("Tick: {}, Human Count: {}, Zombie Count: {}".format(tick, human_count[0], zombie_count[0]),
                      flush=True)


def run(params: Dict):
    """Creates and runs the Zombies Model.

    Args:
        params: the model input parameters
    """
    global model
    model = Model(MPI.COMM_WORLD, params)
    model.run()


if __name__ == "__main__":
    parser = create_args_parser()
    args = parser.parse_args()
    params = init_params(args.parameters_file, args.parameters)
    run(params)

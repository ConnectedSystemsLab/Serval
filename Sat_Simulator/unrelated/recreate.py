import src.simulator as simulator
from src.utils import Time

import src.log as log
import gc

startTime = Time().from_str("2022-06-15 13:00:00")
endTime = Time().from_str("2022-06-15 14:00:00")

sim1 = simulator.Simulator.open_stored_simulator('test.txt', 1, startTime, endTime)
sim1.run()
sim1.save_objects("tmp.txt")

print("Done")

gc.collect()

startTime = Time().from_str("2022-06-15 14:00:00")
endTime = Time().from_str("2022-06-15 15:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")
print("Done")

gc.collect()

startTime = Time().from_str("2022-06-15 15:00:00")
endTime = Time().from_str("2022-06-15 16:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")
print("Done")

gc.collect()

startTime = Time().from_str("2022-06-15 16:00:00")
endTime = Time().from_str("2022-06-15 17:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")
print("Done")

gc.collect()

startTime = Time().from_str("2022-06-15 17:00:00")
endTime = Time().from_str("2022-06-15 18:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")
print("Done")

gc.collect()

startTime = Time().from_str("2022-06-15 18:00:00")
endTime = Time().from_str("2022-06-15 19:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")
print("Done")

gc.collect()

startTime = Time().from_str("2022-06-15 19:00:00")
endTime = Time().from_str("2022-06-15 20:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")
print("Done")

gc.collect()


startTime = Time().from_str("2022-06-15 20:00:00")
endTime = Time().from_str("2022-06-15 21:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")
print("Done")

gc.collect()

startTime = Time().from_str("2022-06-15 21:00:00")
endTime = Time().from_str("2022-06-15 22:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")
print("Done")

gc.collect()

startTime = Time().from_str("2022-06-15 22:00:00")
endTime = Time().from_str("2022-06-15 23:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")
print("Done")

gc.collect()

startTime = Time().from_str("2022-06-15 23:00:00")
endTime = Time().from_str("2022-06-16 00:00:00")

sim2 = simulator.Simulator.open_stored_simulator('tmp.txt', 1, startTime, endTime)
sim2.run()
sim2.save_objects("tmp.txt")

log.plot_collisions()
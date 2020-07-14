import yt
from matplotlib import pyplot as plt

yt.enable_plugins()

ts = yt.load("DD????/output_????")

index_list = []
mass_dict = {}
total = 0
for ds in ts:
    try:
        ad = ds.all_data()
        time = ds.current_time.to('Myr')
        indices = ad['SmartStar','particle_index']
        masses = ad['SmartStar','particle_mass'].to("Msun")
    except:
        continue
    for i in range(len(indices)):
        if ((indices[i] not in index_list) and (masses[i] > 0.5)):
            total += 1
            print("Total stars = " + str(total))
            index_list.append(indices[i])
            mass_dict[int(indices[i])]=([],[])
    for j in range(len(index_list)):
        if (index_list[j] in indices):
            pos = list(indices).index(index_list[j])
            mass_dict[int(index_list[j])][0].append(time)
            mass_dict[int(index_list[j])][1].append(masses[pos])

fig = plt.figure()
for i in range(len(index_list)):
	plt.plot(mass_dict[int(index_list[i])][0],mass_dict[int(index_list[i])][1],label = "{:.2f}".format(mass_dict[int(index_list[i])][1][-1]))

plt.xlabel("Time (Myr)")
plt.yscale("log")
plt.ylabel("Mass (Msun)")
plt.legend()
plt.savefig("Feedback_Masses.png")

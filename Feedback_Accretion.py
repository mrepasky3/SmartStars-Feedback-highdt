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

acc_dict = {}
for i in range(len(index_list)):
    acc_dict[int(index_list[i])] = ([],[])
    for j in range(1,len(mass_dict[int(index_list[i])][0])):
        acc_dict[int(index_list[i])][0].append(mass_dict[int(index_list[i])][0][j]) # append the time
        time_diff = (mass_dict[int(index_list[i])][0][j] - mass_dict[int(index_list[i])][0][j-1]).to("yr")
        mass_diff = mass_dict[int(index_list[i])][1][j] - mass_dict[int(index_list[i])][1][j-1]
        acc_rate = mass_diff / time_diff
        acc_dict[int(index_list[i])][1].append(acc_rate) # append the acc rate 
        
for i in range(len(index_list)):
    plt.plot(acc_dict[int(index_list[i])][0],acc_dict[int(index_list[i])][1],label = "{:.2f}".format(mass_dict[int(index_list[i])][1][-1]))

plt.xlabel("Time (Myr)")
plt.ylabel("Accretion Rate (Msun/yr)")
plt.yscale('log')
plt.legend(fontsize='small')
plt.savefig("Feedback_Accretion.png")

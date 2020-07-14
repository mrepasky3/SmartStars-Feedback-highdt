import yt
import os
import numpy as np
from matplotlib import pyplot as plt

yt.enable_plugins()

outdir = "profiles/"

if not os.path.exists(outdir):
    os.mkdir(outdir)

ts = yt.load("DD????/output_????")


#big_list = ['density',
big_list = ['temperature','H2_fraction']
ext_dict = {}

for field in big_list:
    maxlist = []
    minlist = []
    for ds in ts:
        maxlist.append(ds.find_max(field)[0])
        minlist.append(ds.find_min(field)[0])
    high = max(maxlist)
    low = min(minlist)
    ext_dict[field] = (low,high)

ext_dict['radial_velocity'] = (-10,10)
#ext_dict = {'density':(1e-23,3e-17),'temperature':(1e2,1e4),'H2_fraction':(1e-4,1e-2),'radial_velocity':(-3,0)}

def makeprofile(field):
    low = ext_dict[field][0]
    high = ext_dict[field][1]

    for ds in ts:
        tstring = str(ds)[7:11]
        #decide where to center the profile
        ad = ds.all_data()

        ss_exist = False
        for f in ds.field_list:
            if f[0] == 'SmartStar':
                ss_exist = True
                break

        if not ss_exist:
            gi = (ds.index.grid_levels >= ds.max_level-3).ravel()
            co = ds.data_collection(ds.index.grids[gi])
            rhomax, x, y, z = co.quantities.max_location('density')
            pos = ds.arr([x,y,z])
        else:
            mm = ad['SmartStar','particle_mass'].argmax()
            pos = ad['SmartStar','particle_position'][mm]

        sp = ds.sphere(pos,(5,'pc'))

        #find min bin size
        min_dx, max_dx = sp.quantities.extrema('dx')
        #min_dx = min_dx.to('pc')
        min_dx = ds.quan(0.03,'pc')
        

        prof = yt.create_profile(sp, 'radius',field, extrema={'radius': (min_dx,5),field:(low,high)})
        shift = str(ds.current_redshift)

        pp = yt.ProfilePlot.from_profiles(prof)
        pp.annotate_title(shift)
        pp.set_ylim(field,low,high)
        pp.set_unit('radius','pc')
        pp.set_xlim(min_dx,5)

        pp.save(tstring)
        os.rename(tstring+"_1d-Profile_radius_"+field+".png",outdir+tstring+"_"+field+".png")

def velocityplot(field):
    low = ext_dict[field][0]
    high = ext_dict[field][1]

    for ds in ts:
        tstring = str(ds)[7:11]
        #decide where to center the profile
        ad = ds.all_data()

        ss_exist = False
        for f in ds.field_list:
            if f[0] == 'SmartStar':
                ss_exist = True
                break

        if not ss_exist:
            gi = (ds.index.grid_levels >= ds.max_level-3).ravel()
            co = ds.data_collection(ds.index.grids[gi])
            rhomax, x, y, z = co.quantities.max_location('density')
            pos = ds.arr([x,y,z])
        else:
            mm = ad['SmartStar','particle_mass'].argmax()
            pos = ad['SmartStar','particle_position'][mm]

        sp0 = ds.sphere(pos,(5,'pc'))
        bulk_vel = sp0.quantities.bulk_velocity()
        sp1 = ds.sphere(pos,(5,'pc'))
        sp1.set_field_parameter('bulk_velocity', bulk_vel)

        #find min bin size
        min_dx, max_dx = sp1.quantities.extrema('dx')
        #min_dx = min_dx.to('pc')
        min_dx = ds.quan(0.03,'pc')
        minimum = np.array(min_dx)

        rp = yt.create_profile(sp1, 'radius', field, units = {'radius':'pc'}, extrema={'radius': (min_dx,5)})
        shift = str(ds.current_redshift)

        #make plot
        fig = plt.plot(rp.x.value, rp[field].in_units("km/s").value)
        plt.xlabel(r"$\mathrm{r\ (pc)}$")
        plt.ylabel(r"$\mathrm{v\ (km/s)}$")
        plt.title(shift)
        plt.xlim(minimum,5)
        plt.ylim(low,high)
        plt.xscale('log')
        plt.savefig("%s_profile.png" % ds)

        os.rename("output_"+tstring+"_profile.png",outdir+tstring+"_"+field+".png")
        plt.close()


#makeprofile('density')
makeprofile('temperature')
makeprofile('H2_fraction')
velocityplot('radial_velocity')

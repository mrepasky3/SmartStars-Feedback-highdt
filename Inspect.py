import yt
import os
yt.enable_plugins()
yt.enable_parallelism()

centering = 'most_massive_star'
#centering = 'densest_point'

ts = yt.DatasetSeries('DD????/output_????')
for ds in ts.piter(dynamic=True):
    skip = True
    for dim in 'xyz':
        fname = 'pics-5pc/%s_Projection_%s_temperature_density.png' % (str(ds), dim)
        skip &= os.path.exists(fname)
    if skip:
        continue
    ss_exist = False
    for f in ds.field_list:
        if f[0] == 'SmartStar':
            ss_exist = True
            break
    if centering == 'densest_point' or not ss_exist:
        gi = (ds.index.grid_levels >= ds.max_level-3).ravel()
        co = ds.data_collection(ds.index.grids[gi])
        rhomax, x, y, z = co.quantities.max_location('density')
        pos = ds.arr([x,y,z])
    elif centering == 'most_massive_star':
        ad = ds.all_data()
        mm = ad['SmartStar', 'particle_mass'].argmax()
        pos = ad['SmartStar', 'particle_position'][mm]
    #pos = ds.arr([0.5,0.5,0.5],'unitary')
    width = ds.quan(5, 'pc')
    #width = ds.quan(0.25, 'unitary')
    #width = ds.quan(50, 'pc')
    #vel_scale = ds.quan(1, 'km/s')
    reg = ds.region(pos, pos-0.75*width, pos+0.75*width)
    bv = reg.quantities.bulk_velocity()
    reg.set_field_parameter('bulk_velocity', bv)
    if ss_exist:
        print(reg['SmartStar', 'particle_mass'].to('Msun'))
        print(reg['SmartStar', 'age'].to('kyr'))
        mm = reg['SmartStar', 'particle_mass'].argmax()
        mass = reg['SmartStar', 'particle_mass'][mm]
        age = reg['SmartStar', 'age'][mm]

    for dim in 'xyz':
        fname = 'pics-5pc/%s_Projection_%s_temperature_density.png' % (str(ds), dim)
        if os.path.exists(fname):
            continue
        proj = yt.ProjectionPlot(ds, dim, ['density', 'temperature', 'tangential_velocity', 'radial_velocity'], weight_field='density',
                                 center=pos, width=width, data_source=reg)
        #proj.set_log('temperature', False)
        proj.set_cmap('temperature', 'inferno')
        #proj.set_zlim('temperature', 100, 1000)
        proj.set_log('radial_velocity', False)
        proj.set_cmap('radial_velocity', 'RdGy')
        proj.set_unit('radial_velocity', 'km/s')
        proj.set_zlim('radial_velocity', -5, 5)
        proj.set_log('tangential_velocity', False)
        proj.set_cmap('tangential_velocity', 'Purples')
        proj.set_unit('tangential_velocity', 'km/s')
        proj.set_zlim('tangential_velocity', 0, 10)
        proj.set_cmap('density', 'turbo')
        #proj.set_zlim('density', 1e-22, 1e-17)
        #proj.set_zlim('density', 1e-24, 1e-17)
        proj.set_colorbar_minorticks('temperature', True)
        proj.annotate_velocity(plot_args={'color':'k', 'alpha':0.2})
        #proj.annotate_line_integral_convolution('velocity_x', 'velocity_y', alpha=0.2)
        if ss_exist:
            proj.annotate_particles(width=width, ptype='SmartStar', p_size=25)
            proj.annotate_title(r'Most massive: M$_\star$ = %.3g M$_\odot$, age = %.3g kyr' % (mass.to('Msun'), age.to('kyr')))
        else:
            proj.annotate_title('No stars')
        proj.annotate_timestamp(redshift=True, time=False, draw_inset_box=True,
                            redshift_format='z = {redshift:.5f}')
        proj.save('pics-5pc/%s' % (str(ds)))
